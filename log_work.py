from __future__ import print_function
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


class ExitLog:
  '''Writtes a log file in the Termination logs folder in G Drive'''
  def __init__(self, email, text):
    # If modifying these scopes, delete the file gd_token.json.
    SCOPES = ['https://www.googleapis.com/auth/drive']

    creds = Credentials.from_authorized_user_file('gd_token.json', SCOPES)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
      'name': email,
      'parents': ['1FoAZRghwvL-qMnAFe4OiXyHoibi8rvJC'],
      'mimeType': 'application/vnd.google-apps.document'
    }

    # Call the Drive v3 API
    results = None
    try:
      results = service.files().create(body=file_metadata, fields='id', supportsAllDrives=True).execute()
      print(results)
    except:
      pass

    # The ID of the document.
    DOCUMENT_ID = results['id']

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/documents']

    creds = Credentials.from_authorized_user_file('doc_token.json', SCOPES)

    service = build('docs', 'v1', credentials=creds)

    requests = [
      {
        'insertText': {
          'location': {
            'index': 1,
          },
          'text': text

        }

      },
    ]
    try:
      result = service.documents().batchUpdate(documentId=DOCUMENT_ID, body={'requests': requests}).execute()
      print(result)
    except:
      pass
