import socket
import SMTP_protocol
import base64

CLIENT_NAME = "client.net"
# Add the minimum required fields to the email
# instructions for the project indicated all data should be defined before runtime as opposed to be inputted live
FROM = "<gurpartap@patriots.in>\r\n"
RCPT = "<raj_deol2002in@yahoo.co.in>\r\n"
EMAIL_TEXT =   \
    "From: ...\r\n" \
    "..." \
    "..." \
    "..." \
    "..." \
    "\r\n.\r\n"


# create ehlo command
def create_EHLO():
    return "EHLO {}\r\n".format(CLIENT_NAME).encode()


# create auth command
def create_AUTH():
    return "AUTH LOGIN\r\n".encode()


# create username info
def create_user(user):
    user1 = str(base64.b64encode(("{}".format(user)).encode()).decode())
    return (user1 + "\r\n").encode()


# create password info
def create_passwd(password):
    passwd = str(base64.b64encode(("{}".format(password)).encode()).decode())
    return (passwd + "\r\n").encode()


# create from message
def create_FROM():
    return ("MAIL FROM: {}".format(FROM)).encode()


# create To message
def create_RCPT():
    return ("RCPT TO: {}".format(RCPT)).encode()


# create DATA command
def create_DATA_cmd():
    return "DATA\r\n".encode()


# create QUIT command
def create_QUIT():
    return "QUIT\r\n".encode()


def main():
    # Connect to server
    my_socket = socket.socket()
    my_socket.connect(("127.0.0.1", SMTP_protocol.PORT))

    # 1 server welcome message
    welcome_msg = my_socket.recv(1024).decode()
    print(welcome_msg)
    # Check that the welcome message is according to the protocol
    if not welcome_msg.startswith(SMTP_protocol.SMTP_SERVICE_READY):
        print(welcome_msg, " Error connecting on welcome message")
        my_socket.close()
        return

    # 2 EHLO message
    message = create_EHLO()
    my_socket.send(message)
    response = my_socket.recv(1024).decode()
    print(response)
    if not response.startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print(response, " command syntax error")
        my_socket.close()
        return

    # 3 AUTH LOGIN
    message = create_AUTH()
    my_socket.send(message)
    response = (my_socket.recv(1024).decode())
    code = response[:4]
    response = code + base64.b64decode(response[4:]).decode()
    if not response.startswith(SMTP_protocol.AUTH_INPUT):
        print(response, " command syntax error")
        my_socket.close()
        return
    print(response)

    # 4 User
    user = "barbie"
    message = create_user(user)
    my_socket.send(message)
    response = my_socket.recv(1024).decode()
    code = response[:4]
    response = code + base64.b64decode(response[4:]).decode()
    if not response.startswith(SMTP_protocol.AUTH_INPUT):
        print(response, " Error logging in")
        my_socket.close()
        return
    print(response)
    # 5 password
    password = "helloken"
    message = create_passwd(password)
    my_socket.send(message)
    response = my_socket.recv(1024).decode()
    if not response.startswith(SMTP_protocol.AUTH_SUCCESS):
        print(response, " Error, incorrect Auth")
        my_socket.close()
        return
    print(response)

    # 6 mail from
    message = create_FROM()
    my_socket.send(message)
    response = my_socket.recv(1024).decode()
    if not response.startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print(response, " Parameter syntax error")
        my_socket.close()
        return
    print(response)

    # 7 rcpt to
    message = create_RCPT()
    my_socket.send(message)
    response = my_socket.recv(1024).decode()
    if not response.startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print(response, " Parameter syntax error")
        my_socket.close()
        return
    print(response)

    # 8 data
    message = create_DATA_cmd()
    my_socket.send(message)
    response = my_socket.recv(1024).decode()
    if not response.startswith(SMTP_protocol.ENTER_MESSAGE):
        print(response, " Command syntax error")
        my_socket.close()
        return
    print(response)
    # 9 email content
    my_socket.send(EMAIL_TEXT.encode())
    response = my_socket.recv(1024).decode()
    if not response.startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print(response, " Parameter syntax error")
        my_socket.close()
        return
    print(response)
    # 10 quit
    message = create_QUIT()
    my_socket.send(message)
    response = my_socket.recv(1024).decode()
    if not response.startswith(SMTP_protocol.GOODBYE):
        print(response, " Command syntax error")
        my_socket.close()
        return
    print(response)
    print("Closing\n")
    my_socket.close()


if __name__ == "__main__":
    main()
