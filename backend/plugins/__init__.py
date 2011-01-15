#!/usr/bin/env python3
'''Plugin loader module

'''
import os
import Plugin

def getPluginClasses():
    '''load and return a list of all Plugin derivates in the local modules'''
    # the module name   "package.package. ... .name"
    package= '.'.join(__name__.split('.')[:-1])
    print(__file__)
    # directory of this file
    dirPath= os.path.dirname(__file__) 
    print (dirPath)
    if package:
        # might be nonlocal import
        # 'package.package.'
        package+= '.'
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
        attributes= dir(module)
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
               issubclass(cls, Plugin.Plugin) and\
               cls not in pluginClasses:
                pluginClasses.append(cls)
    return pluginClasses


__all__ = ['getPluginClasses']

if __name__ == '__main__':
    # test module

    # test getPlugins
    print ('-' * 50)
    print('test getPlugins')
    print(getPluginClasses())
    
