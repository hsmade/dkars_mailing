# -*- coding: utf-8 -*-
import os
import logging
logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger('mailing')

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@auth.requires_login()
@auth.requires_membership('admin')
def addresses():
    form = SQLFORM.smartgrid(db.addresses)
    return locals()

def validate_magazine_ready(form):
    year_month = '{}{}'.format(form.vars.f_year, form.vars.f_month)
    logger.error('year_month: {}'.format(year_month))
    if not os.path.isfile('/var/web/dkars.nl/htdocs/DKARS Magazine {}.pdf'.format(year_month)):
        form.errors.f_year = 'Magazine doesn\'t exist at download site for this year and month'
    if not '$link' in form.vars.f_text_dutch:
        form.errors.f_text_dutch = 'Test must contain $link where the link should be'
    if not '$link' in form.vars.f_text_english:
        form.errors.f_text_english = 'Test must contain $link where the link should be'
    
@auth.requires_login()
@auth.requires_membership('admin')
def send_mailing():
   logger.debug('send_mailing called')
   form = SQLFORM(db.mailings)
   
   if form.process(keepvalues=True, onvalidation=validate_magazine_ready).accepted:
       # start sending
       logger.debug('Scheduling')
       result = scheduler.queue_task(send_mailing, pvars={'mailing': form.vars.id})
       logger.debug('Scheduling result: {}'.format(result))
       response.flash = 'Mailing wordt verstuurd'
   elif form.errors:
       response.flash = 'form has errors'
   else:
       response.flash = 'please fill out the form'
   return dict(form=form)


@auth.requires_login()
@auth.requires_membership('admin')
def logs():
    form = SQLFORM.grid(db.logs, editable=False, deletable=False)
    return locals()
