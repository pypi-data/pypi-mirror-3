from tg import expose, flash, require, request, redirect, tmpl_context, TGController, config, validate
from tg.controllers import WSGIAppController
import libacr
from libacr.lib import url as acr_url

from libacr.controllers.admin.base import BaseAdminController
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose
from repoze.what import predicates
from tw.api import WidgetsList
import tw.forms as twf

class OldPasswordValidator(twf.validators.FancyValidator):
    def validate_python(self, value, state):
        if not request.identity["user"].validate_password(value):
            raise twf.validators.Invalid("wrong pass", value, state)

class ChPassForm(twf.TableForm):
    class fields(WidgetsList):
        oldpass = twf.PasswordField(label_text="Current Password",validator = OldPasswordValidator(not_empty=True))
        newpass1 = twf.PasswordField(label_text="New Password", validator = twf.validators.String(not_empty=True))
        newpass2 = twf.PasswordField(label_text="Confirm New Password", validator = twf.validators.String(not_empty=True))

    class NewPassValidator(twf.validators.Schema):
        chained_validators = [twf.validators.FieldsMatch('newpass1','newpass2')]
    validator=NewPassValidator()

chpassform = ChPassForm(submit_text="Change")

class ChpasswdController(BaseAdminController):

    @plugin_expose('index')
    @require(predicates.not_anonymous())
    def index(self, **kw):
        return dict(form=chpassform,values=kw)

    @expose()
    @require(predicates.not_anonymous())
    @validate(form=chpassform,error_handler=index)
    def change(self,**kw):
        request.identity["user"].password = kw['newpass1']
        flash("password changed succesfully")
        return redirect(acr_url('/'))

class ChangePass(AcrPlugin):
    uri = 'chpasswd'

    def __init__(self):
        self.admin_entries = [AdminEntry(self, 'Change My Password', 'index', icon='Gnome-Dialog-Password-64.png', section="General Settings")]
        self.controller = ChpasswdController()
