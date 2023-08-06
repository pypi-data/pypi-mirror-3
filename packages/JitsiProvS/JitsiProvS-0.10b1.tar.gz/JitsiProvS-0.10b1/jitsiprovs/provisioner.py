import sqlobject
from flask import request
from string import Template

from jitsiprovs import dbdata, libprovisioner


class Provisioner( object ):
    """
    Implements processing logic for a request
    Returns the properties.
    """

    req_params = {
                'null': '${null}',
                'default': 'default',
                'domain': 'localdomain'
                } #Some help defaults

    def __init__( self, parent ):
        self._parent = parent


    def _is_auth( self ):
        usr = dbdata.UserAuth.selectBy( username=self.req_params['username'], domain=self.req_params['domain'] ).getOne(None)
        if not usr:
            return False
        if self._parent.settings.pwd_fmt == 'md5':
            return libprovisioner.matches_md5( self.req_params['password'], usr.password )
        elif self._parent.settings.pwd_fmt == 'plain':
            return self.req_params['password'] == usr.password
        return False # Unknown method


    def _set_req_params( self ):
        for key in request.form.keys():
            if key == 'username':
                usr_str = request.form[key]
                if '@' in usr_str:
                    self.req_params['username'], self.req_params['domain'] = request.form[key].split('@')
                else:
                    self.req_params['username'] = usr_str
            else:
                self.req_params[key] = request.form[key]
        return True


    def _get_properties( self ):
        props = []
        filters = ['default', 'username', 'password', 'osname', 'ipaddr', 'hwaddr', 'build', 'uuid', 'arch'] # All Jitsi url params plus default
        or_members = []
        for subj in filters:
            if subj in self.req_params.keys():
                or_members.append( dbdata.JitsiProperty.q.subject == self.req_params[subj] )
        for oprop in dbdata.JitsiProperty.select( sqlobject.OR(*or_members) ):
            if oprop.propertyKey not in [ keys[0] for keys in props ]: # We only add it if not already there
                props.append( ( oprop.propertyKey, oprop.propertyValue ) )
        return props


    def process( self ):
        self._set_req_params()
        if not self._is_auth():
            return ( None, 401, None )
        props = self._get_properties()
        retstr = ''
        for prop in props:
            retstr += Template( '%s=%s\n' % (prop[0],prop[1]) ).substitute(self.req_params)
        return retstr


