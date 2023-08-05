import grok

try:
    from datetime import date

    from zope import interface
    from zope import component

    from horae.notification.interfaces import INotifications
    from horae.notification import notification
    from horae.ticketing.utils import getObjectType

    from horae.planning import _
    from horae.planning import interfaces

    class DeadlineNotReachedNotification(notification.Notification):
        """ A notification about a due date not being reached
        """
        permission = 'horae.Plan'
        cssClass = 'warning'

        def __init__(self, context, due_date, end):
            super(DeadlineNotReachedNotification, self).__init__(context)
            self.due_date = due_date
            self.end = end
            self.username = None

        def url(self, request):
            """ Returns the url to be used for the notification
            """
            return grok.url(request, self.context) + '/@@resolve-conflicts'

        def title(self, request):
            """ Returns the notification title
            """
            return _(u'Deadline for <em>${type} #${no}</em> will not be reached using the current forecast', mapping={'type': getObjectType(self.context),
                                                                                                                      'no': self.context.id})

        def body(self, request):
            """ Returns the notification body
            """
            return None

        def available(self):
            """ Whether this notification is available
            """
            if self.context is None or date.today() > self.date.date():
                return False
            due_date = self.context.get_property('start_due_date_end', None)
            if due_date is None:
                return False
            end = component.getAdapter(self.context, interfaces.ICalculator, 'simple').entries(self.context)[2]
            if due_date >= end:
                return False
            return True

    @grok.subscribe(interface.Interface, interfaces.IForecastRecalculated)
    def forecast_recalculated(obj, event):
        """ Checks if the due date of the object is reached according to the
            calculated forecast and otherwise creates a new notification
        """
        due_date = obj.get_property('start_due_date_end', None)
        if due_date is None:
            return
        end = component.getAdapter(obj, interfaces.ICalculator, 'simple').entries(obj)[2]
        if due_date >= end:
            return
        notifications = INotifications(obj)
        notification = DeadlineNotReachedNotification(obj, due_date, end)
        notifications.add_object(notification)

except: # horae.notification not available
    pass
