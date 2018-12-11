from threading import Thread, current_thread

from analysis.DBhandler import DbHandler
from analysis.localization import analyze


class Analyzer:
    def __init__(self, queue, cv, config, db_persistence=False):
        self.config = config

        self.queue = queue
        self.cv = cv
        self.db_persistence = db_persistence
        self.thread = Thread(target=self.run, args=(self.queue,))

    def start(self):
        if not self.db_persistence:
            try:
                with DbHandler(self.config, self.db_persistence) as dh:
                    dh.createDatabase()
                    dh.createTable()
                    print("Connected to database")
                    print("Created Table and Database")
            except Exception as e:
                print(e)
                print("Unable to connect do database")
        self.thread.start()

    def run(self, queue):
        t = current_thread()
        entries = []
        while getattr(t, "do_run", True):
            print("Analyzer running")
            with self.cv:
                print("Analyzer go to sleep")
                self.cv.wait_for(lambda: not queue.empty() or not getattr(t, "do_run", True), timeout=5)
            print("Analyzer woke up")
            while not queue.empty():
                try:
                    time_frame_analysis = queue.get(timeout=2)
                except Exception as e:
                    print(e)
                    continue
                queue.task_done()

                analyzed_entries = analyze(time_frame_analysis, self.config)

                entries += analyzed_entries
            # If there is at least something to send, i send data to database
            print("is there something to send to the database?")
            if len(entries) > 0:
                print("YES, there is something to send to the database")
                try:
                    print(self.db_persistence)
                    with DbHandler(self.config, persistence=self.db_persistence) as dh:
                        print("Connected to database")
                        dh.insert(entries)
                        print("Data inserted to the database with success")
                        entries = []
                except Exception as e:
                    print(e)
                    print("Unable to send entries, retrying the next time")

    def stop(self):
        print("Stopping Analyzer!")
        self.thread.do_run = False
        with self.cv:
            self.cv.notify()
        self.thread.join()
