# -*- coding: utf-8 -*-
"""Setup the acr application"""

import logging

import transaction
from tg import config

from acr.config.environment import load_environment
from libacr.model.user_permission import AcrUserPermission
from libacr.plugins.manager import PluginsManager

__all__ = ['setup_app']

log = logging.getLogger(__name__)

def create_content(name, data):
    from acr import model
    
    cnt = model.Content(name=name)
    model.DBSession.add(cnt)
    
    cnt_data = model.ContentData(content=cnt, revision=0, value=data)
    model.DBSession.add(cnt_data)
    
    return cnt

def setup_app(command, conf, vars):
    """Place any commands to setup acr here"""
    load_environment(conf.global_conf, conf.local_conf)
    # Load the models
    from acr import model
    model.multisite_engine.force_thread_env({'SCRIPT_FILENAME':'setup-app'})

    print "Creating tables"
    model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)
    print "Creating Data"

    manager = model.User()
    manager.user_name = u'manager'
    manager.display_name = u'Example manager'
    manager.email_address = u'manager@somedomain.com'
    manager.password = u'managepass'
    model.DBSession.add(manager)
    
    editor = model.User()
    editor.user_name = u'editor'
    editor.display_name = u'Example editor'
    editor.email_address = u'editor@somedomain.com'
    editor.password = u'editpass'
    model.DBSession.add(editor)

    group = model.Group()
    group.group_name = u'managers'
    group.display_name = u'Managers Group'
    group.users.append(manager)
    model.DBSession.add(group)
    
    group = model.Group()
    group.group_name = u'editors'
    group.display_name = u'Editors Group'
    group.users.append(manager)
    group.users.append(editor)
    model.DBSession.add(group)
    
    group = model.Group()
    group.group_name = u'acr'
    group.display_name = u'Acr Group'
    group.users.append(manager)
    model.DBSession.add(group)
  
    user_permission = AcrUserPermission()
    user_permission.user=manager
    user_permission.page="all"
    user_permission.can_edit=1
    user_permission.can_create_children=1
    model.DBSession.add(user_permission)

    t = model.Tag(name='story')
    model.DBSession.add(t)
  
    default_page = model.Page(uri='default', title='Default Page for global layout')
    model.DBSession.add(default_page)
  
    p = model.Page(uri='index', title='Index')
    model.DBSession.add(p)

    c = create_content(name='acr_presentation', data=u"""<h1>Welcome to <em>ACR</em></h1>
<img class="left" width="120" height="120" src="/acr/plugins/theme/statics/dragonfly/images/img07.jpg"/>
<p><strong>ACR</strong> is an opensource CMS based on <a href="http://www.turbogears.org">TurboGears2</a> developed by <a href="http://www.axant.it">AXANT</a>
feel free to use it for any project and for more informations refer to <a href="http://labs.axant.it/acr">labs.axant.it</a>. <em>Enjoy ;)</em></p>
<div class="clearfix"></div>
""")
    ci = model.Slice(view='html', content=c, page=p, zone='main', name="acr_presentation")
    model.DBSession.add(ci)

    c = create_content(name='acr_index_part2', data=u"""<h1>Welcome to your page!</h1>
<p>You are now ready to use ACR, this is your index page and in the menu there is already a link to the ACR page itself,
<a href="/login">login</a> and start creating new nodes for your site</p>
""")
    ci = model.Slice(view='html', content=c, page=p, zone='main', name="acr_index_part2")
    model.DBSession.add(ci)

    c = create_content(name='acr_home', data="http://labs.axant.it/acr")
    p = model.Page(uri='acr', title='ACR Project')
    model.DBSession.add(p)
    ci = model.Slice(view='link', content=c, page=p, zone='main', name="acr_home")
    model.DBSession.add(ci)    
      
    c = create_content(name="default_menu", data="[menu]\ndepth=1\nalign=horizontal\nroot=root")
    ci = model.Slice(view='menu', content=c, page=default_page, zone='header', name="menu")
    model.DBSession.add(ci)
    
    c = create_content(name="default_header", data=u"""
<h1><a href="#">ACR</a></h1>
<h2><a href="http://labs.axant.it/acr">Advanced Content Repository</a></h2>
""")
    ci = model.Slice(view='html', content=c, page=default_page, zone='header', name="header")
    model.DBSession.add(ci)
        
    c = create_content(name="default_footer", data=u"""<p>Powered by ACR</p>
<p>Copyright © 2009 AXANT. All Rights Reserved</p>""")
    ci = model.Slice(view='html', content=c, page=default_page, zone='footer', name="footer")
    model.DBSession.add(ci)
    
    c = create_content(name="default_sidebar", data=u"""<div class="orangebox">
<h2>Links</h2>
<ul>
    <li><a href="http://labs.axant.it/acr">ACR</a></li>
    <li><a href="http://www.axant.it">AXANT</a></li>
    <li><a href="http://www.turbogears.org">TurboGears</a></li>
</ul>
</div>
""")
    ci = model.Slice(view='html', content=c, page=default_page, zone='rightbar', name="sidebar")
    model.DBSession.add(ci)

    model.DBSession.flush()
    transaction.commit()
    print "Successfully setup"
