from ftw.referencewidget.interfaces import IReferenceWidget
from z3c.form.browser import widget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.schema.interfaces import IList
import json


class ReferenceBrowserWidget(widget.HTMLTextInputWidget, Widget):
    """ Datepicker widget. """
    implementsOnly(IReferenceWidget)

    klass = u'reference-widget'
    request = None
    block_traversal = None
    allow_traversal = None
    selectable = None
    nonselectable = None
    start = None
    override = None

    def __init__(self,
                 request,
                 block_traversal=[],
                 allow_traversal=[],
                 selectable=[],
                 nonselectable=[],
                 start='',
                 override=False,
                 allow_nonsearched_types=False,):
        self.request = request
        self.block_traversal = block_traversal
        self.allow_traversal = allow_traversal
        self.selectable = selectable
        self.nonselectable = nonselectable
        self.start = start
        self.override = override
        self.allow_nonsearched_types = allow_nonsearched_types

    def update(self):
        super(ReferenceBrowserWidget, self).update()
        widget.addFieldClass(self)

    def is_list(self):
        if IList.providedBy(self.field):
            return 'checkbox'
        else:
            return 'radio'

    def form_url(self):
        return self.form.request.getURL()

    def js_value(self):
        result = []
        if not self.value:
            return
        if isinstance(self.value, list):
            for item in self.value:
                obj = self.context.unrestrictedTraverse(item.encode('utf8'))
                result.append({'path': item.encode('utf8'),
                               'title': obj.title})
        else:
            obj = self.context.unrestrictedTraverse(
                self.value.encode('utf8'))
            result.append({'path': self.value.encode('utf8'),
                           'title': obj.title})
        return json.dumps(result)


@adapter(IReferenceWidget, IFormLayer)
@implementer(IFieldWidget)
def ReferenceWidgetFactory(field,
                           request,
                           block_traversal=[],
                           allow_traversal=[],
                           selectable=[],
                           nonselectable=[],
                           start='',
                           override=False,
                           allow_nonsearched_types=False):
    """IFieldWidget factory for DateTimePickerWidget."""
    return FieldWidget(field, ReferenceBrowserWidget(request,
                                                     block_traversal,
                                                     allow_traversal,
                                                     selectable,
                                                     nonselectable,
                                                     start,
                                                     override,
                                                     allow_nonsearched_types))
