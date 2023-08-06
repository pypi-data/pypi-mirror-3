Introduction
============

collective.memberapproval provides a user interface for
pas.plugins.memberapproval. Together these products form a member approval
process, making it possible to approve or disapprove member registrations to
your website.


Management views
----------------

collective.memberapproval providess the following management views:

* @@usergroup-userprefs: collective.memberapproval overrides the standard
  user management view with one that extends the standard view with a filter
  to list only Approved, only Disapproved or All users.
  
* @@user-approval: This view will allow you to view and change the status of
  a specific user. You access it with the parameter 'userid', ie
  http://localhost:8080/Plone/@@user-approval?userid=theusername
  
* @@user-approve: This view will approve the specified user. It does not
  provide any HTML view, but is usable for services such as providing
  a direct link to approve users from a notification email. Example:
  http://localhost:8080/Plone/@@user-approve?userid=theusername

* @@user-disapprove: This view will disapprove the specified user. It does
  not provide any HTML view, but is usable for services such as providing a
  direct link to disapprove users from a notification email. Example:
  http://localhost:8080/Plone/@@user-disapprove?userid=theusername

* @@user-approved: This view will return True if the user specified is
  approved, or None otherwise. It does not provide any HTML view. Example:
  http://localhost:8080/Plone/@@user-approved?userid=theusername

