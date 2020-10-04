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
    },
    # 'alice2': {
    # },
    # 'bob2': {
    # },
    # 'carol2': {
    # },
    # 'dave2': {
    # },
}

calendarDB = {
    'currentBigWeekEndPerson': None,
    'previousBigWeekEndPerson': None,
    'currentWeekFridayPerson': None
}

########################
## Internal functions ##
########################

def assign_people_to_support_day(dayOfWeek, dayOfWeekMask, calendarDB, peopleDB, settings):
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
                        or peopleDB[person]['bigWeekEndDays'] < peopleDB[assignedPerson]['bigWeekEndDays'])
                ):
                    assignedPerson = person
            peopleDB[assignedPerson]['bigWeekEndPeriod'] += 1
        peopleDB[assignedPerson]['bigWeekEndDays'] += 1
        calendarDB['currentBigWeekEndPerson'] = assignedPerson
    else:
        for person in sorted(peopleDB.keys()):
            if (
                assignedPerson == None
                or ((dayOfWeekMask & ~TUESDAY_MASK or person != calendarDB['previousBigWeekEndPerson'])
                    and (dayOfWeekMask & ~FRIDAY_MASK or peopleDB[person]['bigWeekEndDays'] > peopleDB[assignedPerson]['bigWeekEndDays'])
                    and (peopleDB[person]['supportDaysPeriod'] < peopleDB[assignedPerson]['supportDaysPeriod']
                        or peopleDB[person]['supportDaysThisWeek'] < peopleDB[assignedPerson]['supportDaysThisWeek'])
                    )
            ):
                assignedPerson = person

    peopleDB[assignedPerson]['supportDaysThisWeek'] += 1
    peopleDB[assignedPerson]['supportDaysPeriod'] += 1
    print("- Person assigned to day '%d' is '%s' [WEDays: %d, WE: %d, supDayWeek: %d, supDayTotal: %d]"
        % (dayOfWeek, assignedPerson,
        peopleDB[assignedPerson]['bigWeekEndDays'],
        peopleDB[assignedPerson]['bigWeekEndPeriod'],
        peopleDB[assignedPerson]['supportDaysThisWeek'],
        peopleDB[assignedPerson]['supportDaysPeriod']))

    if dayOfWeekMask & MONDAY_MASK:
        calendarDB['previousBigWeekEndPerson'] = calendarDB['currentBigWeekEndPerson']
        calendarDB['currentBigWeekEndPerson'] = calendarDB['currentWeekFridayPerson'] = None

    if dayOfWeekMask & FRIDAY_MASK:
        calendarDB['currentWeekFridayPerson'] = assignedPerson

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

for week in range(52):
            
    print("<====== We are start Week n°%d ======>" % week)
    
    for day in range(7):
        # print("### Day is '%d' ###" % (day))
        dayOfWeekMask = 0x01 << day
        
        assign_people_to_support_day(day, dayOfWeekMask, calendarDB, peopleDB, {})

        # pp.pprint(peopleDB)
        # pp.pprint(calendarDB)
    
    for person in peopleDB.keys():
        peopleDB[person]['supportDaysThisWeek'] = 0


print("[======================================]")
pp.pprint(peopleDB)