from simple_salesforce import Salesforce
import json


class ExitSF:
  '''Sets the user's isActive property to False'''
  def __init__(self, email):
    self.results = None
    with open("login.json", "r") as login_file:
      creds = json.load(login_file)

    # Authenticate with SalesForce
    sf = Salesforce(username=creds['login']['username'],
                    password=creds['login']['password'],
                    security_token=creds['login']['token'])

    boom = f"SELECT Email " \
           f"FROM User " \
           f"WHERE Email LIKE '%@gumgum.com' " \
           f"OR Email LIKE '%@ic.gumgum.com' " \
           f"OR Email LIKE '%@ti.gumgum.com'"
    boom_data = sf.query(boom)
    boom_data = dict(boom_data)
    boom_data = [dict(x) for x in boom_data['records']]
    if email in [i['Email']for i in boom_data]:
      try:
        # Query the id of the user account
        SOQL = f"SELECT Id, Email FROM User WHERE Email = '{email}'"
        data = sf.query(SOQL)
        data = dict(data)
        data = [dict(x) for x in data['records']]
        id = data[0]['Id']

        offboard = sf.User.update(id, {'IsActive': False})
        if offboard == 204:
          self.results = 'SalesForce - Deactivated'
      except:
        self.results = 'Did not execute SalesForce offboarding'
    else:
      self.results = 'SalesForce - N/A'
