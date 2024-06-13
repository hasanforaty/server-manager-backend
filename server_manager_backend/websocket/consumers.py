import json
import time

from channels.generic.websocket import AsyncWebsocketConsumer

from helper.cache_connection import getOrCreateCash


class ServerSummeryConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        await self.accept()
        while int(1) in [1]:
            catch = getOrCreateCash()
            threads = []
            try:
                summery_list = catch.get_summaries()
                # servers = lastServer
                # for server in servers:
                #     get_server_summery(server_id=server['id'], summery_list=summery_list)
                # #     thread = threading.Thread(target=get_server_summery, args=(server.id, summery_list))
                # #     threads.append(thread)
                # #     thread.start()
                # #
                # # for thread in threads:
                # #     thread.join()

                summery_list.sort(key=lambda summery: summery['id'])
                await self.send(text_data=json.dumps(summery_list))
                # Random.objects.create(text="test")
                time.sleep(1)
            except Exception as e:
                print(e)

        await self.close()

    def disconnect(self, close_code):
        self.close()

    def receive(self):
        self.close()


# @sync_to_async
# def printInfo():
#     print('lastServer', lastServer)
#     print('lastServerInfo', getLastServerInfo())
#     print('lastServiceHistory', lastServiceHistory)
#     print('lastDB', lastDB)
#     print('lastDBHistory', lastDBHistory)


# def get_server_summery(server_id, summery_list):
#     summery = dict()
#     summery['id'] = str(server_id)
#     """
#      config:{
#         id:1,
#         hostName:'همدان',
#         host:'host.com',
#         port:2020,
#         username:'hasan',
#         password:'1234',
#       },
#     """
#     info = lastServerInfo[str(server_id)]
#     """
#      info: {
#         id:1,
#         server : 'همدان',
#         ram : 80,
#         memory : 75,
#         cpu:50,
#         status:[
#           {
#             name:'Server',
#             status:'green',
#           },
#           {
#             name:'Db',
#             status:'red',
#           },
#         ],
#         lastUpdate:"11/11/2020",
#         lastBackup:null,
#       }
#     """
#     if info is not None:
#         server = info['server']
#         summery['config'] = {
#             'id': str(server_id),
#             'hostName': server['name'],
#             'host': server['host'],
#             'port': server['port'],
#             'username': server['username'],
#             'password': server['password'],
#         }
#         lastUpdate = info["created_at"].strftime('%Y/%m/%d %H:%M:%S')
#         summery['info'] = {
#             'id': str(info['id']),
#             'server': info['server']['name'],
#             'ram': info['ram'],
#             'memory': info['memory'],
#             'cpu': info['cpu'],
#             'lastUpdate': lastUpdate,
#             'lastBackup': None,
#             'status': []
#         }
#     services = lastService[str(server_id)]
#     databases = lastDB[str(server_id)]
#     service_convertor = []
#     for service in services:
#         service_convertor.append({
#             'id': str(service['id']),
#             'type': 'سرور',
#             'serviceName': service['name'],
#             'command': service['command'],
#             'contain': service['contain'],
#         })
#         history = lastServiceHistory[str(service['id'])]
#         if history is not None:
#             if history['status']:
#                 status = 'green'
#             else:
#                 status = 'red'
#             summery['info'].get('status').append({
#                 'name': service['name'],
#                 'status': status
#             })
#     for database in databases:
#         service_convertor.append({
#             'id': str(database['id']),
#             'type': 'دیتابیس',
#             'serviceName': database['name'],
#             'username': database['username'],
#             'password': database['password'],
#             'host': database['host'],
#             'port': database['port']
#         })
#         history = lastDBHistory[str(database['id'])]
#         if history is not None:
#             if history['status']:
#                 status = 'green'
#             else:
#                 status = 'red'
#             summery['info'].get('status').append({
#                 'name': database['name'],
#                 'status': status
#             })
#
#     summery['services'] = service_convertor
#     summery_list.append(summery)
