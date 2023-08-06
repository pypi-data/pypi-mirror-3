import urllib

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import getAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from quintagroup.portlet.cumulus import CumulusPortletMessageFactory as _
from quintagroup.portlet.cumulus.interfaces import ITagsRetriever

class ICumulusPortlet(IPortletDataProvider):
    """ A cumulus tag cloud portlet.
    """
    # options for generating <embed ... /> tag
    width = schema.Int(
        title=_(u'Width of the Flash tag cloud'),
        description=_(u'Width in pixels (500 or more is recommended).'),
        required=True,
        default=152)

    height = schema.Int(
        title=_(u'Height of the Flash tag cloud'),
        description=_(u'Height in pixels (ideally around 3/4 of the width).'),
        required=True,
        default=152)

    tcolor = schema.TextLine(
        title=_(u'Color of the tags'),
        description=_(u'This and next 3 fields should be 6 character hex color values without the # prefix (000000 for black, ffffff for white).'),
        required=True,
        default=u'5391d0')

    tcolor2 = schema.TextLine(
        title=_(u'Optional second color for gradient'),
        description=_(u'When this color is available, each tag\'s color will be from a gradient between the two. This allows you to create a multi-colored tag cloud.'),
        required=False,
        default=u'333333')

    hicolor = schema.TextLine(
        title=_(u'Optional highlight color'),
        description=_(u'Color of the tag when mouse is over it.'),
        required=False,
        default=u'578308')

    bgcolor = schema.TextLine(
        title=_(u'Background color'),
        description=_(u'The hex value for the background color you\'d like to use. This options has no effect when \'Use transparent mode\' is selected.'),
        required=True,
        default=u'ffffff')

    trans = schema.Bool(
        title=_(u'Use transparent mode'),
        description=_(u'Switches on Flash\'s wmode-transparent setting.'),
        required=True,
        default=False)

    speed = schema.Int(
        title=_(u'Rotation speed'),
        description=_(u'Speed of the sphere. Options between 25 and 500 work best.'),
        required=True,
        default=100)

    distr = schema.Bool(
        title=_(u'Distribute tags evenly on sphere'),
        description=_(u'When enabled, the movie will attempt to distribute the tags evenly over the surface of the sphere.'),
        required=True,
        default=True)

    compmode = schema.Bool(
        title=_(u'Use compatibility mode?'),
        description=_(u'Enabling this option switches the plugin to a different way of embedding Flash into the page. Use this if your page has markup errors or if you\'re having trouble getting tag cloud to display correctly.'),
        required=True,
        default=False)

    # options for generating tag cloud data
    smallest = schema.Int(
        title=_(u'Smallest tag size'),
        description=_(u'The text size of the tag with the smallest count value (units given by unit parameter).'),
        required=True,
        default=8)

    largest = schema.Int(
        title=_(u'Largest tag size'),
        description=_(u'The text size of the tag with the highest count value (units given by the unit parameter).'),
        required=True,
        default=22)

    unit = schema.TextLine(
        title=_(u'Unit of measure'),
        description=_(u'Unit of measure as pertains to the smallest and largest values. This can be any CSS length value, e.g. pt, px, em, %.'),
        required=True,
        default=u'pt')

    max_tags = schema.Int(
        title=_(u'Maximum number of tags to display'),
        description=_(u'Used when too many tags make the display ugly.'),
        required=True,
        default=50)

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ICumulusPortlet)

    width    = 152;
    height   = 152;
    tcolor   = u'5391d0'
    tcolor2  = u'333333'
    hicolor  = u'578308'
    bgcolor  = u'ffffff'
    speed    = 100
    trans    = False
    distr    = True
    compmode = False

    smallest = 8
    largest  = 22
    unit     = u'pt'
    max_tags = 50

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _("Tag Cloud (cumulus)")


class Renderer(base.Renderer):
    """Portlet renderer.
    """

    render = ViewPageTemplateFile('cumulusportlet.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()
        portal_properties = getMultiAdapter((context, request), name=u'plone_tools').properties()
        self.default_charset = portal_properties.site_properties.getProperty('default_charset', 'utf-8')

    @property
    def title(self):
        return _("Tag Cloud")

    @property
    def compmode(self):
        return self.data.compmode

    def getScript(self):
        params = self.getParams()
        return """<script type="text/javascript">
                var so = new SWFObject("%(url)s", "tagcloudflash", "%(width)s", "%(height)s", "9", "#%(bgcolor)s");
                %(trans)s
                so.addParam("allowScriptAccess", "always");
                so.addVariable("tcolor", "0x%(tcolor)s");
                so.addVariable("tcolor2", "0x%(tcolor2)s");
                so.addVariable("hicolor", "0x%(hicolor)s");
                so.addVariable("tspeed", "%(tspeed)s");
                so.addVariable("distr", "%(distr)s");
                so.addVariable("mode", "%(mode)s");
                so.addVariable("tagcloud", "%(tagcloud)s");
                so.write("comulus");
            </script>""" % params

    def getParams(self):
        tagcloud = '<tags>%s</tags>' % self.getTagAnchors()
        tagcloud = tagcloud.encode(self.default_charset)
        tagcloud = urllib.quote(tagcloud)
        params = {
            'url': self.portal_url + '/++resource++tagcloud.swf',
            'width': self.data.width,
            'height': self.data.height,
            'bgcolor': self.data.bgcolor,
            'trans': self.data.trans and 'so.addParam("wmode", "transparent");' or '',
            'tcolor': self.data.tcolor,
            'tcolor2': self.data.tcolor2 or self.data.tcolor,
            'hicolor': self.data.hicolor or self.data.tcolor,
            'tspeed': self.data.speed,
            'distr': self.data.distr and 'true' or 'false',
            'mode': 'tags',
            'tagcloud': tagcloud,
        }
        flashvars = []
        for var in ('tcolor', 'tcolor2', 'hicolor', 'tspeed', 'distr', 'mode', 'tagcloud'):
            flashvars.append('%s=%s' % (var, params[var]))
        params['flashvars'] = '&'.join(flashvars)
        return params

    @memoize
    def getTagAnchors(self):
        tags = ''
        for tag in self.getTags():
            tags += '<a href="%s" title="%s entries" rel="tag" style="font-size: %.1f%s;">%s</a>\n' % \
                (tag['url'], tag['number_of_entries'], tag['size'], self.data.unit, tag['name'])
        return tags

    def getTags(self):
        tags = ITagsRetriever(self.context).getTags()
        if tags == []:
            return []

        tags.sort(lambda x,y: (x[1]<y[1] and 1) or (x[1]>y[1] and -1) or 0)
        tags = tags[:self.data.max_tags]

        number_of_entries = [i[1] for i in tags]

        min_number = min(number_of_entries)
        max_number = max(number_of_entries)
        distance = float(max_number - min_number) or 1
        step = (self.data.largest - self.data.smallest) / distance

        result = []
        for name, number, url in tags:
            size = self.data.smallest + step * (number - min_number)
            result.append({
                'name': name,
                'size': size,
                'number_of_entries': number,
                'url': url
            })
        return result

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ICumulusPortlet)

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ICumulusPortlet)
