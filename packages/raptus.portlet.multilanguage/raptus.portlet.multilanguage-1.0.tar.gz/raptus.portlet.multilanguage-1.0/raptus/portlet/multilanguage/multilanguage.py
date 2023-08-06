from zope import schema
from zope.i18n import translate
from zope.i18nmessageid.message import Message
from zope.interface import implements
from zope.component import getUtility, getMultiAdapter
from zope.formlib import form

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from plone.app.controlpanel.widgets import MultiCheckBoxColumnsWidget

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

from plone.portlet.static import static

class CustomMultiCheckBoxColumnsWidget(MultiCheckBoxColumnsWidget):
    how_many_columns = 5

    def __init__(self, field, request):
        """Initialize the widget."""
        super(CustomMultiCheckBoxColumnsWidget, self).__init__(field, request)

class IMultilanguagePortlet(static.IStaticPortlet):
    """A portlet which renders predefined static HTML for a defined set 
    of languages.

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    
    languages = schema.List(
        title=_(u"heading_languages",
                default=u"Languages"),
        description=_(u"description_languages",
                      default=u"The languages for which this portlet should be displayed."),
        required=False,
        value_type = schema.Choice(
            vocabulary="plone.app.vocabularies.SupportedContentLanguages"))


class Assignment(static.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IMultilanguagePortlet)

    languages = []

    def __init__(self, languages=[], **args):
        super(Assignment, self).__init__(**args)
        self.languages = languages

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        title = self.header
        if isinstance(title, Message):
            title = translate(title, context=self.request)
        return '%s (%s)' % (title, ','.join(self.languages))


class Renderer(static.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('multilanguage.pt')

    def css_class(self):
        """Generate a CSS class from the portlet header
        """
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return "portlet-multilanguage-%s" % normalizer.normalize(header)

    @property
    def available(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        lang = portal_state.language().lower()
        if lang in self.data.languages or lang[:2] in self.data.languages:
            return True
        return False


class AddForm(static.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IMultilanguagePortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields['languages'].custom_widget = CustomMultiCheckBoxColumnsWidget
    label = _(u"title_edit_multilanguage_portlet",
              default=u"Edit multilanguage portlet")
    description = _(u"description_multilanguage_portlet",
                    default=u"A portlet which can display static HTML text for a defined set of languages.")

    def create(self, data):
        return Assignment(**data)


class EditForm(static.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IMultilanguagePortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields['languages'].custom_widget = CustomMultiCheckBoxColumnsWidget
    label = _(u"title_edit_multilanguage_portlet",
              default=u"Edit multilanguage portlet")
    description = _(u"description_multilanguage_portlet",
                    default=u"A portlet which can display static HTML text for a defined set of languages.")
