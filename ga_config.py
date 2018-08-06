# import libraries
from credentials import client_id
from oauth2client.client import OAuth2WebServerFlow, GoogleCredentials
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from googleapiclient.discovery import build



SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'ga_project-4c6f6cf2ed45.json'

# create connection based on project credentials


# capture different states of connection

    # third and future run connect through access token an refresh token
credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, SCOPES)

service = build('analyticsreporting', 'v4', credentials=credentials)