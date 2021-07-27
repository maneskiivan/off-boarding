import requests
import os


token = os.environ.get('token')


class ExitZoom:
  '''Deletes the account and transfers the recording to itsupport'''
  def __init__(self, email):
    self.results = None
    url = f'https://api.zoom.us/v2/users/{email}'

    headers = {
      'Accept': 'application/json',
      'Authorization': f'Bearer {token}'
    }

    query = {
      'action': 'delete',
      'transfer_email': 'test@example.com',
      'transfer_recording': True
    }

    response = requests.delete(
      url,
      headers=headers,
      params=query,
    )

    if str(response) == '<Response [204]>':
      self.results = 'Zoom Deleted'
    elif str(response) == '<Response [404]>':
      self.results = 'N/A'
    else:
      self.results = 'Did not execute Zoom offboarding'
