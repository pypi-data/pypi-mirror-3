from datetime import datetime
from tg import expose, flash, require, request, redirect, tmpl_context, TGController, config, validate
from tg.controllers import WSGIAppController
import libacr
from libacr.controllers.admin.base import _create_node
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose
from libacr.controllers.admin.base import _create_node, BaseAdminController
from libacr.model.core import DBSession
from libacr.model.content import Tag, Page, Slice, Content, ContentData
from libacr.lib import url, current_user_id, language, icons, user_can_modify, get_page_from_urllist
from repoze.what import predicates
from tw.api import WidgetsList
import tw.forms as twf
from paste.urlparser import StaticURLParser
import os, shutil, zipfile, tempfile
from libacr.views.manager import ViewsManager

class ThemeStaticsController(TGController):
    @expose()
    def lookup(self, theme, *args):
        site_dir = os.path.join(config.get('public_dir'), 'themes', theme)
        return WSGIAppController(StaticURLParser(site_dir)), args

class ThemeController(BaseAdminController):
    statics = ThemeStaticsController()

    @plugin_expose('edit_css')
    @require(predicates.in_group("acr"))
    def edit_css(self):
        class EditCssForm(WidgetsList):
            css = twf.TextArea(suppress_label=True)
        css_form = twf.TableForm(fields=EditCssForm(), submit_text="Save")

        active_theme = Themable.get_theme_data()
        current_css = {}
        current_css['css'] = open(os.path.join(config.get('public_dir'), 'themes',
                                  active_theme.get_property('theme', 'active'), 'main.css')).read().decode('utf-8')
        return dict(form=css_form, current_css=current_css)

    @expose()
    @require(predicates.in_group("acr"))
    def save_css(self, css):
        active_theme = Themable.get_theme_data()
        css_file = open(os.path.join(config.get('public_dir'), 'themes',
                        active_theme.get_property('theme', 'active'), 'main.css'), 'w').write(css.encode('utf-8'))

        flash('CSS Successfully updated')
        return redirect(url('/plugins/theme/edit_css'))

    @plugin_expose('manage_themes')
    @require(predicates.in_group("acr"))
    def manage_themes(self):
        themes_path = os.path.join(config.get('public_dir'), 'themes')
        available_themes = os.listdir(themes_path)
        active_theme = Themable.get_theme_data().get_property('theme', 'active')
        return dict(available_themes=available_themes, active_theme=active_theme)

    @expose()
    @require(predicates.in_group("acr"))
    def delete(self, theme):
        active_theme = Themable.get_theme_data().get_property('theme', 'active')
        if theme == active_theme:
            flash('Cannot delete active theme')
            return redirect(url('/plugins/theme/manage_themes'))
        else:
            theme_path = os.path.join(config.get('public_dir'), 'themes', theme)
            shutil.rmtree(theme_path)
            flash('Theme deleted')
            return redirect(url('/plugins/theme/manage_themes'))

    @expose()
    @require(predicates.in_group("acr"))
    def clone(self, theme):
        old_theme_path = os.path.join(config.get('public_dir'), 'themes', theme)
        new_theme = theme + str(len(os.listdir(os.path.join(config.get('public_dir'), 'themes'))))
        new_theme_path = os.path.join(config.get('public_dir'), 'themes', new_theme)

        if os.path.exists(new_theme_path):
            flash('A theme with that name already exists')
            return redirect(url('/plugins/theme/manage_themes'))

        if not os.path.exists(old_theme_path):
            flash('Origin theme not found')
            return redirect(url('/plugins/theme/manage_themes'))

        shutil.copytree(old_theme_path, new_theme_path)
        flash('Theme copied')
        return redirect(url('/plugins/theme/manage_themes'))

    @expose()
    @require(predicates.in_group("acr"))
    def switch(self, theme, setup=False, clear=False):
        theme_path = os.path.join(config.get('public_dir'), 'themes', theme)
        if not os.path.exists(theme_path):
            flash('Theme does not exists')
            return redirect(url('/plugins/theme/manage_themes'))

        if setup and os.path.exists(os.path.join(theme_path, 'setup.acr')):
            if clear:
                for slice in DBSession.query(Slice):
                    DBSession.delete(slice)
            execute_acri(open(os.path.join(theme_path, 'setup.acr')).read())

        Themable.get_theme_data().set_property('theme', 'active', theme)
        flash('Theme enabled')
        return redirect(url('/plugins/theme/manage_themes'))

    @plugin_expose('upload_theme')
    @require(predicates.in_group("acr"))
    def upload_theme(self, **kw):
        class ThemeUploadForm(WidgetsList):
            themezip = twf.FileField(suppress_label=True)
        upload_form = twf.TableForm(fields=ThemeUploadForm(), submit_text="Upload")
        return dict(form=upload_form)

    @expose()
    @require(predicates.in_group("acr"))
    @validate(validators=dict(themezip=twf.validators.FieldStorageUploadConverter(not_empty=True)), error_handler=upload_theme)
    def do_upload(self, themezip):
        tfile = tempfile.NamedTemporaryFile('rw+b')
        tfile.write(themezip.file.read())
        tfile.flush()

        if not zipfile.is_zipfile(tfile.name):
            flash('Not a valid zip file')
            return redirect(url('/admin'))

        themezip = zipfile.ZipFile(tfile.name, 'r')
        theme_entries = themezip.namelist()
        if theme_entries[0].startswith('..') or theme_entries[0].startswith('/'):
            flash('Theme zip file cannot contain relative paths')
            return redirect(url('/admin'))

        for entry in theme_entries:
            if not entry.startswith(theme_entries[0]):
                flash('Theme zip file must contain all the theme files inside a root directory with theme name')
                return redirect(url('/admin'))

        themes_dir = os.path.join(config.get('public_dir'), 'themes')
        if os.path.exists(os.path.join(themes_dir, theme_entries[0])):
            flash('Theme already exists')
            return redirect(url('/plugins/theme/manage_themes'))

        for entry in theme_entries:
            data = themezip.read(entry)
            path = os.path.join(themes_dir, entry)
            if not data:
                os.mkdir(path)
            else:
                f = open(path, 'w')
                f.write(data)
                f.close()
        flash('Theme extracted')
        return redirect(url('/plugins/theme/manage_themes'))

