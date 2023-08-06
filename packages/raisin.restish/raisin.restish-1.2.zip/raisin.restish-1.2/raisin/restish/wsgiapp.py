"""
WSGI/PasteDeploy application bootstrap module.
"""
import os
import sqlite3
from configobj import ConfigObj
from restish.app import RestishApp
from raisin.resource import root
from raisin.mysqldb import DB


def make_app(global_conf, **app_conf):
    """
    PasteDeploy WSGI application factory. Called by PasteDeploy (or a compatable WSGI application
    host) to create the raisin.restish WSGI application.
    """
    app = RestishApp(root.Root())
    app = setup_environ(app, global_conf, app_conf)
    return app


def setup_environ(app, global_conf, app_conf):
    """
    WSGI application wrapper factory for extending the WSGI environ with application-specific keys.
    """
    sqlite3_database = sqlite3.connect(global_conf['sqlite3_database'],
                                       check_same_thread = False)

    # Create any objects that should exist for the lifetime of the application
    # here. Don't forget to actually include them in the environ below!
    print "Settings:"
    for key, value in global_conf.items():
        print " " * 4, key, value

    pickles_cache_path = None
    if global_conf['use_pickles_cache'] == 'True':
        pickles_cache_path = os.path.abspath(global_conf['pickles_cache_path'])
    dbs = {}
    if global_conf['use_sql_database']:
        connections = ConfigObj(os.path.abspath(global_conf['mysql_connections']))
        databases = ConfigObj(os.path.abspath(global_conf['mysql_databases']))
        projects = ConfigObj(os.path.abspath(global_conf['projects']))
        for id, info in projects.items():
            for project in info['projects']:
                dbs[project] = {'RNAseqPipelineWarehouse':sqlite3_database}
                for db_id, db_name in projects[id]['dbs'].items():
                    databases_for_dbname = None
                    try:
                        databases_for_dbname = databases[db_name]
                    except:
                        ini = os.path.abspath(global_conf['mysql_databases'])
                        #raise KeyError("project %s not found in %s" % (db_name, ini))
                    if not databases_for_dbname is None:
                        database_connection = databases_for_dbname['connection']
                        connection = connections[database_connection]
                        database = databases[db_name]['db']
                        db = DB(database, connection)
                        dbs[project][db_id] = db
                    
        parameters = ConfigObj(os.path.abspath(global_conf['parameters']))
        project_parameters = ConfigObj(os.path.abspath(global_conf['project_parameters']))
        parameter_labels = {}
        parameter_columns = {}
        parameter_mapping = {}
        for parameter, info in parameters.items():
            parameter_labels[parameter] = (info['title'], info['type'])
            parameter_columns[parameter] = info['column']
        for project, info in project_parameters.items():
            parameter_mapping[project] = info['parameters']

    def application(environ, start_response):
        # Making the following additional keys available to the environ.
        # They become available to the request like this:
        # request.environ['myvar']
        environ['pickles_cache_path'] = pickles_cache_path
        environ['dbs'] = dbs
        environ['parameter_columns'] = parameter_columns
        environ['parameter_labels'] = parameter_labels
        environ['parameter_mapping'] = parameter_mapping
        return app(environ, start_response)

    return application
