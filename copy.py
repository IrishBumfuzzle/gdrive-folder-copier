from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

source_id = "1Okx1aY4ceaDq27ZXZtNaVGbQYOy5aZQG"
parent_id = "1YKDeCD-nbJNccawtC6Vz7Hsk_BCAoIDO"
prefix = ""

gauth = GoogleAuth()

gauth.LoadCredentialsFile("creds.json")

if gauth.credentials is None:
    gauth.CommandLineAuth()

elif gauth.access_token_expired:
    gauth.Refresh()

else:
    gauth.Authorize()

drive = GoogleDrive(gauth)

def copy_file(service, source_id, parent_folder_id):
    source = drive.CreateFile({'id': source_id})
    source.FetchMetadata('title')
    print('title: %s, id: %s' % (source['title'], source['id']))
    
    dest_title = prefix + source['title']
    copied_file = {'title': dest_title, 'parents': [{'id': parent_folder_id}]}
    f = service.files().copy(fileId=source_id, supportsAllDrives=True, body=copied_file).execute()

    print('title: %s, id: %s' % (f['title'], f['id']))

def copy_folder(folder, parent_id):
    print('title: %s, id: %s' % (folder['title'], folder['id']))
    dest_file = prefix + folder['title']
    folder1 = drive.CreateFile({'mimeType': 'application/vnd.google-apps.folder', 'title': dest_file , 'parents': [{'id': parent_id}]})
    folder1.Upload()
    print('title: %s, id: %s' % (folder1['title'], folder1['id']))
    return folder1['id']


subfolders = {}

def copy_from_folder(folder_id, parent_folder_id):
    file_list = drive.ListFile({'corpora': "allDrives", 'q': "'%s' in parents and trashed = false" % (folder_id) }).GetList()

    for file1 in file_list:
        if file1['mimeType'] == 'application/vnd.google-apps.folder':
            copied_folder = copy_folder(file1, parent_folder_id)
            original_folder = file1['id']
            copy_from_folder(original_folder, copied_folder)
        else:
            copy_file(drive.auth.service, file1['id'], parent_folder_id)

copy_from_folder(source_id, parent_id)