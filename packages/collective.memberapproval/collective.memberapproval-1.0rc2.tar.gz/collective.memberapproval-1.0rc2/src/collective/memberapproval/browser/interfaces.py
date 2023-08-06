from zope.interface import Interface

class IMemberApprovalLayer(Interface):
    pass

class IApprovalView(Interface):
    
    def approve_user(userid):
        """ Approve particular user """

    def disapprove_user(userid):
        """ Unapprove particular user """    

    def approval_status(userid):
        """ Returns current approval status """    

    def user_exists(userid):
        """ Returns True if particular user exists in PAS """    


