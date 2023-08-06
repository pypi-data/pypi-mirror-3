# IMAP server we're using as a backend
authentication_server = "mail.mailgateway.no"
# Domains we're accepting for logins
authentication_domains = ["nidelven-it.no", "aktivnett.no", "wow-medialab.com"]
# Roles given to any user who authenticates
# using this plugin.
authentication_roles = ('Editor', 'Reviewer', 'Member')
