import datetime

import paramiko

"""
{
host: connection
}
"""
_connections = dict()
_connections_time = dict()
_cash = None


def getOrCreateCash():
    global _cash
    print('access cached')
    if _cash is None:
        print('create cashed ')
        _cash = CashLastData()
    return _cash


class CashLastData:
    def __init__(self):
        self.lastServerInfo = dict()
        self.lastServiceHistory = dict()
        self.lastService = dict()
        self.lastServer = []
        self.lastDB = dict()
        self.lastDBHistory = dict()

    def get_server_summery(self, server_id, summery_list):
        summery = dict()
        summery['id'] = str(server_id)
        """
         config:{
            id:1,
            hostName:'همدان',
            host:'host.com',
            port:2020,
            username:'hasan',
            password:'1234',
          },
        """
        info = self.lastServerInfo[str(server_id)]
        """
         info: {
            id:1,
            server : 'همدان',
            ram : 80,
            memory : 75,
            cpu:50,
            status:[
              {
                name:'Server',
                status:'green',
              },
              {
                name:'Db',
                status:'red',
              },
            ],
            lastUpdate:"11/11/2020",
            lastBackup:null,
          }
        """
        if info is not None:
            server = info['server']
            summery['config'] = {
                'id': str(server_id),
                'hostName': server['name'],
                'host': server['host'],
                'port': server['port'],
                'username': server['username'],
                'password': server['password'],
            }
            lastUpdate = info["created_at"].strftime('%Y/%m/%d %H:%M:%S')
            summery['info'] = {
                'id': str(info['id']),
                'server': info['server']['name'],
                'ram': info['ram'],
                'memory': info['memory'],
                'cpu': info['cpu'],
                'lastUpdate': lastUpdate,
                'lastBackup': None,
                'status': []
            }
        services = self.lastService[str(server_id)]
        databases = self.lastDB[str(server_id)]
        service_convertor = []
        for service in services:
            service_convertor.append({
                'id': str(service['id']),
                'type': 'سرور',
                'serviceName': service['name'],
                'command': service['command'],
                'contain': service['contain'],
            })
            history = self.lastServiceHistory[str(service['id'])]
            if history is not None:
                if history['status']:
                    status = 'green'
                else:
                    status = 'red'
                summery['info'].get('status').append({
                    'name': service['name'],
                    'status': status
                })
        for database in databases:
            service_convertor.append({
                'id': str(database['id']),
                'type': 'دیتابیس',
                'serviceName': database['name'],
                'username': database['username'],
                'password': database['password'],
                'host': database['host'],
                'port': database['port']
            })
            history = self.lastDBHistory[str(database['id'])]
            if history is not None:
                if history['status']:
                    status = 'green'
                else:
                    status = 'red'
                summery['info'].get('status').append({
                    'name': database['name'],
                    'status': status
                })

        summery['services'] = service_convertor
        summery_list.append(summery)

    def get_summaries(self):
        summaries = []
        for server in self.lastServer:
            self.get_server_summery(server_id=server['id'], summery_list=summaries)
        return summaries


# def getLastServerInfo():
#     temp = dict()
#     print(lastServerInfo)
#     temp.update(lastServerInfo)
#     return temp


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
        _connections_time[key] = datetime.datetime.now()

    return connection


def removeAndCloseConnection(host, port, username):
    key = "{}:{}:{}".format(host, port, username)
    client = _connections.pop(key, None)
    if client is not None:
        if isinstance(client, paramiko.client.SSHClient):
            client.close()
