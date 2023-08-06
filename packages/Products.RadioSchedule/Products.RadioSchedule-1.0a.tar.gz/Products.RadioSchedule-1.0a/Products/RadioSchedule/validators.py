from Products.validation.interfaces import ivalidator
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

class TimeValidator:
    implements(ivalidator)

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        context = kwargs.get('instance', None)
        message = check_format(context, value)
        if message:
            return message
        message = overlapping_schedule(context, value)
        if message:
            return message

class EndTimeValidator:
    implements(ivalidator)

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        context = kwargs.get('instance', None)
        req = kwargs['REQUEST']       
        message = check_format(context, value)
        if message:
            return message
        message = overlapping_schedule(context, value)
        if message:
            return message
        message = check_end_time(req, value)
        if message:
            return message

def check_end_time(req, value):
    fail_message = """End time must come after start time """
    start = req.form.get('start_time', None)
    try:
        start = int(start.replace(':', ''))
        value = int(value.replace(':', ''))
    except ValueError:
        return fail_message
    if value <= start:
        return fail_message

def check_format(context, value):
    fail_message = """Use the format hh:mm. 'hh' should be in the range 00-23, 'mm' 
                      should be in the range 00-59."""
    if len(value) != 5:
        return fail_message
    if value[2] != ':':
        return fail_message
    hour = value[:2]
    minute = value[3:]
    try:
        if int(hour) > 23:
            return fail_message
        if int(minute) > 59:
            return fail_message
    except ValueError:
        return fail_message

def overlapping_schedule(context, value):
    fail_message = """The time you have entered is overlapping with another scheduled program. """
    query = {}
    catalog = getToolByName(context, 'portal_catalog')
    query['Type'] = 'Radioshow'
    query['path'] = ('/').join(context.getPhysicalPath()[:-1])
    results = catalog.searchResults(**query)
    for item in results:
        obj = item.getObject()
        if obj == context:
            pass
        else:
            start = int(obj.getStart_time().replace(':', ''))
            end = int(obj.getEnd_time().replace(':', ''))
            v = int(value.replace(':', ''))
            if start <= v < end:
                return fail_message
