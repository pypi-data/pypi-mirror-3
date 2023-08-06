#!/System/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
from __future__ import with_statement

import os
import sys
import re
import shutil
import jsmin
import time
from optparse import OptionParser
import logging

#TODO: refactor using these classes
class BaseBundle(object):
    
    def __init__(self):
        pass
    
class JsBundle(object):
    
    def __init__(self):
        super(JsBundle, self).__init__()
        
class CssBundle(object):
    
    def __init__(self):
        super(JsBundle, self).__init__()        

class AssetCompressor(object):
    
    bundles = {}
    
    excluded_dirs = ['.svn', '.git']
    
    jsbundle_regex = re.compile(r'<!--\s*jsbundle "(?P<bundle_name>\w*)"\s*-->(?P<content>.*?)<!--\s*endbundle\s*-->', re.DOTALL)
    scripts_regex = re.compile(r'<script (?P<attrs_before>[^>]*)src="(?P<src>[^"]+)"(?P<attrs_after>[^>]*)>')
    
    def __init__(self, app_path, burst_cache=True):
        self.app_path = app_path
        self.template_dir = os.path.join(app_path, 'templates')

        self.templates_min_path = os.path.join(self.app_path, '_bundled_templates')
        self.static_path = os.path.join(self.app_path, 'static')
        self.gen_bundles_path = os.path.join(self.static_path, 'bundles')
        self.burst_cache = burst_cache
        

    def parse_template(self, template_path, template_content):
        replaced_template = ''
        template_bundles = {}
        found_bundles = []
        for match in self.jsbundle_regex.finditer(template_content):
            template_bundles[match.group('bundle_name')] = {'scripts': [], 'filters': [], 'timestamp': int(time.time())}
            found_bundles.append(match.group('bundle_name'))
            content = match.group('content')
            if not content:
                return [], False
            for m in self.scripts_regex.finditer(content):
                asset_src = self.__normalize_asset_filename(m.group('src'))
                asset_path = os.path.join(self.static_path, asset_src[1:])
                if os.path.isfile(asset_path):
                    template_bundles[match.group('bundle_name')]['scripts'].append(dict(m.groupdict(), src=asset_src))
                else:
                    logging.warn('Missing asset file, ignoring it: %s' % asset_path)
    
        if not template_bundles:
            return [], False
    
        replaced_template = template_content
        for bundle_name, bundle_data in template_bundles.items():
            regex = re.compile(r'<!--\s*jsbundle "%s"\s*-->(.*?)<!--\s*endbundle\s*-->' % bundle_name, re.DOTALL)
            replaced_template = regex.sub(
                '<script type="text/javascript" src="/bundles/js/%s"></script>' % self.__bundle_filename(bundle_name, bundle_data['timestamp']),
                replaced_template
            )
            
        self.bundles[template_path] = template_bundles    
        return found_bundles, replaced_template
    

    def generate_bundles(self, burst_cache=True):
        if not self.bundles:
            return True
        
        js_bunles_path = os.path.join(self.gen_bundles_path, 'js')
        
        if not os.path.isdir(js_bunles_path):
            os.makedirs(js_bunles_path)
        
        for filepath, bundle in self.bundles.items():
            for bundle_name, bundle_data in bundle.items():
                bundle_content = []
                for src_file in bundle_data['scripts']:
                    pieces = src_file['src'].split('/')
                    src_path = os.path.join(self.static_path, *pieces)
                    with open(src_path, 'r') as f:
                        bundle_content.append(f.read())
                
                bundle_content = jsmin.jsmin('\n'.join(bundle_content))
                
                packed_path = os.path.join(js_bunles_path, self.__bundle_filename(bundle_name, bundle_data['timestamp']))
                with open(packed_path, 'w+') as f:
                    f.write(bundle_content)
                    
    def __bundle_filename(self, bundle_name, timestamp):
        if self.burst_cache:
            bundle_filename = '%s.%s.js' % (bundle_name, timestamp)
        else:
            bundle_filename = bundle_name + '.js'
            
        return bundle_filename
    
    def __normalize_asset_filename(self, filename):
        querystring_index = filename.find('?')
        if querystring_index > 1:
            filename = filename[:querystring_index]
        return filename
        

    def run(self):
        logging.info("Processing template files ...")
        for root, subFolders, files in os.walk(self.template_dir):
            for filename in files:
                filePath = os.path.join(root, filename)
                with open(filePath, 'r') as f:
                    found_bundles, replace_content = self.parse_template(filePath, f.read())
                if found_bundles:
                    base_path = root.replace(self.template_dir, '')
                    full_path = os.path.join(self.templates_min_path, base_path[1:])
                    if not os.path.exists(full_path):
                        os.makedirs(full_path)
                    new_file_path = os.path.join(full_path, filename)
                    logging.info("... Found bundle(s) '%s', generating %s" % (', '.join(found_bundles), os.path.join(full_path, filename)))
                    with open(new_file_path, 'w+') as f:
                        f.write(replace_content)
        self.generate_bundles()


if __name__ == '__main__':
    logging.basicConfig(format=('%(message)s'), level=logging.DEBUG)
    parser = OptionParser()
    parser.add_option("-c", "--burst_cache", action="store_true", dest="burst_cache", help="Generate cache-bursting filenames for bundles")
    (options, args) = parser.parse_args()
    
    app_path = os.path.abspath(sys.argv[1])
    compressor = AssetCompressor(app_path, burst_cache=options.burst_cache)
    compressor.run()
