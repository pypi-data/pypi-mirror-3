from collections import defaultdict
import threading
from circus.commands import get_commands
from circus.client import CircusClient, CallError

try:
    from gevent import monkey, local
    if not threading.local is local.local:
        monkey.patch_all()
except ImportError:
    pass

cmds = get_commands()


class LiveClient(object):
    def __init__(self, endpoint):
        self.endpoint = str(endpoint)
        self.stats_endpoint = None
        self.client = CircusClient(endpoint=self.endpoint)
        self.connected = False
        self.watchers = []
        self.stats = defaultdict(list)
        self.dstats = []

    def stop(self):
        self.client.stop()

    def verify(self):
        self.watchers = []
        # trying to list the watchers
        msg = cmds['list'].make_message()
        try:
            res = self.client.call(msg)
            self.connected = True
            for watcher in res['watchers']:
                if watcher == 'circusd-stats':
                    continue
                msg = cmds['options'].make_message(name=watcher)
                options = self.client.call(msg)
                self.watchers.append((watcher, options['options']))
            self.watchers.sort()
            self.stats_endpoint = self.get_global_options()['stats_endpoint']
        except CallError:
            self.connected = False

    def killproc(self, name, pid):
        msg = cmds['signal'].make_message(name=name, process=int(pid),
                signum=9)
        res = self.client.call(msg)
        self.verify()  # will do better later
        return res['status'] == 'ok'

    def get_option(self, name, option):
        watchers = dict(self.watchers)
        return watchers[name][option]

    def get_global_options(self):
        msg = cmds['globaloptions'].make_message()
        options = self.client.call(msg)
        return options['options']

    def get_options(self, name):
        watchers = dict(self.watchers)
        return watchers[name].items()

    def incrproc(self, name):
        msg = cmds['incr'].make_message(name=name)
        res = self.client.call(msg)
        self.verify()  # will do better later
        return res['numprocesses']

    def decrproc(self, name):
        msg = cmds['decr'].make_message(name=name)
        res = self.client.call(msg)
        self.verify()  # will do better later
        return res['numprocesses']

    def get_stats(self, name, start=0, end=-1):
        return self.stats[name][start:end]

    def get_dstats(self, field, start=0, end=-1):
        stats = self.dstats[start:end]
        res = []
        for stat in stats:
            res.append(stat[field])
        return res

    def get_pids(self, name):
        msg = cmds['listpids'].make_message(name=name)
        res = self.client.call(msg)
        return res['pids']

    def get_series(self, name, pid, field, start=0, end=-1):
        stats = self.get_stats(name, start, end)
        res = []
        for stat in stats:
            pids = stat['pid']
            if isinstance(pids, list):
                continue
            if str(pid) == str(stat['pid']):
                res.append(stat[field])
        return res

    def get_status(self, name):
        msg = cmds['status'].make_message(name=name)
        res = self.client.call(msg)
        return res['status']

    def switch_status(self, name):
        msg = cmds['status'].make_message(name=name)
        res = self.client.call(msg)
        status = res['status']
        if status == 'active':
            # stopping the watcher
            msg = cmds['stop'].make_message(name=name)
        else:
            msg = cmds['start'].make_message(name=name)
        res = self.client.call(msg)
        return res

    def add_watcher(self, name, cmd, **kw):
        msg = cmds['add'].make_message(name=name, cmd=cmd)
        res = self.client.call(msg)
        if res['status'] == 'ok':
            # now configuring the options
            options = {}
            options['numprocesses'] = int(kw.get('numprocesses', '5'))
            options['working_dir'] = kw.get('working_dir')
            options['shell'] = kw.get('shell', 'off') == 'on'
            msg = cmds['set'].make_message(name=name, options=options)
            res = self.client.call(msg)
            self.verify()  # will do better later
            return res['status'] == 'ok'
        else:
            return False
