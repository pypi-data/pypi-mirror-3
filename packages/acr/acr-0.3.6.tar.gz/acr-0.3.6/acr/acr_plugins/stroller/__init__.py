from tg import expose, flash, require, request, redirect, tmpl_context, TGController, config, validate
from tg.controllers import WSGIAppController
import libacr

from libacr.controllers.admin.base import BaseAdminController
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose
from pylons.controllers.util import abort
import acr.lib.helpers
import acr.model
from repoze.what import predicates
from tw.api import WidgetsList
import tw.forms as twf

from sqlalchemy.exc import OperationalError

class StrollerPluginController(TGController):
    @expose('stroller.templates.index')
    def index(self, *args, **kw):
        self.check_for_enabled_stroller()
        from stroller.controllers.ecommerce import StrollerController
        return StrollerController().index(*args, **kw)

    @expose()
    def lookup(self, *args, **kw):
        self.check_for_enabled_stroller()
        from stroller.controllers.ecommerce import StrollerController
        return StrollerController(), list(args)

    def check_for_enabled_stroller(self):
        if not config.get('stroller_enabled', False):
            return abort(404, "eCommerce support not available")

class StrollerPlugin(AcrPlugin):
    uri = 'shop'
    last_version = 3

    @property
    def controller(self):
        config['stroller_root'] = self.plugin_url()
        return StrollerPluginController()

    def upgrade(self, DBSession, current_version):
        if current_version < 1:
            from stroller.model.commerce import Product, Category
            from stroller.model import init_stroller_model

            init_stroller_model(DBSession, acr.model.DeclarativeBase,
                                acr.model.User, acr.model.Group)

            if not Product.__table__.exists(bind=DBSession.bind):
                acr.model.metadata.create_all(bind=DBSession.bind)

            main_category = DBSession.query(Category).filter_by(name='Shop').first()
            if not main_category:
                from stroller.model import setup_stroller_database
                setup_stroller_database(DBSession, acr.model.DeclarativeBase,
                                        acr.model.User, acr.model.Group)

        elif current_version < 2:
            from stroller.model.commerce import ProductPhoto
            if not DBSession.bind.has_table(ProductPhoto.__tablename__):
                DBSession.bind.create(ProductPhoto.__table__)
        elif current_version < 3:
            try:
                DBSession.bind.execute('ALTER TABLE stroller_order ADD confirmed SMALLINT;')
            except OperationalError:
                pass

    def init_helpers(self):
        import stroller.helpers
        acr.lib.helpers.stroller_url = stroller.helpers.stroller_url
        acr.lib.helpers.icons.update(stroller.helpers.icons)
        acr.lib.helpers.category_icon = stroller.helpers.category_icon
 
    def init_model(self):
        from stroller.model import init_stroller_model
        Product, ProductInfo, Category, Order, OrderItem = init_stroller_model(acr.model.DBSession, acr.model.DeclarativeBase,
                                                                               acr.model.User, acr.model.Group)

    def __init__(self):
        try:
            import stroller
        except:
            config['stroller_enabled'] = False

        self.init_model()
        self.init_helpers()
