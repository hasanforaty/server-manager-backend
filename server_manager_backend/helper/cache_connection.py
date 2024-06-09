import paramiko

"""
{
host: connection
}
"""
_connections = dict()


def getOrCreateConnection(host, port, username, password) -> paramiko.client.SSHClient:
    key = "{}:{}:{}".format(host, port, username)
    connection = _connections.get(key, None)
    if connection is None:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            host,
            port=port,
            username=username,
            password=password
        )
        _connections[key] = client
        connection = client
    return connection


def removeAndCloseConnection(host, port, username):
    key = "{}:{}:{}".format(host, port, username)
    client = _connections.pop(key, None)
    if client is not None:
        if isinstance(client, paramiko.client.SSHClient):
            client.close()

