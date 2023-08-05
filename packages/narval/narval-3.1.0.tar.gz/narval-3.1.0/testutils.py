import os
import sys
import subprocess

from logilab.common.tasksqueue import LOW

from cubicweb.devtools.testlib import CubicWebTC

from cubes.narval import proxy

import narvalbot as bot
from narvalbot import server, main


os.killpg = lambda x,y: None


class Popen:
    pid = -1
    returncode = 0

    def __init__(self, command, bufsize, stdout, stderr):
        self.command = command
        self.stdout = stdout
        self.stderr = stderr

    def communicate(self):
        try:
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            main.run(self.command[1:])
        except SystemExit, ex:
            self.returncode = ex.code
        except:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            import traceback
            traceback.print_exc()
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__


class NarvalBaseTC(CubicWebTC):
    """Narval Base class for Narval Recipe test."""

    def setUp(self):
        super(NarvalBaseTC, self).setUp()
        config = bot.NarvalConfiguration()
        config['plugins'] = config.get_option_def('plugins')['default']
        self.npm = server.NarvalProcessManager(config)
        # monkey patch the connection handler
        def mp_connect(ch):
            ch.cnx = self.cnx
            ch.cw = self.cnx.request()
            ch._cu = self.cnx.cursor(ch.cw)
            return self.cnx
        self.orig_connect = bot.ConnectionHandler.connect
        bot.ConnectionHandler.connect = mp_connect
        self.orig_close = bot.ConnectionHandler.close
        bot.ConnectionHandler.close = lambda x: None
        # monkey patch proxy
        def mp_proxy(config, cache):
            return self.npm
        self.orig_proxy = proxy.bot_proxy
        proxy.bot_proxy = mp_proxy
        # monkey patch npm
        server.Popen = Popen
        if not self.session.user.is_in_group('narval'):
            self.execute('SET U in_group G WHERE U login "admin", G name "narval"')
            self.commit()
        self.req = self.request()

    def tearDown(self):
        self.npm._quit()
        super(NarvalBaseTC, self).tearDown()
        bot.ConnectionHandler.connect = self.orig_connect
        bot.ConnectionHandler.close = self.orig_close
        proxy.bot_proxy = self.orig_proxy
        server.Popen = subprocess.Popen

    def run_recipe(self, recipe, expected_status="done", arguments=None):
        req = recipe._cw
        cwplan = req.create_entity('Plan', priority=LOW, arguments=arguments,
                                   execution_of=recipe)
        self.assertEqual(self.npm._queue.qsize(), 0)
        req.cnx.commit()
        self.assertEqual(cwplan.execution_status, 'ready')
        self.assertEqual(self.npm._queue.qsize(), 1)
        self.npm._start_processes()
        self.assertEqual(self.npm._queue.qsize(), 0)
        for thread, plan in self.npm._running_tasks.copy():
            thread.join()
        cwplan = self.execute('Any X,XS WHERE X eid %(x)s, X execution_status XS',
                              {'x': cwplan.eid}).get_entity(0, 0)
        self.assertEqual(cwplan.execution_status, expected_status, cwplan.execution_log)
        return cwplan
