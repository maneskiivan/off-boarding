import requests
import json
import os


lastpass_token = os.environ.get('lastpass_token')


class ExitLP:
  '''Disables the LastPass account'''
  def __init__(self, email):
    self.results = None
    url = 'https://lastpass.com/enterpriseapi.php'

    payload = json.dumps(
      {
        "cid": 11111111,
        "provhash": lastpass_token,
        "cmd": "deluser",
        "data": {
          "username": email,
          "deleteaction": 0
        }
      }
    )

    response = requests.post(url, data=payload)
    if response.text == '{"status":"OK"}' or response.text == '{"status":"OK","error":"User already disabled: ' + email + '"}':
      self.results = 'LastPass Disabled'
    elif response.text == '{"status":"FAIL","error":"No such user: ' + email + '"}':
      self.results = 'N/A'
    else:
      self.results = 'Did not execute LastPass offboarding'
