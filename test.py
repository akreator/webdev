# -----------
# User Instructions
# 
# Modify the valid_month() function to verify 
# whether the data a user enters is a valid 
# month. If the passed in parameter 'month' 
# is not a valid month, return None. 
# If 'month' is a valid month, then return 
# the name of the month with the first letter 
# capitalized.
#

months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']

def lower(word):
    return word.lower()

lowerCaseMonths = map(lower,months)
print lowerCaseMonths

def valid_month_2(month):
    if month.lower() in lowerCaseMonths:
        return month.capitalize()
    return None

def valid_month(month):
    for i in range(0, len(months)):
        if months[i].lower() == month.lower():
            return months[i]
        return None

print valid_month_2("january") 
  
print valid_month_2("January") 
# => "January"
print valid_month_2("foo")
# => None
print valid_month_2("")
# => None

