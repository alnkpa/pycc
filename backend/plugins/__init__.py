#!/usr/bin/env python3
'''Plugin loader module

'''
import sys
import os
from manager import PyCCBackendPluginManager

#PLUGIN_BASE_MODULE_NAME is the Plugin module of which all Plugins inherit
PLUGIN_BASE_MODULE_NAME = 'Plugin'
PLUGIN_BASE_CLASS_NAME = 'Plugin'

def getPluginClasses():
    '''load and return a list of all Plugin derivates in the local modules'''
    # the module name   "package.package. ... .name"    so only show the packages
    package = '.'.join(__name__.split('.')[:-1])
    # directory of this file
    dirPath = os.path.dirname(__file__) 
    if package:
        # might be nonlocal import, from another Plugin
        # 'package.package.'
        package += '.'
    # get the plugin class
    pluginModuleName = package + PLUGIN_BASE_MODULE_NAME
    # enable simple import in Plugins as possible during tests
    sys.path.append(dirPath)
    try:
        module = __import__(pluginModuleName)
        Plugin = getattr(module, PLUGIN_BASE_CLASS_NAME)
        assert isinstance(Plugin, type), "the Plugin base class should be a class"
        # fileList of the local directory
        fileList= os.listdir(dirPath)
        # load the plugins in order
        fileList.sort()
        # list of the Plugin classes - classes derived from Plugin
        pluginClasses= []
        for pModuleFile in fileList:
            print (pModuleFile)
            # split .py or .pyc from file name
            modName, ext= os.path.splitext(pModuleFile)
            if modName.startswith('_'):
                # do not load _modules
                continue
            try:
                # try importing
                module= __import__(package+modName)
            except ImportError:
                continue
            attributes = dir(module)
            # search for Plugin classes
            for attr in attributes:
                if attr.startswith('_'):
                    # variables starting with _ shall not be considered
                    continue
                try:
                    cls= getattr(module, attr)
                except AttributeError:
                    # should not occour
                    continue
                # 1. find classes
                # 2. issubclass only on classes -> find Plugin derivates
                # 3. assure we do not load plugins twice
                if isinstance(cls, type) and \
                   issubclass(cls, Plugin) and\
                   cls not in pluginClasses:
                    pluginClasses.append(cls)
    finally:
        try:
            sys.path.remove(dirPath)
        except ValueError:
            # already removed
            pass
    return pluginClasses


__all__ = ['getPluginClasses']

if __name__ == '__main__':
    # test module

    # test getPluginClasses
    print ('-' * 50)
    print('test getPlugins')
    print(getPluginClasses())