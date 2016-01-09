from math import pi, sin, cos
import json
import urllib2
 
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import *
 
#TODO: separate concerns
class MyApp(ShowBase):


    def __init__(self):
        ShowBase.__init__(self)
        ShowBase.disableMouse(self)
        
        self.nodes = []
        self.ways = []
        self.meter = 200.0 / 2200.0 #2200 meters - diameter of rendered area
        
        self.setBackgroundColor(135.0/256.0,206.0/256.0,235.0/256.0)
       
        self.prepareFloor()
        
        self.downloadOSMData()
        
        self.loadLines()

        self.camera.setPos(0,0,3.0*self.meter)
 
        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
 
    # Define a procedure to move the camera.

    def spinCameraTask(self, task):
        angleDegrees = task.time * 2.0
        angleRadians = angleDegrees * (pi / 180.0)
        #self.camera.setPos(100 * sin(angleRadians), -100.0 * cos(angleRadians), 2)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont
        
    def prepareFloor(self):
        #step 1) create GeomVertexData and add vertex information
        format=GeomVertexFormat.getV3c4()
        vdata=GeomVertexData("vertices", format, Geom.UHStatic)

        vertexWriter=GeomVertexWriter(vdata, "vertex")
        colorWriter = GeomVertexWriter(vdata, "color")
        vertexWriter.addData3f(-1000,-1000,0)
        colorWriter.addData4f(0.8, 0.8, 0.8, 1)
        vertexWriter.addData3f(1000,-1000,0)
        colorWriter.addData4f(0.8, 0.8, 0.8, 1)
        vertexWriter.addData3f(1000,1000,0)
        colorWriter.addData4f(0.8, 0.8, 0.8, 1)
        vertexWriter.addData3f(-1000,1000,0)
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
        
        for node in self.nodes:
            vertexWriter.addData3f(node["lat"], node["lon"], 0.2*self.meter)
            colorWriter.addData4f(0,0,0,1)
            
        lines = []
        
        for way in self.ways:
            line = GeomLinestrips(Geom.UHStatic)
            for pointer in way["pointers"]:
                line.addVertex(pointer)
            line.closePrimitive()
            lines.append(line)
        
        linesGeom = Geom(vdata)
        for line in lines:
          linesGeom.addPrimitive(line)
        
        lineGN = GeomNode("tracks")
        lineGN.addGeom(linesGeom)
        self.render.attachNewNode(lineGN)
        
    def downloadOSMData(self):
        # for now, hardcoded OpenStreetMap Overpass API URL for Tczew's area squared
        # Tczew station centre - 54.0972478, 18.7897812
        self.bboxTop = 54.1072478
        self.bboxBottom = 54.0872478
        self.bboxLeft = 18.7697812
        self.bboxRight = 18.8097812
        apiUrl = "http://overpass.osm.rambler.ru/cgi/interpreter?data=[out:json][timeout:25];%28way[%22railway%22]%28%20" + str(self.bboxBottom) + ",%20" + str(self.bboxLeft) + ",%20" + str(self.bboxTop) + ",%20" + str(self.bboxRight) + "%29;%29;out%20body;%3E;out;"
        print(apiUrl)
        jsonString = urllib2.urlopen(apiUrl).read()
        jsonData = json.loads(jsonString)
        jsonWays = filter(lambda x: x["type"] == "way", jsonData["elements"])
        jsonNodes = filter(lambda x: x["type"] == "node", jsonData["elements"])
        #TODO: keep bbox as one object
        self.convertAndSaveNodes(jsonNodes, self.bboxTop, self.bboxBottom, self.bboxLeft, self.bboxRight)
        self.convertAndSaveWays(jsonWays)
        
    def convertAndSaveNodes(self, jsonNodes, bboxTop, bboxBottom, bboxLeft, bboxRight):
        print("There are " + str(len(jsonNodes)) + " nodes to parse")
        index = len(self.nodes)
        for node in jsonNodes:
            node["index"] = index
            index += 1
            # normalize for -100;+100 scale
            node["lat"] = 200.0 * (bboxTop - node["lat"]) / (bboxTop - bboxBottom) - 100.0
            node["lon"] = -1.0 * (200.0 * (bboxRight - node["lon"]) / (bboxRight - bboxLeft) - 100.0)
            self.nodes.append(node)
        print("Nodes parsed")
            
    def convertAndSaveWays(self, jsonWays):
        print("There are " + str(len(jsonWays)) + " ways to parse")
        index = len(self.ways)
        for way in jsonWays:
            way["pointers"] = []
            for node in way["nodes"]:
                nodePointers = filter(lambda x: x["id"] == node, self.nodes)
                if len(nodePointers) > 1:
                    print("WARNING: more than one node available!")
                elif len(nodePointers) == 0:
                    print("ERROR: node " + str(node) + " not found, skipping!")
                    continue
                way["pointers"].append(nodePointers[0]["index"])
            self.ways.append(way)
        print("Ways parsed")
        
app = MyApp()
app.run()
