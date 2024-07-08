import asyncio
import json

from asgiref.sync import sync_to_async, async_to_sync
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncWebsocketConsumer

from history.models import ServerInfo, ServiceHistory
from server.models import Server, Service, DBService


class ServerSummeryConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        await self.accept()
        while int(1) in [1]:
            try:
                summery_list = await sync_to_async(get_summery)()

                if summery_list:
                    my_json: dict = summery_list
                    my_response = []

                    # servers = lastServer
                    # for server in servers:
                    #     get_server_summery(server_id=server['id'], summery_list=summery_list)
                    # #     thread = threading.Thread(target=get_server_summery, args=(server.id, summery_list))
                    # #     threads.append(thread)
                    # #     thread.start()
                    # #
                    # # for thread in threads:
                    # #     thread.join()
                    for key in my_json.keys():
                        my_response.append(my_json.get(key))
                    # my_response.sort(key=lambda summery: summery['id'])
                    # print('my_response : ', my_response)
                    # print('emit : ...... ')
                    # print(my_response)
                    await self.send(text_data=json.dumps(my_response))
                    # Random.objects.create(text="test")
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(2)
            except Exception as e:
                print(e)
                await asyncio.sleep(4)

        await self.close()

    # def disconnect(self, close_code):
    #     self.close()
    #
    # def receive(self):
    #     self.close()
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        raise StopConsumer()


# @sync_to_async
# def printInfo():
#     print('lastServer', lastServer)
#     print('lastServerInfo', getLastServerInfo())
#     print('lastServiceHistory', lastServiceHistory)
#     print('lastDB', lastDB)
#     print('lastDBHistory', lastDBHistory)

def get_summery():
    summery_list = dict()
    servers = Server.objects.all()
    for server in servers:
        summery = dict()
        summery['id'] = str(server.id)
        history: ServerInfo = ServerInfo.objects.filter(server=server).order_by('created_at').last()
        summery['config'] = {
            'id': str(server.id),
            'name': server.name,
            'host': server.host,
            'port': server.port,
            'username': server.username,
            'password': server.password,
            'active': server.active,
        }
        log = ''
        if len(server.log) != 0 or server.log != "None":
            log = server.log
        if history is not None:
            summery['info'] = {
                'id': str(history.id),
                'server': server.name,
                'ram': history.ram,
                'memory': history.memory,
                'cpu': history.cpu,
                'lastUpdate': str(history.created_at),
                'lastBackup': None,
                'status': [],
                'log': log
            }
        else:
            summery['info'] = {
                'id': '',
                'server': server.name,
                'ram': 0,
                'memory': 0,
                'cpu': 0,
                'lastUpdate': '',
                'lastBackup': None,
                'status': [],
                'log': log
            }
        services = Service.objects.all().filter(server=server)
        service_convertor = []
        for service in services:
            service_convertor.append({
                'id': str(service.id),
                'type': 'سرور',
                'serviceName': service.serviceName,
                'command': service.command,
                'contain': service.contain,
            })
            history: ServiceHistory = ServiceHistory.objects.filter(service=service).order_by('created_at').last()
            if history is not None:
                if history.status:
                    status = 'green'
                else:
                    status = 'red'
                summery['info'].get('status').append({
                    'name': service.serviceName,
                    'status': status
                })
            else:
                status = 'red'
                summery['info'].get('status').append({
                    'name': service.serviceName,
                    'status': status
                })

        databases = DBService.objects.all().filter(server=server)
        for database in databases:
            service_convertor.append({
                'id': str(database.id),
                'type': 'دیتابیس',
                'serviceName': database.serviceName,
                'username': database.username,
                'password': database.password,
                'host': database.host,
                'port': database.port
            })
            history: ServiceHistory = ServiceHistory.objects.filter(serviceDB=database).last()
            if history is not None:
                if history.status:
                    status = 'green'
                else:
                    status = 'red'
                summery['info'].get('status').append({
                    'name': database.serviceName,
                    'status': status
                })
            else:
                status = 'red'
                summery['info'].get('status').append({
                    'name': database.serviceName,
                    'status': status
                })
        summery['services'] = service_convertor
        summery_list[str(server.id)] = summery
    return summery_list
