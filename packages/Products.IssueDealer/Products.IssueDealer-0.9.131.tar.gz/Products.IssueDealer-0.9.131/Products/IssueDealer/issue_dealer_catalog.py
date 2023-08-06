import AccessControl
import utilities
from Products.laf import url_utilities
import permissions
import time
from Products import ZCatalog
from Globals import InitializeClass

class issue_dealer_catalog:

    security = AccessControl.ClassSecurityInfo()

    indexes = (
      ('title', 'FieldIndex', None),
      ('id', 'FieldIndex', None),
      ('meta_type', 'FieldIndex', None),
      ('modified', 'FieldIndex', None),
      ('get_type', 'FieldIndex', None),
      ('state', 'FieldIndex', None),
      ('get_parent_url', 'FieldIndex', None),
      ('contents', 'ZCTextIndex', utilities.simple(doc_attr='',
                                             index_type='Cosine Measure',
                                             lexicon_id='lexicon'),),
      ('get_all_text', 'ZCTextIndex', utilities.simple(doc_attr='',
                                             index_type='Cosine Measure',
                                             lexicon_id='lexicon'),
       ),
      ('get_title', 'FieldIndex', None),
      ('creator', 'FieldIndex', None),
      ('deleted', 'FieldIndex', None),
      ('importance', 'FieldIndex', None),
      ('get_state_importance_title_sort', 'FieldIndex', None),
      ('get_relative_state', 'FieldIndex', None),
      ('get_relative_importance', 'FieldIndex', None),
      ('users', 'KeywordIndex', None),
      ('path','PathIndex', None),
      ('get_level', 'FieldIndex', None),
      ('created', 'FieldIndex', None),
      ('relation', 'FieldIndex', None),
      ('get_order', 'FieldIndex', None),
      ('publisher', 'FieldIndex', None),
      ('get_local_image_ids', 'KeywordIndex', None),
      ('get_published_ids', 'KeywordIndex', None),
      ('get_parent_ids', 'KeywordIndex', None),
      ('get_parent_id', 'FieldIndex', None),
      ('due', 'FieldIndex', None),
      ('get_state_importance_due_sort', 'FieldIndex', None),
      ('get_published_ids', 'KeywordIndex', None),
      ('published_in', 'KeywordIndex', None),
      ('format', 'FieldIndex', None),
      ('get_referenced_ids', 'KeywordIndex', None),
      ('tags', 'KeywordIndex', None),
      ('owners', 'KeywordIndex', None),
      ('is_action_issue', 'FieldIndex', None),
    )

    columns = ('contents', 'absolute_url', 'state',
               'get_type', 'get_title', 'get_number_of_issues',
               'creator', 'owner', 'deleted', 'importance',
               'get_short_url', 'get_level', 'relation',
               'get_number_of_issues', 'render_contents_as_text',
               'format', 'meta_type', 'created', 'get_parent_titles',
               'get_parent_ids', 'get_parent_meta_types', 'id', 'title',
               'modified', 'due', 'render_due', 'filename', 'format',
               'last_modified_by', 'tags', 'render_tags'
    )

    security.declarePrivate('add_indexes')
    def add_indexes(self):
        """Adds the indexes we're using."""
        catalog = self.get_catalog()
        if not hasattr(catalog.aq_base, 'lexicon'):
            self.add_lexicon()
        for index in self.indexes:
            # If the type of index is updated, delete the old one
            # so a new can be created
            try:
                if catalog._catalog.indexes[index[0]].meta_type != index[1]:
                    catalog.manage_delIndex(index[0])
            except KeyError:
                pass
            if not catalog._catalog.indexes.has_key(index[0]):
                catalog.manage_addIndex(index[0], index[1], index[2])

    security.declarePrivate('add_lexicon')
    def add_lexicon(self):
        """Adds a lexicon."""
        from Products.ZCTextIndex import ZCTextIndex, Lexicon
        lexicon = ZCTextIndex.PLexicon('lexicon', '',
          Lexicon.CaseNormalizer(),
          Lexicon.StopWordRemover(),
          Lexicon.Splitter())
        self.get_catalog()._setObject('lexicon', lexicon)

    security.declarePrivate('add_columns')
    def add_columns(self):
        """Adds the columns we're using."""
        catalog = self.get_catalog()
        for column in self.columns:
            if not catalog._catalog.schema.has_key(column):
                catalog.manage_addColumn(column)

    security.declareProtected(permissions.manage_issue_dealer, 'update_catalog')
    def update_catalog(self, start=0, sleep=0, batch_size=1000, update=1, delete=0):
        """Updates the catalog, reindexing all objects.

        If update is specified, it will be run for each object."""
        self.version = self.filesystem_version
        if not hasattr(self.aq_base, 'missing'):
            issue = self.manage_add_issue('missing', title='Object missing or not found',
                                          contents='The object pointed to is missing - '\
                                          'this issue is used to help with broken pointers',
                                          state='closed')
            issue.delete()
        if not hasattr(self.aq_base, 'laf'):
            from Products.laf.laf import laf
            laf_instance = laf('laf')
            self._setObject('laf', laf_instance)
        if not self.public_url.strip(): self.public_url = self.absolute_url()
        if delete:
            self.manage_delObjects(ids=['Catalog'])
            self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/update_catalog?' + \
              url_utilities.create_query_string(None, '', start=0, update=update))
            return
        try:
            catalog = self.get_catalog()._catalog
        except AttributeError:
            ZCatalog.ZCatalog.manage_addZCatalog(self, 'Catalog', 'Issue catalog')
            self.add_indexes()
            self.add_columns()
            catalog = self.get_catalog()._catalog
            catalog.ZopeFindAndApply(self, apply_func=catalog.catalog_object, search_sub=1,
		apply_path = '/'.join(self.getPhysicalPath()))
            self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/update_catalog?' + \
              url_utilities.create_query_string(None, '', start=0, update=update))
            return
        start = int(start)
        batch_size = int(batch_size)
        stop = 0
        if start == 0:
            if not hasattr(self, 'order'):
                # We need to include deleted objects and
                # reset the default sort order
                self.get_user_preferences().show_deleted = 1
                self.get_user_preferences().sort_order = ''
            self.update()
            self._uids = list(catalog.uids.keys()[:])
            self.add_indexes()
            self.add_columns()
        batch = self._uids[start:start+batch_size]
        if not batch:
            stop = 1
            del self._uids
        for uid in batch:
            try:
                object = self.unrestrictedTraverse(uid)
            except KeyError:
                # It doesn't exist, remove it from the catalog.
                print 'got KeyError in update_catalog', uid
                catalog.uncatalog_object(uid)
		continue
            if int(update):
                try:
                    object.update()
                except AttributeError:
                    pass
            if getattr(object, 'version', 0) != self.filesystem_version:
                object.version = self.filesystem_version
            if hasattr(object.aq_base, 'index_object'):
                object.index_object()
            else:
                catalog.uncatalog_object(uid)
        sleep = int(sleep)
        time.sleep(sleep)
        if stop:
            self.REQUEST.RESPONSE.redirect(self.absolute_url())
        else:
            self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/update_catalog?' + \
              url_utilities.create_query_string(None, '', start=start+batch_size, update=update,
                batch_size=batch_size, sleep=sleep))

InitializeClass(issue_dealer_catalog)
