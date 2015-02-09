from __future__ import with_statement
from fabric.api import *
from fabric.context_managers import shell_env

env.user = 'root'
env.hosts = ['supremote.com']

def deploy():
	code_dir = '/home/django/supremote'
	with cd(code_dir):
	with(shell_env(DJANGO_SETTINGS_MODULE='supremote.settings.production'))
		run('git pull')
		run('./manage.py migrate')
		run('./manage.py collectstatic --noinput')
		run('service gunicorn restart')
		run('service node restart')
