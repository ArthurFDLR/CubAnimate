from enum import Enum
from PyQt5.QtGui import QColor

class Axis(Enum):
    X = 0
    Y = 1
    Z = 2

class CubeSize:
    def __init__(self, x: int = 0, y: int = 0, z: int = 0):
        self.size = {}
        self.size[Axis.X] = max(0,x)
        self.size[Axis.Y] = max(0,y)
        self.size[Axis.Z] = max(0,z)
    
    def getSize(self, axis : Axis) -> int:
        return self.size[axis]

    def setSize(self, axis : Axis, size : int):
        self.size[axis] = max(0,size)
    
    def pointDefined(self, x:int, y:int, z:int) -> bool:
        return x < self.size[Axis.X] and y < self.size[Axis.Y] and z < self.size[Axis.Z]
    
    def getTotalNode(self) -> int:
        return self.size[Axis.X] * self.size[Axis.Y] *self.size[Axis.Z]

    def max(self):
        return max(self.size.values())

class CubeLEDFrame_DATA:
    def __init__(self, cubeSize:CubeSize):

        self.illustration = None
        
        self.cubeSize = cubeSize

        self.nullColor = QColor(255,255,255)

        self.LEDcolors = []
        for i in range(self.cubeSize.getSize(Axis.X)):
            self.LEDcolors.append([])
            for j in range(self.cubeSize.getSize(Axis.Y)):
                self.LEDcolors[i].append([])
                for k in range(self.cubeSize.getSize(Axis.Z)):
                    self.LEDcolors[i][j].append(self.nullColor)
    
    def setColorLED(self, x:int, y:int, z:int, color : QColor):
        if self.cubeSize.pointDefined(x,y,z):
            self.LEDcolors[x][y][z] = color
        else:
            print("No matching LED")
    
    def eraseColorLED(self, x:int, y :int, z :int):
        if self.cubeSize.pointDefined(x,y,z):
            self.LEDcolors[x][y][z] = self.nullColor
        else:
            print("No matching LED")
    
    def getColorLED(self, x :int, y :int, z :int) -> QColor:
        if self.cubeSize.pointDefined(x,y,z):
            return self.LEDcolors[x][y][z]
        else:
            print("No matching LED")
            return self.nullColor
    
    def getColorLED_HEX(self, x :int, y :int, z :int) -> str:
        if self.cubeSize.pointDefined(x,y,z):
            return self.LEDcolors[x][y][z].name()
        else:
            print("No matching LED")
            return self.nullColor.name()
    
    def getSize(self) -> CubeSize:
        return self.cubeSize
    
    def getSizeAxis(self, axis : Axis) -> int:
        return self.cubeSize.getSize(axis)
    
    def encode(self) -> str:
        """ Generate data line representing the frame for creating .anim file """
        strOut = ''
        for z in range(self.cubeSize.getSize(Axis.Z)):
            for y in range(self.cubeSize.getSize(Axis.Y)):
                for x in range(self.cubeSize.getSize(Axis.X)):
                    strOut = strOut + self.LEDcolors[x][y][z].name()
        return strOut
    
    def decode(self, dataLine : str):
        
        colorNameSize = 7
        dataLength = len(dataLine)
        listColorName = [ dataLine[i:i+colorNameSize] for i in range(0, dataLength, colorNameSize) ]
        
        self.LEDcolors.clear()
        for i in range(self.cubeSize.getSize(Axis.X)):
            self.LEDcolors.append([])
            for j in range(self.cubeSize.getSize(Axis.Y)):
                self.LEDcolors[i].append([])
                for k in range(self.cubeSize.getSize(Axis.Z)):
                    index = i + j * self.cubeSize.getSize(Axis.X) + k * self.cubeSize.getSize(Axis.X) * self.cubeSize.getSize(Axis.Y) 
                    self.LEDcolors[i][j].append(QColor(listColorName[index]))
    
    def printColors(self):
        for z in range(self.cubeSize.getSize(Axis.Z)):
                for y in range(self.cubeSize.getSize(Axis.Y)):
                    for x in range(self.cubeSize.getSize(Axis.X)):
                        print(self.LEDcolors[x][y][z].name())


