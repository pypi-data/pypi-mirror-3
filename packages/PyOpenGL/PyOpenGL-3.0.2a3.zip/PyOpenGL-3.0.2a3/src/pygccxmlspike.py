#! /usr/bin/env python
"""Spike test script to extract OpenGL headers"""
from pygccxml import parser
from pygccxml.parser.config import gccxml_configuration_t

def core_and_extensions():
    config = gccxml_configuration_t( 
        define_symbols=['GL_GLEXT_PROTOTYPES'] 
    )
    tree = parser.parse( [
        '/usr/include/GL/gl.h',
        'glext.h'
    ], 
        compilation_mode=parser.COMPILATION_MODE.ALL_AT_ONCE, 
        config = config,
    )[0]
    
    for declaration in [x for x in tree.declarations[:] if x.partial_name.startswith( 'gl' )]:
        print declaration.partial_name 

if __name__ == "__main__":
    core_and_extensions()

    
