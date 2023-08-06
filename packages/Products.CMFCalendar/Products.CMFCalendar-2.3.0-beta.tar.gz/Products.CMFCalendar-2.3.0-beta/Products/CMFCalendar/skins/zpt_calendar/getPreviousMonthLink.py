##parameters=base_url, month, year
##
from Products.CMFCore.utils import getUtilityByInterfaceName

caltool = getUtilityByInterfaceName('Products.CMFCalendar.interfaces.ICalendarTool')
prevMonthTime = caltool.getPreviousMonth(month, year)

# Takes a base url and returns a link to the previous month
x = '%s?month:int=%d&year:int=%d' % (
                                     base_url,
                                     prevMonthTime.month(),
                                     prevMonthTime.year()
                                     )

return x
