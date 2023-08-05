##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import imp
import os

class Recipe:

    def __init__(self, buildout, name, options):
        self.name, self.options, self.buildout = name, options, buildout
        options['location'] = options['prefix'] = os.path.join(
            buildout['buildout']['parts-directory'],
            name)

    def callScript(self, script):
        filename, callable = script.rsplit(':', 1)
        filename = os.path.abspath(filename)
        module = imp.load_source('script', filename)
        # Run the script with all options
        getattr(module, callable)(self.options, self.buildout)

    def install(self):
        # Create directory
        dest = self.options['location']
        if not os.path.exists(dest):
            os.mkdir(dest)
        # Retrieve ans run the script with all options
        script = self.options['install-script']
        self.callScript(script)
        return dest

    def update(self):
        if 'update-script' not in self.options:
            return
        # Retrieve ans run the script with all options
        script = self.options['update-script']
        self.callScript(script)


