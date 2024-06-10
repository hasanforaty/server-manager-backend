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
            ca.getOrCreateConnection(self.host, port=self.port, username=self.username, password=self.password)
            return True
        except BaseException as ex:
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
            size += float(value['Size'].strip('G'))
            used += float(value['Used'].strip('G'))
        return float(used / size) * 100
