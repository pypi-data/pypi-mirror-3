from zope.interface import Interface
  
class IMemberApprovalPlugin(Interface):
    """interface for MemberApprovalPlugin."""

    def userStatus(user_id):
        """ Returns true if user is approved, false if dissapproved and None if pendning """

    def approveUser(user_id):
        """ Approve particular user """

    def disapproveUser( user_id):
        """ Disnapprove particular user """

