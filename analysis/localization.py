from random import uniform
from math import sqrt
from itertools import combinations
from functools import reduce
from statistics import mean

def getD(rssi, d0 = 1, n = 5.4,a = -41):
    return d0 * 10 ** ((a - rssi) / (n * 10))


def getXY(room_id, rssi_measures, esp_ids, config):
    # save in a local variable much the room is big
    x_room = config["room"][room_id]["X"]
    y_room = config["room"][room_id]["Y"]

    x = -1.
    y = -1.

    measures = list()

    for espid, rssi in zip(esp_ids, rssi_measures):
        x_esp = float(config["room"][room_id]["EspCoor"][espid]["X"])
        y_esp = float(config["room"][room_id]["EspCoor"][espid]["Y"])
        d = int(rssi)
        measures.append((x_esp, y_esp, d))

    # calculate x and y
    if len(measures) == 1:
        # wtfcase, i put a random point in the room
        if measures[0][2] >= -90:
            x, y = uniform(0, float(x_room)), uniform(0, float(y_room))
            return x, y
        else:
            return -1, -1
        
    # len == 2, when we have just two esp we have a circumference that gives two analytic solution to the trilateration
    elif len(measures) == 2:
        results = []
        num_measures = 0

        for measure in measures:
            if measure[2] < -100:
                continue
            # number between 0 and 1
            local = get_trilateration_local_coordinate(measure[2], config)

            x_src = measure[0]
            y_src = measure[1]

            # line directed toward the opposite direction
            x_dest = abs(x_room - x_src)
            y_dest = abs(y_room - y_src)

            x = local * x_dest + (1 - local) * x_src
            y = local * y_dest + (1 - local) * y_src
            # DEBUG
            # print("x, y : ", x, y, "\n\n")
            # print("Source x,y: ", x_src, y_src, " Destionation: ", x_dest, y_dest)
            # print("Local coordinate: ", local)
            num_measures += 1

            results.append((x, y))
        print(results)
        final_result = reduce(lambda val_1, val_2: (val_1[0] + val_2[0], val_1[1] + val_2[1]), results)
        # Some pruning can be done before to send data to database
        return final_result[0] / num_measures, final_result[1] / num_measures

    elif len(measures) == 3:
        x, y = get_trilateration(measures[0], measures[1], measures[2])

    elif len(measures) > 3:
        # normal case, with 3 or more
        Xp = 0.0
        Yp = 0.0
        N = 0.0
        for three_result in combinations(measures, 3):
            xp, yp = get_trilateration(three_result[0], three_result[1], three_result[2])
            if xp != -1:
                N = N + 1
                Xp += xp
                Yp += yp
        x, y = (Xp / N), (Yp / N)

    if x >= 0. and x <= x_room and y >=0. and y <= y_room:
        return x, y
    else:
        return getXY_new(room_id, rssi_measures, esp_ids, config)


def calculate_m(y2, y1, x2, x1):
    return (1.0 * y2 - y1) / (1.0*x2 - x1)


def calculate_k(m):
    return 1.0 / sqrt(1 + m**2)


def geta(x1, y1, r1, x2, y2, r2):
    return r1 ** 2 - r2 ** 2 - x1 ** 2 + x2 ** 2 - y1 ** 2 + y2 ** 2

def get_trilateration(measure1, measure2, measure3, type='circumference'):
    if type == 'circumference':
        try:
            x1, y1, r1 = list(map(lambda value: float(value), measure1))
            x2, y2, r2 = list(map(lambda value: float(value), measure2))
            x3, y3, r3 = list(map(lambda value: float(value), measure3))
            r1 = getD(r1)
            r2 = getD(r2)
            r3 = getD(r3)
        except Exception as e:
            print(e)
            print('Error while parsing measures')
            print(measure1, measure2, measure3)
            return -1., -1.
        a12 = geta(x1, y1, r1, x2, y2, r2)
        a13 = geta(x1, y1, r1, x3, y3, r3)

        try:
            xp = (a12 * (y1 - y3) - a13 * (y1 - y2)) / (2 * ((y1 - y2) * (x1 - x3) - (x1 - x2) * (y1 - y3)))
            yp = (a12 * (x1 - x3) - a13 * (x1 - x2)) / (2 * ((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)))
        except Exception as e:
            print(e)
            xp, yp = -1, -1

        return xp, yp
    else:
        # unknown type
        return -1., -1.


