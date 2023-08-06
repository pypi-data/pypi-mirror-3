# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py 49925 2012-06-01 12:11:22Z sylvain $

import zc.recipe.egg
import zc.buildout.easy_install


SCRIPT_REQUIRES = [
    'zope.configuration',
    'zope.app.locales [extract]',
    'zope.i18nmessageid',
    'infrae.i18nextract']


def string_to_lines(string):
    return filter(
        lambda v: v, map(
            lambda s: s.strip(), string.split('\n')))


class Recipe(object):
    """Install scripts
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.options['eggs'] = self.options.get('eggs', '') + '\n' + \
            '\n '.join(SCRIPT_REQUIRES) + \
            '\n ' + options['packages'] + \
            '\n ' + options.get('output-package', '')
        self.packages = string_to_lines(options['packages'])
        self.output_dir = options.get('output', '').strip()
        self.output_package = options.get('output-package', '').strip()
        self.domain = options.get('domain', 'silva').strip()
        self.products = string_to_lines(options.get('zope-products', ''))
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        """Install the recipe.
        """
        scripts = []
        requirements, ws = self.egg.working_set()

        arguments = {'packages': self.packages,
                     'output_dir': self.output_dir,
                     'output_package': self.output_package,
                     'domain': self.domain,
                     'products': self.products}
        scripts.extend(
            zc.buildout.easy_install.scripts(
                [('%s-extract'% self.name,
                  'infrae.i18nextract.extract',
                  'egg_entry_point')],
                ws, self.options['executable'],
                self.buildout['buildout']['bin-directory'],
                arguments = arguments,
                extra_paths = self.egg.extra_paths,
                ))

        arguments = {'output_package': self.output_package,
                     'products': self.products,
                     'domain': self.domain}
        scripts.extend(
            zc.buildout.easy_install.scripts(
                [('%s-manage'% self.name,
                  'infrae.i18nextract.manage',
                  'egg_entry_point')],
                ws, self.options['executable'],
                self.buildout['buildout']['bin-directory'],
                arguments = arguments,
                extra_paths = self.egg.extra_paths,
                ))

        return scripts

    update = install
