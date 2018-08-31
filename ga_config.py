# import libraries
from credentials import client_id, pxy, prt, pxy_usr, pxy_pw
from oauth2client.client import OAuth2WebServerFlow, GoogleCredentials
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from googleapiclient.discovery import build
import socket
import socks

socket.setdefaulttimeout(300)

h=httplib2.Http(proxy_info=httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP,pxy,prt, pxy_usr,pxy_pw))


SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'ga_project-4c6f6cf2ed45.json'

# create connection based on project credentials


# capture different states of connection

    # third and future run connect through access token an refresh token
credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, SCOPES)
h=credentials.authorize(h)

service = build('analyticsreporting', 'v4', http=h)
