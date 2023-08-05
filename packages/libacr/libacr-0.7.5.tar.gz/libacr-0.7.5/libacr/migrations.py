try:
    from tg import cache
except:
    from pylons import cache

from tg import request
import transaction
from libacr.plugins.manager import PluginsManager

import logging
log = logging.getLogger('libacr')

class MigrationsManager(object):
    def __init__(self):
        self.cache = cache.get_cache('libacr_versions')
        self.last_versions = {}

        self.last_versions['core'] = 1
        for plugin in PluginsManager.plugins.itervalues():
            try:
                self.last_versions[plugin.uri] = plugin.last_version
            except:
                continue

    def __call__(self):
        return self

    def uncached_model_version(self, module):
        from libacr.model.core import DBSession
        from libacr.model.versioning import Version

        if not DBSession.bind.has_table(Version.__tablename__):
            DBSession.bind.create(Version.__table__)

        version = DBSession.query(Version).filter_by(module=module).first()
        if not version:
            return 0
        return version.number

    def module_cache_key(self, module):
        return '%s_%s' % (request.environ['HTTP_HOST'], module)
        
    def model_version(self, module):
        cachedvalue = self.cache.get_value(key=self.module_cache_key(module), expiretime=3600,
                                           createfunc=lambda: self.uncached_model_version(module))
        return cachedvalue

    def upgrade_core(self, DBSession, current_version):
        if current_version < 1:
            from libacr.model.assets import Asset
            from libacr.model.attributes import Attribute

            if not DBSession.bind.has_table(Asset.__tablename__):
                DBSession.bind.create(Asset.__table__)
            if not DBSession.bind.has_table(Attribute.__tablename__):
                DBSession.bind.create(Attribute.__table__)

    def upgrade(self, module):
        from libacr.model.core import DBSession
        from libacr.model.versioning import Version

        self.cache.remove_value(self.module_cache_key(module))
        current_version = self.model_version(module)

        log.info('Upgrading %s: %s -> %s' % (module, current_version, current_version+1))
        transaction.begin()
        if module == 'core':
            self.upgrade_core(DBSession, current_version)
        else:
            plugin = PluginsManager.plugins[module]
            plugin.upgrade(DBSession, current_version)

        cur_ver_obj = DBSession.query(Version).filter_by(module=module).first()
        if cur_ver_obj:
            cur_ver_obj.number = current_version+1
        else:
            DBSession.add(Version(module=module, number=current_version+1))
            DBSession.flush()
        transaction.commit()

        self.cache.remove_value(self.module_cache_key(module))

    def check_and_evolve(self):
        for module, last_version in self.last_versions.iteritems():
            while self.model_version(module) < last_version:
                self.upgrade(module)

MigrationsManager = MigrationsManager()
