"""
Deployment script for ORES setup on Wikimedia Labs

Fabric script for doing multiple operations on ORES servers,
both production and staging.

## Setting up a new server ##

This assumes that the puppet role has been applied, and then you
can initialize it with:

    fab initialize_server:hosts="<fqdn1>;<fqdn2>"

This:
    1. Sets up the virtualenv appropriately
    2. Downloads NLTK corpuses
    3. Sets up latest models
    4. Does a deploy / restarts uwsgi

For first time use, just doing this step should provide a working server!

## Deploying a code update to staging ##

This pushes the 'staging' branch to the staging server. Make sure to push
the changes you want to test / stage to the 'staging' branch before running
this! You can run this with:

    fab stage

This updates the staging server (ores-staging.wmflabs.org) with code from
the staging branch, and restarts uwsgi so the changes take effect.

## Deploying a code update to 'production' ##

This pushes the 'deploy' branch to the production servers. Make sure to push
the changes you want deployed to the 'deploy' branch before running this!
This can be simply run by:

    fab deploy

This updates all the web workers of ores to the new code and restarts them.
"""
from fabric.api import sudo, env, cd, roles, shell_env

env.roledefs = {
    'web': ['ores-web-01.eqiad.wmflabs', 'ores-web-02.eqiad.wmflabs'],
    'staging': ['ores-staging.eqiad.wmflabs'],
}
env.use_ssh_config = True

src_dir = '/srv/ores/src'
venv_dir = '/srv/ores/venv'
data_dir = '/srv/ores/data'


def sr(*cmd):
    with shell_env(HOME='/srv/ores'):
        return sudo(' '.join(cmd), user='www-data', group='www-data')


def initialize_server():
    """
    Setup an initial deployment on a fresh host.

    This currently does:

    - Creates the virtualenv
    - Installs virtualenv
    - Installs nltk corpuses
    - Installs the model files
    """
    update_git()
    sr('mkdir', '-p', venv_dir)
    sr('virtualenv', '--python', 'python3', '--system-site-packages', venv_dir)
    sr(venv_dir + '/bin/pip', 'install', '--upgrade',
       '-r', src_dir + '/requirements.txt')
    sr(venv_dir + '/bin/python', '-m', 'nltk.downloader',
       '-d', data_dir + '/nltk',
       'wordnet', 'omw', 'stopwords')
    sr('git', 'clone', 'https://github.com/yuvipanda/ores-models.git',
       '/srv/ores/src/models')
    restart_uwsgi()


@roles('web')
def update_git(branch='deploy'):
    with cd(src_dir):
        sr('git', 'fetch', 'origin')
        sr('git', 'reset', '--hard', 'origin/%s' % branch)


@roles('web')
def restart_uwsgi():
    sudo('uwsgictl restart')


@roles('web')
def deploy_web():
    update_git()
    restart_uwsgi()


@roles('staging')
def stage():
    update_git('staging')
    restart_uwsgi()


def run_puppet():
    sudo('puppet agent -tv')
