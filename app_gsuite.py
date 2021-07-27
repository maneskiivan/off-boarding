import pickle
from googleapiclient.discovery import build
from google.oauth2 import service_account


class ExitGsuite:
  '''Offboards the user from G Suite'''
  def __init__(self, email, password, forwarding=False, forward_to_email=None):
    self.__email = email
    self.__forward_to_email = forward_to_email
    self.__customer_id = None
    self.__resource_ids = []
    self.__google_groups = []
    self.__gmail_service = None
    self.results = None
    self.results_granual = ''
    self.forwarding_results = None

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    # Create a new token.pickle file if needed on a local machine and upload it to AWS
    with open('token.pickle', 'rb') as token:
      creds = pickle.load(token)

    self.__service = build('admin', 'directory_v1', credentials=creds)

    # Get's the user's customerID which is used when wiping mobile devices
    try:
      results = self.__service.users().get(userKey=self.__email).execute()
      self.__customer_id = results['customerId']
    except:
      pass

    body = {
      'password': password,
      'changePasswordAtNextLogin': False,
      'recoveryEmail': '',
      'recoveryPhone': ''
    }

    # Changes password and removes recovery email and phone
    try:
      results = self.__service.users().update(userKey=self.__email, body=body).execute()
      print(results)
    except:
      self.results = 'Did not execute G Suite offboarding'

    # Gets the groups where the user is a member
    try:
      results = self.__service.groups().list(userKey=self.__email).execute()
      groups = results['groups']
      for group in groups:
        self.__google_groups.append(group['id'])
    except:
      pass

    # Remove the user from the groups
    try:
      for group_id in self.__google_groups:
        results = self.__service.members().delete(groupKey=group_id, memberKey=self.__email).execute()
        print(results)
    except:
      self.results = 'Did not execute G Suite offboarding'

    # Gets the user's mobile devices (Google apps only)
    try:
      page_token = None
      while True:
        results = self.__service.mobiledevices().list(customerId=self.__customer_id, maxResults=100, orderBy='email', pageToken=page_token).execute()
        page_token = results['nextPageToken']
        for device in results['mobiledevices']:
          if self.__email in device['email']:
            self.__resource_ids.append(device['resourceId'])
    except:
      pass

    # Wipes the mobile devices (Google apps only)
    body = {
      'action': 'admin_account_wipe'
    }
    for id in self.__resource_ids:
      try:
        results = self.__service.mobiledevices().action(customerId=self.__customer_id, resourceId=id, body=body).execute()
        print(results)
      except:
        self.results = 'Did not execute G Suite offboarding'

    # Get's the user's tokens
    apps_list = None
    try:
      results = self.__service.tokens().list(userKey=self.__email).execute()
      apps_list = results['items']
    except:
      pass

    # Deletes the tokens for the user's connected applications
    if apps_list:
      for app in apps_list:
        try:
          results = self.__service.tokens().delete(userKey=self.__email, clientId=app['clientId']).execute()
          print(results)
        except:
          self.results = 'Did not execute G Suite offboarding'

    # Moves the account to the Terminated Users/Suspended or the Terminated Users/Email Only OU
    if forwarding:
      body = {
        'orgUnitPath': '/Terminated Users/Email Only'
      }
    else:
      body = {
        'suspended': True,
        'orgUnitPath': '/Terminated Users/Suspended',
        'includeInGlobalAddressList': False
      }

    try:
      results = self.__service.users().update(userKey=self.__email, body=body).execute()
      self.results = 'G Suite Suspended'
    except:
      self.results = 'Did not execute G Suite offboarding'


  def email_forward(self):
    '''Sets up forwarding and reactivates the account'''
    body = {
      'suspended': False
    }
    try:
      results = self.__service.users().update(userKey=self.__email, body=body).execute()
      print(results)
    except:
      self.results = 'Did not execute G Suite offboarding'

    scopes = ['https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.settings.sharing']

    # Authenticates with the service account and enable it to act on behalf of the offboarded user account
    creds = service_account.Credentials.from_service_account_file('creds.json', scopes=scopes)
    delegated_credentials = creds.with_subject(self.__email)

    self.__gmail_service = build('gmail', 'v1', credentials=delegated_credentials)

    address = {'forwardingEmail': self.__forward_to_email}
    # Adds the forwarding email address and enables forwarding
    try:
      result = self.__gmail_service.users().settings().forwardingAddresses().create(userId=self.__email, body=address).execute()
      print(result)
      if result.get('verificationStatus') == 'accepted':
        body = {
          'emailAddress': result.get('forwardingEmail'),
          'enabled': True,
          'disposition': 'LEAVE_IN_INBOX'
        }
        result = self.__gmail_service.users().settings().updateAutoForwarding(userId=self.__email, body=body).execute()
        print(result)
        self.results = 'G Suite Email Only'
    except:
      self.results = 'Did not execute G Suite offboarding'
