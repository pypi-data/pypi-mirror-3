import csv
import os
import logging

logger = logging.getLogger('raisin.recipe.server.server')


def read_csv(file_name):
    return [line for line in csv.DictReader(open(file_name, 'r'),
                                            delimiter='\t',
                                            skipinitialspace=True)]


def projects_ini(buildout_directory, projects):
    """
    Produce a projects.ini file:
    
    etc/projects/projects.ini
    
    Like this:
    
    [Test]
    projects = Test,
        [[dbs]]
        RNAseqPipeline = db
        RNAseqPipelineCommon = dbcommon
    """
    path = os.path.join(buildout_directory, 'etc/projects')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(buildout_directory, 'etc/projects/projects.ini')
    ini = open(path, 'w')
    for project in projects:
        ini.write('[%s]\n' % project)
        ini.write('projects = %s,\n' % project)
        ini.write('    [[dbs]]\n')
        ini.write('    RNAseqPipeline = %s\n' % project)
        ini.write('    RNAseqPipelineCommon = %sCommon\n' % project)
        ini.write('\n')
    ini.close()
    logger.info('Writing :%s' % path)


def databases_ini(buildout_directory, dbs):
    """
    Produce a databases.ini file:

    etc/databases/databases.ini

    Like this:
    
    [Test]
    connection = raisin
    db = Test_RNAseqPipeline
    description = Contains the meta data
    
    [TestCommon]
    connection = raisin
    db = Test_RNAseqPipelineCommon
    description = Contains all the statistics results
    """
    path = os.path.join(buildout_directory, 'etc/databases')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(buildout_directory, 'etc/databases/databases.ini')
    ini = open(path, 'w')
    projects = []
    for project_id, db, commondb in dbs:
        if project_id in projects:
            print "Ignoring project", project_id, db, commondb
            continue
        else:
            projects.append(project_id)
        ini.write('[%s]\n' % project_id)
        ini.write('connection = raisin\n')
        ini.write('db = %s\n' % db)
        ini.write('description = Contains the meta data\n')
        ini.write('\n')
        ini.write('[%sCommon]\n' % project_id)
        ini.write('connection = raisin\n')
        ini.write('db = %s\n' % commondb)
        ini.write('description = Contains all the statistics results\n')
        ini.write('\n')
    ini.close()
    logger.info('Writing :%s' % path)

def get_profiles(staging):
    profiles = read_csv(os.path.join(staging, 'profiles.csv'))
    profiles = [profile for profile in profiles]
    profiles.sort()
    return profiles

def get_projects(profiles):
    projects = set()
    for profile in profiles:
        projects.add(profile['project_id'])
    projects = list(projects)
    projects.sort()
    return projects


def get_dbs(profiles):
    dbs = set()
    for profile in profiles:
        dbs.add((profile['project_id'], profile['DB'], profile['COMMONDB'],))
    dbs = list(dbs)
    dbs.sort()
    return dbs

def pyramid_projects_ini(buildout_directory, projects, project_users):
    """
    Produce a projects.ini file for pyramid:
    
    etc/pyramid/projects.ini
    
    Like this:
    
    [Test]
    users = "raisin",
    """
    path = os.path.join(buildout_directory, 'etc/pyramid')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(buildout_directory, 'etc/pyramid/projects.ini')
    ini = open(path, 'w')
    for project in projects:
        ini.write('[%s]\n' % project)
        ini.write('users = %s,\n' % ','.join(project_users[project]))
        ini.write('\n')
    ini.close()
    logger.info('Writing :%s' % path)

def get_parameters(buildout):
    vocabulary = buildout['parameter_vocabulary']
    categories = buildout['parameter_categories']
    types = buildout['parameter_types']
    columns = buildout['parameter_columns']
    parameters = {}
    for key, value in vocabulary.items():
        parameters[key] = {'title':value,
                           'category':categories[key],
                           'type':types[key],
                           'column':columns[key]
                           }
    return parameters
    
def misc_parameters_ini(buildout_directory, parameters):
    """
    Produce a parameters.ini file:
    
    etc/misc/parameters.ini
    
    Like this:
    
    [partition]
    title = Partition
    type = string
    """
    path = os.path.join(buildout_directory, 'etc/misc')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(buildout_directory, 'etc/misc/parameters.ini')
    ini = open(path, 'w')
    keys = parameters.keys()
    keys.sort()
    for key in keys:
        parameter = parameters[key]
        ini.write('[%s]\n' % key)
        ini.write('title = %s\n' % parameter['title'])
        ini.write('category = %s\n' % parameter['category'])
        ini.write('type = %s\n' % parameter['type'])
        ini.write('column = %s\n' % parameter['column'])
        ini.write('\n')
    ini.close()
    logger.info('Writing :%s' % path)

