from ftw.referencewidget.browser.utils import get_selectable_types
from ftw.referencewidget.browser.utils import get_traversal_types
from ftw.referencewidget.browser.utils import get_path_from_widget_start
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from ftw.referencewidget.browser.utils import extend_with_batching
import json


class ReferenceJsonEndpoint(BrowserView):

    def find_start_path(self):

        widget = self.context
        effective_path = ""
        if widget.request.get('start'):
            effective_path = widget.request.get('start')
        elif not widget.start:
            effective_path = '/'.join(widget.form.context.getPhysicalPath())
        else:
            effective_path = get_path_from_widget_start(widget)
        return effective_path

    def __call__(self):
        widget = self.context
        effective_path = self.find_start_path()
        current_depth = len(effective_path.split('/'))
        results = self.search_catalog(widget, effective_path)
        results, batch_html = extend_with_batching(widget, results)
        traversel_type = get_traversal_types(widget)
        selectable_types = get_selectable_types(widget)
        result = {'batching': batch_html, 'items': []}
        for item in results:
            depth = len(item.getPath().split('/')) - current_depth
            if depth == 0:
                continue
            contenttype = item.portal_type.replace('.', '-').lower()
            traversable = item.is_folderish and  \
                (item.portal_type in traversel_type)
            obj_dict = {'path': item.getPath(),
                        'id': item.id,
                        'title': item.Title or item.id,
                        'folderish': item.is_folderish,
                        'traversable': traversable,
                        'selectable': item.portal_type in selectable_types,
                        'content-type': 'contenttype-' + contenttype}

            result['items'].append(obj_dict)

        self.request.RESPONSE.setHeader("Content-type", "application/json")
        return json.dumps(result)

    def search_catalog(self, widget, effective_path):
        traversel_type = get_traversal_types(widget)
        query = {'portal_type': traversel_type,
                 'path': {'query': effective_path,
                          'depth': 1},
                 'is_folderish': True
                 }
        catalog = getToolByName(self.context.context, 'portal_catalog')
        results_folderish = catalog(query)

        selectable_types = get_selectable_types(widget)
        query = {'portal_type': selectable_types,
                 'path': {'query': effective_path,
                          'depth': 1},
                 'is_folderish': False
                 }

        results_content = catalog(query)

        folderish_selectable = set(selectable_types).difference(
            set(traversel_type))
        query = {'portal_type': list(folderish_selectable),
                 'path': {'query': effective_path,
                          'depth': 1},
                 'is_folderish': True
                 }

        results_folder_select = catalog(query)
        results = results_folderish + results_content + results_folder_select
        return results
