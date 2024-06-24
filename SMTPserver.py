import socket
import SMTP_protocol
from datetime import datetime
import base64

IP = "127.0.0.1"
SOCKET_TIMEOUT = 1
SERVER_NAME = "SMTP_server.com"

user_names = {"shooki": "abcd1234", "barbie": "helloken"}


# create a response with ehcode, server name and date ready to send
def create_initial_response():
    return ("{0}-{1} ESMTP Exim 4.69 #1 {2}\r\n".format(SMTP_protocol.SMTP_SERVICE_READY, SERVER_NAME, datetime.today())
            ).encode()


# if we received an EHLO, respond with hello to the client
def create_EHLO_response(client_message):
    """ Check if client message is legal EHLO message
        If yes - returns proper Hello response
        Else - returns proper protocol error code"""
    if not client_message.startswith("EHLO"):
        return ("{}".format(SMTP_protocol.COMMAND_SYNTAX_ERROR)).encode()
    client_name = client_message.split()[1]
    return "{}-{} Hello {}\r\n".format(SMTP_protocol.REQUESTED_ACTION_COMPLETED, SERVER_NAME, client_name).encode()


# check if AUTH command was received, if so respond with authentication process
def create_AUTH_response(client_message):
    """check if authentication command was received
        if yes - request username and password
        else - return error code"""
    try:
        assert client_message == "AUTH LOGIN\r\n"
        request = str(base64.b64encode("Username:".encode()).decode())
        return ("{0} {1} \r\n".format(SMTP_protocol.AUTH_INPUT, request)).encode()
    except AssertionError:
        return ("{}".format(SMTP_protocol.COMMAND_SYNTAX_ERROR)).encode()


# as opposed to checking if the username exists here we can check the username whilst we check the password.
# by doing that we minimize run time
def create_username_response():
    """request the password"""
    request = str(base64.b64encode("Password:".encode()).decode())
    return ("{0} {1} \r\n".format(SMTP_protocol.AUTH_INPUT, request)).encode()


# checks if user is in the list if users and if so compares the password
def create_success_response(username, password):
    """check if user is in the database
            if yes - check if password matches
            else - return error code"""
    for user in user_names.keys():
        if username == user:
            if password == user_names[user]:
                return ("{} authentication succeeded\r\n".format(SMTP_protocol.AUTH_SUCCESS)).encode()
            else:
                break
    return ("{}".format(SMTP_protocol.INCORRECT_AUTH)).encode()


# confirms mail address is valid (local-part@domain) and creates response for both RCPT and FROM
def create_mail_response(mail, rcpt):
    """check if provided address is valid following local-part@domain
            if yes - accept it
            else - return error code"""
    # boolean flags to confirm we have a domain, local part and have one @
    local, domain, at = False, False, False
    for tav in mail:
        if tav == '@':
            if not local:
                break
            if not at:
                at = True
            else:
                at = False
        elif mail.index(tav) == 0:
            local = True
        elif at:
            domain = True
    if domain and at and local:
        # if it's a rcpt or from address
        if rcpt:
            return ("{} Accepted\r\n".format(SMTP_protocol.REQUESTED_ACTION_COMPLETED)).encode()
        else:
            return ("{} OK\r\n".format(SMTP_protocol.REQUESTED_ACTION_COMPLETED)).encode()
    else:
        return ("{}".format(SMTP_protocol.SYNTAX_ERROR)).encode()


# create a response if the DATA command is received
def create_data_response(client_message):
    """check if data command is legal
                if yes - accept it and request mail content
                else - return error code"""
    try:
        assert client_message == "DATA\r\n"
        return ("{0} Enter message, ending with \"{1}\" on a line by itself\r\n"
                .format(SMTP_protocol.ENTER_MESSAGE, SMTP_protocol.EMAIL_END)).encode()
    except AssertionError:
        return ("{}".format(SMTP_protocol.COMMAND_SYNTAX_ERROR)).encode()


# create a response once user finishes inputting email
def create_end_response():
    # since there is no requirement in the hw to process the email data (as mentioned in the rfc at point 4.1.1.4)
    # we will not check if it's processed as of now
    """confirms email is done"""
    return ("{} OK\r\n".format(SMTP_protocol.REQUESTED_ACTION_COMPLETED)).encode()


# create closing response for when user quits
def create_QUIT_response(client_message):
    """check if input is valid QUIT command
                if yes - accept it, say goodbye and quit
                else - return error code"""
    try:
        assert client_message == "QUIT\r\n"
        return ("{0} {1} closing connection\r\n".format(SMTP_protocol.GOODBYE, SERVER_NAME)).encode()
    except AssertionError:
        return ("{}".format(SMTP_protocol.COMMAND_SYNTAX_ERROR)).encode()
# More functions must follow, in the form of create_EHLO_response, for every server response
# ...


# handle a new SMTP client
def handle_SMTP_client(client_socket):
    # 1 send initial message
    message = create_initial_response()
    client_socket.send(message)

    # 2 receive and send EHLO
    message = client_socket.recv(1024).decode()
    print(message)
    response = create_EHLO_response(message)
    client_socket.send(response)
    # breaks out of program if EHLO was not completed
    if not response.decode().startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("Error client-EHLO")
        return

    # 3 receive and send AUTH Login
    message = client_socket.recv(1024).decode()
    print(message)
    response = create_AUTH_response(message)
    client_socket.send(response)
    if not response.decode().startswith(SMTP_protocol.AUTH_INPUT):
        print("Error client-AUTH command")
        return

    # 4 receive and send USER message
    username = base64.b64decode(client_socket.recv(1024).decode()).decode()
    print(username)
    response = create_username_response()
    client_socket.send(response)

    # 5 password
    password = base64.b64decode(client_socket.recv(1024).decode()).decode()
    print(password)
    response = create_success_response(username, password)
    client_socket.send(response)
    if not response.decode().startswith(SMTP_protocol.AUTH_SUCCESS):
        print("Error client-bad login")
        return
    # 6 mail from
    mail_from = client_socket.recv(1024).decode()
    print(mail_from)
    response = create_mail_response(mail_from, False)
    if not response.decode().startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("Error client-bad mail address")
        return
    client_socket.send(response)

    # 7 rcpt to
    mail_to = client_socket.recv(1024).decode()
    print(mail_to)
    response = create_mail_response(mail_to, True)
    if not response.decode().startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("Error client-bad mail address")
        return
    client_socket.send(response)

    # 8 DATA
    message = client_socket.recv(1024).decode()
    print(message)
    response = create_data_response(message)
    if not response.decode().startswith(SMTP_protocol.ENTER_MESSAGE):
        print("Error client-DATA command")
        return
    client_socket.send(response)

    # 9 email content
    # The server should keep receiving data, until the sign of end email is received
    mail_body = ""
    done = False
    while not done:
        message = client_socket.recv(1024).decode()
        mail_body += message
        # check if end of email matches rfc req of "<CRLF>.<CRLF>"
        if "\r\n" + SMTP_protocol.EMAIL_END + "\r\n" in message:
            response = create_end_response()
            if not response.decode().startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
                print("Error processing email")
                return
            client_socket.send(response)
            done = True

    print(mail_body)

    # 10 quit
    message = client_socket.recv(1024).decode()
    response = create_QUIT_response(message)
    print(message)
    if not response.decode().startswith(SMTP_protocol.GOODBYE):
        print("Error client-QUIT command")
        return
    client_socket.send(response)


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, SMTP_protocol.PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(SMTP_protocol.PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_SMTP_client(client_socket)
        print("Connection closed")


if __name__ == "__main__":
    # Call the main handler function
    main()