def get_project_users(buildout, projects):
    project_users = {}
    for project in projects:
        if project in buildout['project_users']:
            project_users[project] = buildout['project_users'][project].split('\n')
        else:
            # If no users are specified for a project, use the anonymous user
            project_users[project] = ['anonymous']
    return project_users


def get_project_parameters(buildout, projects):
    project_parameters = buildout['project_parameters']
    results = {}
    for project in projects:
        if project in project_parameters:
            results[project] = project_parameters[project].split("\n")
        else:
            # If no project parameters are given, use read_length
            results[project] = ['read_length']
    return results

def misc_project_parameters_ini(buildout_directory, project_parameters):
    """
    Produce a project_parameters.ini file:
    
    etc/misc/project_parameters.ini
    
    Like this:
    
    [Test]
    parameters = 'read_length',
    """
    path = os.path.join(buildout_directory, 'etc/misc')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(buildout_directory, 'etc/misc/project_parameters.ini')
    ini = open(path, 'w')
    keys = project_parameters.keys()
    keys.sort()
    for key in keys:
        parameters = project_parameters[key]
        ini.write('[%s]\n' % key)
        value = ['"%s"' % p for p in parameters]
        ini.write('parameters = %s,\n' % ', '.join(value))
        ini.write('\n')
    ini.close()
    logger.info('Writing :%s' % path)

def connections_mysql_ini(buildout_directory):
    """Create the mysql connection file"""
    path = os.path.join(buildout_directory, 'etc/connections')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(buildout_directory, 'etc/connections/mysql.ini')
    if os.path.exists(path):
        logger.info('Keeping existing configuration file: %s' % path)
    else:
        ini = open(path, 'w')
        ini.write("[raisin]\n")
        ini.write("port = 3306\n")
        ini.write("server = 127.0.0.1\n")
        ini.write("user = raisin\n")
        ini.write("password = raisin\n")
        ini.close()
        logger.info('Writing: %s' % path)

def pyramid_development_ini(buildout_directory):
    path = os.path.join(buildout_directory, 'etc/pyramid')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(buildout_directory, 'etc/pyramid/development.ini')
    if os.path.exists(path):
        logger.info('Keeping existing configuration file: %s' % path)
    else:
        ini = open(path, 'w')
        ini.write("""[app:main]
use = egg:raisin.pyramid

pyramid.reload_templates = true
pyramid.debug_authorization = false
pyramid.debug_notfound = false
pyramid.debug_routematch = false
pyramid.debug_templates = true
pyramid.default_locale_name = en
pyramid.includes = pyramid_debugtoolbar

[server:main]
use = egg:waitress#main
host = 0.0.0.0
port = 7777

# Begin logging configuration

[loggers]
keys = root, raisin

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = INFO
handlers = console

[logger_raisin]
level = DEBUG
handlers =
qualname = raisin

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s

# End logging configuration""")
        ini.close()
        logger.info('Writing: %s' % path)

def restish_development_ini(buildout_directory):
    path = os.path.join(buildout_directory, 'etc/restish')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(buildout_directory, 'etc/restish/development.ini')
    if os.path.exists(path):
        logger.info('Keeping existing configuration file: %s' % path)
    else:
        ini = open(path, 'w')
        ini.write("""[DEFAULT]
; Application id used to prefix logs, errors, etc with something unique to this
; instance.
APP_ID = raisin.restish@localhost
; Email settings.
SMTP_SERVER = localhost
ERROR_EMAIL_FROM = %(APP_ID)s
ERROR_EMAIL_TO = %(APP_ID)s

CACHE_DIR = %(here)s/cache

use_pickles_cache = False
use_sql_database = True
pickles_cache_path = %(here)s/../../cache
mysql_connections = %(here)s/../connections/mysql.ini
mysql_databases = %(here)s/../databases/databases.ini
projects = %(here)s/../projects/projects.ini
parameters = %(here)s/../misc/parameters.ini
project_parameters = %(here)s/../misc/project_parameters.ini
sqlite3_database = %(here)s/../../etl/database/database.db

[composite:main]
use = egg:Paste#cascade
app1 = public
app2 = raisin.restish

[app:raisin.restish]
use = config:raisin.restish.ini#raisin.restish

[app:public]
use = egg:Paste#static
document_root = %(here)s/raisin.restish/public

[server:main]
use = egg:Paste#http
host = 127.0.0.1
port = 6464

# Logging configuration
[loggers]
keys = root, raisin.restish

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = DEBUG
handlers = console

[logger_raisin.restish]
level = DEBUG
handlers =
qualname = raisin.restish

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S""")
        ini.close()
        logger.info('Writing: %s' % path)

