from redsolutioncms.make import BaseMake
from redsolutioncms.models import CMSSettings
from os.path import dirname, join
import shutil

class Make(BaseMake):

    def make(self):
        super(Make, self).make()
        cms_settings = CMSSettings.objects.get_settings()

        cms_settings.render_to('settings.py', 'tinymce/redsolutioncms/settings.pyt')
        cms_settings.render_to('urls.py', 'tinymce/redsolutioncms/urls.pyt')

    def postmake(self):
        super(Make, self).postmake()
        cms_settings = CMSSettings.objects.get_settings()
        if 'redsolutioncms.django-server-config' not in cms_settings.installed_packages:
            tinymce_media_dir = join(dirname(dirname(__file__)), 'media')
            project_media_dir = join(cms_settings.project_dir, 'media')
#           WARNING! Silently delete media dirs
            try:
                shutil.rmtree(join(project_media_dir, 'tinymce'))
#                no such directory
            except OSError:
                pass
#           copy files to media directory
            shutil.copytree(
                join(tinymce_media_dir, 'tinymce'),
                join(project_media_dir, 'tinymce'),
            )

make = Make()
