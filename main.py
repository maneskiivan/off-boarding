from app_jira import ExitJira
from app_jumpcloud import ExitJC
from app_gsuite import ExitGsuite
from app_dropbox import ExitDB
from app_zoom import ExitZoom
from app_salesforce import ExitSF
from app_hellosign import ExitHS
from app_lastpass import ExitLP
from log_work import ExitLog
import time
import json


def lambda_handler(event, context):
  data = event['body']
  data_dict = json.loads(data)
  issue_key = data_dict['id']
  # Gets the information from the POE jira ticket
  off_user = ExitJira(issue_key)
  # Offboards the G Suite account
  off_user_g_suite = ExitGsuite(off_user.email, off_user.password, off_user.forwarding, off_user.forward_to_email)
  # Deletes the JumpCloud account
  off_user_jc = ExitJC(off_user.email)
  time.sleep(10)
  # Deletes Zoom
  off_user_zoom = ExitZoom(off_user.email)
  # Sets up email forwarding if requested
  if off_user.forwarding:
    off_user_g_suite.email_forward()
  # Deactivates the Atlassian account
  off_user.deactivate_account()
  # Suspends the DropBox account
  off_user_db = ExitDB()
  off_user_db.suspend(off_user.email)
  # Deletes the HelloSign account
  off_user_hs = ExitHS(off_user.email)
  # Disables LastPass
  off_user_lp = ExitLP(off_user.email)
  # Deactivates the SalesForce account
  off_user_sf = ExitSF(off_user.email)

  # Logging the work
  log_work_text = f'''
  The following actions have been taken:
  {off_user_g_suite.results}
  {off_user_jc.results}
  {off_user.results}
  {off_user_zoom.results}
  Slack Deactivated
  {off_user_hs.results}
  {off_user_lp.results}
  {off_user_db.results}
  {off_user_sf.results}
  '''
  # Creating a log file in Google Drive
  new_log = ExitLog(off_user.email, log_work_text)
  # Commenting in the ticket
  ticket_comment = off_user.update_ticket(log_work_text)

  return {
    'statusCode': 200,
  }
