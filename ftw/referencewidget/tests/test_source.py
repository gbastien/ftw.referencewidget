from ftw.builder import Builder
from ftw.builder import create
from ftw.referencewidget.selectable import DefaultSelectable
from ftw.referencewidget.sources import ReferenceObjSourceBinder
from ftw.referencewidget.tests import FunctionalTestCase


class TestReferenceObjSource(FunctionalTestCase):

    def setUp(self):
        super(TestReferenceObjSource, self).setUp()
        self.setup_fti()
        self.grant('Manager')

    def test_root_path_restriction(self):
        folder = create(Builder('folder'))
        subfolder = create(Builder('folder').within(folder))
        subsubfolder = create(Builder('folder').within(subfolder))
        sibling = create(Builder('folder'))

        source = ReferenceObjSourceBinder(
            root_path='/folder/folder')(subfolder)

        self.assertIn(subsubfolder, source)
        self.assertIn(subfolder, source)

        self.assertNotIn(folder, source)
        self.assertNotIn(sibling, source)

    def test_root_path_callable(self):
        folder = create(Builder('folder'))
        subfolder = create(Builder('folder').within(folder))
        subsubfolder = create(Builder('folder').within(subfolder))
        sibling = create(Builder('folder'))

        def current_path(context):
            return '/'.join(context.getPhysicalPath())

        source = ReferenceObjSourceBinder(
            root_path=current_path)(subfolder)

        self.assertIn(subsubfolder, source)
        self.assertIn(subfolder, source)

        self.assertNotIn(folder, source)
        self.assertNotIn(sibling, source)

        sibling_source = source = ReferenceObjSourceBinder(
            root_path=current_path)(sibling)

        self.assertNotIn(folder, sibling_source)
        self.assertNotIn(subfolder, sibling_source)
        self.assertNotIn(subsubfolder, sibling_source)
        self.assertIn(sibling, sibling_source)

    def test_nonselectable_option(self):
        folder = create(Builder('folder'))
        content = create(Builder('sample content'))

        source_content = create(Builder('folder'))

        source = ReferenceObjSourceBinder(
            nonselectable=['Folder'])(source_content)

        self.assertNotIn(folder, source)
        self.assertIn(content, source)

    def test_custom_selectable_class(self):
        folder = create(Builder('folder'))
        folder_titled = create(Builder('folder').titled(u'dummy title'))
        source_content = create(Builder('sample content'))

        class CustomSelectable(DefaultSelectable):
            def is_selectable(self):
                return u'dummy title' == self.content.title

        source = ReferenceObjSourceBinder(
            selectable_class=CustomSelectable)(source_content)

        self.assertNotIn(folder, source)
        self.assertIn(folder_titled, source)

    def test_force_selectable_types(self):
        folder = create(Builder('folder'))
        sample = create(Builder('sample content'))
        source_content = create(Builder('sample content'))

        source = ReferenceObjSourceBinder(
            override=True,
            selectable=['Folder'])(source_content)

        self.assertNotIn(sample, source)
        self.assertIn(folder, source)

    def test_not_searched_types_are_disabled_by_default(self):
        folder = create(Builder('folder'))
        sample = create(Builder('sample content'))

        self._set_not_searched_types('Folder')
        source = ReferenceObjSourceBinder()(sample)
        self.assertNotIn(folder, source)

    def test_allow_not_searched_types(self):
        folder = create(Builder('folder'))
        sample = create(Builder('sample content'))

        self._set_not_searched_types('Folder')
        source = ReferenceObjSourceBinder(
            allow_nonsearched_types=True)(sample)
        self.assertIn(folder, source)

    def _set_not_searched_types(self, *types):
        site_properties = self.portal.portal_properties.site_properties
        site_properties.types_not_searched = tuple(types)