def get_trilateration_local_coordinate(rssi, config, type_measure='0-1_mapping'):
    if type_measure == '0-1_mapping':
        # The interest only in the RSSI
        try:
            z_max = float(abs(config['z_max'])) ** (1. / 1.)
            z_off = float(config['z_off'])
        except Exception as e:
            print('parameter z_off or z1 or z0 not set')
            return -1., -1.
        z = (abs(rssi - z_off)) ** (1. / 1.)

        #print(z)
        #m = 1. / (z_1 - z_0)
        #local_coordinate = m * (z - z_0)
        local_coordinate = z / z_max
        return round(local_coordinate, 3)
    else:
        # Unknown type of trialteration
        return -1.

def getXY_new(room_id, rssi_measures, esp_ids, config):
    # save in a local variable much the room is big
    x_room = config["room"][room_id]["X"]
    y_room = config["room"][room_id]["Y"]

    measures = []
    results = []
    num_measures = 0

    for espid, rssi in zip(esp_ids, rssi_measures):
        x_esp = float(config["room"][room_id]["EspCoor"][espid]["X"])
        y_esp = float(config["room"][room_id]["EspCoor"][espid]["Y"])
        rssi = int(rssi)
        measures.append((x_esp, y_esp, rssi))

    for measure in measures:
        if measure[2] < -100:
            continue
        # number between 0 and 1
        local = get_trilateration_local_coordinate(measure[2], config)

        x_src = measure[0]
        y_src = measure[1]

        # line directed toward the opposite direction
        x_dest = abs(x_room - x_src)
        y_dest = abs(y_room - y_src)

        x = local * x_dest + (1 - local) * x_src
        y = local * y_dest + (1 - local) * y_src
        # DEBUG
        # print("x, y : ", x, y, "\n\n")
        # print("Source x,y: ", x_src, y_src, " Destionation: ", x_dest, y_dest)
        # print("Local coordinate: ", local)
        num_measures += 1

        results.append((x, y))
    print(results)
    final_result = reduce(lambda val_1, val_2: (val_1[0]+val_2[0], val_1[1]+val_2[1]), results)
    # Some pruning can be done before to send data to database
    return final_result[0] / num_measures, final_result[1] / num_measures


def analyze(time_frame_analysis, config):
    # values format
    # ESPID | MAC | SSID | TIMESTAMP | HASH | RSSI | SN | HTCI

    # initializing empty entries list
    entries = []
    num_esp = time_frame_analysis.numEsp
    room_id = time_frame_analysis.roomid

    # DEBUG
    print("sniffed packet ready to be analyzed")
    fd = time_frame_analysis.getDataFrame()

    grouped_fd = fd.groupby(['HASH'])

    # it's supposed there is no conflicts
    for device in grouped_fd:
        device_fd = device[1]

        rssi_measurements = device_fd['RSSI'].tolist()
        esp_ids = device_fd['ESPID'].tolist()
        if len(rssi_measurements) == num_esp:
            #x, y = getXY_new(room_id, rssi_measurements, esp_ids, config)
            x, y = getXY(room_id, rssi_measurements, esp_ids, config)
            mac = device_fd['MAC'].tolist()[0]
            hash = device[0]
            tid = int(device_fd['TIMESTAMP'].tolist()[0])
            sn = device_fd['SN'].tolist()[0]
            htci = device_fd['HTCI'].tolist()[0]

            if x > 0. and y > 0.:
                entry = (hash, mac, tid, room_id, x, y, sn, htci)
                entries.append(entry)
    return entries
