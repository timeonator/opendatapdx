# https://erlerobotics.gitbooks.io/erle-robotics-python-gitbook-free/telnet_and_ssh/sftp_file_transfer_over_ssh.html
# Was used as a reference.

import functools
import paramiko
from tempfile import TemporaryFile
import requests
from urllib.parse import urlparse
from . import schema_generator
import logging


class AllowAnythingPolicy(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        return


class FailedDownloadingFileException(Exception):
    """The exception raised if there is an error with downloading the file"""
    def __init__(self, *args):
        self.args = args


class FileDownloader:
    """This class functionality is to read supported file types into temporary files."""

    @staticmethod
    def download_temp(url, sftp_username=None, sftp_password=None):
        """Parses the url and downloads the file into a temporary file."""
        try:
            # It then attempts to parse the url with the urllib library.
            parsed_url = urlparse(url)
        except Exception as e:
            logging.error('Failed to parse url: ' + str(e))
            # If it fails, it sends a message back.
            raise FailedDownloadingFileException('The provided url is not in a recognized format.')
        # If the file doesn't end with a supported type, it throws an error.
        if not parsed_url.path.lower().split('?')[0].endswith(schema_generator.SchemaGenerator.valid_extensions):
            raise FailedDownloadingFileException('The provided URL does not point to a supported file type.')
        if parsed_url.scheme.lower() == 'https':
            return FileDownloader.__https_file_downloader(url)
        elif parsed_url.scheme.lower() == 'sftp':
            return FileDownloader.__sftp_file_downloader(parsed_url, sftp_username, sftp_password)
        else:
            raise FailedDownloadingFileException('The provided URL does not use a https nor a sftp schema.')

    @staticmethod
    def __https_file_downloader(url):
        """Takes in a given https url and downloads the file into a temporary file."""
        try:
            output = TemporaryFile()
            # attempts to open the file using the url.
            file = requests.get(url, stream=True)
            # writes the file into the temporary file in chunks.
            for chunk in file.iter_content(chunk_size=1024):
                output.write(chunk)
            # returns the start of the file before returning the temporary file.
            output.seek(0)
            return output
        except Exception as e:
            logging.error('Failed to download https file: ' + str(e))
            # if there is any errors in the above process, an exception is raised.
            raise FailedDownloadingFileException('An error occurred while downloading the file from a https url.')

    @staticmethod
    def __sftp_file_downloader(parsed_url, sftp_username, sftp_password):
        """Takes in a given sftp url and downloads the file into a temporary file."""
        # Assumes sftp if sftp_* inputs into the method aren't None.
        # The format of the URL for sftp is sftp://[host]:[port]/[path to file] which is defined in the Uniform Resource
        # Identifier schemes.
        # https://www.iana.org/assignments/uri-schemes/prov/sftp
        try:
            # Attempts to open a connection to the sftp server.
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(AllowAnythingPolicy())
            # If a username isn't provided, it tried to parse one from the url.
            if sftp_username == "" and parsed_url.username != None:
                sftp_username = parsed_url.username
            if parsed_url.port is not None:
                client.connect(hostname=parsed_url.hostname, port=parsed_url.port, username=sftp_username,
                               password=sftp_password)
            else:
                client.connect(hostname=parsed_url.hostname, username=sftp_username, password=sftp_password)
            # Creates a temporary file and attempts to open the file using the given file path. It then copies it into
            # the temporary file.
            sftp = client.open_sftp()
            fileobject = sftp.file(parsed_url.path[1:], 'rb')
            temp_file = TemporaryFile()
            for chunk in fileobject.xreadlines():
                temp_file.write(chunk)
            
            # Closes the connection to the server and navigates back to the top of the file before returning the
            # temporary file.
            client.close()
            temp_file.seek(0)
            return temp_file
        except Exception as e:
            logging.error('Failed to download sftp file: ' + str(e))
            # if there is any errors in the above process, an exception is raised.
            raise FailedDownloadingFileException('An error occurred while downloading the file from a sftp url.')
