from zope.interface import alsoProvides
from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from quintagroup.portlet.cumulus import cumulusportlet

from quintagroup.portlet.cumulus.tests.base import TestCase, HAS_QUILLS_ENABLED

class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='quintagroup.portlet.cumulus.CumulusPortlet')
        self.assertEquals(portlet.addview,
                          'quintagroup.portlet.cumulus.CumulusPortlet')

    def test_interfaces(self):
        portlet = cumulusportlet.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='quintagroup.portlet.cumulus.CumulusPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   cumulusportlet.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = cumulusportlet.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, cumulusportlet.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        assignment = cumulusportlet.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, cumulusportlet.Renderer))


class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        self.portal['front-page'].edit(subject=['global', 'tags'])
        id_ = self.folder.invokeFactory('Document', id='blog-entry')
        self.folder[id_].edit(subject=['blog', 'tags'])
        if HAS_QUILLS_ENABLED:
            from quills.core.interfaces import IWeblogEnhanced
            alsoProvides(self.folder, IWeblogEnhanced)
            self.folder.reindexObject()

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = assignment or cumulusportlet.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_render_default(self):
        r = self.renderer(context=self.portal,
                          assignment=cumulusportlet.Assignment())
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        expected = """<script type="text/javascript"
                    src="http://nohost/plone/++resource++swfobject.js">
            </script>
            <div id="comulus">
                <p style="display:none;"><a href="http://nohost/plone/search?Subject:list=blog" title="1 entries" rel="tag" style="font-size: 8.0pt;">blog</a>
<a href="http://nohost/plone/search?Subject:list=global" title="1 entries" rel="tag" style="font-size: 8.0pt;">global</a>
<a href="http://nohost/plone/search?Subject:list=tags" title="2 entries" rel="tag" style="font-size: 22.0pt;">tags</a>
</p>
                <p style="padding: 1em; margin-bottom: 0;">
                    WP Cumulus Flash tag cloud by <a href="http://www.roytanck.com">Roy Tanck</a>
                    requires Flash Player 9 or better.
                </p>
            </div>
            <script type="text/javascript">
                var so = new SWFObject("http://nohost/plone/++resource++tagcloud.swf", "tagcloudflash", "152", "152", "9", "#ffffff");
                
                so.addParam("allowScriptAccess", "always");
                so.addVariable("tcolor", "0x5391d0");
                so.addVariable("tcolor2", "0x333333");
                so.addVariable("hicolor", "0x578308");
                so.addVariable("tspeed", "100");
                so.addVariable("distr", "true");
                so.addVariable("mode", "tags");
                so.addVariable("tagcloud", "%3Ctags%3E%3Ca%20href%3D%22http%3A//nohost/plone/search%3FSubject%3Alist%3Dblog%22%20title%3D%221%20entries%22%20rel%3D%22tag%22%20style%3D%22font-size%3A%208.0pt%3B%22%3Eblog%3C/a%3E%0A%3Ca%20href%3D%22http%3A//nohost/plone/search%3FSubject%3Alist%3Dglobal%22%20title%3D%221%20entries%22%20rel%3D%22tag%22%20style%3D%22font-size%3A%208.0pt%3B%22%3Eglobal%3C/a%3E%0A%3Ca%20href%3D%22http%3A//nohost/plone/search%3FSubject%3Alist%3Dtags%22%20title%3D%222%20entries%22%20rel%3D%22tag%22%20style%3D%22font-size%3A%2022.0pt%3B%22%3Etags%3C/a%3E%0A%3C/tags%3E");
                so.write("comulus");
            </script>"""
        self.failUnless(expected in output, 'Bad output')

    def test_render_compmode(self):
        r = self.renderer(context=self.portal,
                          assignment=cumulusportlet.Assignment(compmode=True, width=200, height=200))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        expected = """<object type="application/x-shockwave-flash"
                    data="http://nohost/plone/++resource++tagcloud.swf"
                    width="200" height="200">
                <param name="movie"
                       value="http://nohost/plone/++resource++tagcloud.swf" />
                <param name="bgcolor" value="ffffff" />
                <param name="AllowScriptAccess" value="always">
                
                <param name="flashvars"
                       value="tcolor=5391d0&amp;tcolor2=333333&amp;hicolor=578308&amp;tspeed=100&amp;distr=true&amp;mode=tags&amp;tagcloud=%3Ctags%3E%3Ca%20href%3D%22http%3A//nohost/plone/search%3FSubject%3Alist%3Dblog%22%20title%3D%221%20entries%22%20rel%3D%22tag%22%20style%3D%22font-size%3A%208.0pt%3B%22%3Eblog%3C/a%3E%0A%3Ca%20href%3D%22http%3A//nohost/plone/search%3FSubject%3Alist%3Dglobal%22%20title%3D%221%20entries%22%20rel%3D%22tag%22%20style%3D%22font-size%3A%208.0pt%3B%22%3Eglobal%3C/a%3E%0A%3Ca%20href%3D%22http%3A//nohost/plone/search%3FSubject%3Alist%3Dtags%22%20title%3D%222%20entries%22%20rel%3D%22tag%22%20style%3D%22font-size%3A%2022.0pt%3B%22%3Etags%3C/a%3E%0A%3C/tags%3E" />
                <p style="padding: 1em;"><a href="http://nohost/plone/search?Subject:list=blog" title="1 entries" rel="tag" style="font-size: 8.0pt;">blog</a>
<a href="http://nohost/plone/search?Subject:list=global" title="1 entries" rel="tag" style="font-size: 8.0pt;">global</a>
<a href="http://nohost/plone/search?Subject:list=tags" title="2 entries" rel="tag" style="font-size: 22.0pt;">tags</a>
</p>
                <p style="padding: 1em; margin-bottom: 0;">
                    WP-Cumulus by <a href="http://www.roytanck.com/">Roy Tanck</a>
                    requires Flash Player 9 or better.
                </p>
            </object>"""
        self.failUnless(expected in output, 'Bad output')

    if HAS_QUILLS_ENABLED:
        def test_render_on_blog(self):
            r = self.renderer(context=self.folder,
                            assignment=cumulusportlet.Assignment(compmode=True, width=200, height=200))
            r = r.__of__(self.folder)
            r.update()
            output = r.render()
            expected = """<param name="flashvars"
                       value="tcolor=5391d0&amp;tcolor2=333333&amp;hicolor=578308&amp;tspeed=100&amp;distr=true&amp;mode=tags&amp;tagcloud=%3Ctags%3E%3Ca%20href%3D%22http%3A//nohost/plone/Members/test_user_1_/topics/blog%22%20title%3D%220%20entries%22%20rel%3D%22tag%22%20style%3D%22font-size%3A%208.0pt%3B%22%3Eblog%3C/a%3E%0A%3Ca%20href%3D%22http%3A//nohost/plone/Members/test_user_1_/topics/tags%22%20title%3D%220%20entries%22%20rel%3D%22tag%22%20style%3D%22font-size%3A%208.0pt%3B%22%3Etags%3C/a%3E%0A%3C/tags%3E" />"""
            self.failUnless(expected in output, 'Bad output')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
