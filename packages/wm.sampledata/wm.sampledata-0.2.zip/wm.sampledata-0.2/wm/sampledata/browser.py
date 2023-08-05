from Products.Five.browser import BrowserView
from zope.component import getUtilitiesFor, getUtility
from wm.sampledata.interfaces import ISampleDataPlugin
from Products.statusmessages.interfaces import IStatusMessage
from zope.component.interfaces import ComponentLookupError
from operator import itemgetter

class SampleDataView(BrowserView):

    def listPlugins(self):
        """list all available plugins sorted by their name
        """
        plugins = []
        for name, util in getUtilitiesFor(ISampleDataPlugin):
            plugins.append(dict(name=name,
                                title = util.title,
                                description=util.description))

        return sorted(plugins, key=itemgetter('name'))

    def runPlugin(self,plugin,debug=False):
        """run a named plugin and redirect to the sampledata page again.
        show a status message that tells the user if the plugin could not be found,
        raised an error or ran successfully.
        """
        result = None
        try:
            plugin = getUtility(ISampleDataPlugin,name=plugin)
            result = plugin.generate(self.context)
            IStatusMessage(self.request).addStatusMessage(u"successfully ran %s" % plugin.title , 'info')
        except ComponentLookupError, e:
            IStatusMessage(self.request).addStatusMessage(u"could not find plugin %s" % plugin , 'error')
            if debug:
                raise e
        except Exception, e:
            IStatusMessage(self.request).addStatusMessage(u"error running %s: %s" % (plugin.title, str(e)) , 'error')
            #TODO: log stacktrace to error log
            if debug:
                raise e
        finally:
            #return to listing
            self.request.response.redirect(self.context.absolute_url() + '/@@'  + self.__name__)
            return result



