import datetime
import logging

import paramiko

"""
{
host: connection
}
"""
_connections = dict()
_connections_time = dict()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# def getLastServerInfo():
#     temp = dict()
#     print(lastServerInfo)
#     temp.update(lastServerInfo)
#     return temp


# def getOrCreateConnection(host, port, username, password) -> paramiko.client.SSHClient:
#     key = "{}:{}:{}".format(host, port, username)
#     connection: paramiko.SSHClient | None = _connections.get(key, None)
#
#     if connection is not None:
#         try:
#             connection.exec_command('ls')
#         except Exception as ex:
#             print('connection error', ex)
#             _connections.pop(key)
#             connection = None
#     if connection is None:
#         client = paramiko.SSHClient()
#         client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         client.connect(
#             host,
#             port=port,
#             username=username,
#             password=password
#         )
#         _connections[key] = client
#         connection = client
#         _connections_time[key] = datetime.datetime.now()
#
#     return connection
def getOrCreateConnection(host: str, port: int, username: str, password: str) -> paramiko.client.SSHClient:
    """
    Establishes and returns an SSH connection. Reuses existing connections if available.

    :param host: SSH server hostname
    :param port: SSH server port
    :param username: SSH username
    :param password: SSH password
    :return: Established SSHClient connection
    """
    key = f"{host}:{port}:{username}"
    connection = _connections.get(key)

    if connection is not None:
        try:
            connection.exec_command('ls')
        except Exception as ex:
            logger.error('Connection error: %s', ex)
            _connections.pop(key)
            connection = None
    if connection is None:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(host, port=port, username=username, password=password)
            _connections[key] = client
            _connections_time[key] = datetime.datetime.now()
            connection = client
        # except paramiko.AuthenticationException:
        #     logger.error("Authentication failed, please verify your credentials")
        # except paramiko.BadHostKeyException as badHostKeyException:
        #     logger.error("Unable to verify server's host key: %s", badHostKeyException)
        # except paramiko.SSHException as sshException:
        #     logger.error("Unable to establish SSH connection: %s", sshException)
        except Exception as ex:
            logger.error("Failed to connect: %s", ex)
            raise ex
    return connection


def removeAndCloseConnection(host, port, username):
    key = "{}:{}:{}".format(host, port, username)
    client = _connections.pop(key, None)
    if client is not None:
        if isinstance(client, paramiko.client.SSHClient):
            client.close()
