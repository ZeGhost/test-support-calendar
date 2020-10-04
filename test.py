#!/usr/bin/python

import pprint

pp = pprint.PrettyPrinter(indent=4, compact=False, width=80)

##pp.pprint(dict)

## Globals

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

# Internal functions

def assign_people_to_support_day(dayOfWeekMask, calendarDB, peopleDB, settings):
    assignedPerson = None

#    if dayOfWeekMask & MONDAY_MASK:
#        print("- We are on Monday !")

#    if dayOfWeekMask & TUESDAY_MASK:
#        print("- We are on Tuesday !")

#     if dayOfWeekMask & WEDNESDAY_MASK:
#         print("- We are on Wednesday !")

#     if dayOfWeekMask & THURSDAY_MASK:
#         print("- We are on Thursday !")

#     if dayOfWeekMask & FRIDAY_MASK:
#         print("- We are on Friday !")

#     if dayOfWeekMask & SATURDAY_MASK:
#         print("- We are on Saturday !")

#     if dayOfWeekMask & SUNDAY_MASK:
#         print("- We are on Sunday !")

    if dayOfWeekMask & NORMALDAY_MASK:
        # print("=> We are on a Normal day !")

        for person in peopleDB.keys():
            if (
                assignedPerson == None or peopleDB[person]['supportDaysThisWeek'] < peopleDB[assignedPerson]['supportDaysThisWeek']
                or peopleDB[person]['supportDaysPeriod'] < peopleDB[assignedPerson]['supportDaysPeriod']
            ):
                assignedPerson = person
    else:
        # print("=> We are on a Big Week End day !")

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
#    if dayOfWeekMask & BIGWEEKEND_MASK:
        
    
    

## MAIN

for person in peopleDB.keys():
    if ('supportDaysThisWeek' not in peopleDB[person]):
        peopleDB[person]['supportDaysThisWeek'] = 0
    if ('supportDaysPeriod' not in peopleDB[person]):
        peopleDB[person]['supportDaysPeriod'] = 0
#    if ('currentBigWeekEnd' not in peopleDB[person]):
#        peopleDB[person]['currentBigWeekEnd'] = False
    if ('bigWeekEndPeriod' not in peopleDB[person]):
        peopleDB[person]['bigWeekEndPeriod'] = 0

for week in range(6):
            
    print("<====== We are start Week n°%d ======>" % week)
    
    for day in range(7):
        print("### Day is '%d' ###" % (day))
        dayOfWeekMask = 0x01 << day
        
        assign_people_to_support_day(dayOfWeekMask, calendarDB, peopleDB, {})

        # pp.pprint(peopleDB)
        # pp.pprint(calendarDB)
    
    for person in peopleDB.keys():
        peopleDB[person]['supportDaysThisWeek'] = 0


print("[======================================]")
pp.pprint(peopleDB)