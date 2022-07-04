import csv
from datetime import datetime


class Logger:


    def initializeLog(self, file_name: str):
        # write the header of CSV file
        self.file_name = file_name
        with open(self.file_name, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "RR"])

    def write(self, rr: float, record_time: datetime):
        # add data to the CSV file
        with open(self.file_name, 'a', newline='') as f:
            writer = csv.writer(f)
            ts = datetime.timestamp(record_time)
            writer.writerow([str(ts), str(rr)])
            f.close()
