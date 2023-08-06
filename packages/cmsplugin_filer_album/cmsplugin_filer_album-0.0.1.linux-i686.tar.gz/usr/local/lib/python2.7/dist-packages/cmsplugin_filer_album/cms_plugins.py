from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
import models

class FilerAlbumPlugin(CMSPluginBase):
    model = models.FilerAlbum
    name = _("Album")
    text_enabled = False
    admin_preview = False

    def get_folder_images(self, folder, user):
        qs_files = folder.files.filter(image__isnull=False)
        if user.is_staff:
            return qs_files
        else:
            return qs_files.filter(is_public=True)

    def render(self, context, instance, placeholder):

        self.render_template = instance.template

        context.update({
            'object': instance,
            'folder_images': self.get_folder_images(instance.folder, context['request'].user),
            'placeholder': placeholder
        })    

        return context

plugin_pool.register_plugin(FilerAlbumPlugin)
