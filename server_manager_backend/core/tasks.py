import datetime
import logging
import threading
import time

import schedule
from django.db import connections, OperationalError
from django.db.models import QuerySet
from schedule import Scheduler

from core.closable_connection_thread import ConnectionThread

from backup.models import FolderBackup
from backup.serializers import BackupSerializer
from core.models import CacheModel, TaskModel
from core.serializers import CacheModelSerializer
from helper import check
from helper.check import StatusResult
from history.models import BackupHistory
from history.serializers import ServerInfoSerializer, ServiceHistorySerializer, ActionHistorySerializer, \
    BackupHistorySerializer
from server.models import Server, DBService, Action, Service
from server.serializers import ServerSerializer, DBServiceSerializer, ActionGetSerializer, ServiceSerializer

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


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
job: schedule.Job = None
_do_thread: ConnectionThread
scheduler: Scheduler = None
continues = None
action_jobs = dict()
backup_jobs: schedule.Job


def start_scheduler(do_every: int = 180, do_while: bool = True):
    """
    Starts a scheduler to do the server's task
    :param do_every: do the task every N seconds
    :return: None
    """
    global job, scheduler, continues
    # check_server = check.CheckServer(
    #     host=host,
    #     port=port,
    #     username=username,
    #     password=password
    # )
    # check_server.check_server()
    developMode = True
    if continues is not None:
        """closing opened connections """
        continues.set()
    if not developMode:
        scheduler = Scheduler()
        job = scheduler.every(do_every).seconds.do(check_servers)
        continues = scheduler.run_continuously()
        # if do_while:
        #     _do_thread = ConnectionThread(target=check_servers)
        #     _do_thread.start()
        start_backup_scheduler()


# def test_function():
#     taskModel = TaskModel.objects.all().last()
#     if not taskModel.active:
#         continues.set()
#     else:
#         print('test_function')
#     print(continues)


def start_backup_scheduler(hours: str = '21', minutes: str = '00'):
    global backup_jobs
    backup_jobs = scheduler.every().day.at(f'{hours}:{minutes}', "Iran").do(do_backup_scheduler)


def stop_scheduler():
    # schedule.clear()
    TaskModel(active=False).save()


def restart_scheduler(do_every: int = 180):
    stop_scheduler()
    for conn in connections.all():
        conn.close()
    start_scheduler(do_every=do_every)


