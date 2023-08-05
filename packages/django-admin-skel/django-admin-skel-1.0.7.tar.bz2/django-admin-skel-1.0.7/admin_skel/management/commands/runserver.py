
from os.path import realpath, dirname, join
import warnings

from django.core.management.commands.runserver import Command as _Command


class Command(_Command):
    def __init__(self, *args, **kwargs):
        _Command.__init__(self, *args, **kwargs)
        warnings.warn('You are using modified runserver from django-admin-skel.', Warning)
        for opt in self.option_list:
            if opt.dest == 'admin_media_path':
                opt.default = join(dirname(dirname(dirname(realpath(__file__)))), 'media')



