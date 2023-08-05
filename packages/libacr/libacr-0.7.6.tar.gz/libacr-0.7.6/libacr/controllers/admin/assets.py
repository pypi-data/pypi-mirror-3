from tg import expose, flash, require, url, request, redirect, tmpl_context, validate, config
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from pylons.controllers.util import abort
from repoze.what import predicates

from libacr import acr_zones, forms
from libacr.lib import url, current_user_id, language, icons, user_can_modify
from libacr.model.core import DBSession
from libacr.model.assets import Asset

from tw.api import WidgetsList
import tw.forms as widgets
from tw.tinymce import TinyMCE, MarkupConverter
from formencode import validators
from libacr.views.manager import ViewsManager
from libacr.forms import order_values

import mimetypes, os
from datetime import datetime
from base import BaseAdminController, _create_node

class UploadAssetForm(widgets.TableForm):
    class fields(WidgetsList):
        from_box = widgets.HiddenField(default=0, validator=validators.Int(not_empty=True))
        uid = widgets.HiddenField()
        asset_file = widgets.FileField(label_text="File:",
                                       validator=validators.FieldStorageUploadConverter(not_empty=True))
asset_upload_form = UploadAssetForm()

class AssetsController(BaseAdminController):
    @expose('libacr.templates.admin.assets_index')
    @require(predicates.in_group("acr"))
    def index(self, *args, **kw):
        assets = DBSession.query(Asset).all()
        return dict(upload_form=asset_upload_form, values=kw, assets=assets)

    @expose()
    @require(predicates.in_group("acr"))
    @validate(asset_upload_form, error_handler=index)
    def upload(self, from_box, uid, asset_file):
        if not uid:
            asset = Asset(name=asset_file.filename, content_type=self.guess_mime(asset_file.filename))
            DBSession.add(asset)
            DBSession.flush()
        else:
            asset = DBSession.query(Asset).get(uid)
        self.store_file(asset, asset_file.file)
        flash('Asset Stored')

        if not from_box:
            return redirect(url('/admin/assets'))
        else:
            return redirect(url('/admin/assets/box'))

    @expose()
    @require(predicates.in_group("acr"))
    def delete(self, uid):
        asset = DBSession.query(Asset).filter_by(uid=uid).first()
        if asset:
            DBSession.delete(asset)
        flash('Asset Removed')
        return redirect(url('/admin/assets'))

    @expose('libacr.templates.admin.assets_box')
    @require(predicates.in_group("acr"))
    def box(self, uid=None):
        assets = DBSession.query(Asset).all()
        try:
            uid = int(uid)
        except:
            pass
        return dict(upload_form=asset_upload_form, selected_asset_id=uid, assets=assets)

    def guess_mime(self, name):
        mimetypes.init()
        mime = mimetypes.guess_type(name, False)[0]
        if not mime:
            mime = 'application/octet-stream'
        return mime

    def store_file(self, asset, data):
        public_dir = config.get('public_dir')
        assets_path = os.path.join(public_dir, 'assets')

        if not os.path.exists(assets_path):
            os.makedirs(assets_path)

        asset.write(data)
