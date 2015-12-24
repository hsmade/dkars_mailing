# -*- coding: utf-8 -*-
from datetime import datetime

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

db.define_table('addresses',
                Field('f_call', 'string'),
                Field('f_naam', 'string'),
                Field('f_email', 'string', requires = IS_EMAIL(error_message='invalid email!')),
                Field('f_taal', 'string', requires=IS_IN_SET(('dutch', 'english'))),
                Field('f_type', 'string')
                )

db.define_table('mailings',
                Field('f_year', 'integer', default=datetime.now().year, requires=IS_NOT_EMPTY(), label='Jaar'),
                Field('f_month', 'integer', default=datetime.now().month, requires=IS_NOT_EMPTY(), label='Maand', comment='2 cijfers'),
                Field('f_issue_number', 'integer', requires=IS_NOT_EMPTY(), label='Uitgave nummer'),
                Field('f_text_dutch', 'text', requires=IS_NOT_EMPTY(), label='Nederlandse tekst', comment='Gebruikt $link voor waar de link moet komen'),
                Field('f_text_english', 'text', requires=IS_NOT_EMPTY(), label='Engelse tekst', comment='Gebruikt $link voor waar de link moet komen'),
                Field('f_test_mode', 'boolean', label='Stuur alleen test mail'),
                Field('f_test_address', 'string', label='Mail adres voor test mail')
               )


db.define_table('custom_mailings',
                Field('f_subject_dutch', 'text', requires=IS_NOT_EMPTY(), label='Nederlands subject'),
                Field('f_subject_english', 'text', requires=IS_NOT_EMPTY(), label='Engels subject'),
                Field('f_text_dutch', 'text', requires=IS_NOT_EMPTY(), label='Nederlandse tekst'),
                Field('f_text_english', 'text', requires=IS_NOT_EMPTY(), label='Engelse tekst'),
                Field('f_test_mode', 'boolean', label='Stuur alleen test mail'),
                Field('f_test_address', 'string', label='Mail adres voor test mail')
               )

db.define_table('logs',
                Field('f_issue_number', 'string'),
                Field('f_log', 'text'),
                )
