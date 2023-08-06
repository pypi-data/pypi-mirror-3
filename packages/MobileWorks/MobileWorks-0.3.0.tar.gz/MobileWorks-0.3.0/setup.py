from distutils.core import setup

setup( 
    name = 'MobileWorks',
    version = '0.3.0',
    py_modules = ['mobileworks'],
    url = 'http://www.mobileworks.com/',
    description = 'A library for the MobileWorks API.',
)

def get_credentials():
    '''
    This will read username/password from the user and check if they are correct or not.
    '''
    while True:
        username = raw_input( 'Username: ' )
        if username:
            password = raw_input( 'Password: ' )
            try:
                check_credentials( username, password )
                return username, password
            except Exception, e:
                print e
        else:
            return None, None

def check_credentials( username, password ):
    mw.username = username
    mw.password = password
    mw._authenticate()

import sys

cmd = sys.argv[1]

if cmd == 'install':
    import mobileworks as mw
    if not mw._credentials:
        print 'Would you please enter your username and password (leave the username empty to skip this step)'
        username, password = get_credentials()
        if username and password:
            mw.username = username
            mw.password = password
            mw._store_credentials()
