import re
print("....")
perms = {'ticketapp.view_tags', 'ticketapp.change_outgoinemailsettings', 'ticketapp.add_mediafiles', 'ticketapp.delete_tags', 'ticketapp.view_comment', 'ticketapp.delete_emaildetails', 'ticketapp.delete_outgoinemailsettings', 'ticketapp.change_tags', 'ticketapp.change_mediafiles', 'ticketapp.view_mediafiles', 'ticketapp.delete_imapsettings', 'ticketapp.change_comment', 'ticketapp.add_tags', 'ticketapp.delete_mediafiles', 'ticketapp.delete_comment', 'ticketapp.add_outgoinemailsettings',
         'ticketapp.delete_ticket', 'ticketapp.view_ticketsettings', 'ticketapp.view_imapsettings', 'ticketapp.add_comment', 'auth.view_user', 'ticketapp.add_ticket', 'ticketapp.view_outgoinemailsettings', 'ticketapp.delete_ticketsettings', 'ticketapp.add_ticketsettings', 'ticketapp.view_emaildetails', 'ticketapp.change_ticketsettings', 'ticketapp.change_emaildetails', 'ticketapp.change_ticket', 'ticketapp.change_imapsettings', 'ticketapp.add_emaildetails', 'ticketapp.add_imapsettings'}

perm = 'ticketapp.view_ticket'
if perm not in perms:
    print(perm)
else:
    print("no match")
