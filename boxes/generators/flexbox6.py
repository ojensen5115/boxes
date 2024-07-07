# Copyright (C) 2024 Oliver Jensen
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *


class FlexBox6(Boxes):
    """A small jewelry box with flexed corners and a flex hinge."""

    ui_group = "FlexBox"

    description = """
A small jewelry box with flexed corners and a flex hinge.

IMPORTANT NOTE: entered x and y will be treated as targets, and may be adjusted
to accommodate the checkerboard pattern according to your material width."""

    def __init__(self) -> None:
        '''
        dovetail: 
        '''
        Boxes.__init__(self)
        self.addSettingsArgs(edges.DoveTailSettings, angle=30, size=2)
        self.addSettingsArgs(edges.FlexSettings)
        self.buildArgParser(x=165.0, y=115.0, h=60.0)
        self.argparser.add_argument(
            "--radiusFactor", action="store", type=int, default=7,
            help="corner radius, multiple thickness (must be even)")
        self.argparser.add_argument(
            "--lipWidthX", action="store", type=int, default=4,
            help="inner x lip width, in multiples of thickness")
        self.argparser.add_argument(
            "--lipWidthY", action="store", type=int, default=3,
            help="inner y lip width, in multiples of thickness")
        self.argparser.add_argument(
            "--splitSides", action="store", type=bool, default=True,
            help="whether to split the sides into two pieces (dovetailing on the sides)")
    




    def fingeredFlexArea(self, numFingers, width, thickness, idxOffset=0):

        fgap = 2/3 * thickness
        fll  = 10 * thickness

        segments = max(math.ceil(width / (fll + fgap)), 2)
        segmentLength = (width - 2*thickness) / segments - fgap

        single = width < fll

        self.moveTo(0, -thickness)

        def segmentedEdge(idx, segments):
            self.moveTo(thickness)
            self.edge(segmentLength / 2)
            self.moveTo(fgap)
            for _ in range(segments - 1):
                self.edge(segmentLength)
                self.moveTo(fgap)
            self.edge(segmentLength / 2)
            self.moveTo(thickness)

        
        def segmentedReverseEdge(idx, segments):
            idx += idxOffset
            if idx%2==0:
                self.moveTo(thickness + fgap)
            else:
                self.moveTo(fgap)
                self.edge(thickness)

            if single:
                self.edge(segmentLength + fgap)
            else:
                for _ in range(segments - 1):
                    self.edge(segmentLength)
                    self.moveTo(fgap)
            self.edge(segmentLength - fgap)
            
            if idx%2==0:
                self.edge(thickness)
                self.moveTo(fgap)
            else:
                self.moveTo(thickness + fgap)

        self.moveTo(0, 0, 90)
        for idx in range(numFingers * 2):
            segmentedEdge(idx, segments)
            self.moveTo(0, -thickness/2, 180)
            segmentedReverseEdge(idx, segments)
            self.moveTo(0, thickness/2, 180)
        self.moveTo(thickness)
        self.corner(-90)


    def fingerEdge(self, numFingers, thickness, fingerSign, skip=0):
        num = int(numFingers)
        if numFingers != num:
            raise
        for idx in range(num):
            if not (skip==1 and idx==0):
                self.corner(fingerSign * -90)
                self.edge(thickness)
                self.corner(fingerSign * 90)
            self.edge(thickness)
            self.corner(fingerSign * 90)
            self.edge(thickness)
            self.corner(fingerSign * -90)
            self.edge(thickness)

    def plate(self, p, fingerSign=1, plate=False, move=None):

        xfingers = p['xfingers']
        yfingers = p['yfingers']
        hingefingers = p['hingefingers']
        thickness = p['thickness']
        radius = p['radius']
        lipX = p['xlipfingers']
        lipY = p['ylipfingers']

        boundingX = 2 * (xfingers * thickness + radius + thickness)
        boundingY = 2 * (yfingers * thickness + radius + thickness) + thickness
        if self.move(boundingX, boundingY, move, True):
            return
        
        fingerArc = 90 / p['cornerFingers'] / 2

        def fingeredCorner():
            # adjust for the middle of the piece
            centerRadius = radius - thickness/2
            # return self.moveArc(90, radius + thickness)
            if fingerSign == -1:
                r = centerRadius + thickness
            else:
                r = centerRadius
            
            for idx in range(p['cornerFingers']):
                self.corner(fingerSign * -90, 0)
                self.edge(thickness)
                self.corner(fingerSign * 90, 0)
                self.corner(fingerArc, r + fingerSign * thickness)
                self.corner(fingerSign * 90, 0)
                self.edge(thickness)
                self.corner(fingerSign * -90, 0)
                self.corner(fingerArc, r)
        
        self.moveTo(radius, 0, 0)
        self.fingerEdge(xfingers, thickness, fingerSign)
        fingeredCorner()
        self.fingerEdge(yfingers, thickness, fingerSign)
        fingeredCorner()
        if plate:
            self.fingerEdge((xfingers - hingefingers)/2, thickness, fingerSign)
            if fingerSign == 1:
                self.edge(hingefingers * thickness * 2)
                self.fingerEdge((xfingers - hingefingers)/2, thickness, fingerSign)
            else:
                self.corner(90)
                self.edge(thickness)
                self.corner(-90)
                self.edge(hingefingers * thickness * 2)
                self.fingerEdge((xfingers - hingefingers)/2, thickness, fingerSign, skip=1)
        else:
            self.fingerEdge(xfingers, thickness, fingerSign)
        fingeredCorner()
        self.fingerEdge(yfingers, thickness, fingerSign)
        fingeredCorner()

        if plate:
            holeX = 2*(radius + thickness*(xfingers - lipX))
            holeY = 2*(radius + thickness*(yfingers - lipY))
            centerX = boundingX / 2 - thickness - radius
            centerY = boundingY / 2 - thickness
            if fingerSign == 1:
                centerY -= thickness
            self.rectangularHole(centerX, centerY, holeX, holeY)
        
        self.move(boundingX, boundingY, move)

    


    def frontPlate(self, height, xBaseFingers, yBaseFingers, cornerFingers, thickness, move=None):

        fingers = 2*(math.ceil(yBaseFingers/2) + cornerFingers) + xBaseFingers

        boundingX = fingers * 2*thickness
        boundingY = height + thickness

        if self.move(boundingX, boundingY, move, True):
            return

        self.fingerEdge(fingers, thickness, 1)
        self.corner(90)
        self.edges['d'](height - thickness)
        self.corner(90)
        self.fingerEdge(fingers, thickness, 1)
        self.corner(90)
        self.edges['d'](height - thickness)
        self.corner(90)

        self.moveTo(yBaseFingers * thickness + 2*thickness)
        self.fingeredFlexArea(cornerFingers, height+thickness, thickness, idxOffset=yBaseFingers%2)
        self.moveTo(xBaseFingers * thickness * 2)
        self.fingeredFlexArea(cornerFingers, height+thickness, thickness, idxOffset=yBaseFingers%2)

        self.move(boundingX, boundingY, move)
    
    def backPlates(self,
                   xBaseFingers, yBaseFingers, cornerFingers,
                   preHingeFingers, hingeFingers, hingeHeight,
                   baseH, lidH, thickness):

        hingeLength = hingeFingers * thickness * 2
        preHingeLength = preHingeFingers * thickness * 2

        # bottom
        self.fingerEdge(
            preHingeFingers*2 + hingeFingers,
            thickness, 1)
        self.corner(90)
        self.edges['D'](baseH - thickness)
        self.corner(90)
        self.fingerEdge(
            preHingeFingers,
            thickness, 1)
        self.moveTo(hingeLength, 0)
        self.fingerEdge(
            preHingeFingers,
            thickness, 1)
        self.corner(90)
        self.edges['D'](baseH - thickness)
        self.corner(90)
        self.moveTo(0, -thickness)

        # bends
        with self.saved_context():
            self.moveTo(yBaseFingers * thickness, thickness)
            self.fingeredFlexArea(cornerFingers, baseH + thickness, thickness, idxOffset=yBaseFingers%2)
            
            self.moveTo(xBaseFingers * thickness * 2)
            self.fingeredFlexArea(cornerFingers, baseH + thickness, thickness, idxOffset=yBaseFingers%2)

        # hinge
        with self.saved_context():
            self.moveTo(preHingeLength + hingeLength, baseH / 2, 90)
            self.edges['X'](hingeHeight, hingeLength - self.burn * 2)
            self.moveTo(0, hingeLength, 180)
            self.edges['e'](hingeHeight)


        with self.saved_context():
            self.moveTo(yBaseFingers * thickness, thickness + baseH + thickness)
            self.fingeredFlexArea(cornerFingers, lidH + thickness, thickness, idxOffset=yBaseFingers%2)
            
            self.moveTo(xBaseFingers * thickness * 2)
            self.fingeredFlexArea(cornerFingers, lidH + thickness, thickness, idxOffset=yBaseFingers%2)
        
        # top
        self.moveTo(0, baseH + 2*thickness)
        self.fingerEdge(preHingeFingers, thickness, 1)
        self.moveTo(hingeLength, 0)
        self.fingerEdge(preHingeFingers, thickness, 1)
        self.corner(90)
        self.edges['D'](lidH - thickness)
        self.corner(90)
        self.fingerEdge(preHingeFingers*2 + hingeFingers, thickness, 1)
        self.corner(90)
        self.edges['D'](lidH - thickness)
        self.corner(90)
        self.moveTo(0, -thickness)

        

        




    def render(self):

        x = self.x
        y = self.y
        h = self.h


        thickness = self.thickness
        lipX = self.lipWidthX
        lipY = self.lipWidthY

        targetRadius = thickness * self.radiusFactor

        lidH = 0.3 * h
        baseH = 0.7 * h



        targetC4 = math.pi * targetRadius / 2
        targetCornerFingers = targetC4 / (2 * thickness)
        cornerFingers = round(targetCornerFingers)
        c4 = cornerFingers * thickness * 2
        radius = c4 * 2 / math.pi

        xBaseFingers = int(round((x - 2*radius) / thickness / 2))
        yBaseFingers = int(round((y - 2*radius) / thickness / 2))

        # back calculations
        hingeFingers = xBaseFingers // 2
        if (hingeFingers + xBaseFingers) % 2 == 1:
            hingeFingers += 1
        preHingeFingers = math.floor(yBaseFingers/2) + cornerFingers + (xBaseFingers - hingeFingers)/2
        hingeHeight = h / 2 + 2*thickness

        self.moveTo(0,10,0)

        plateParams = {
            'xfingers': xBaseFingers,
            'yfingers': yBaseFingers,
            'xlipfingers': lipX,
            'ylipfingers': lipY,
            'hingefingers': hingeFingers,
            'radius': radius,
            'cornerFingers': cornerFingers,
            'thickness': thickness
        }

        with self.saved_context():
            self.plate(plateParams, move="right")
            self.plate(plateParams, plate=True)
        self.plate(plateParams, move="up only")

        with self.saved_context():
            self.plate(plateParams, fingerSign=-1, move="right")
            self.plate(plateParams, fingerSign=-1, plate=True)
        self.plate(plateParams, fingerSign=-1, move="up only")

        self.frontPlate(baseH, xBaseFingers, yBaseFingers, cornerFingers, thickness, move="up")
        self.frontPlate(lidH, xBaseFingers, yBaseFingers, cornerFingers, thickness, move="up")
        
        self.backPlates(xBaseFingers, yBaseFingers, cornerFingers, preHingeFingers, hingeFingers, hingeHeight, baseH, lidH, thickness)