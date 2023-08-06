from gevent import sleep, spawn
from syslog import syslog
import sqlobject

from jitsiprovs.rootapp import RootApplication

def jp_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--http_ip", type="string", dest="http_ip",
                      default="0.0.0.0", help="Provisioning server listening IP Address [default: %default].",
                      metavar="HTTP_IP")
    parser.add_option("--http_port", type="int", dest="http_port",
                      default=8080, help="Provisioning server listening port [default: %default].",
                      metavar="HTTP_PORT")
    parser.add_option("--ssl_keyfile", type="string", dest="ssl_keyfile",
                      default=None, help="SSL Key file [default: %default].",
                      metavar="SSL_KEYFILE")
    parser.add_option("--ssl_certfile", type="string", dest="ssl_certfile",
                      default=None, help="SSL Certificate file [default: %default].",
                      metavar="SSL_CERTFILE")                      
    parser.add_option("--db_type", type="string", dest="db_type",
                      default="mysql", help="Database Type [default: %default].",
                      metavar="mysql")
    parser.add_option("--db_ip", type="string", dest="db_ip",
                      default="127.0.0.1", help="Database IP Address [default: %default].",
                      metavar="DB_ADDR")
    parser.add_option("--db_port", type="int", dest="db_port",
                      default=3306, help="Database port [default: %default].",
                      metavar="DB_PORT")
    parser.add_option("--db_name", type="string", dest="db_name",
                      default="jitsiprovs", help="Database name [default: %default].",
                      metavar="DB_NAME")
    parser.add_option("--db_user", type="string", dest="db_user",
                      default="jitsiprovs", help="Database user [default: %default].",
                      metavar="DB_USER")
    parser.add_option("--db_pwd", type="string", dest="db_pwd",
                      default="jitsi.org", help="Database name [default: %default].",
                      metavar="DB_PWD")
    parser.add_option("--db_from", type="string", dest="db_from",
                      default="127.0.0.1", help="IP Address from where we connect to db [default: %default].",
                      metavar="DB_FROM")
    parser.add_option("--pwd_fmt", type="string", dest="pwd_fmt",
                      default="md5", help="Password format stored in user_auth table [default: %default].",
                      metavar="md5|plain")
    parser.add_option("--setup", action="store_true", dest="setup",
                      default=False, help="Fire up data initialization")
    parser.add_option("--db_admin", type="string", dest="db_admin",
                      default="root", help="Database administrator username [default: %default].",
                      metavar="DB_ADMIN")
    parser.add_option("--db_apwd", type="string", dest="db_apwd",
                      default="jitsi.org", help="Database administrator password [default: %default].",
                      metavar="DB_APWD")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False, help="Set app debug on.")
    parser.add_option('-n', "--foreground", action="store_false", dest="daemon",
                      default=True, help="Run app in foreground.")
    parser.add_option("-p", "--pidfile", type="string", dest="pidfile",
                      default="/var/run/jitsiprovs.pid", help="Write pid to PIDFILE [default: %default].",
                      metavar="PIDFILE")
    parser.add_option("-u", "--user", type="string", dest="user",
                      default=None, help="User to start daemon with [default: %default].",
                      metavar="USER")
    parser.add_option("-g", "--group", type="string", dest="group",
                      default=None, help="Group to start daemon with [default: %default].",
                      metavar="GROUP")
    return parser.parse_args()


class JPApplication( RootApplication ):

    def __init__( self, options ):
        self.settings = options

    def _setup_db_mysql( self ):
        import MySQLdb
        db=MySQLdb.connect(host=self.settings.db_ip, port=self.settings.db_port,
                            user=self.settings.db_admin, passwd=self.settings.db_apwd )
        c=db.cursor()
        c.execute("""CREATE DATABASE %s""" % self.settings.db_name )
        c.execute("""GRANT ALL ON %s.* TO %s@%s IDENTIFIED BY '%s'""" % (
                        self.settings.db_name, self.settings.db_user, self.settings.db_from, self.settings.db_pwd ) )
        db.close()
        syslog("[%s] Database, user creation completed."%self.__class__.__name__)
        return

    def _setup_db_tables( self ):
        from jitsiprovs import dbdata, libdata
        if self.settings.db_type == 'mysql':
            self._setup_db_mysql()
        else:
            raise Exception("[%s] Unsupported database type" % self.__class__.__name__ )
        dbdata.UserAuth.createTable()
        dbdata.JitsiProperty.createTable()
        for prop, val in libdata.default_properties():
            propt = dbdata.JitsiProperty(subject='default', propertyKey=prop, propertyValue=val)
        syslog("[%s] Tables creation completed."%self.__class__.__name__)
        return


    def _db_up( self ):
        import sqlobject
        conn_str = "%s://%s:%s@%s:%s/%s" % (
                                self.settings.db_type, self.settings.db_user, self.settings.db_pwd, 
                                self.settings.db_ip, self.settings.db_port, self.settings.db_name )
        sqlobject.sqlhub.processConnection = sqlobject.connectionForURI(conn_str)
        return

    def _http_up( self ):
        from gevent.pywsgi import WSGIServer as WSGIServerS
        from gevent.wsgi import WSGIServer
        from flask import Flask
        from jitsiprovs.provisioner import Provisioner
        prov_app = Flask(__name__)
        prov_app.add_url_rule( '/jitsiprovs/', 'provisioner', Provisioner(self).process, methods=['POST'] )
        if self.settings.ssl_keyfile and self.settings.ssl_certfile: #Run on TLS
            prov_srv = WSGIServerS( (self.settings.http_ip, self.settings.http_port), prov_app, 
                                    keyfile=self.settings.ssl_keyfile, certfile=self.settings.ssl_certfile )
        else:
            prov_srv = WSGIServer( (self.settings.http_ip, self.settings.http_port), prov_app )
        syslog("[%s] Started provisioning server at %s:%s." % (self.__class__.__name__, self.settings.http_ip, self.settings.http_port))
        prov_srv.serve_forever()
        



    def start( self ):
        syslog("[%s] Started."%self.__class__.__name__)
        self._db_up()

        if self.settings.setup: #Initialization requested
            self._setup_db_tables()
            self._stop()

        self._http_up()

        while self._run: #Will continue running until something disconnects us
            sleep(0.1)

    def stop( self ):
        syslog("[%s] Stopped."%self.__class__.__name__)

