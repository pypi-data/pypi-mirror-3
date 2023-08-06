from django.utils.translation import ugettext_lazy as _
from django.db import models
from cms.models import CMSPlugin
from filer.fields.folder import FilerFolderField
from django.conf import settings

CMSPLUGIN_FILER_ALBUM_TEMPLATES = (
    ('cmsplugin_filer_album/prettyphoto.html', 'PrettyPhoto'),
    ('cmsplugin_filer_album/jcarousel_overlay.html', 'JCarousel + Overlay'),
    ('cmsplugin_filer_album/carousel.html', 'Carousel'),
)

def get_templates():
    return getattr(settings, 'CMSPLUGIN_FILER_ALBUM_TEMPLATES', CMSPLUGIN_FILER_ALBUM_TEMPLATES)

def get_default_template():
    return get_templates()[0]

class FilerAlbum(CMSPlugin):
    """
    Plugin for storing Filer Album.
    
    Default template displays files store inside this folder.
    """

    class Meta(object):
        verbose_name = _('Filer Album')
        verbose_name_plural = _('Filer Albums')

    folder = FilerFolderField()
    template = models.CharField(_("Template"),max_length=256,
                            choices=get_templates(), default=get_default_template())

    def __unicode__(self):
        if self.folder.name:
            return self.folder.name;
        return "<empty>"

    search_fields = ('title',)
