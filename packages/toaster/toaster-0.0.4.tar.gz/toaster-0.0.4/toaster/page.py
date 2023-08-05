# -*- coding: utf-8 -*-

import os, re, yaml

from toaster.convertible import Convertible


class Page(Convertible):
    
    def __init__(self, site, path):
        
        # store page path data
        self.site = site
        self.path = path
        self.filename = os.path.basename(path)
        
        # process data from page file
        self.process(self.filename)
        
    
    def __repr__(self):
        return '<Page: %s>' % self.url


    def process(self, filename):
        self.url = os.path.join(self.site.settings['destination'], self.path)
        self.meta, self.content = self.read_yaml(self.path)
        self.context = { 'content': self.content, 'site': self.site }


    def render(self):
        
        # get the desired template file from the environment
        template = self.site.template_environment.get_template(os.path.relpath(self.path))
        
        # create the base path if it does not exist
        if not os.path.exists(os.path.dirname(self.url)):
            os.makedirs(os.path.dirname(self.url))
        
        # write the rendered post to disk
        with open(self.url, 'w') as stream:
            stream.writelines(template.render(self.context))