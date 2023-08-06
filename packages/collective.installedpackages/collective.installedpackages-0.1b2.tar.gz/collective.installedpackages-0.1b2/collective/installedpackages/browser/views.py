#coding=utf8
from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from yolk.yolklib import Distributions
import sys

grok.templatedir('view_templates')

class BaseListPythonPackages(grok.View):
    grok.context(ISiteRoot)
    grok.require('cmf.ManagePortal')
    grok.baseclass()
    
    def get_installed_packages(self):
        dists = Distributions()        
        packages = [
            dict(
                name=dist.project_name,
                version=dist.version,
                platform=dist.platform or 'any',
                location=dist.location,
            )
            for (dist, active) 
            in dists.get_distributions('all')
            if active
        ]
        packages.sort(key=lambda d: (d['name'], d['version']))
        
        return packages    

class ListPythonPackages(BaseListPythonPackages):
    grok.name('list-python-packages')
        
class ListPythonPackagesCfg(BaseListPythonPackages):
    grok.name('list-python-packages-cfg')
    
    def render(self):
        lines = ['[versions]']
        lines.extend(
            '%s = %s' % (d['name'], d['version']) 
            for d in self.get_installed_packages()
        )
        return '\n'.join(lines)
        
            
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
    
