from __future__ import with_statement
from fabric.api import *
import os
import glob
import time


# Local Development
def run_local_server():
    """ Runs local development Django server """
    local("python manage.py runserver --settings=settings.local")
    
def run_local():
    """ Runs the local development process.  PIP, SYNC, MIGRATE """
    pip_install_req('local')
    sync_db('local')
    migrate('local')
    run_local_server()
    
def start_celery():
    """ Start a local celery instance with the django broker. """
    local("python manage.py celeryd -l info --concurrency=5 --settings=settings.local")
    
def test(app=None):
    """ Test(app) tests a given app name, if none is provided, runs the test runner for every single app, Django included. """
    if app:
        local('python manage.py test %s --settings=settings.local' % app)
    else:
        local('python manage.py test --settings=settings.local')
        
        
def self_upgrade(version):
    """ Upgrades the version of Hadrian in your local and to your designated server.  Pass the version (Branch, Tag) """
    local("pip install git+git://github.com/dstegelman/hadrian@%s#egg=hadrian --upgrade" % version)
    if env.branch:
        virtualenv("pip install git+git://github.com/dstegelman/hadrian@%s#egg=hadrian --upgrade" % version)

# Helper Functions

def collect_static():
    """ Collect static files, run before comitting call alpha or production first """
    local("python manage.py collectstatic --noinput --settings=settings.%s" % env.branch)

def virtualenv(command):
    with cd(env.directory):
        run(env.activate + '&&' + command)

def pip_install_req(environment):
    if environment == 'local':
        local("pip install -r conf/requirements.txt")
    else:
        virtualenv('pip install -r conf/requirements.txt') 

def sync_db(environment):
    if environment == "local":
        local("python manage.py syncdb --settings=settings.local")
    else:
        virtualenv('python manage.py syncdb --settings=settings.%s' % environment)
    
def migrate(environment):
    if environment == "local":
        local("python manage.py migrate --settings=settings.local")
    else:
        virtualenv('python manage.py migrate --settings=settings.%s' % environment)
        
def custom_migration(app, migration, environment):
    """ Runs a custom migration, takes App, Migration, and the settings environment to be run on.  HOSTED ONLY. """
    virtualenv('python manage.py migrate:%s %s --settings=settings.%s' % (app, migration, environment))

def build_migration(app):
    """ (app) Builds a migration for the specified app. """
    local("python manage.py schemamigration %s --auto --settings=settings.local" % app)
 
def make_release(tag):
    """ Makes a new production release.  Ensure you are on the production branch first.  Takes a tag. """
    local("git tag -a %s -m 'version %s'" % (tag, tag))
    local("git push --tags")
    print("Release %s has been made and pushed to github." % tag)
    
# Remote commands

def view_log():
    """ View the log of a given app. """
    run('sudo cat %s' % env.log_location)

def kick_apache():
    """ Kick the apache server for this app. """
    with cd(env.apache_bin_dir):
            run("./restart")

def get_code_latest(branch):
    with cd(env.directory):
        run('git pull origin %s' % branch)
        
def get_code_release(tag):
    with cd(env.directory):
        run('git fetch --tags')
        run('git checkout %s' % tag)
        
def copy_static():
    with cd(env.directory + '/static'):
        run('cp -r * ' + env.static_dir)
        
def alpha():
    """ Set environment to alpha. """
    env.branch = "alpha"
    set_hosts("alpha")        
        
def production():
    """ Set environment to production. """
    env.branch = "production"

def deploy(release_tag=None):
    """ Deploy an app on either alpha or production.  If production, a tag is required. """
    if env.branch == "production":
        get_code_release(release_tag)
    elif env.branch == "alpha":
        get_code_latest(env.branch)
    pip_install_req(env.branch)
    copy_static()
    sync_db(env.branch)
    migrate(env.branch)
    kick_apache()
    # Need to find out what we are going to do to restart.
    print("Deployment completed.")