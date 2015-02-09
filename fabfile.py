from __future__ import with_statement
from fabric.api import *


env.user = 'root'
env.hosts = ['supremote.com']

def deploy():
	code_dir = '/home/django/supremote'
	with cd(code_dir):
		run('git pull')
		run('./manage.py migrate')
		run('./manage.py collectstatic --noinput')
		run('service gunicorn restart')
		run('service node restart')
