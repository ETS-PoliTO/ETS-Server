import mysql.connector
# from mysql.connector import errorcode


class DbHandler:

    def __init__(self, config, persistence=False):
        self.config = config
        self.persistence = persistence

    def __enter__(self):
        print("connessione al database")
        if self.persistence:
            try:
                self.mydb = mysql.connector.connect(
                    host=self.config["host"],
                    user=self.config["username"],
                    password=self.config["password"],
                    database="pds"
                    # ,auth_plugin = "mysql_native_password"
                )
                self.mycursor = self.mydb.cursor()
                return self
            except:
                raise Exception("Problemi di connessione!")
        else:
            try:
                self.mydb = mysql.connector.connect(
                    host=self.config["host"],
                    user=self.config["username"],
                    password=self.config["password"],
                    # ,auth_plugin = "mysql_native_password"
                )
                self.mycursor = self.mydb.cursor()
                return self
            except Exception as e:
                print(e)
                raise Exception("Problemi di connessione!")


    def createDatabase(self):
        self.mycursor.execute("CREATE DATABASE IF NOT EXISTS pds")

    def createTable(self):
        if not self.persistence:
            try:
                self.mycursor.execute("USE pds")
                self.mycursor.execute("DROP TABLE IF EXISTS devices")
                self.mycursor.execute("CREATE TABLE devices ("
                                      "HASH VARCHAR(256),"
                                      "MAC VARCHAR(256), "
                                      "TID INTEGER(200), "
                                      "ROOMID VARCHAR(16),"
                                      "X DECIMAL(7, 4), "
                                      "Y DECIMAL(7 ,4),"
                                      "SN INTEGER(200),"
                                      "HTCI VARCHAR(50),"
                                      "primary key (TID, HASH)"
                                      ")")
            except Exception as e:
                print(e)
                exit(1)
        print("table created/reset with success")


    def insert (self, value):
        mycursor = self.mydb.cursor()
        sql_formula = "INSERT INTO devices (HASH, MAC, TID, ROOMID, X, Y, SN, HTCI) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            mycursor.execute("USE pds")
            print("Trying to insert this")
            print(value)
            mycursor.executemany(sql_formula, value)
            self.mydb.commit()
        except Exception as e:
            print(e)
            self.mydb.rollback()
            raise e
        mycursor.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mydb.close()

