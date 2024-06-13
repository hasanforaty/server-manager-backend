import json
import threading
import datetime
import time
from channels.generic.websocket import WebsocketConsumer
from server.models import Server, Service, DBService
from history.models import ServerInfo, ServiceHistory


class ServerSummeryConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        while int(1) in [1]:
            threads = []
            try:
                summery_list = []
                for server in Server.objects.all():
                    get_server_summery(server_id=server.id, summery_list= summery_list)
                #     thread = threading.Thread(target=get_server_summery, args=(server.id, summery_list))
                #     threads.append(thread)
                #     thread.start()
                #
                # for thread in threads:
                #     thread.join()

                summery_list.sort(key=lambda summery: summery['id'])
                self.send(text_data=json.dumps(summery_list))
                # Random.objects.create(text="test")
                time.sleep(1)
            except Exception as e:
                print(e)

        self.close()

    def disconnect(self, close_code):
        self.close()

    def receive(self):
        self.close()


def get_server_summery(server_id, summery_list):
    server = Server.objects.get(id=server_id)
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
    summery['config'] = {
        'id': str(server_id),
        'hostName': server.name,
        'host': server.host,
        'port': server.port,
        'username': server.username,
        'password': server.password,
    }
    info: ServerInfo = ServerInfo.objects.filter(server_id=server_id).order_by('-created_at').first()
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
        lastUpdate = info.created_at.strftime('%Y/%m/%d %H:%M:%S')
        summery['info'] = {
            'id': str(info.id),
            'server': server.name,
            'ram': info.ram,
            'memory': info.memory,
            'cpu': info.cpu,
            'lastUpdate': lastUpdate,
            'lastBackup': None,
            'status': []
        }
    services = Service.objects.filter(server_id=server_id).all()
    databases = DBService.objects.filter(server_id=server_id).all()
    service_convertor = []
    for service in services:
        service_convertor.append({
            'id': str(service.id),
            'type': 'سرور',
            'serviceName': service.name,
            'command': service.command,
            'contain': service.contain,
        })
        history = ServiceHistory.objects.all().filter(service_id=service.id).order_by('-created_at').first()
        if history is not None:
            if history.status:
                status = 'green'
            else:
                status = 'red'
            summery['info'].get('status').append({
                'name': service.name,
                'status': status
            })
    for database in databases:
        service_convertor.append({
            'id': str(database.id),
            'type': 'دیتابیس',
            'serviceName': database.name,
            'username': database.username,
            'password': database.password,
            'host': database.host,
            'port': database.port
        })
        history = ServiceHistory.objects.all().filter(serviceDB_id=database.id).order_by('-created_at').first()
        if history is not None:
            if history.status:
                status = 'green'
            else:
                status = 'red'
            summery['info'].get('status').append({
                'name': database.name,
                'status': status
            })

    summery['services'] = service_convertor
    summery_list.append(summery)
