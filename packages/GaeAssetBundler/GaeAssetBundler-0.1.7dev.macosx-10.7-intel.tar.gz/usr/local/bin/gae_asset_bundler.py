#!/System/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
from __future__ import with_statement

import os
import sys
import re
import shutil
import jsmin
import time
from optparse import OptionParser

def copy_directory(source, target, excluded_dirs=(), excluded_exts=()):
    ''' http://tarekziade.wordpress.com/2008/07/08/shutilcopytree-small-improvement/ '''
    if not os.path.exists(target):
        os.mkdir(target)
    for root, dirs, files in os.walk(source):
        for to_exclude in excluded_dirs:
            if to_exclude in dirs:
                dirs.remove(to_exclude)
        for file in files:
            if os.path.splitext(file)[-1] in excluded_exts:
                continue
            from_ = os.path.join(root, file)           
            to_ = from_.replace(source, target, 1)
            to_directory = os.path.split(to_)[0]
            if not os.path.exists(to_directory):
                os.makedirs(to_directory)
            shutil.copyfile(from_, to_)

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
    
    jsbundle_regex = re.compile(r'<!-- jsbundle "(?P<bundle_name>\w*)" -->(?P<content>.*?)<!-- endbundle -->', re.DOTALL)
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
        for match in self.jsbundle_regex.finditer(template_content):
            template_bundles[match.group('bundle_name')] = {'scripts': [], 'filters': [], 'timestamp': int(time.time())}
            content = match.group('content')
            if not content:
                return False
            for m in self.scripts_regex.finditer(content):
                template_bundles[match.group('bundle_name')]['scripts'].append(m.groupdict())
    
        if not template_bundles:
            return False
    
        replaced_template = template_content
        for bundle_name, bundle_data in template_bundles.items():
            regex = re.compile(r'<!-- jsbundle "%s" -->(.*)<!-- endbundle -->' % bundle_name, re.DOTALL)
            replaced_template = regex.sub(
                '<script type="text/javascript" src="/bundles/js/%s"></script>' % self.__bundle_filename(bundle_name, bundle_data['timestamp']),
                replaced_template
            )
            
        self.bundles[template_path] = template_bundles    
        return replaced_template
    

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
        
                
    def __copy_templates(self):
        if os.path.isdir(self.templates_min_path):
            shutil.rmtree(self.templates_min_path)
        #shutil.copytree(self.template_dir, self.templates_min_path)
        copy_directory(self.template_dir, self.templates_min_path, excluded_dirs=self.excluded_dirs)


    def run(self):
        self.__copy_templates()
        for root, subFolders, files in os.walk(self.templates_min_path):
            for filename in files:
                filePath = os.path.join(root, filename)
                print "Processing template file %s ..." % filePath
                with open(filePath, 'r') as f:
                    replace_content = self.parse_template(filePath, f.read())
                if replace_content:
                    print "... Find some bundle"
                    with open(filePath, 'w+') as f:
                        f.write(replace_content)
        self.generate_bundles()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-c", "--burst_cache", action="store_true", dest="burst_cache", help="Generate cache-bursting filenames for bundles")
    (options, args) = parser.parse_args()
    
    app_path = os.path.abspath(sys.argv[1])
    compressor = AssetCompressor(app_path, burst_cache=options.burst_cache)
    compressor.run()
