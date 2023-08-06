from zope.interface import implements
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent

class IUserApprovedEvent(IObjectEvent):
    """ User has been approved """

class IUserDisapprovedEvent(IObjectEvent):
    """ User has been disapproved """

class IUserAddedEvent(IObjectEvent):
    """ User has been added for approval """

class IUserRemoveEvent(IObjectEvent):
    """ User will be removed """
    # Notice the difference in tempus. This event is sent *before* the
    # removal. Although for a generic case we might want to send an event
    # after the removal as well, we don't need it here.

class UserApprovedEvent(ObjectEvent):

    implements(IUserApprovedEvent)
    
    def __init__(self, object, userid):
        self.userid = userid
        ObjectEvent.__init__(self, object)

class UserDisapprovedEvent(ObjectEvent):

    implements(IUserDisapprovedEvent)
    
    def __init__(self, object, userid):
        self.userid = userid
        ObjectEvent.__init__(self, object)

class UserAddedEvent(ObjectEvent):

    implements(IUserAddedEvent)
    
    def __init__(self, object, userid):
        self.userid = userid
        ObjectEvent.__init__(self, object)

class UserRemoveEvent(ObjectEvent):

    implements(IUserRemoveEvent)
    
    def __init__(self, object, userid):
        self.userid = userid
        ObjectEvent.__init__(self, object)
