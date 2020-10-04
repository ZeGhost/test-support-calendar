#!/usr/bin/python

import pprint

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
    }
}

calendarDB = {
    'currentBigWeekEndPerson': None,
    'previousBigWeekEndPerson': None,
    'currentWeekFridayPerson': None
}

########################
## Internal functions ##
########################

def assign_people_to_support_day(dayOfWeekMask, calendarDB, peopleDB, settings):
    assignedPerson = None

    if dayOfWeekMask & MONDAY_MASK:
        for person in peopleDB.keys():
            peopleDB[person]['supportDaysThisWeek'] = 0

    if dayOfWeekMask & NORMALDAY_MASK:
        for person in peopleDB.keys():
            if (
                assignedPerson == None 
                or (dayOfWeekMask & FRIDAY_MASK and peopleDB[person]['bigWeekEndDays'] > peopleDB[assignedPerson]['bigWeekEndDays'])
                or peopleDB[person]['supportDaysThisWeek'] < peopleDB[assignedPerson]['supportDaysThisWeek']
                or peopleDB[person]['supportDaysPeriod'] < peopleDB[assignedPerson]['supportDaysPeriod']
            ):
                assignedPerson = person
    else:
        if calendarDB['currentBigWeekEndPerson'] != None :
            assignedPerson = calendarDB['currentBigWeekEndPerson']
        else:
            for person in peopleDB.keys():
                if (
                    person != calendarDB['currentWeekFridayPerson'] and 
                    (assignedPerson == None or peopleDB[person]['bigWeekEndPeriod'] < peopleDB[assignedPerson]['bigWeekEndPeriod']
                    or peopleDB[person]['supportDaysPeriod'] < peopleDB[assignedPerson]['supportDaysPeriod'])
                ):
                    assignedPerson = person
            peopleDB[assignedPerson]['bigWeekEndPeriod'] += 1
        peopleDB[assignedPerson]['bigWeekEndDays'] += 1
        calendarDB['currentBigWeekEndPerson'] = assignedPerson

    peopleDB[assignedPerson]['supportDaysThisWeek'] += 1
    peopleDB[assignedPerson]['supportDaysPeriod'] += 1
    print("- Person assigned to this day is '%s'" % assignedPerson)

    if dayOfWeekMask & MONDAY_MASK:
        calendarDB['previousBigWeekEndPerson'] = calendarDB['currentBigWeekEndPerson']
        calendarDB['currentBigWeekEndPerson'] = None
        calendarDB['currentWeekFridayPerson'] = None

    if dayOfWeekMask & FRIDAY_MASK:
        calendarDB['currentWeekFridayPerson'] = assignedPerson

    if dayOfWeekMask & SATURDAY_MASK:
        peopleDB[assignedPerson]['bigWeekEndPeriod'] += 1

##########
## MAIN ##
##########

for person in peopleDB.keys():
    if ('supportDaysThisWeek' not in peopleDB[person]):
        peopleDB[person]['supportDaysThisWeek'] = 0
    if ('supportDaysPeriod' not in peopleDB[person]):
        peopleDB[person]['supportDaysPeriod'] = 0
    if ('bigWeekEndDays' not in peopleDB[person]):
        peopleDB[person]['bigWeekEndDays'] = 0
    if ('bigWeekEndPeriod' not in peopleDB[person]):
        peopleDB[person]['bigWeekEndPeriod'] = 0

for week in range(48):
            
    print("<====== We are start Week n°%d ======>" % week)
    
    for day in range(7):
        print("### Day is '%d' ###" % (day))
        dayOfWeekMask = 0x01 << day
        
        assign_people_to_support_day(dayOfWeekMask, calendarDB, peopleDB, {})

        pp.pprint(peopleDB)
        # pp.pprint(calendarDB)
    
    for person in peopleDB.keys():
        peopleDB[person]['supportDaysThisWeek'] = 0


print("[======================================]")
pp.pprint(peopleDB)