import datetime
import threading
import time

import schedule
from django.db.models import QuerySet
from schedule import Scheduler
from core.serializers import CacheModelSerializer

from helper import check
from history.serializers import ServerInfoSerializer, ServiceHistorySerializer, ActionHistorySerializer, \
    BackupHistorySerializer
from server.models import Server, DBService, Action, Service
from server.serializers import ServerSerializer, DBServiceSerializer, ActionSerializer, ServiceSerializer
from backup.models import FolderBackup
from backup.serializers import BackupSerializer
from core.models import CacheModel


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
_backup_jobs: schedule.Job


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
    start_backup_scheduler()


def start_backup_scheduler(hours: str = '18', minutes: str = '00'):
    global _backup_jobs
    _backup_jobs = _scheduler.every().day.at(f'{hours}:{minutes}').do(do_backup_scheduler)


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
    print('start checking ............ ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    cashed = get_or_create_cache()
    threads = []
    servers = ServerSerializer(Server.objects.all(), many=True).data
    get_or_create_cache().lastServer.clear()
    for value in servers:
        get_or_create_cache().lastServer.append(value)
        thread = threading.Thread(target=check_server, args=(value['id'],))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    print('start creating summary ............ ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    cashed.save_summary()
    cashed.clear_cache()
    print('end creating summary ............ ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('end checking ............ ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def trimActionsJob(actions: QuerySet[Action], server_id):
    """
    Check actions a job list for Action that are disconnected from server
    and stop their correspond Job
    :param actions:
    :param server_id:
    :return:
    """
    static_part = "_{}_".format(server_id)
    servers_key = dict()
    for ke in _action_jobs.keys():
        if static_part in ke:
            servers_key[ke] = _action_jobs[ke]
    for key in servers_key.keys():
        actionId = key.split('_')[0]
        if not actions.filter(id=actionId).exists():
            oldJob = _action_jobs.pop(key)
            _scheduler.cancel_job(oldJob)


def check_server(server_id):
    # threads = []

    server = Server.objects.get(id=server_id)
    server_serializer = ServerSerializer(server).data
    checked_server = check.CheckServer(
        host=server_serializer['host'],
        port=server_serializer['port'],
        username=server_serializer['username'],
        password=server_serializer['password']
    )
    if checked_server.check_server():
        # s_thread = threading.Thread(target=check_server_info, args=(server_id,))
        check_server_info(server_id)
        # threads.append(s_thread)
        # s_thread.start()

        actions = server.actions.all()
        trimActionsJob(actions, server_id)
        for action in actions:
            create_get_action_job(action.id, server_id, action.interval)
            # thread = threading.Thread(target=create_get_action_job, args=(action.id, server_id, action.interval))
            # threads.append(thread)
            # thread.start()

        dbServices = DBService.objects.filter(server_id=server_id).all()
        db_serializer = DBServiceSerializer(dbServices, many=True).data
        get_or_create_cache().lastDB[str(server_id)] = db_serializer
        for db in db_serializer:
            check_db(db['id'])
            # thread = threading.Thread(target=check_db, args=(db['id'],))
            # threads.append(thread)
            # thread.start()

        services = Service.objects.filter(server_id=server_id).all()
        get_or_create_cache().lastService[str(server_id)] = ServiceSerializer(services, many=True).data
        for service in services:
            check_service(service.id)
            # thread = threading.Thread(target=check_service, args=(service.id,))
            # threads.append(thread)
            # thread.start()

        # for thread in threads:
        #     thread.join()
    else:
        print('server has problem ', server_serializer)


def check_service(service_id):
    service = Service.objects.get(id=service_id)
    server = service.server
    server_serializer = ServerSerializer(server).data
    checked_server = check.CheckServer(
        host=server_serializer['host'],
        port=server_serializer['port'],
        username=server_serializer['username'],
        password=server_serializer['password']
    )
    result = checked_server.checkByCommand(
        command=service.command,
        contain=service.contain,
    )
    serializer = ServiceHistorySerializer(
        data={
            'status': result['success'],
            'type': 'server'
        }
    )
    if serializer.is_valid():
        serializer.save(service=service)
        get_or_create_cache().lastServiceHistory[str(service_id)] = serializer.data
    else:
        print(serializer.errors)


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
        get_or_create_cache().lastDBHistory[str(db_id)] = serializer.data
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
    created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cpu = round(info.get('cpu'))
    memory = round(info.get('memory'))
    ram = round(info.get('ram'))
    data = dict()
    data['cpu'] = cpu
    data['memory'] = memory
    data['ram'] = ram
    serializer = ServerInfoSerializer(data=data, )
    if serializer.is_valid():
        serializer.save(server=server)
        data = serializer.data
        data.pop('created_at')
        data['created_at'] = created_at
        get_or_create_cache().lastServerInfo[str(server_id)] = data

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
                break
        job = _scheduler.every(interval).seconds.do(do_action, action_id, server_id)
        _action_jobs[key] = job
    return job


def do_action(action_id, server_id):
    action = Action.objects.get(id=action_id)
    action_serializer = ActionSerializer(action).data
    server = Server.objects.get(id=server_id)
    server_serializer = ServerSerializer(server).data
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


def do_backup_scheduler():
    threads = []
    DBs = DBService.objects.filter(backup=True).all()
    for DB in DBs:
        thread = threading.Thread(target=backup_database, args=(DB,))
        threads.append(thread)
        thread.start()

    folders = FolderBackup.objects.all()
    for folder in folders:
        thread = threading.Thread(target=backup_folder, args=(folder,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def backup_database(db_id):
    print("start backup databse ")
    pass


def backup_folder(folder_id):
    folder = FolderBackup.objects.get(id=folder_id)
    folder_serializer = BackupSerializer(folder, many=False).data
    server = folder.server
    server_serializer = ServerSerializer(server).data
    checked_server = check.CheckServer(
        host=server_serializer['host'],
        port=server_serializer['port'],
        username=server_serializer['username'],
        password=server_serializer['password']
    )
    backup_result = checked_server.backupDirectory(
        path=folder_serializer['path'],
        to=folder_serializer['destination']
    )
    serializer = BackupHistorySerializer(
        data={
            'status': backup_result,
            'type': 'folder',
        }
    )
    if serializer.is_valid():
        serializer.save(folder=folder)
    else:
        print(serializer.errors)


_cash = None


def get_or_create_cache():
    global _cash

    if _cash is None:
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
        try:
            summery = dict()
            summery['id'] = str(server_id)
            """
             config:{
                id:1,
                name:'همدان',
                host:'host.com',
                port:2020,
                username:'hasan',
                password:'1234',
              },
            """
            info = self.lastServerInfo[str(server_id)]
            # if str(server_id) == '655fb319-bf83-496e-9fe5-0d58c520e59e':
            #     print('info is ', info)
            #     print('lastServerInfo is ', self.lastServerInfo)
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
                    'name': server['name'],
                    'host': server['host'],
                    'port': server['port'],
                    'username': server['username'],
                    'password': server['password'],
                }
                lastUpdate = info["created_at"]
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
            summery_list[server_id] = summery
            return summery
        except Exception as ex:
            print('in get_server_summery', ex)
            summery = dict()
            if summery_list.get(server_id,None) is None:
                for server in self.lastServer:
                    if server['id'] == str(server_id):
                        summery['config'] = {
                            'id': str(server_id),
                            'name': server['name'],
                            'host': server['host'],
                            'port': server['port'],
                            'username': server['username'],
                            'password': server['password'],
                        }
                        summery_list[server_id] = summery
                        return summery

    def get_summaries(self, oldSummery: dict):
        summaries = dict()
        for server in self.lastServer:
            old = oldSummery.get(server['id'], None)
            if old is not None:
                summaries[server['id']] = old
            temp = self.get_server_summery(server_id=server['id'], summery_list=summaries)
            print('for server ', server, 'temp ', temp)
        return summaries

    def save_summary(self):
        serializer = CacheModelSerializer(CacheModel.objects.order_by('-created_at').first(), many=False).data
        oldSummery = serializer['json']
        if oldSummery is None:
            oldSummery = dict()
        jsonResponse = self.get_summaries(oldSummery)

        CacheModel.objects.all().delete()

        CacheModel.objects.create(json=jsonResponse)

    def clear_cache(self):
        self.lastServerInfo.clear()
        self.lastServiceHistory.clear()
        self.lastService.clear()
        self.lastServer.clear()
        self.lastDB.clear()
        self.lastDBHistory.clear()
