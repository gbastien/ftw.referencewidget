from ftw.referencewidget.browser.utils import get_selectable_types
from ftw.referencewidget.browser.utils import get_traversal_types
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
import json


class ReferenceJsonEndpoint(BrowserView):

    def __call__(self):
        widget = self.context
        if widget.request.get('start'):
            effective_path = widget.request.get('start')
            effective_context = widget.context.unrestrictedTraverse(effective_path.encode("utf-8"))
        elif not widget.start:
            effective_context = widget.form.context
        else:
            effective_context = widget.context.unrestrictedTraverse(widget.start)

        current_depth = len(effective_context.getPhysicalPath())

        traversel_type = get_traversal_types(widget)
        query = {'portal_type': traversel_type,
                 'path': {'query': '/'.join(effective_context.getPhysicalPath()),
                          'depth': 2},
                 'is_folderish': True
                 }
        catalog = getToolByName(self.context.context, 'portal_catalog')
        results_folderish = catalog(query)

        selectable_types = get_selectable_types(widget)
        query = {'portal_type': selectable_types,
                 'path': {'query': '/'.join(effective_context.getPhysicalPath()),
                          'depth': 2},
                 'is_folderish': False
                 }

        results_content = catalog(query)

        folderish_selectable = set(selectable_types).difference(set(traversel_type))
        query = {'portal_type': list(folderish_selectable),
                 'path': {'query': '/'.join(effective_context.getPhysicalPath()),
                          'depth': 2},
                 'is_folderish': True
                 }

        results_folder_select = catalog(query)
        results = results_folderish + results_content + results_folder_select
        lookup_table = {}
        result = []
        for item in results:
            depth = len(item.getPath().split('/')) - current_depth
            if depth == 0:
                continue
            obj_dict = {'path': item.getPath(),
                        'id': item.id,
                        'title': item.Title,
                        'folderish': item.is_folderish,
                        'selectable': item.portal_type in selectable_types,
                        'children': []}

            if depth == 1:
                result.append(obj_dict)
                lookup_table[item['id']] = len(result) - 1
            else:
                phys_path = item.getPath().split('/')
                if phys_path[current_depth] not in lookup_table.keys():
                    continue
                parent = result[lookup_table[phys_path[current_depth]]]
                for counter in range(1, depth - 1):
                    parent = parent['children'][phys_path[current_depth + counter]]
                parent['children'].append(obj_dict)
        return json.dumps(result)
