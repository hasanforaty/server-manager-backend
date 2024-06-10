import threading
import time
import datetime

from schedule import Scheduler
from server.models import Server
from server.serializers import ServerSerializer
from helper import check
from history.models import ServerInfo


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
    scheduler.every(4).seconds.do(test)
    scheduler.run_continuously()


host = '85.185.122.28'
port = 2233
username = 'root'
password = 'Bis0nRid3r'


def test():
    print('start at :', datetime.datetime.now())
    threads = []
    servers = ServerSerializer(Server.objects.all(), many=True).data
    for value in servers:
        thread = threading.Thread(target=testInner, args=(value['id'],))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    print('finished test at ', datetime.datetime.now())


def testInner(value):
    # check_server = check.CheckServer(
    #     host=host,
    #     port=port,
    #     username=username,
    #     password=password
    # )
    # print(check_server.getServerInfo())
    server = ServerSerializer(Server.objects.get(id=value)).data
    print('server:', server)
    check_server = check.CheckServer(
        host=server['host'],
        port=server['port'],
        username=server['username'],
        password=server['password']
    )
    info = check_server.getServerInfo()
    print('check server:',info)
