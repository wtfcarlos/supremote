from fabric.api import *

"""
Base configuration
"""
env.project_name = 'supremote'
env.database_password = ''
env.path = '/home/django/supremote' % env

def setup():
	print 'hello'