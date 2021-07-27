import dropbox
import dropbox.team
import os


drop_box_token = os.environ.get('drop_box_token')


class ExitDB:

  def __init__(self):
    self.results = None

  def suspend(self, email):
    '''Suspends the user account and wipes the data from signed in devices'''
    try:
      dbx_team = dropbox.DropboxTeam(drop_box_token)
      user = dropbox.team.UserSelectorArg.email(email)
      user_value = dbx_team.team_members_get_info([user])
      if str(user_value[0]) == f"MembersGetInfoItem('id_not_found', '{email}')":
        self.results = 'N/A'
      else:
        try:
          dbx_team.team_members_suspend(user, wipe_data=True)
          self.results = 'DropBox Disabled'
        except:
          self.results = 'Did not execute DropBox offboarding'
    except:
      self.results = 'Did not execute DropBox offboarding'
