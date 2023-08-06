

JitsiProvS is a provisioning server for Jitsi(http://jitsi.org/).
Detailed information about Jitsi provisioning can be found here(http://jitsi.org/provisioning/).


The following concepts/ideas apply:

 * JitsiProvS is multitenant through the use of domain parameter. Domain parameter is taken from url or decoded from username (following @ symbol). Default domain is used in case none received, and that is 'localdomain'.
 * Simple authentication is built using username+domain+password values. The password value can be stored in plain text ('plain') or encrypted ('md5').
 * Https and http supported as transport protocols. Switch automatically done by defining both server key as well as certificate file.
 * Path url to be used: https://yourserverip:yourport/jitsiprovs/?$list_of_params.
 * Properties to be returned are loaded from database. For the moment the implementation is using MySQL, however more back-ends can be easily added on request.
 * Properties stored are in the form of string templates and for rendering are available the same parameters exported from Jitsi in provisioning url.
 * Properties returned overwrite themselves based on priority fields. Subjects available are the values of provisioning parameters exported by Jitsi plus a special subject named 'default' which serves as a "match-all" rule.
 * Priorities are taken in order, first the subject then property one. For each of priority category smallest priority value wins.
 * Application settings available as command line arguments. One can see all the options by running "jitsiprovs -h".
 * Asynchronous code execution through the use of gevent.
 * Horizontal scalable by using http loadbalancers in front (eg: nginx).


HowTo install the JitsiProvS on Debian (Squeeze by me):

1. Install debian related packages by running:
apt-get install python-pip python-dev python-mysqldb
2. Install Gevent 1.02 Beta (will get rid of this step when Gevent1 will be officially released):
pip install -U http://gevent.googlecode.com/files/gevent-1.0b2.tar.gz
3. Install JitsiProvS by running:
pip install JitsiProvS
4. Setup database:
/usr/local/scripts/jitsiprovs -n --setup
5. Run jitsiprovs (output on syslog):
/usr/local/scripts/jitsiprovs


For questions/issues please join us on google groups (jitsiprovs@googlegroups.com).

