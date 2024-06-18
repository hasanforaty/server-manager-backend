import pandas as pd
import psycopg2 as db
from sshtunnel import SSHTunnelForwarder
import datetime

import helper.cache_connection as ca


class CheckServer:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def check_server(self):
        try:
            connection = ca.getOrCreateConnection(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password
            )
            channel = connection.invoke_shell()
            channel.close()
            return True
        except Exception as ex:
            return False

    def check_database(self, database_name, username, password):
        sql = "select * from information_schema.tables  limit 1000"
        try:
            with SSHTunnelForwarder(
                    (self.host, self.port),
                    ssh_username=self.username,
                    ssh_password=self.password,
                    remote_bind_address=('localhost', 5432)
            ) as server:
                conn = db.connect(host='localhost',
                                  port=server.local_bind_port,
                                  user=username,
                                  password=password,
                                  dbname=database_name)
                pd.read_sql_query(sql, conn)
                return True
        except BaseException as ex:
            return False

    def getServerInfo(self):
        client = ca.getOrCreateConnection(self.host, port=self.port, username=self.username, password=self.password)
        cpu = self._getCPU(client)
        memory = self._getMemory(client)
        ram = self._getRAM(client)
        return {
            'cpu': cpu,
            'memory': memory,
            'ram': ram
        }

    def checkByCommand(self, command, contain):
        connection = ca.getOrCreateConnection(self.host, port=self.port, username=self.username, password=self.password)
        stdin, stdout, stderr = connection.exec_command(command)
        success = False
        output = ''
        for line in stdout:
            output += line
        if contain.lower() in output.lower():
            success = True
        else:
            success = False
        return {
            'success': success,
            'command': command,
            'log': output,
            'date': datetime.datetime.now()
        }

    def _getCPU(self, connection):
        stdin, stdout, stderr = connection.exec_command("""iostat -c""")
        """
        avg-cpu:  %user   %nice %system %iowait  %steal   %idle
                   0.46    0.03    0.16    0.04    0.00   99.30
        """
        responses = []
        for line in stdout:
            result = line.strip('\n')
            responses.append(result)
        index = 0
        for i in range(0, len(responses)):
            if 'avg' in responses[i]:
                index = i
        split = responses[index + 1].split()
        return 100 - float(split[len(split) - 1])

    def _getRAM(self, connection):
        stdin, stdout, stderr = connection.exec_command("""free -m""")
        """
                      total        used        free      shared  buff/cache   available
        Mem:          16012        4006         883         203       11122       11476
        Swap:          4095         249        3846
        """
        responses = []
        answer = {}
        for line in stdout:
            result = line.strip('\n')
            responses.append(result)
        keys = responses[0].split()
        values = responses[1].split()
        for i in range(0, len(keys)):
            answer[keys[i]] = values[i + 1]
        return float(int(answer['used']) / float(answer['total'])) * 100

    def _getMemory(self, connection):
        stdin, stdout, stderr = connection.exec_command("""df -ht ext4""")
        """
        Filesystem      Size  Used Avail Use% Mounted on
        /dev/sda2        98G  9.0G   84G  10% /
        /dev/sda3       909G  341G  523G  40% /var
        """
        responses = []
        for line in stdout:
            result = line.strip('\n')
            responses.append(result)
        keys = responses[0].split()
        remain = len(responses) - 1
        listValue = []
        """
        [
        {'Filesystem': '/dev/sda2', 'Size': '98G', 'Used': '9.0G', 'Avail': '84G', 'Use%': '10%', 'Mounted': '/'},
        {'Filesystem': '/dev/sda3', 'Size': '909G', 'Used': '341G', 'Avail': '523G', 'Use%': '40%', 'Mounted': '/var'}
        ]
        """
        for index in range(0, remain):
            answer = {}
            values = responses[index + 1].split()
            for i in range(0, len(keys) - 1):
                answer[keys[i]] = values[i]
            listValue.append(answer)

        size = 0
        used = 0
        for value in listValue:
            size_temp = float(value['Size'][:-1])
            if value['Size'].endswith('G'):
                size_temp = size_temp * 1024
            size += size_temp
            used_temp = float(value['Used'][:-1])
            if value['Used'].endswith('G'):
                used_temp = used_temp * 1024
            used += used_temp
        return float(used / size) * 100

    # def backup_database(self, database_name, username, password, ):
    #     # sql = "select * from information_schema.tables  limit 1000"
    #     sql = f"pg_dump {database_name} > backup"
    #     try:
    #         with SSHTunnelForwarder(
    #                 (self.host, self.port),
    #                 ssh_username=self.username,
    #                 ssh_password=self.password,
    #                 remote_bind_address=('localhost', 5432)
    #         ) as server:
    #             conn = db.connect(host='localhost',
    #                               port=server.local_bind_port,
    #                               user=username,
    #                               password=password,
    #                               dbname=database_name)
    #             pd.read_sql_query(sql, conn)
    #             return True
    #     except BaseException as ex:
    #         return False

    def backup_database(self, database_name, database_password, database_user, database_host, database_port):
        client = ca.getOrCreateConnection(self.host, port=self.port, username=self.username, password=self.password)
        connection = client.invoke_shell()
        channel_data = ''
        send_pass = False
        try:
            while True:
                if connection.recv_ready():
                    channel_data += str(connection.recv(9999))
                    print(channel_data)
                else:
                    continue
                if channel_data.endswith("~# '"):
                    connection.send(
                        f"pg_dump -h {database_host} -d {database_name} -U {database_user} -p {database_port} -f backup{datetime.datetime.now()}.sql \n")
                elif channel_data.endswith("Password: '"):
                    connection.send(f'{database_password}\n')
                    send_pass = True
                    continue
                if send_pass:
                    while True:
                        if connection.recv_ready():
                            channel_data += str(connection.recv(9999))
                        else:
                            continue
                        if channel_data.endswith("~# '"):
                            return True
        except Exception as ex:
            return False
        finally:
            connection.close()

    def backupDirectory(self, path: str, to: str):
        connection = ca.getOrCreateConnection(self.host, port=self.port, username=self.username, password=self.password)
        if path.endswith('/'):
            path = path[:-1]
        list = path.strip().split('/')
        name = list[len(list) - 1]
        output = ''
        dic_name = name + '_' + datetime.datetime.now().strftime("%Y_%m_%d_%H:%M")
        stdin, stdout, stderr = connection.exec_command("cp -v -r {} {}/{}".format(path, to, dic_name))
        for line in stdout:
            output += line
        re = False
        expectedOutput = "'{}' -> '{}/{}'".format(path, to, dic_name)
        if expectedOutput in output:
            re = True
        return re

    def check_backupDirectory(self, to_path: str):
        connection = ca.getOrCreateConnection(self.host, port=self.port, username=self.username, password=self.password)
        if to_path.endswith('/'):
            to_path = to_path[:-1]

        stdin, stdout, stderr = connection.exec_command("cd {} && ls -lt ".format(to_path))
        output = ""
        current_day = datetime.datetime.now().strftime("%d")
        for line in stdout:
            output += line
        output_list = output.split('\n')
        """
        total 24
        drwxr-xr-x 2 root root 4096 ژوئن    11 11:42 backup_2024_06_11_11:42
        drwxr-xr-x 2 root root 4096 ژوئن    11 11:34 backup_2024_06_11_11:34
        drwxr-xr-x 3 root root 4096 ژوئن    11 11:28 backup_2024_06_11_11:28
        drwxr-xr-x 2 root root 4096 ژوئن    11 11:25 backup_2024_06_11_11:25
        drwxr-xr-x 2 root root 4096 ژوئن    11 11:22 backup
        -rwxr-xr-x 1 root root 1491 ژوئن    11 11:22 code.txt
        """
        index = 0
        if 'total' in output_list[index]:
            index += 1
        if len(output_list) < 2:
            return False
        latest_backup_entry = output_list[index].split()
        if current_day in latest_backup_entry:
            return True
        return False

    # def check_backupDirectory(self, from_path: str, to_path: str):
    #     connection = ca.getOrCreateConnection(self.host, port=self.port, username=self.username, password=self.password)
    #     if to_path.endswith('/'):
    #         to_path = to_path[:-1]
    #     if from_path.endswith('/'):
    #         from_path = from_path[:-1]
    #
    #     stdin, stdout, stderr = connection.exec_command("cd {} && ls -lA".format(to_path))
    #     output = ""
    #     today_date = datetime.datetime.now().strftime("%Y_%m_%d")
    #     for line in stdout:
    #         output += line
    #     output_list = output.split()
    #     for line in output_list:
    #         if from_path in line and today_date in line:
    #             return True
    #     return False
