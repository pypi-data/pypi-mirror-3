""" CSS
"""
from App.Common import rfc1123_date
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ResourceRegistries.tools.packer import CSSPacker

class CSS(object):
    """ Handle criteria
    """
    def __init__(self, context, request, resources=()):
        self.context = context
        self.request = request
        self._resources = resources
        self.duration = 3600*24*365

        self.csstool = getToolByName(context, 'portal_css', None)
        if self.csstool:
            self.debug = self.csstool.getDebugMode()

    @property
    def resources(self):
        """ Return resources
        """
        return self._resources

    def get_resource(self, resource):
        """ Get resource content
        """
        obj = self.context.restrictedTraverse(resource, None)
        if not obj:
            return '/* ERROR */'
        try:
            content = obj.GET()
        except AttributeError, err:
            return str(obj)
        except Exception, err:
            return '/* ERROR: %s */' % err
        else:
            return content

    def get_content(self, **kwargs):
        """ Get content
        """
        output = []
        for resource in self.resources:
            content = self.get_resource(resource)
            header = '\n/* - %s - */\n' % resource
            if not self.debug:
                content = CSSPacker('safe').pack(content)
            output.append(header + content)
        return '\n'.join(output)

    @property
    def helper_css(self):
        """ Helper css
        """
        return []

class ViewCSS(CSS):
    """ CSS libs used in view mode
    """
    @property
    def css_libs(self):
        """ CSS libs
        """
        return (
            '++resource++eea.daviz.view.css',
        )

    @property
    def resources(self):
        """ Return view resources
        """
        res = self.helper_css
        res.extend(self.css_libs)
        return res

    def __call__(self, *args, **kwargs):
        """ view.css
        """
        self.request.RESPONSE.setHeader('content-type', 'text/css')
        expires = rfc1123_date((DateTime() + 365).timeTime())
        self.request.RESPONSE.setHeader('Expires', expires)
        self.request.RESPONSE.setHeader('Cache-Control',
                                        'max-age=%d' % self.duration)
        return self.get_content()

class EditCSS(CSS):
    """ CSS libs used in edit form
    """
    @property
    def css_libs(self):
        """ CSS Libs
        """
        return (
            '++resource++eea.daviz.edit.css',
        )

    @property
    def resources(self):
        """ Return edit resources
        """
        res = self.helper_css
        res.extend(self.css_libs)
        return res

    def __call__(self, *args, **kwargs):
        """ edit.css
        """
        self.request.RESPONSE.setHeader('content-type', 'text/css')
        expires = rfc1123_date((DateTime() + 365).timeTime())
        self.request.RESPONSE.setHeader('Expires', expires)
        self.request.RESPONSE.setHeader('Cache-Control',
                                        'max-age=%d' % self.duration)
        return self.get_content()
