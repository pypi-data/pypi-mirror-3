from zope import schema
from zope.component import adapts, getMultiAdapter
from zope.formlib.form import FormFields

from zope.interface import implements
from zope.interface import Interface
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from my315ok.watermarkImage.browser.catalog_vocabulary import MineSearchableTextSourceBinder

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFPlone.interfaces import IPloneSiteRoot
#from Products.ATContentTypes.interface.topic import IATTopic
#from Products.ATContentTypes.interface.image import IATImage

from plone.app.controlpanel.form import ControlPanelForm

from my315ok.watermarkImage import watermarkImageMessageFactory as  _
from my315ok.watermarkImage.interfaces import Iwatermark

class IWatermarkSchema(Interface):
    """
    """
    
    wartermark_item = schema.List(
                    title=_(u"Site watermark"),
                    description=_(u'help_site_wartermark_item',
                                  default=u"You may search for and choose a "
                                            "image "
                                            "to act as the source of Watermark logo "
                                            "Use search box below to search "
                                            "items in the portal and select "
                                            "items you want to provide as Watermark "
                                            "logo"),
                    required=False,
                    value_type=schema.Choice(
                                    source=MineSearchableTextSourceBinder({'object_provides':Iwatermark.__identifier__},
                                                      default_query='path:')
                                            )
                )


   
class SiteWatermarkControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IWatermarkSchema)

    def __init__(self, context):
        super(SiteWatermarkControlPanelAdapter, self).__init__(context)
        self.portal = context
        pprop = getToolByName(self.portal, 'portal_properties')
        self.context = pprop.site_properties

    def get_wartermark_item(self):
        # uberselection widget does not like empty values
        wartermark_item = [x for x in getattr(self.context, 'site_wartermark_item', []) if x]
        return wartermark_item

    def set_wartermark_item(self, value):
        if value is not None:
            self.context.site_wartermark_item = value
        else:
            self.context.site_wartermark_item = []



    wartermark_item = property(get_wartermark_item, set_wartermark_item)

    
class SiteWatermarkControlPanel(ControlPanelForm):

    form_fields = FormFields(IWatermarkSchema)
    form_fields['wartermark_item'].custom_widget = UberMultiSelectionWidget

    label = _("Site Watermark settings")
    description = _("Setup Site Watermark logo.")
    form_name = _("Site Watermark settings")

