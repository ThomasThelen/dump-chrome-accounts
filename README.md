# Dump Chrome Accounts
Dumps accounts stored in Google Chrome to Dropbox or disk 

## Background
Google Chrome stores saved account information in a sqllite database stored at ``a``. The database stores the passwords in an encrypted form. The passwords are encrypted using the Win32 method, `CryptProtectData`. The passwords can be decrypted using `CryptUnprotectData`, as long as it's done on the same user account that was used to encrypt them.

## Usage

Create an instance of the `ChromeAccountDatabase` class to load and parse the database. 

`chrome_database = ChromeAccountDatabase()`

To show the accounts inside the database, print the `ChromeAccountDatabase` object 

`print(chrome_database)`

To upload the accounts to Dropbox, pass the API key to `ChromeAccountDatabase::to_dropbox`

` chrome_database.to_dropbox(API_KEY)`

To save locally as a csv with a defualt filename

`chrome_database.to_csv()`

or specify a custom filepath,

`chrome_database.to_csv()`

To get the accounts as a string stream,

`csv_stream: StringIO = chrome_database.to_csv(as_stream=True)`
