from math import pi, sin, cos
 
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import *
 
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        self.setBackgroundColor(135.0/256.0,206.0/256.0,235.0/256.0)
       
        self.prepareFloor()
        
        self.loadLines()
 
        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
 
    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 2)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont
        
    def prepareFloor(self):
                #step 1) create GeomVertexData and add vertex information
        format=GeomVertexFormat.getV3c4()
        vdata=GeomVertexData("vertices", format, Geom.UHStatic)
        

        vertexWriter=GeomVertexWriter(vdata, "vertex")
        colorWriter = GeomVertexWriter(vdata, "color")
        vertexWriter.addData3f(-100,-100,0)
        colorWriter.addData4f(0.8, 0.8, 0.8, 1)
        vertexWriter.addData3f(100,-100,0)
        colorWriter.addData4f(0.8, 0.8, 0.8, 1)
        vertexWriter.addData3f(100,100,0)
        colorWriter.addData4f(0.8, 0.8, 0.8, 1)
        vertexWriter.addData3f(-100,100,0)
        colorWriter.addData4f(0.8, 0.8, 0.8, 1)

        #step 2) make primitives and assign vertices to them
        tri1=GeomTriangles(Geom.UHStatic)
        tri2=GeomTriangles(Geom.UHStatic)

        #have to add vertices one by one since they are not in order
        tri1.addVertex(0)
        tri1.addVertex(1)
        tri1.addVertex(3)

        #makes sure primitive is valid (in this case, make sure tri1 has 3 and only 3 vertices)
        tri1.closePrimitive()

        #since the coordinates are in order we can use this convenience function.
        tri2.addConsecutiveVertices(1,3) #add vertex 1, 2 and 3
        tri2.closePrimitive()

        #step 3) make a Geom object to hold the primitives
        squareGeom=Geom(vdata)
        #squareGeom.setVertexData(vdata)
        squareGeom.addPrimitive(tri1)
        squareGeom.addPrimitive(tri2)

        #now put squareGeom in a GeomNode. You can now position your geometry in the scene graph.
        squareGN=GeomNode("square")
        squareGN.addGeom(squareGeom)
        self.render.attachNewNode(squareGN) 
        
    def loadLines(self):
        format=GeomVertexFormat.getV3c4()
        vdata=GeomVertexData("vertices", format, Geom.UHStatic)
        
        vertexWriter=GeomVertexWriter(vdata, "vertex")
        colorWriter = GeomVertexWriter(vdata, "color")
        
        vertexWriter.addData3f(-100,-50,-0.001)
        colorWriter.addData4f(0,0,0,1)
        vertexWriter.addData3f(0,0,-0.001)
        colorWriter.addData4f(0,0,0,1)
        vertexWriter.addData3f(5,5,-0.001)
        colorWriter.addData4f(0,0,0,1)
        vertexWriter.addData3f(5,50,-0.001)
        colorWriter.addData4f(0,0,0,1)
        vertexWriter.addData3f(99,99,-0.001)
        colorWriter.addData4f(0,0,0,1)
        vertexWriter.addData3f(-100,-50.001,-0.001)
        colorWriter.addData4f(0,0,0,1)
        vertexWriter.addData3f(-0.001,-0.001,-0.001)
        colorWriter.addData4f(0,0,0,1)
        vertexWriter.addData3f(4.999,4.999,-0.001)
        colorWriter.addData4f(0,0,0,1)
        vertexWriter.addData3f(4.999,49.999,-0.001)
        colorWriter.addData4f(0,0,0,1)
        vertexWriter.addData3f(98.999,98.999,-0.001)
        colorWriter.addData4f(0,0,0,1)
        
        line1 = GeomLinestrips(Geom.UHStatic)
        line1.addConsecutiveVertices(0,5)
        line1.closePrimitive()
        
        line2 = GeomLinestrips(Geom.UHStatic)
        line2.addConsecutiveVertices(5,5)
        line2.closePrimitive()
        
        linesGeom = Geom(vdata)
        linesGeom.addPrimitive(line1)
        linesGeom.addPrimitive(line2)
        
        lineGN = GeomNode("tracks")
        lineGN.addGeom(linesGeom)
        self.render.attachNewNode(lineGN)
 
app = MyApp()
app.run()
