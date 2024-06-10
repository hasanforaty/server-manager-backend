import threading
import time
import datetime

from schedule import Scheduler
from server.models import Server
from server.serializers import ServerSerializer
from helper import check
from history.models import ServerInfo
from history.serializers import ServerInfoSerializer


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
    scheduler.every(4).seconds.do(check_servers_info)
    scheduler.run_continuously()


def check_servers_info():
    threads = []
    servers = ServerSerializer(Server.objects.all(), many=True).data
    for value in servers:
        thread = threading.Thread(target=check_server_info, args=(value['id'],))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def check_server_info(server_id):
    print('start at :', datetime.datetime.now())
    server = Server.objects.get(id=server_id)
    server_serializer = ServerSerializer(server).data
    check_server = check.CheckServer(
        host=server_serializer['host'],
        port=server_serializer['port'],
        username=server_serializer['username'],
        password=server_serializer['password']
    )
    info = check_server.getServerInfo()
    created_at = datetime.datetime.now()
    cpu = round(info.get('cpu'))
    memory = round(info.get('memory'))
    ram = round(info.get('ram'))
    print(created_at, cpu, memory, ram)
    data = dict()
    data['cpu'] = cpu
    data['memory'] = memory
    data['ram'] = ram
    serializer = ServerInfoSerializer(data=data,)
    if serializer.is_valid():
        serializer.save(server=server)
    else:
        print(serializer.errors)
    print('finished test at ', datetime.datetime.now())
