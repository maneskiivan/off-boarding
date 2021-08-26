import requests
from requests.auth import HTTPBasicAuth
import random
import string
import json
import os


jira_api_email = os.environ.get('jira_api_email')
jira_api_token = os.environ.get('jira_api_token')
api_key = os.environ.get('api_key')


class ExitJira:
  '''Retreives the data from the new hire ticket, comments and transition the ticket'''
  def __init__(self, issue_key):
    '''Gets the required fields from the POE issue. Assigns them to the appropriate variables.'''
    self.results = None
    self.username = None
    self.__issue_key = issue_key
    url = f"https://gumgum.jira.com/rest/api/2/issue/{self.__issue_key}"

    self.__auth = HTTPBasicAuth(jira_api_email, jira_api_token)

    headers = {
      "Accept": "application/json"
    }

    query = {
      'fields': [
        'customfield_13906',
        'customfield_14023',
        'customfield_14024'
      ]
    }

    response = requests.request(
      "GET",
      url,
      headers=headers,
      params=query,
      auth=self.__auth,
    )

    response_dict = response.json()

    # Adding the values from the custom fields to the appropriate variables
    self.email = response_dict['fields']['customfield_13906']
    self.forwarding = False
    if response_dict['fields']['customfield_14023']['value'] == 'Yes':
      self.forwarding = True
    self.forward_to_email = None
    if self.forwarding:
      self.forward_to_email = response_dict['fields']['customfield_14024']['emailAddress']

    # create a random password
    random_source = string.ascii_letters + string.digits + string.punctuation
    generated_password = random.choice(string.ascii_lowercase)
    generated_password += random.choice(string.ascii_uppercase)
    generated_password += random.choice(string.digits)
    generated_password += random.choice(string.punctuation)

    for i in range(4):
      generated_password += random.choice(random_source)

    password_list = list(generated_password)
    random.SystemRandom().shuffle(password_list)
    self.password = ''.join(password_list)

  def __get_user_id(self):
    self.username = self.email[:self.email.index("@")]
    url = f"https://gumgum.jira.com/rest/api/3/user/search?query={self.username}"
    auth = HTTPBasicAuth(jira_api_email, jira_api_token)

    headers = {
      "Accept": "application/json",
      "Content-Type": "application/json"
    }

    response = requests.request(
      "GET",
      url,
      headers=headers,
      auth=auth
    )

    response_dict = response.json()
    if response_dict and response_dict[0]['accountId'] != '557058:0a52a8d2-54f8-4375-a679-a1f639f7ccbd':
      return response_dict[0]['accountId']
    else:
      return None

  def deactivate_account(self):
    '''Deactivates the user account in Atlassian'''
    account_id = self.__get_user_id()

    url = f"https://api.atlassian.com/users/{account_id}/manage/lifecycle/disable"

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
    }

    if account_id:
      try:
        response = requests.request(
          "POST",
          url,
          headers=headers
        )
        print(response.text)
        self.results = 'Jira - Deactivated'
      except:
        self.results = 'Did not execute Jira offboarding'
    else:
      self.results = 'Jira - N/A'

  def update_ticket(self, text):
    '''Comments in the Jira ticket'''
    url = f'https://gumgum.jira.com/rest/api/2/issue/{self.__issue_key}/comment'

    headers = {
      "Accept": "application/json",
      "Content-Type": "application/json"
    }


    payload = json.dumps({"body": text})

    response = requests.request(
      "POST",
      url,
      data=payload,
      headers=headers,
      auth=self.__auth
      )
    print(response)