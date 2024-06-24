PORT = 25

# I did not add text descriptors to the codes but I did print them on the client side for debugging purposes.

SMTP_SERVICE_READY = "220"
REQUESTED_ACTION_COMPLETED = "250"
COMMAND_SYNTAX_ERROR = "500"
SYNTAX_ERROR = "501"
INCORRECT_AUTH = "535"
ENTER_MESSAGE = "354"
AUTH_INPUT = "334"
AUTH_SUCCESS = "235"
# the reason I didn't add a <CRLF> here is so that if we change the email
# end character it will let us know in the 354 message.
EMAIL_END = "."
GOODBYE = "221"
