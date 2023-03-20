# !/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import math
from planet import Direction
from typing import Tuple, List
from enum import IntEnum, unique

@unique
class Color(IntEnum):
    UNDEFINED = 0
    BLUE = 1
    RED = 2

class Odometry:
    def __init__(self, wheel_distance=12.3, wheel_diameter=5.5):
        self.wheel_distance = 12.3
        self.wheel_diameter = 5.6
        self.count_per_rot = 360
        self.grid_size = 50#cm

        self.x_position = 0
        self.y_position = 0
        self.direction = Direction.NORTH
    
    def calculatePosition(self, motorValues: List[Tuple[int,int]], lastNodeColor: Color=Color.UNDEFINED, currentNodeColor: Color=Color.UNDEFINED):
        deltaX = 0
        deltaY = 0

        oldL=motorValues[0][0]
        oldR=motorValues[0][1]

        self.direction = math.radians(self.direction)
        
        for d in motorValues:
            delta = self.__calculateDelta((d[0]-oldL,d[1]-oldR))
            deltaX += delta[0]
            deltaY += delta[1]
            self.direction -= delta[2]

            oldL = d[0]
            oldR = d[1]
        print("Deltas in cm: ",deltaX,";",deltaY)

        roundedGridX = round(deltaX/self.grid_size)
        roundedGridY = round(deltaY/self.grid_size)

        self.direction = Direction((round(math.degrees(self.direction)/90)*90)%360)

        if lastNodeColor is not Color.UNDEFINED and currentNodeColor is not Color.UNDEFINED:
            if (lastNodeColor == currentNodeColor and (roundedGridX+roundedGridY)%2 != 0) or (lastNodeColor != currentNodeColor and (roundedGridX+roundedGridY)%2 == 0):
                #korrektur
                deltaX /= self.grid_size
                deltaY /= self.grid_size

                cXn = roundedGridX-1
                cXp = roundedGridX+1
                cYn = roundedGridY-1
                cYp = roundedGridY+1

                # verwende satz des pythagoras um nächstliegenden roten knoten zu berechnen
                dDict = {}
                dDict[(cXn-deltaX)**2+(roundedGridY-deltaY)**2] = (cXn,roundedGridY)
                dDict[(roundedGridX-deltaX)**2+(cYp-deltaY)**2] = (roundedGridX, cYp)
                dDict[(roundedGridX-deltaX)**2+(cYn-deltaY)**2] = (roundedGridX, cYn)
                dDict[(cXp-deltaX)**2+(roundedGridY-deltaY)**2] = (cXp,roundedGridY)

                self.x_position,self.y_position = dDict[min(dDict.keys())]  
                return          
        
        self.x_position += roundedGridX
        self.y_position += roundedGridY
        

    def __calculateDelta(self, d: Tuple[int,int]):
        dl = (d[0]/self.count_per_rot)*self.wheel_diameter*math.pi
        dr = (d[1]/self.count_per_rot)*self.wheel_diameter*math.pi
        beta = (dr-dl)/(self.wheel_distance*2)
        try:
            s = ((dr+dl)/(2*beta))*math.sin(beta)
        except ZeroDivisionError:
            s = dl
        delX = s*math.sin(self.direction+beta)
        delY = s*math.cos(self.direction+beta)
        delDir = 2*beta

        return (delX,delY,delDir)

    def set_position(self, coord: Tuple[int, int]):
        self.x_position = coord[0]
        self.y_position = coord[1]
    
    def set_direction(self, direct: Direction):
        self.direction = direct

    def get_position(self):
        return (self.x_position, self.y_position)

    def get_direction(self):
        return self.direction