def execute_acri(script):
    def create_tag(tname):
        if not DBSession.query(Tag).filter_by(name=tname).first():
            t = Tag(name=tname)
            DBSession.add(t)

    def create_slice(parent, name, view='html', data={'data':''}):
        page = get_page_from_urllist(parent.split('/'))

        if not DBSession.query(Slice).filter_by(name=name).first():
            slice_data = {}
            slice_data['name'] = name
            slice_data['page'] = page.uid
            slice_data['zone'] = 'main'
            slice_data['order'] = 0
            slice_data['tags'] = []
            slice_data['view'] = view
            slice_data['data'] = ViewsManager.encode(view, data)
            _create_node(**slice_data)

    def add_slice_tag(slice_name, tag_name):
        sli = DBSession.query(Slice).filter_by(name=slice_name).one()
        t = DBSession.query(Tag).filter_by(name=tag_name).one()
        sli.tags.append(t)

    def attach_javascript(pname, filename):
        page = ''
        if not pname:
            page = DBSession.query(Page).filter_by(uri='default').one()
        else:
            page = DBSession.query(Page).filter_by(name=pname).one()

        name = strip(filename, punctuation) # check
        js = ''
        if os.path.exists(os.path.join(theme_path, filename)):
            js = open(os.path.join(theme_path, filename)).read()
        #open file and read it

        if js and not DBSession.query(Slice).filter_by(name=name).first():
            slice_data = {}
            slice_data['name'] = name
            slice_data['page'] = page.uid
            slice_data['zone'] = 'main'
            slice_data['order'] = 0
            slice_data['tags'] = []
            slice_data['view'] = 'script'
            slice_data['data'] = js #file content
            _create_node(**slice_data)

    def create_page(uri, parent=None):
        parent_page = None
        if parent:
            parent_page = get_page_from_urllist(parent.split('/'))

        page = DBSession.query(Page).filter_by(uri=uri).first()
        if not page and ((parent and parent_page) or (not parent)):
            page = Page(uri=uri, title='Unknown', parent=parent_page)
            DBSession.add(page)

    def set_page_title(uri, *args):
        page = get_page_from_urllist(uri.split('/'))
        if page:
            page.title = ' '.join(args)

    def set_slice_zone(slice_name, zone):
        sli = DBSession.query(Slice).filter_by(name=slice_name).one()
        sli.zone = zone

    commands = {'create_tag':create_tag,
                'create_slice':create_slice,
                'add_slice_tag':add_slice_tag,
                'create_page':create_page,
                'set_page_title':set_page_title,
                'set_slice_zone':set_slice_zone,
                'attach_javascript':attach_javascript}

    for line in script.split('\n'):
        params = line.split()

        if params:
            cmd = params[0]
            params = params[1:]
            commands[cmd](*params)

class Themable(AcrPlugin):
    uri = 'theme'

    @staticmethod
    def get_theme_data():
        config = DBSession.query(Content).filter_by(name='_acr_config_theme').first()
        if not config:
            config = Content(name='_acr_config_theme')
            cdata = ContentData(content=config, revision=0)
            cdata.set_property('theme', 'active', 'dragonfly')
            DBSession.add(config)
            DBSession.add(cdata)
        return config.get_data_instance_for_lang()

    def __init__(self):
        self.admin_entries = [AdminEntry(self, 'Edit Css', 'edit_css', icon='edit_css.png', section="Themes"),
                              AdminEntry(self, 'Manage Themes', 'manage_themes', icon='switch_theme.png', section="Themes"),
                              AdminEntry(self, 'Upload Theme', 'upload_theme', icon='upload_theme.png', section="Themes")]
        self.controller = ThemeController()

    def theme_url(self, what):
        config = Themable.get_theme_data()
        what = 'statics/%s/%s' % (config.get_property('theme', 'active'), what)
        return self.plugin_url(what)
