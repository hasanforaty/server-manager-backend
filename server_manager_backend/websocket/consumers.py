import json
import asyncio
import concurrent.futures
import logging

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from history.models import ServerInfo, ServiceHistory
from server.models import Server, Service, DBService
from core.models import CacheModel

logger = logging.getLogger(__name__)
connected_clients = set()


class ServerSummeryConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.latest_summary = None  # Cache to store the latest summary
        # print('init .............')
        # self.loop_task = asyncio.create_task(self.periodic_update())

    # async def connect(self):
    #     print('WebSocket connect called')
    #     await self.accept()
    #     print('WebSocket connection accepted')
    #     await self.send(text_data=json.dumps({}))
    #     self.loop_task = asyncio.create_task(self.periodic_update())
    #
    # async def disconnect(self, close_code):
    #     print(f'WebSocket disconnect called with close code: {close_code}')
    #     if hasattr(self, 'loop_task'):
    #         self.loop_task.cancel()
    #     print('WebSocket connection closed')
    #     raise StopConsumer()

    # async def connect(self):
    #     logger.info('WebSocket connect called')
    #     await self.accept()
    #     sync_to_async()
    #     connected_clients.add(self)
    #
    #     logger.info('WebSocket connection accepted')
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

    async def disconnect(self, close_code):
        logger.info(f'WebSocket disconnect called with close code: {close_code}')
        connected_clients.remove(self)
        logger.info('WebSocket connection closed')
        raise StopConsumer()

    async def receive(self, text_data):
        # Handle incoming messages if needed
        pass


async def periodic_update():
    await asyncio.sleep(20)
    while True:
        try:
            logger.info('WebSocket try to get summery')
            summery_list = await sync_to_async(_get_summery)()
            await sync_to_async(create_cash)(summery_list)
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error in WebSocket update loop: {e}")
            await asyncio.sleep(4)


def create_cash(summery_list):
    CacheModel.objects.create(json=summery_list)


def process_server(server):
    """Process a single server and return its summary."""
    summery = dict()
    summery['id'] = str(server.id)
    history = ServerInfo.objects.filter(server=server).order_by('created_at').last()
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
    services = Service.objects.filter(server=server)
    service_convertor = []
    for service in services:
        service_convertor.append({
            'id': str(service.id),
            'type': 'سرور',
            'serviceName': service.serviceName,
            'command': service.command,
            'contain': service.contain,
        })
        history = ServiceHistory.objects.filter(service=service).order_by('created_at').last()
        if history is not None:
            status = 'green' if history.status else 'red'
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

    databases = DBService.objects.filter(server=server)
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
        history = ServiceHistory.objects.filter(serviceDB=database).last()
        if history is not None:
            status = 'green' if history.status else 'red'
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
    return (str(server.id), summery)


def _get_summery():
    summery_list = dict()
    servers = Server.objects.all()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_server, server) for server in servers]
        for future in concurrent.futures.as_completed(futures):
            server_id, server_summery = future.result()
            summery_list[server_id] = server_summery
    return summery_list


def get_summery():
    model = CacheModel.objects.all().last()
    print('data : ', model.created_at)
    return model.json
