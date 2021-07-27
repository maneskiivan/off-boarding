import jcapiv1
from jcapiv1.rest import ApiException
import os


jumpcloud_org_id = os.environ.get('jumpcloud_org_id')
jumpcloud_apikey = os.environ.get('jumpcloud_apikey')


class ExitJC:
  '''Offboards the user from JumpCloud'''
  def __init__(self, email):
    self.results = None
    self.__acc_id = None
    accounts_list = []
    # Configure API key authorization: x-api-key
    configuration = jcapiv1.Configuration()
    configuration.api_key['x-api-key'] = jumpcloud_apikey
    # create an instance of the API class
    api_instance = jcapiv1.SystemusersApi(jcapiv1.ApiClient(configuration))
    content_type = 'application/json'  # str |  (default to application/json)
    accept = 'application/json'  # str |  (default to application/json)
    skip = 0
    limit = 100
    x_org_id = jumpcloud_org_id  # str |  (optional) (default to )
    for i in range(0, 5):
      try:
        # List all system users
        api_response = api_instance.systemusers_list(content_type, accept, skip=skip, limit=limit, x_org_id=x_org_id)
        for account in api_response.results:
          accounts_list.append(account)
        skip += 100
      except ApiException as e:
        print("Exception when calling SystemusersApi->systemusers_list: %s\n" % e)
    for account in accounts_list:
      if email == account.email:
        self.__acc_id = account.id

    try:
      # Delete a system user
      api_response = api_instance.systemusers_delete(self.__acc_id, content_type, accept, x_org_id=x_org_id)
      self.results = 'JumpCloud Deleted'
    except:
      self.results = 'Did not execute JumpCloud offboarding'
