from ftplib import FTP

from storage.FileManager import FileManager


class FtpFileManager(FileManager):
    def __init__(self, conn_string):
        super().__init__(conn_string)
        self.conn_string = conn_string
        prefix, self.user, passwd_and_location = conn_string.split(':')
        self.passwd, self.location = passwd_and_location.split('@')

    def setup(self):
        ftp = FTP(host=self.location, user=self.user, passwd=self.passwd)
        ftp.login()

    def get_all_files_metadata(self):
        pass

