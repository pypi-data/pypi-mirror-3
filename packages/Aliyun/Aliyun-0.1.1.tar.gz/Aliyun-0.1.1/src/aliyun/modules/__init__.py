# -*- coding: utf-8 -*-

def simple_module_factory(name):
    name = name.lower()
    module = None
    if name == 'moye':
        from aliyun.modules import moye as module
        from aliyun.modules.moye import metadata, functions
    return module