def restish_raisin_restish_ini(buildout_directory):
    path = os.path.join(buildout_directory, 'etc/restish')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(buildout_directory, 'etc/restish/raisin.restish.ini')
    if os.path.exists(path):
        logger.info('Keeping existing configuration file: %s' % path)
    else:
        ini = open(path, 'w')
        ini.write("""[app:raisin.restish]
use = egg:raisin.restish
cache_dir = %(CACHE_DIR)s""")
        ini.close()
        logger.info('Writing: %s' % path)

def pyramid_users_ini(buildout_directory):
    path = os.path.join(buildout_directory, 'etc/pyramid')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(buildout_directory, 'etc/pyramid/users.ini')
    if os.path.exists(path):
        logger.info('Keeping existing configuration file: %s' % path)
    else:
        ini = open(path, 'w')
        ini.write('''[raisin]
password = "raisin"''')
        ini.close()
        logger.info('Writing: %s' % path)

def supervisord_conf(buildout_directory, mode):
    path = os.path.join(buildout_directory, 'etc/supervisor')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(buildout_directory, 'etc/supervisor/%s.conf' % mode)
    if os.path.exists(path):
        logger.info('Keeping existing configuration file: %s' % path)
    else:
        conf = open(path, 'w')
        conf.write("""[supervisord]\n""")
        path = os.path.join(buildout_directory, "var/log")
        conf.write("""childlogdir = %s\n""" % path)
        path = os.path.join(buildout_directory, "var/log/supervisord.log")
        conf.write("""logfile = %s\n""" % path)
        conf.write("""logfile_maxbytes = 50MB\n""")
        conf.write("""logfile_backups = 10\n""")
        conf.write("""loglevel = info\n""")
        path = os.path.join(buildout_directory, "var/supervisord.pid")
        conf.write("""pidfile = %s\n""" % path)
        conf.write("""umask = 022\n""")
        conf.write("""nodaemon = false\n""")
        conf.write("""nocleanup = false\n""")
        conf.write("""\n""")
        conf.write("""[inet_http_server]\n""")
        conf.write("""port = 127.0.0.1:9001\n""")
        conf.write("""username = \n""")
        conf.write("""password = \n""")
        conf.write("""\n""")
        conf.write("""[supervisorctl]\n""")
        conf.write("""serverurl = http://127.0.0.1:9001\n""")
        conf.write("""username = \n""")
        conf.write("""password = \n""")
        conf.write("""\n""")
        conf.write("""[rpcinterface:supervisor]\n""")
        conf.write("""supervisor.rpcinterface_factory=supervisor.rpcinterface:make_main_rpcinterface\n""")
        conf.write("""\n""")
        conf.write("""[program:restish]\n""")
        path = os.path.join(buildout_directory, "bin/pserve")
        config_file = os.path.join(buildout_directory, "etc/restish/%s.ini" % mode)
        conf.write("""command = %s %s\n""" % (path, config_file))
        conf.write("""process_name = restish\n""")
        conf.write("""directory = %s\n""" % buildout_directory)
        conf.write("""priority = 10\n""")
        conf.write("""redirect_stderr = false\n""")
        conf.write("""\n""")
        conf.write("""[program:pyramid]\n""")
        path = os.path.join(buildout_directory, "bin/pserve")
        config_file = os.path.join(buildout_directory, "etc/pyramid/%s.ini" % mode)
        conf.write("""command = %s %s\n""" % (path, config_file))
        conf.write("""process_name = pyramid\n""")
        conf.write("""directory = %s\n""" % buildout_directory)
        conf.write("""priority = 20\n""")
        conf.write("""redirect_stderr = false\n""")
        conf.close()
        logger.info('Writing: %s' % path)


def var_log_folder(buildout_directory):
    """
    Create the var/log folder needed when starting raisin with supervisord.
    """
    path = os.path.join(buildout_directory, 'var/log')
    if not os.path.exists(path):
        os.makedirs(path)

        
def main(buildout, buildout_directory, staging):
    profiles = get_profiles(staging)
    projects = get_projects(profiles)
    projects_ini(buildout_directory, projects)
    dbs = get_dbs(profiles)
    databases_ini(buildout_directory, dbs)
    project_users = get_project_users(buildout, projects)
    pyramid_projects_ini(buildout_directory, projects, project_users)
    parameters = get_parameters(buildout)
    misc_parameters_ini(buildout_directory, parameters)
    project_parameters = get_project_parameters(buildout, projects)
    misc_project_parameters_ini(buildout_directory, project_parameters)
    connections_mysql_ini(buildout_directory)
    pyramid_development_ini(buildout_directory)
    restish_development_ini(buildout_directory)
    restish_raisin_restish_ini(buildout_directory)
    pyramid_users_ini(buildout_directory)
    supervisord_conf(buildout_directory, "development")
    supervisord_conf(buildout_directory, "production")
    var_log_folder(buildout_directory)
