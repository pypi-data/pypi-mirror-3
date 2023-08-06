#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
import os
import shutil

APPCFG_PATH = '/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/google/appengine/tools/'

class install(_install):
    def run(self):
        _install.run(self)
        print 'Backup and replace appcfg.py script...'
        appcfg_file = os.path.join(APPCFG_PATH, 'appcfg.py')
        if not os.path.isfile(appcfg_file):
            print "Couldn't find GAE SDK appcfg.py file in %s" % appcfg_file
            return
        os.rename(appcfg_file, os.path.join(APPCFG_PATH, 'appcfg.py.original'))
        try:
            import gae_asset_bundler
        except ImportError:
            print "Installation failed, unable to import module"
        shutil.copy(os.path.abspath('scripts/appcfg.py'), os.path.join(APPCFG_PATH, 'appcfg.py'))
        print '... done'

setup(
    name = "GaeAssetBundler",
    cmdclass={'install': install},
    version = "0.1.3dev",
    description='Assets compression and bundling for GAE',
    author='Fabio Sussetto',
    author_email='fabio@bynd.com',
    packages = find_packages(),
    package_data = {
        '': ['scripts/appcfg.py']
    },
    scripts=['gae_asset_bundler/asset_compressor.py']
)