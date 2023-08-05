import os

from distutils.core import setup
from distutils.command.install_scripts import install_scripts


ETC_DIR = '/etc/chartio'
ETC_SSH_DIR = '/etc/chartio/sshkey'
CONF_LOCATION = '/etc/chartio/chartio.cfg'
PIDFILE_LOCTATION = '/var/run/chartio_connect.pid'
LOGFILE_LOCATION = '/var/log/chartio_connect.log'

class PostInstall(install_scripts):

    def run(self):
        install_scripts.run(self)
        # Touch files as root and make writeable
        if not os.path.exists(ETC_DIR):
            os.system('mkdir %s' % ETC_DIR)
            os.system('chmod 755 %s' % ETC_DIR)
        if not os.path.exists(ETC_SSH_DIR):
            os.system('mkdir %s' % ETC_SSH_DIR)
            os.system('chmod 777 %s' % ETC_SSH_DIR)
        for fi in [CONF_LOCATION, PIDFILE_LOCTATION, LOGFILE_LOCATION]:
            os.system('touch %s' % fi)
            os.system('chmod 666 %s' % fi)


setup(  cmdclass=dict(install_scripts=PostInstall),
        name='chartio',
        version='1.1.2',
        scripts=['chartio_setup', 'chartio_connect'],
        classifiers = ['Environment :: Console',
                       'Intended Audience :: System Administrators',
                       'License :: Other/Proprietary License',
                       'Natural Language :: English',
                       'Operating System :: POSIX',
                       'Programming Language :: Python',
                       'Programming Language :: Python :: 2.4',
                       'Programming Language :: Python :: 2.5',
                       'Programming Language :: Python :: 2.6',
                       'Programming Language :: Python :: 2.7',
                       'Topic :: System :: Monitoring',
                       'Topic :: Database',
                       'Topic :: Database :: Database Engines/Servers',
                       ],
        requires=['simplejson'],
        url="http://chart.io/", 
        author="chart.io",
        author_email="support@chart.io",
        description="Setup wizard and connection client for connecting MySQL databases to chart.io",
)
