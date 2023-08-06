from zope import component
from zope import schema
from zope import interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


from plone.app.layout.viewlets import common
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from plone.registry.field import Tuple
from plone.z3cform import layout
from z3c.form import form

from collective.metarobots import _


content_vocabulary = SimpleVocabulary([
  SimpleTerm('all', 'all', u"all"),
  SimpleTerm('noindex', 'noindex', u"noindex"),
  SimpleTerm('nofollow', 'nofollow', u"nofollow"),
  SimpleTerm('none', 'none', u"none"),
  SimpleTerm('noarchive', 'noarchive', u"noarchive"),
  SimpleTerm('nosnippet', 'nosnippet', u"nosnippet"),
  SimpleTerm('noodp', 'noodp', u"noodp"),
  SimpleTerm('notranslate', 'notranslate', u"notranslate"),
  SimpleTerm('noimageindex', 'noimageindex', u"noimageindex"),
  SimpleTerm('unavailable_after_end', 'unavailable_after_end', u"unavailable after end time"),
])


class TagSettings(interface.Interface):
    """This schema define the settings to use to build the tag"""

    content = schema.List(title=_(u"Content"),
                          description=_(u"settings_content_description"),
                          value_type=schema.Choice(title=_(u"Content value"),
                                               vocabulary=content_vocabulary),
                          required=True)


class Tag(common.ViewletBase):

    def update(self):
        super(Tag, self).update()
        registry = component.getUtility(IRegistry)
        self.contextual = False

        if registry:
            self.settings = registry.forInterface(TagSettings)
            content = self.settings.content

            if content and "unavailable_after_end" in content and \
               hasattr(self.context, 'getExpirationDate'):
                self.contextual = True

    def render(self):
        self.update()
        if self.settings.content and self.content():
            return self.index()

        return u""


    def content(self):
        if self.contextual:
            return self.content_contextual()
        else:
            return self.content_cached()

    @view.memoize
    def content_contextual(self):
        content = list(self.settings.content)
        content.remove("unavailable_after_end")
        expiration = self.context.getExpirationDate()
        if expiration:
            dt_formated = expiration.strftime('%d %b %Y %H:%M:%S %Z')
            value = "unavailable_after: %s" % formated
            value = value.strip()
            content.append(value)

        return u", ".join(content)

    @view.memoize_contextless
    def content_cached(self):
        content = list(self.settings.content)
        content.remove("unavailable_after_end")
        return u", ".join(content)


class ControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = TagSettings

ControlPanelView = layout.wrap_form(ControlPanelForm, ControlPanelFormWrapper)
ControlPanelView.label = _(u"Meta tag Robots settings")
