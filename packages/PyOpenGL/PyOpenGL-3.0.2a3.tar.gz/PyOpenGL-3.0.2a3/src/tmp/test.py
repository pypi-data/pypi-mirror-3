#! /usr/bin/env python
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from osmesa import *
from numpy import *

def main():
    ctx = OSMesaCreateContext(OSMESA_RGBA, None)
    data = zeros( (300,300,4), 'B' )
    OSMesaMakeCurrent(
        ctx, data, GL_UNSIGNED_BYTE,
        300,300
    )
    glMatrixMode(GL_PROJECTION)
    gluPerspective(40.,1.,1.,40.)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(0,0,10,
              0,0,0,
              0,1,0)
    glDisable( GL_LIGHTING )
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glutInit( [] )
    glutSolidSphere(2,20,20)
    print sum(data)

if __name__ == "__main__":
    main()
