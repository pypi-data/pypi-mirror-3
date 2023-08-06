from Products.ATContentTypes.permission import permissions

PROJECTNAME = 'monet.calendar.event'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'MonetEvent': permissions['Event'],
}
