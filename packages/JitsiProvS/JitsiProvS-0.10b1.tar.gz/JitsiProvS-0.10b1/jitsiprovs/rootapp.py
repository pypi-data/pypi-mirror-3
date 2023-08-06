from syslog import syslog
import signal


class RootApplication(object):

    def daemon_context(self, pidfile, user, group, signal_map):
        """This will daemonize the current application
        """
        from daemon import DaemonContext
        from daemon.runner import make_pidlockfile
        import pwd, grp
        dc = DaemonContext()
        dc.signal_map = signal_map
        dc.pidfile = make_pidlockfile( pidfile, 2 )#Timeout of 2 seconds to wait for creation of pid file
        if user:
            dc.uid = int(pwd.getpwnam(user)[2])
        if group:
            dc.gid = int(grp.getgrnam(group)[2])
        return dc


    def _setup_gsignals(self, signal_map):
        from gevent import signal
        for sgnal, func in signal_map.items():
            args = [sgnal, None]
            signal(sgnal, func, *args)
        return


    def start(self):
        """Rewrite in children apps"""
        raise NotImplementerError


    def stop(self):
        """Rewrite in children apps"""
        raise NotImplementedError


    def _start(self):
        import signal
        from gevent import monkey
        signal_map={ signal.SIGTERM: self._stop, signal.SIGINT: self._stop }
        if self.settings.daemon:
            self.daemon_context(self.settings.pidfile, self.settings.user, self.settings.group, signal_map).open()
        else:
            self._setup_gsignals( signal_map ) #in case of python daemon, gevent inherits signals
        monkey.patch_all(thread=False)
        self._run = True
        self.start()


    def _stop(self, *args):
        import sys
        self._run = False
        self.stop()
        sys.exit()


    def run(self):
        self._start()
        self._stop()



