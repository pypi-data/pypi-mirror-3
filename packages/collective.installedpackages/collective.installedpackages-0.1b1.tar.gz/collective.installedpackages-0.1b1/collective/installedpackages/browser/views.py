#coding=utf8
from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from yolk.yolklib import Distributions
import sys

grok.templatedir('view_templates')

class ListPythonPackages(grok.View):
    grok.context(ISiteRoot)
    grok.name('list-python-packages')
    grok.require('cmf.ManagePortal')
    
    def get_installed_packages(self):
        dists = Distributions()
        
        return [
            dict(
                name=dist.project_name,
                version=dist.version,
                platform=dist.platform or 'any',
                location=dist.location,
                active='yes' if active else 'no',
            )
            for (dist, active) 
            in dists.get_distributions('all')
            if active
        ]
        
class ListSysPath(grok.View):
    grok.context(ISiteRoot)
    grok.name('list-sys-path')
    grok.require('cmf.ManagePortal')
    
    def get_sys_path(self):
        return list(sys.path)
    
class InstalledPackagesControlPanel(grok.View):
    grok.context(ISiteRoot)
    grok.name('installed-packages-controlpanel')
    grok.require('cmf.ManagePortal')
    
