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

file_list = drive.ListFile({'q': f"'{sys.argv[1]}' in parents and trashed=false"}).GetList()

while not len(file_list) == 0: #for file1 in file_list:

    file1 = file_list.pop(0)

    try:

        if file1['mimeType'] == 'application/vnd.google-apps.folder': # is directory
            file_list.extend (  drive.ListFile({'q': f"'{file1['id']}' in parents and trashed=false"}).GetList() )
            print (f"found subdir {file1['title']}. indexed.")
            continue

        if os.path.exists(file1['title']) and os.path.getsize(file1['title']) > 0:
            print(f"{file1['title']} exists, skipping")
            continue

        print('title: %s, id: %s, mt %s' % (file1['title'], file1['id'], file1['mimeType']))

        if gauth.access_token_expired:
            gauth.Refresh()

        file6 = drive.CreateFile({'id': file1['id']})
        file6.GetContentFile(file1['title']) # note: no directory structures here

    except Exception as e:

        print (f"failed to download {file1['title']}; sent to back of queue:\n {e}")
        file_list.append (file1)
        time.sleep(1)


