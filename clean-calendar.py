#!/usr/bin/python3

import pprint
import time
from datetime import datetime, date, timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

#############
## Globals ##
#############

pp = pprint.PrettyPrinter(indent=4, compact=False, width=80)

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_FILE = 'credentials.json'
GOOGLE_CALENDAR_ID = 'r9mdghs8cja9p9n5c2ntav7nqc@group.calendar.google.com'

startDate = '2021-01-01'
startDateObj = None
endDate = '2021-12-31'
endDateObj = None
calendar = None

########################
## Internal functions ##
########################

def get_calendar_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_console()
            # creds = flow.run_local_server(port=39666, host='localhost')
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

##########
## MAIN ##
##########

def main():
    global startDate
    global startDateObj
    global endDate
    global endDateObj
    global calendar

    try:
        curDateObj = startDateObj = date.fromisoformat(startDate)
    except:
        print("ERROR: Invalid Start Date: '%s' !" % startDate)
        exit(-1)
    try:
        endDateObj = date.fromisoformat(endDate)
    except:
        print("ERROR: Invalid End Date: '%s' !" % endDate)
        exit(-1)

    # Get the Google Calendar Service (auth with Oauth2)
    calendar = get_calendar_service()

    # Clean all Google Calendar events from Start Date to End Date
    events_result = calendar.events().list(calendarId=GOOGLE_CALENDAR_ID,
                                        timeMin=datetime(year=startDateObj.year, month=startDateObj.month, day=startDateObj.day).isoformat()+'Z',
                                        timeMax=datetime(year=endDateObj.year, month=endDateObj.month, day=endDateObj.day).isoformat()+'Z',
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('INFO: No events to clean.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        #pp.pprint(event)
        time.sleep(200/1000000.0) # Tempo to avoid Rate Limit Exceeded
        calendar.events().delete(calendarId=GOOGLE_CALENDAR_ID, eventId=event['id']).execute()

if __name__ == '__main__':
    main()

