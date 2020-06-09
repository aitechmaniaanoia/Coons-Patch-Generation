# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 19:24:33 2019

@author: Zoe

Blender_version : 2.7
"""

#import random
import sys
import os
import numpy as np
#from mpl_toolkits.mplot3d import Axes3D
#import matplotlib.pyplot as plt
import bpy
import bmesh
from bpy import context

## define control points for 4 boundary
#g1ctrl = np.array([[0,0,0],[2,0,3],[3,0,1],[5,0,0]]) # points on y = 0 plane
#g2ctrl = np.array([[0,5,0],[1,5,2],[3,5,2],[5,5,0]]) # points on y = 5 plane
#h1ctrl = np.array([[0,0,0],[0,2,1],[0,3,5],[0,5,0]]) # points on x = 0 plane
#h2ctrl = np.array([[5,0,0],[5,1,2],[5,3,4],[5,5,0]]) # points on x = 5 plane

## create random control points
#def createcontrolpoints(width, length):
#    # number of control points
#    n = random.randint(4, 6) 

#    coorArrX = []
#    coorArrY = []
#    for k in range(n):
#        x = random.randint(0, width - 1)
#        y = random.randint(0, length - 1)
#        coorArrX.append(x)
#        coorArrY.append(y)
        
#    return coorArrX, coorArrY 

## read control points from file:
def readCtrls(fileName):
    ctrls=[]
    for line in open(fileName,"r"):
        if line.startswith('#'):continue
        values=line.split()
        if not values:continue
        if values[0]=='v':
            ctrl=[]
            ctrl.append(float(values[1]))
            ctrl.append(float(values[2]))
            ctrl.append(float(values[3]))
            ctrls.append(ctrl)
    ctrls = np.array(ctrls)
    return ctrls
  
## De Casteljau algorithm to get curves for 4 boundaries
def B(coorArr, i, j, t):
    if j == 0:
        return coorArr[i]
    return B(coorArr, i, j - 1, t) * (1 - t) + B(coorArr, i + 1, j - 1, t) * t

def decasteljau(coorArrX, coorArrY, numSteps):
    length = int(1/numSteps)
    vertics = []
    n = len(coorArrX)
    for k in range(length):
        t = float(k) / (length - 1)
        x = B(coorArrX, 0, n - 1, t)
        y = B(coorArrY, 0, n - 1, t)
        vertics.append([x,y])
    
    return vertics

## coons patch points interpolation
def createface(h1, h2, g1, g2, numSteps):
    #numSteps = 0.01
    S1 = []
    S2 = []
    S3 = []
    #for v in range(numSteps):
    #    s1 = (1 - v*0.01)*h1 + v*0.01*h2
    #    S1.append(s1)
    #for u in range(numSteps):
    #    s2 = (1 - u*0.01)*g1 + u*0.01*g2
    #    S2.append(s2)
        
    ## calculate s1, s2, s3
    p1 = g1[0]
    p2 = h2[0]
    p3 = g2[0]
    p4 = g2[-1]
    for u in range(int(1/numSteps)):
        for v in range(int(1/numSteps)):
            s1 = (1 - u*numSteps)*h1[u,:] + u*numSteps*h2[u,:]
            s2 = (1 - v*numSteps)*g1[v,:] + v*numSteps*g2[v,:]
            s3 = (1-u*numSteps)*(1-v*numSteps)*p1 + u*numSteps*(1-v*numSteps)*p2 + v*numSteps*(1-u*numSteps)*p3 + u*numSteps*v*numSteps*p4
            S1.append(s1)
            S2.append(s2)
            S3.append(s3)
        
    P = np.array(S1) + np.array(S2) - np.array(S3)
    #P = P.reshape((P.shape[0]*P.shape[1]), P.shape[2])
    return P

## create the surface
def makeFaces(verts):
    faces=[]
    #index=[]
    length = int(np.sqrt(len(verts)))
    #for i in range(half):
    #    index.append(i)
    #faces.append(index)
    ## append the points for each mesh
    for i in range(length - 1):
        for j in range(length - 1):
            index = []
            index.append(i*length + j)
            index.append((i+1)*length+j)
            index.append((i+1)*length+j+1)
            #index.append(i*101+j)
            #index.append(i*101+j+1)
            index.append(i*length+j+1)
            faces.append(index)
    return faces

def triangulate_object(obj):
    me = obj.data
    # Get a BMesh representation
    bm = bmesh.new()
    bm.from_mesh(me)

    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)

    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(me)
    bm.free()
    return me

def createMeshFromData(name, origin, verts, faces):
    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob.show_name = True
 
    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True
 
    # Create mesh from given verts, faces.
    me.from_pydata(verts, [], faces)
    # Update mesh with new data
    me=triangulate_object(ob)
    me.update()    
    return ob

def make_ob_file(verts):
    faces=makeFaces(verts)
    ob=createMeshFromData("test",(0,0,0),verts,faces)
    return ob

## export objects
def export_obj(filepath,obj):
    mesh = obj.data
    with open(filepath, 'w') as f:
        f.write("# OBJ file\n")
        for v in mesh.vertices:
            f.write("v %.4f %.4f %.4f\n" % v.co[:])
        for p in mesh.polygons:
            f.write("f")
            for i in p.vertices:
                f.write(" %d" % (i + 1))
            f.write("\n")
  
  
## read control points file:
#filepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
filepath = os.path.dirname(bpy.context.space_data.text.filepath)

g1ctrl = readCtrls(filepath + "\g1ctrl.txt")
g2ctrl = readCtrls(filepath + "\g2ctrl.txt")
h1ctrl = readCtrls(filepath + "\h1ctrl.txt")
h2ctrl = readCtrls(filepath + "\h2ctrl.txt")

## De Casteljau algorithm get Bezier Curves
numSteps = 0.01

g1 = decasteljau(g1ctrl[:,0], g1ctrl[:,2], numSteps)
g1 = np.insert(g1, 1, 0, axis=1)
g2 = decasteljau(g2ctrl[:,0], g2ctrl[:,2], numSteps)
g2 = np.insert(g2, 1, 5, axis=1)
h1 = decasteljau(h1ctrl[:,1], h1ctrl[:,2], numSteps)
h1 = np.insert(h1, 0, 0, axis=1)
h2 = decasteljau(h2ctrl[:,1], h2ctrl[:,2], numSteps)
h2 = np.insert(h2, 0, 5, axis=1)

## calculate coons patch points
verts = createface(h1, h2, g1, g2, numSteps)
#verts = np.array(verts)

## check the Bezier Curves
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')

#ax.scatter(h1[:,0], h1[:,1], h1[:,2])
#ax.scatter(h2[:,0], h2[:,1], h2[:,2])
#ax.scatter(g1[:,0], g1[:,1], g1[:,2])
#ax.scatter(g2[:,0], g2[:,1], g2[:,2])
#ax.scatter(verts[:,0], verts[:,1], verts[:,2])
#plt.show()

#verts = dplicate(verts)

## make surface
objects = make_ob_file(verts)

## export objects
obj = context.object
export_obj(filepath + "/result.obj",obj)