def check_servers():
    global continues
    taskModel = TaskModel.objects.all().last()
    if taskModel is None:
        TaskModel(active=True).save()
        taskModel = TaskModel.objects.all().last()
    if not taskModel.active:
        continues.set()
        continues = None
    else:
        try:
            print('start checking ............ ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            cashed = get_or_create_cache()
            threads = []
            servers = ServerSerializer(Server.objects.all(), many=True).data
            get_or_create_cache().lastServer.clear()
            for value in servers:
                get_or_create_cache().lastServer.append(value)
                if value['active']:
                    thread = ConnectionThread(target=check_server, args=(value['id'],))
                    threads.append(thread)
                    thread.start()

            for thread in threads:
                thread.join(timeout=5)
            print('start creating summary ............ ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            cashed.save_summary()
            cashed.clear_cache()
            print('end creating summary ............ ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            print('end checking ............ ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        except Exception as e:
            print("restart Scheduler")
            restart_scheduler()


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
    for ke in action_jobs.keys():
        if static_part in ke:
            servers_key[ke] = action_jobs[ke]
    for key in servers_key.keys():
        actionId = key.split('_')[0]
        if not actions.filter(id=actionId).exists():
            oldJob = action_jobs.pop(key)
            scheduler.cancel_job(oldJob)


def check_server(server_id):
    # threads = []
    try:
        server = Server.objects.get(id=server_id)
        server_serializer = ServerSerializer(server).data
        checked_server = check.CheckServer(
            host=server_serializer['host'],
            port=server_serializer['port'],
            username=server_serializer['username'],
            password=server_serializer['password']
        )
        status = checked_server.check_server()
        get_or_create_cache().serverStatus[str(server_id)] = status
        logg = status.message + '' + str(status.exception)
        if logg == 'None':
            logg = ''
        server.log = logg
        server.save()
        if status.status:
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
    except OperationalError as e:
        print('restart scheduler ', e)
        # for conn in connections.all():
        #     logger.info('connection closed ', conn)
        #     conn.close()
        # restart_scheduler()
    except Exception as e:
        print('in task :', e)


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
            'type': 'server',
            'log': result['log'],
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
        database_name=db_serializer['serviceName'],
        username=db_serializer['username'],
        password=db_serializer['password'],
        type=db_serializer['type']
    )

    data = {
        'status': checked['success'],
        'type': "service",
        'log': checked['log'],
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
    # created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
        # data.pop('created_at')
        # data['created_at'] = created_at
        get_or_create_cache().lastServerInfo[str(server_id)] = data

    else:
        print(serializer.errors)


def create_get_action_job(action_id, server_id, interval):
    global action_jobs, scheduler
    key = "{}_{}_{}".format(action_id, server_id, str(interval))
    job = action_jobs.get(key, None)

    if job is None:
        # check to see if an interval has changes
        static_part = "{}_{}_".format(action_id, server_id)
        for ke in action_jobs.keys():
            if static_part in ke:
                old_job = action_jobs.pop(ke)
                scheduler.cancel_job(old_job)
                break
        job = scheduler.every(interval).seconds.do(do_action, action_id, server_id)
        action_jobs[key] = job
    return job


def do_action(action_id, server_id):
    action = Action.objects.get(id=action_id)
    action_serializer = ActionGetSerializer(action).data
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
        contain=''
    )
    serializer = ActionHistorySerializer(
        data={
            'log': result['log'],
            'created_at': result['date'],
            'status': result['success'],
        }
    )
    if serializer.is_valid():
        serializer.save(action=action, server=server)
    else:
        print(serializer.errors)


def do_backup_scheduler():
    print('start backup.....', datetime.datetime.now())
    threads = []
    DBs = DBServiceSerializer(DBService.objects.filter(backup=True).all(), many=True).data
    for DB in DBs:
        thread = ConnectionThread(target=backup_database, args=(DB['id'],))
        threads.append(thread)
        thread.start()

    folders = BackupSerializer(FolderBackup.objects.all(), many=True).data
    for folder in folders:
        is_checking = folder['is_checking']
        if is_checking is None:
            is_checking = False
        print('is_checking', is_checking)
        if is_checking:
            thread = ConnectionThread(target=check_folder_backup, args=(folder['id'],))
        else:
            thread = ConnectionThread(target=backup_folder, args=(folder['id'],))
        threads.append(thread)
        thread.start()

    # checkFolders = CheckBackupSerializer(CheckFolderBackup.objects.all(), many=True).data
    # for checkFolder in checkFolders:
    #
    #     threads.append(thread)
    #     thread.start()

    for thread in threads:
        thread.join()

    print('end backup.....', datetime.datetime.now())


def check_folder_backup(check_folder_id):
    print('start')
    check_folder = FolderBackup.objects.all().get(id=check_folder_id)
    server = check_folder.server
    server_serializer = ServerSerializer(server).data
    checked_server = check.CheckServer(
        host=server_serializer['host'],
        port=server_serializer['port'],
        username=server_serializer['username'],
        password=server_serializer['password']
    )
    deform_history = BackupHistory.objects.filter(
        folder_id=check_folder_id,
        status=False,
        created_at__month=datetime.datetime.now().month
    )
    for his in deform_history:
        result = checked_server.check_Folder_backupDirectory(
            check_folder.path,
            check_folder.pattern,
            check_date=his.created_at
        )
        print('result : ', result)
        if result:
            serializer = BackupHistorySerializer(his, data={
                'status': result,
            }, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)

    today = datetime.date.today()
    result = checked_server.check_Folder_backupDirectory(check_folder.path, check_folder.pattern, today)
    serializer = BackupHistorySerializer(
        data={
            'status': result,
            'type': 'backup',
            'log': ''
        }
    )
    if serializer.is_valid():
        serializer.save(folder=check_folder)
    else:
        print(serializer.errors)


def backup_database(db_id):
    db = DBService.objects.get(id=db_id)
    server = db.server
    server_serializer = ServerSerializer(server).data
    checked_server = check.CheckServer(
        host=server_serializer['host'],
        port=server_serializer['port'],
        username=server_serializer['username'],
        password=server_serializer['password']
    )
    backup_result = checked_server.backup_database(
        database_user=db.username,
        database_password=db.password,
        database_name=db.dbName,
        database_host=db.host,
        database_port=db.port,
        dbPath=db.backupPath,
        type=db.type,
    )
    serializer = BackupHistorySerializer(
        data={
            'status': backup_result['success'],
            'type': 'backup',
            'log': backup_result['log']
        }
    )
    if serializer.is_valid():
        serializer.save(service=db)
    else:
        print(serializer.errors)


def backup_folder(folder_id):
    folder = FolderBackup.objects.get(id=folder_id)
    try:
        print('in folder backup')
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
                'status': backup_result['success'],
                'type': 'folder',
                'log': backup_result['log']
            }
        )
        if serializer.is_valid():
            serializer.save(folder=folder)
        else:
            print(serializer.errors)
    except Exception as ex:
        print('in exception ')
        serializer = BackupHistorySerializer(
            data={
                'status': False,
                'type': 'folder',
                'log': str(ex)
            }
        )
        if serializer.is_valid():
            serializer.save(folder=folder)


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
        self.serverStatus = dict()

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
                server_status = self.serverStatus.get(str(server_id), None)
                if server_status is None:
                    server_status = StatusResult(status=True)
                summery['config'] = {
                    'id': str(server_id),
                    'name': server['name'],
                    'host': server['host'],
                    'port': server['port'],
                    'username': server['username'],
                    'password': server['password'],
                    'active': server['active'],
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
                    'status': [],
                    'log': server_status.message
                }
            services = self.lastService[str(server_id)]
            databases = self.lastDB[str(server_id)]
            service_convertor = []
            for service in services:
                service_convertor.append({
                    'id': str(service['id']),
                    'type': 'سرور',
                    'serviceName': service['serviceName'],
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
                        'name': service['serviceName'],
                        'status': status
                    })
            for database in databases:
                service_convertor.append({
                    'id': str(database['id']),
                    'type': 'دیتابیس',
                    'serviceName': database['serviceName'],
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
                        'name': database['serviceName'],
                        'status': status
                    })

            summery['services'] = service_convertor
            summery_list[server_id] = summery
            return summery
        except Exception as ex:
            print('in get_server_summery', ex)
            summery = dict()
            server_status = self.serverStatus.get(str(server_id), None)
            if server_status is None:
                server_status = StatusResult(status=True)
            for server in self.lastServer:
                if server['id'] == str(server_id):
                    if summery_list.get(server_id, None) is None:
                        summery['id'] = str(server_id)
                        summery['config'] = {
                            'id': str(server_id),
                            'name': server['name'],
                            'host': server['host'],
                            'port': server['port'],
                            'username': server['username'],
                            'password': server['password'],
                            'active': server['active'],
                        }
                        print('config : ', summery)
                        summery['info'] = {
                            'id': '',
                            'server': server['name'],
                            'ram': 0,
                            'memory': 0,
                            'cpu': 0,
                            'lastUpdate': None,
                            'lastBackup': None,
                            'status': [],
                            'log': server_status.message + ' ' + str(server_status.exception)
                        }
                        summery_list[server_id] = summery
                        return summery
                    else:
                        try:
                            summery_list.get(server_id)['info']['log'] = server_status.message + ' ' + str(
                                server_status.exception)
                            summery_list.get(server_id)['config']['active'] = server['active']
                        except Exception as e:
                            print('in summery', e)

    def get_summaries(self, oldSummery: dict):
        summaries = dict()
        for server in self.lastServer:
            old = oldSummery.get(server['id'], None)
            if old is not None:
                summaries[server['id']] = old
            temp = self.get_server_summery(server_id=server['id'], summery_list=summaries)
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
