from enum import Enum

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
