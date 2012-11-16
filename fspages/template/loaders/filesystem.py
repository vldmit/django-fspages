from django.template.loaders.filesystem import Loader as FileSystemLoader
from django.conf import settings
from django.utils._os import safe_join
from django.utils.translation import get_language

class I18NLoader(FileSystemLoader):
    """
    When searching for template, prepeng
    """
    is_usable = True
    
    def get_template_sources(self, template_name, template_dirs=None):
        """
        Returns the absolute paths to "template_name", when appended to each
        directory in "template_dirs". Any paths that don't lie inside one of the
        template dirs are excluded from the result set, for security reasons.
        
        If current language is not default, prepend each path with language
        name. E.g. 'include/banner.html' would become 'de/include/banner.html'
        """
        if not template_dirs:
            template_dirs = settings.TEMPLATE_DIRS
        if get_language() != settings.LANGUAGE_CODE:
            lang = get_language()
            new_dirs = []
            for i in template_dirs:
                new_dirs.extend([safe_join(i, lang) ,i])
            template_dirs = new_dirs

        for template_dir in template_dirs:
            try:
                yield safe_join(template_dir, template_name)
            except UnicodeDecodeError:
                # The template dir name was a bytestring that wasn't valid UTF-8.
                raise
            except ValueError:
                # The joined path was located outside of this particular
                # template_dir (it might be inside another one, so this isn't
                # fatal).
                pass
