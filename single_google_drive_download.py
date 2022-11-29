from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os, time, sys

gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.CommandLineAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()

    # Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)

try:

    file6 = drive.CreateFile({'id': sys.argv[1]})
    file6.GetContentFile(sys.argv[1])  # note: no directory structures here

except Exception as e:
    print(traceback.format_exc())


