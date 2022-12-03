from datetime import datetime
from ftplib import FTP

from storage.FileManager import FileManager

DEFAULT_PORT = 21

DEFAULT_TIMEOUT = 30


class FtpFileManager(FileManager):
    def __init__(self, conn_string):
        super().__init__(conn_string)
        self.conn_string = conn_string
        prefix, self.user, passwd_and_host = conn_string.split(':')
        self.passwd, self.host = passwd_and_host.split('@')
        self.ftp = FTP(timeout=DEFAULT_TIMEOUT)
        self.metadata = dict()
        self.current_dirs = []

    def setup(self):
        self.ftp.connect(host=self.host, port=DEFAULT_PORT)
        self.ftp.login(user=self.user, passwd=self.passwd)

    @staticmethod
    def to_mili_from_str(input_date: str, input_hour: str):
        date_time = [int(element) for element in input_date.split('-')]
        date_time.reverse()
        date_time[0] += 2000

        delta_hour = 0
        if input_hour.endswith('PM'):
            delta_hour += 12
        hour, minuntes = input_hour.split(':')
        minutes = minuntes[:-2]
        date_time.extend([int(hour) + delta_hour, int(minutes)])

        return (datetime(date_time[0], month=date_time[1], day=date_time[2], hour=date_time[3], minute=date_time[4]) -
                datetime(1970, month=1, day=1)).total_seconds()

    def __get_all_files_metadata__(self):
        content = []

        self.ftp.dir('.', content.append)
        data = [list(filter(lambda x: x != '', element.split(' ')))
                for element in content]

        files_data = [element for element in data if "DIR" not in element[2]]
        self.metadata = {file_data[3]: self.to_mili_from_str(file_data[0], file_data[1])
                         for file_data in files_data}

    def dive_into_dir(self, child_dir: str):
        self.ftp.cwd(child_dir)

    def leave_dir(self):
        self.ftp.cwd("..")

    def retrieve_file(self, file: str, fd):
        self.ftp.retrbinary(f"RETR {file}", fd.write)

    def save_file(self, file, fd):
        self.ftp.storbinary(f'STOR {file}', fd)

    def create_dir(self, directory):
        self.ftp.mkd(directory)

    def get_all_files_metadata(self):
        self.metadata = dict()
        self.__get_all_files_metadata__()
        self.ftp.close()
        return self.metadata
