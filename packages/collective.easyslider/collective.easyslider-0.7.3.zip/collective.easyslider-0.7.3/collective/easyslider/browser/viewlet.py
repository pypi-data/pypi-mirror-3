from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from collective.easyslider.settings import PageSliderSettings
from collective.easyslider.interfaces import ISliderPage
from collective.easyslider.browser.base import AbstractSliderView

try:
    from collective.easytemplate.engine import getTemplateContext
    from collective.easytemplate.utils import applyTemplate
    easytemplate_installed = True
except:
    easytemplate_installed = False

import logging
logger = logging.getLogger('collective.easyslider')

class BaseSliderViewlet(ViewletBase):
    override_hidden = False # show even if settings say not to.

    @memoize
    def get_settings(self):
        return PageSliderSettings(self.context)
    
    settings = property(get_settings)
    
    @memoize
    def get_show(self):
        if not ISliderPage.providedBy(self.context):
            return False
        else:
            if len(self.settings.slides) == 0:
                return False
            else:
                return self.override_hidden or self.settings.show
    
    @property
    def slides(self):
        return self.settings.slides

    show = property(get_show)

class EasySlider(BaseSliderViewlet):

    def render_slide(self, slide):
        if not easytemplate_installed or not self.settings.easytemplate_enabled:
            return slide

        context = getTemplateContext(self.context, expose_schema=False)
        text, errors = applyTemplate(context, slide, logger)
        
        if errors:
            return slide
        else:
            return text


class EasySliderHead(BaseSliderViewlet, AbstractSliderView):
   pass 
    
