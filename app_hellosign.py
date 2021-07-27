import requests
import json
import os


hello_sign_apikey = os.environ.get('hello_sign_apikey')


class ExitHS:
  '''Removes the account and transfers the data to the specified account'''
  def __init__(self, email):
    self.results = None
    url = f"https://{hello_sign_apikey}:@api.hellosign.com/v3/team/remove_member"
    try:
      req = requests.post(url,
                          data={
                            # ACCOUNT ID OR EMAIL ADDRESS ACCEPTED TO SPECIFY TEAM MEMBER FOR REMOVAL
                            "email_address": email,
                            "new_owner_email_address": 'imaneski@gumgum.com',
                          })
      response = json.loads(req.text)
      if 'team' in response.keys():
        self.results = 'HelloSign Deleted'
      elif 'error' in response.keys():
        if response['error']['error_name'] == 'not_found':
          self.results = 'N/A'
        elif response['error']['error_msg'] == 'Unauthorized api key':
          self.results = 'Did not execute HelloSign offboarding'
    except:
      self.results = 'Did not execute HelloSign offboarding'
