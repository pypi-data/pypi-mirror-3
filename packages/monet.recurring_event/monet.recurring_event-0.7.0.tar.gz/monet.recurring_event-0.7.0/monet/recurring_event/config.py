from Products.ATContentTypes.permission import permissions

PROJECTNAME = 'monet.recurring_event'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'RecurringEvent': permissions['Event'],
}
