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

MONDAY_MASK=0x01
TUESDAY_MASK=0x02
WEDNESDAY_MASK=0x04
THURSDAY_MASK=0x08
FRIDAY_MASK=0x10
SATURDAY_MASK=0x20
SUNDAY_MASK=0x40
BIGWEEKEND_MASK=0x61
NORMALDAY_MASK=0x1E

peopleDB = {
    'alice': {
    },
    'bob': {
    },
    'carol': {
    },
    'dave': {
    },
    # 'joe': {
    # },
    # 'toto': {
    # },
    # 'titi': {
    # },
    # 'tata': {
    # },
}

calendarDB = {
    'currentBigWeekEndPerson': None,
    'previousBigWeekEndPerson': None,
    'currentWeekFridayPerson': None,
    'currentWeekPreviousDayPerson': None
}

startDate = '2021-01-01'
startDateObj = None
endDate = '2021-12-31'
endDateObj = None
deltaDaysObj = None
curDateObj = None
weekNumber = 0
calendar = None

########################
## Internal functions ##
########################

def assign_people_to_support_day(dayNumber, date, dayOfWeekMask, calendarDB, peopleDB, settings):
    global calendar
    assignedPerson = None

    if dayOfWeekMask & MONDAY_MASK:
        for person in peopleDB.keys():
            peopleDB[person]['supportDaysThisWeek'] = 0

    if dayOfWeekMask & BIGWEEKEND_MASK:
        if calendarDB['currentBigWeekEndPerson'] != None :
            assignedPerson = calendarDB['currentBigWeekEndPerson']
        else:
            for person in sorted(peopleDB.keys()):
                if (
                    person != calendarDB['currentWeekFridayPerson']
                    and (assignedPerson == None
                        or peopleDB[person]['bigWeekEndDays'] < peopleDB[assignedPerson]['bigWeekEndDays']
                        or peopleDB[person]['supportDaysThisWeek'] < peopleDB[assignedPerson]['supportDaysThisWeek']
                    )
                ):
                    assignedPerson = person
            peopleDB[assignedPerson]['bigWeekEndPeriod'] += 1
        peopleDB[assignedPerson]['bigWeekEndDays'] += 1
        calendarDB['currentBigWeekEndPerson'] = assignedPerson
    else:
        for person in sorted(peopleDB.keys()):
            if (person != calendarDB['currentWeekPreviousDayPerson']
                and (dayOfWeekMask & ~TUESDAY_MASK or person != calendarDB['previousBigWeekEndPerson'])
                and (assignedPerson == None
                    or ((dayOfWeekMask & ~FRIDAY_MASK
                            or peopleDB[person]['bigWeekEndDays'] > peopleDB[assignedPerson]['bigWeekEndDays']
                            or peopleDB[person]['supportFridayPeriod'] < peopleDB[assignedPerson]['supportFridayPeriod']
                        )
                        and peopleDB[person]['supportDaysPeriod'] < peopleDB[assignedPerson]['supportDaysPeriod']
                    )
                )
            ):
                assignedPerson = person

    peopleDB[assignedPerson]['supportDaysThisWeek'] += 1
    peopleDB[assignedPerson]['supportDaysPeriod'] += 1
    calendarDB['currentWeekPreviousDayPerson'] = assignedPerson
    print("- Person assigned to day n°%d ('%s') is '%s' [WEDays: %d, WE: %d, Friday: %d, supDayWeek: %d, supDayTotal: %d]"
        % (dayNumber, date, assignedPerson,
        peopleDB[assignedPerson]['bigWeekEndDays'],
        peopleDB[assignedPerson]['bigWeekEndPeriod'],
        peopleDB[assignedPerson]['supportFridayPeriod'],
        peopleDB[assignedPerson]['supportDaysThisWeek'],
        peopleDB[assignedPerson]['supportDaysPeriod']))
    calendarBody = {
        'summary': assignedPerson,
        'start': {
            'date': date
        },
        'end': {
            'date': date
        },
    }
    time.sleep(200/1000000.0) # Tempo to avoid Rate Limit Exceeded
    event = calendar.events().insert(calendarId=GOOGLE_CALENDAR_ID,
                                    body=calendarBody).execute()

    if dayOfWeekMask & MONDAY_MASK:
        calendarDB['previousBigWeekEndPerson'] = calendarDB['currentBigWeekEndPerson']
        calendarDB['currentBigWeekEndPerson'] = calendarDB['currentWeekFridayPerson'] = None

    if dayOfWeekMask & FRIDAY_MASK:
        calendarDB['currentWeekFridayPerson'] = assignedPerson
        peopleDB[assignedPerson]['supportFridayPeriod'] += 1

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
    global deltaDaysObj
    global curDateObj
    global weekNumber
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
    deltaDaysObj = endDateObj - startDateObj
    if deltaDaysObj.days <= 0:
        print("ERROR: End Date '%s' is anterior or equal to Start Date '%s' !" % (endDate, startDate))
        exit(-1)

    if len(peopleDB.keys()) < 3:
        print("ERROR: Minimum people in PeopleDB is 3, actual number is %d !" % len(peopleDB.keys()))
        exit(-1)

    for person in peopleDB.keys():
        if ('supportDaysThisWeek' not in peopleDB[person]):
            peopleDB[person]['supportDaysThisWeek'] = 0
        if ('supportDaysPeriod' not in peopleDB[person]):
            peopleDB[person]['supportDaysPeriod'] = 0
        if ('bigWeekEndDays' not in peopleDB[person]):
            peopleDB[person]['bigWeekEndDays'] = 0
        if ('bigWeekEndPeriod' not in peopleDB[person]):
            peopleDB[person]['bigWeekEndPeriod'] = 0
        if ('supportFridayPeriod' not in peopleDB[person]):
            peopleDB[person]['supportFridayPeriod'] = 0

    # Get the Google Calendar Service (auth with Oauth2)
    calendar = get_calendar_service()

    # Call the Calendar API
    # now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    # print('Getting the upcoming 10 events')
    # events_result = calendar.events().list(calendarId=GOOGLE_CALENDAR_ID, timeMin=now,
    #                                     maxResults=10, singleEvents=True,
    #                                     orderBy='startTime').execute()
    # events = events_result.get('items', [])

    # if not events:
    #     print('No upcoming events found.')
    # for event in events:
    #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     print(start, event['summary'])

    # exit()

    for idx in range(deltaDaysObj.days+1):
        dayOfWeek = curDateObj.isoweekday()-1
        # print ("- Date n°%d: %d/%d/%d (dow: %d)" % (idx+1, curDateObj.year,
        #         curDateObj.month, curDateObj.day, dayOfWeek))

        if dayOfWeek == 0:
            weekNumber += 1
            print("<====== We are start Week n°%d ======>" % weekNumber)

        dayOfWeekMask = 0x01 << dayOfWeek

        assign_people_to_support_day(idx+1, curDateObj.isoformat(), dayOfWeekMask, calendarDB, peopleDB, {})

        curDateObj = curDateObj + timedelta(days=1)

    print("[======================================]")
    pp.pprint(peopleDB)

if __name__ == '__main__':
    main()