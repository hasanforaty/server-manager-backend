import datetime
import threading
import time

import schedule
from schedule import Scheduler

from helper import check
from history.serializers import ServerInfoSerializer, ServiceHistorySerializer, ActionHistorySerializer
from server.models import Server, DBService, Action
from server.serializers import ServerSerializer, DBServiceSerializer, ActionSerializer


def run_continuously(self, interval=1):
    """Continuously run, while executing pending jobs at each elapsed
    time interval.
    @return cease_continuous_run: threading.Event which can be set to
    cease continuous run.
    Please note that it is *intended behavior that run_continuously()
    does not run missed jobs*. For example, if you've registered a job
    that should run every minute and you set a continuous run interval
    of one hour, then your job won't be run 60 times at each interval but
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
_job: schedule.Job
_scheduler: Scheduler
_action_jobs = dict()


def start_scheduler(do_every: int = 4):
    """
    Starts a scheduler to do the server's task
    :param do_every: do the task every N seconds
    :return: None
    """
    global _job, _scheduler
    # check_server = check.CheckServer(
    #     host=host,
    #     port=port,
    #     username=username,
    #     password=password
    # )
    # check_server.check_server()
    _scheduler = Scheduler()
    _job = _scheduler.every(do_every).seconds.do(check_servers)
    _scheduler.run_continuously()


def stop_scheduler():
    global _job, _scheduler
    if _job is not None and _scheduler is not None:
        _scheduler.cancel_job(_job)
        _job = None
    else:
        raise Exception("Scheduler not running")


def restart_scheduler(do_every: int = 4):
    stop_scheduler()
    start_scheduler(do_every=do_every)


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

    actions = server.actions.all()
    for action in actions:
        thread = threading.Thread(target=create_get_action_job, args=(action.id, server_id, action.interval))
        threads.append(thread)
        thread.start()

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


def create_get_action_job(action_id, server_id, interval):
    global _action_jobs, _scheduler
    key = "{}_{}_{}".format(action_id, server_id, str(interval))
    job = _action_jobs.get(key, None)

    if job is None:
        # check to see if an interval has changes
        static_part = "{}_{}_".format(action_id, server_id)
        for ke in _action_jobs.keys():
            if static_part in ke:
                old_job = _action_jobs.pop(ke)
                _scheduler.cancel_job(old_job)
        job = _scheduler.every(interval).seconds.do(do_action, action_id, server_id)
        _action_jobs[key] = job
    return job


def do_action(action_id, server_id):
    action = Action.objects.get(id=action_id)
    action_serializer = ActionSerializer(action).data
    server = Server.objects.get(id=server_id)
    server_serializer = ServerSerializer(server).data
    print('at : ', datetime.datetime.now(), 'doing action : ', action_id, )
    checked_server = check.CheckServer(
        host=server_serializer['host'],
        port=server_serializer['port'],
        username=server_serializer['username'],
        password=server_serializer['password']
    )
    result = checked_server.checkByCommand(
        command=action_serializer['command'],
        contain=action_serializer['onSuccess']
    )
    serializer = ActionHistorySerializer(
        data={
            'log': result['log'],
            'created_at': result['date'],
            'status': result['success']
        }
    )
    if serializer.is_valid():
        serializer.save(action=action, server=server)
    else:
        print(serializer.errors)
