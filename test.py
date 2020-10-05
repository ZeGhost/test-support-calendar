#!/usr/bin/python3

import pprint
from datetime import date, timedelta

#############
## Globals ##
#############

pp = pprint.PrettyPrinter(indent=4, compact=False, width=80)

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

########################
## Internal functions ##
########################

def assign_people_to_support_day(dayNumber, date, dayOfWeekMask, calendarDB, peopleDB, settings):
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

    if dayOfWeekMask & MONDAY_MASK:
        calendarDB['previousBigWeekEndPerson'] = calendarDB['currentBigWeekEndPerson']
        calendarDB['currentBigWeekEndPerson'] = calendarDB['currentWeekFridayPerson'] = None

    if dayOfWeekMask & FRIDAY_MASK:
        calendarDB['currentWeekFridayPerson'] = assignedPerson
        peopleDB[assignedPerson]['supportFridayPeriod'] += 1

##########
## MAIN ##
##########

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


