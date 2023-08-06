"""

"""
import sys
import os
from copy import copy as shallow_copy
from optparse import make_option
from codecs import open
from itertools import chain

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.template import loader, Context
from django.contrib.flatpages.models import FlatPage
from django.conf import settings

from pelican import Pelican, main, generators, writers, settings as pelican_settings

class AltContext(Context):
    """
    A Django Context object does not have the 'copy' method that pelican
    expects, but it does support shallow copying (ie. has a __copy__ method)
    """

    def copy(self):
        return shallow_copy(self)

class AltGenerator(generators.Generator):
    """
    Subclass of the base pelican Generator class without the Jinja setup.

    This works because of duck-typing(ha!) - pelican only cares that a template
    object has a method called `render` and that it returns a string.
    """

    def __init__(self, *args, **kwargs):
        for idx, item in enumerate(('context', 'settings', 'path', 'theme',
                'output_path', 'markup')):
            if idx == 0:
                setattr(self, item, AltContext(args[idx]))
            else:
                setattr(self, item, args[idx])
        for arg, value in kwargs.items():
            setattr(self, arg, value)

    def get_template(self, name):
        return loader.get_template('bigmouth/' + name + '.html')

class AltWriter(writers.Writer):
    """
    A Writer class that writes each file as an index.html in its own directory.
    This requires that templates are updated with the correct urls, eg.

        /blog/first-post.html  -->  /blog/first-post/

    """

    def write_file(self, name, template, context, relative_urls=True,
        paginated=None, **kwargs):
        if name != 'index.html':
            name = os.path.splitext(name)[0].rstrip('/') + '/index.html'
        super(AltWriter, self).write_file(
            name, template, context, relative_urls, paginated, **kwargs
        )

class ArticlesGenerator(generators.ArticlesGenerator, AltGenerator):
    """Generate blog articles"""

    def __init__(self, *args, **kwargs):
        super(ArticlesGenerator, self).__init__(*args, **kwargs)

class PagesGenerator(generators.PagesGenerator, AltGenerator):
    """Generate pages"""

    def __init__(self, *args, **kwargs):
        super(PagesGenerator, self).__init__(*args, **kwargs)

class StaticGenerator(generators.StaticGenerator, AltGenerator):
    """copy static paths (what you want to cpy, like images, medias etc.
    to output"""

    def __init__(self, *args, **kwargs):
        super(StaticGenerator, self).__init__(*args, **kwargs)

class Cormorant(Pelican):
    """
    Subclass of the Pelican application class. The management command below
    will ultimately kick off the `Pelican.run` method which itself invokes a
    list of generators to do the heavy lifting; this subclass ensures that the
    generators are our own "Django Inside!" versions.
    """
    
    def get_generator_classes(self):
        generator_list = [ArticlesGenerator, PagesGenerator, StaticGenerator]
        return generator_list

    def get_writer(self):
        return AltWriter(self.output_path, settings=self.settings)

class Command(BaseCommand):
    """
    There is no doubt a better way to do this, but because we don't want to
    duplicate the pelican main function itself, we unfortunately do have to
    duplicate the configuration of the command line options expected by
    pelican main, because the Django command line introspection happens first
    and will fail if something is passed that it doesn't expect. This raises
    the further problem that '--settings' is a valid option for both this
    function and pelican main, and we resolve this for the minute by
    declaring that pelican config options must be placed in the Django settings
    file and so '--settings' will refer to the same module regardless.

    eg. python manage.py run_pelican \
            -s bigmouth_example/settings.py
            -o bigmouth_example/blog/
            bigmouth_example/blog_content 
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '-t',
            '--theme-path',
            dest='theme',
            type='string',
            help='Path where to find the theme templates. If not specified, it'
                'will use the default one included with pelican.'),
        make_option(
            '-o',
            '--output',
            dest='output',
            type='string',
            help='Where to output the generated files. If not specified, a directory'
                ' will be created, named "output" in the current path.'),
        make_option(
            '-m',
            '--markup',
            dest='markup',
            type='string',
            help='the list of markup language to use (rst or md). Please indicate '
                'them separated by commas'),
        make_option(
            '-x',
            '--no-flatpages',
            dest='flatpages',
            action="store_false",
            default=True,
            help='the list of markup language to use (rst or md). Please indicate '
                'them separated by commas'),
    )

    def handle(self, *args, **options):
        if not args:
            raise CommandError("Missing content source directory.")
        # the Django settings file will be execfiled by pelican
        cfg = os.path.splitext(
            sys.modules[os.environ['DJANGO_SETTINGS_MODULE']].__file__
        )[0] + '.py'
        assert os.path.exists(cfg)
        argv = [
            'pelican',
            '--settings=%s' % cfg,
            '--verbose',
        ]
        if options['output']:
            argv.append('--output=%s' % options['output'])
        if options['markup']:
            argv.append('--markup=%s' % options['markup'])
        if options['theme']:
            argv.append('--theme-path=%s' % options['theme'])
        argv.append(args[0])
        sys.argv[:] = argv
        # use our own Pelican subclass
        pelican_settings._DEFAULT_CONFIG['PELICAN_CLASS'] = Cormorant
        main()
        if options['flatpages']:
            outdir = options['output'].rstrip(os.sep)
            url_prefix = '/' + os.path.basename(outdir) + '/'
            query = FlatPage.objects.filter(
                sites__id=settings.SITE_ID
            ).filter(
                url__startswith=url_prefix
            )
            # delete existing flatpages
            query.delete()
            for root, dirs, files in os.walk(outdir):
                for f in files:
                    filename = os.path.join(root, f)
                    url = url_prefix + filename[len(outdir)+1:]
                    if url.endswith('/index.html'):
                        url = url[:-10]
                    with open(filename, encoding='utf-8' ) as fileobj:
                        try:
                            s = fileobj.read()
                            page = FlatPage.objects.create(
                                url=url, title=url, content=s,
                            )
                            page.sites.add(settings.SITE_ID)
                        except UnicodeDecodeError:
                            self.stdout.write(
                                'Flatfile creation - skipping undecodable file:'
                                ' %s%s' % (filename, os.linesep)
                            )



