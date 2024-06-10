import threading
import time
import datetime

from schedule import Scheduler
from server.models import Server, Service, DBService
from server.serializers import ServerSerializer, DBServiceSerializer
from helper import check
from history.models import ServerInfo
from history.serializers import ServerInfoSerializer, ServiceHistorySerializer


def run_continuously(self, interval=1):
    """Continuously run, while executing pending jobs at each elapsed
    time interval.
    @return cease_continuous_run: threading.Event which can be set to
    cease continuous run.
    Please note that it is *intended behavior that run_continuously()
    does not run missed jobs*. For example, if you've registered a job
    that should run every minute and you set a continuous run interval
    of one hour then your job won't be run 60 times at each interval but
    only once.
    """

    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run


Scheduler.run_continuously = run_continuously


def start_scheduler():
    # check_server = check.CheckServer(
    #     host=host,
    #     port=port,
    #     username=username,
    #     password=password
    # )
    # check_server.check_server()
    scheduler = Scheduler()
    scheduler.every(4).seconds.do(check_servers)
    scheduler.run_continuously()


def check_servers():
    threads = []
    servers = ServerSerializer(Server.objects.all(), many=True).data
    for value in servers:
        thread = threading.Thread(target=check_server, args=(value['id'],))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def check_server(server_id):
    print('start at :', datetime.datetime.now())
    threads = []
    server = Server.objects.get(id=server_id)
    server_serializer = ServerSerializer(server).data
    s_thread = threading.Thread(target=check_server_info, args=(server_id,))
    threads.append(s_thread)
    s_thread.start()

    actions = server_serializer['actions']
    dbServices = DBService.objects.filter(server_id=server_id).all()
    db_serializer = DBServiceSerializer(dbServices, many=True).data
    for db in db_serializer:
        thread = threading.Thread(target=check_db, args=(db['id'],))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    print('finished test at ', datetime.datetime.now())


def check_db(db_id):
    service = DBService.objects.get(id=db_id)
    db_serializer = DBServiceSerializer(service).data
    server = Server.objects.get(id=service.server_id)
    server_serializer = ServerSerializer(server).data
    checked_server = check.CheckServer(
        host=server_serializer['host'],
        port=server_serializer['port'],
        username=server_serializer['username'],
        password=server_serializer['password']
    )
    checked = checked_server.check_database(
        database_name=db_serializer['name'],
        username=db_serializer['username'],
        password=db_serializer['password']
    )
    data = {
        'status': checked,
        'type': "service",
    }
    serializer = ServiceHistorySerializer(data=data)
    if serializer.is_valid():
        serializer.save(
            serviceDB=service
        )
    else:
        print(serializer.errors)


def check_server_info(server_id):
    server = Server.objects.get(id=server_id)
    server_serializer = ServerSerializer(server).data
    checked_server = check.CheckServer(
        host=server_serializer['host'],
        port=server_serializer['port'],
        username=server_serializer['username'],
        password=server_serializer['password']
    )
    info = checked_server.getServerInfo()
    created_at = datetime.datetime.now()
    cpu = round(info.get('cpu'))
    memory = round(info.get('memory'))
    ram = round(info.get('ram'))
    print(created_at, cpu, memory, ram)
    data = dict()
    data['cpu'] = cpu
    data['memory'] = memory
    data['ram'] = ram
    serializer = ServerInfoSerializer(data=data, )
    if serializer.is_valid():
        serializer.save(server=server)
    else:
        print(serializer.errors)
