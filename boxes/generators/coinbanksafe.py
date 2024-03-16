# Copyright (C) 2013-2014 Florian Festi
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

class CoinBankSafe(Boxes):
    """A piggy-bank designed to look like a safe."""

    description ='''
When gluing together the dials, you're pretty much guaranteed to get some glue between them and the door.
Make sure to actuate the dials a couple times while the glue is curing to ensure they can turn at the end.

Make sure not to discard the circle cutouts from the lid, base, and door. They are all needed.

![Open](static/samples/CoinBankSafe-2.jpg)
'''
    
    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "h")
        self.argparser.add_argument(
            "--slotlength", action="store", type=float, default=30,
            help="Length of the coin slot in mm")
        self.argparser.add_argument(
            "--slotwidth", action="store", type=float, default=4,
            help="Width of the coin slot in mm")
        self.argparser.add_argument(
            "--handlelength", action="store", type=float, default=8,
            help="Length of handle in multiples of thickness")
        self.argparser.add_argument(
            "--handleclearance", action="store", type=float, default=1.5,
            help="Clearance of handle in multiples of thickness")
    
    def circleSquareHole(self, x, y, radius, variant=False):
        t = self.thickness
        with self.saved_context():
            self.moveTo(x, y)
            self.rectangularHole(0, 0, t, t)
            if variant == "D":
                self.moveTo(0,0,45)
                self.rectangularHole(0, 0, t, t)
        with self.saved_context():
            if not variant:
                self.circle(x, y, radius)
            elif variant == "D":
                # can't use dhole because it's a part, not a hole
                # self.dHole(x, y, radius, rel_w=0.80)
                rel_w = 0.8
                w = 2.0 * radius * rel_w
                w -= radius
                a = math.degrees(math.acos(w / radius))
                self.moveTo(x, y, -a)
                self.moveTo(radius, 0, -90)
                self.corner(-360+2*a, radius)
                self.corner(-a)
                self.edge(2*radius*math.sin(math.radians(a)))
            elif variant == "W":
                # need to deal with the annoying margin applied to all Parts
                self.moveTo(-t/2, -t/2) # resolve weird margin thing of parts
                self.parts.waivyKnob(radius*2)

    def drawNumbers(self, radius, cover):
        fontsize = 0.9 * (radius - cover)
        with self.saved_context():
            self.moveTo(radius, radius)
            for num in range(8):
                angle = num*45
                x = (cover + fontsize *0.4) * math.sin(math.radians(angle))
                y = (cover + fontsize *0.4) * math.cos(math.radians(angle))
                self.text(str(num+1), align="center middle", fontsize=fontsize, angle=-angle, color=[1,0,0],
                          y=y, x=x)

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        slot_length = self.slotlength
        slot_width = self.slotwidth

        handle_length = self.handlelength * t
        handle_clearance = self.handleclearance * t

        # lock parameters
        big_radius = 2.25 * t
        small_radius = 1.4 * t
        spacing = 1

        # side walls
        with self.saved_context():
            self.rectangularWall(x, h, "seFf", move="mirror right")
            self.rectangularWall(y, h, "sFFF", move="right")

            # wall with holes for the locking bar
            # I don't know what that extra 0.3 is doing, this equation was derived experimentally
            # from measuring the correct distances at t=3 and t=6, and doing a regression.
            # The distance between the holes and the edge should be equal to t plus the distance
            # between the bottom of the square in the hinge of the lid.
            self.fingerHolesAt(x - 1.52*t + 0.3, 4.3*t, h, 90)
            self.rectangularWall(x, h, "sfFe", ignore_widths=[3,4,7,8], move="mirror right")

            # locking bar
            with self.saved_context():
                self.moveTo(0, 4*t)
                self.rectangularWall(1.5*t, h, "eeef", move="right")
            self.rectangularWall(1.5*t, h, "eeef", move="right only")
            # door
            door_clearance = .25 * t # amount to shave off of the door width so it can open
            self.moveTo(1, 1+t*4)
            self.polyline(
                (y - 2.25*t - door_clearance), -90, t, 90, t, 90, t, -90, 1.25*t, 90,
                h, 90,
                1.25*t, -90, t, 90, t, 90, t, -90, (y - 2.25*t - door_clearance), 90,
                h, 90)
            num_dials = 3
            space_under_dials = 6*big_radius
            space_not_under_dials = h - space_under_dials
            dial_spacing = space_not_under_dials / (num_dials + 1)
            if dial_spacing < 1 :
                min_height = 6*big_radius + 4
                raise ValueError(f"With thickness {t}, h must be at least {min_height} to fit the dials.")

            self.circleSquareHole(3*t - door_clearance, h/2, 1.25 * t)
            self.circleSquareHole(3*t - door_clearance, h/2 - (2*big_radius + dial_spacing), 1.25 * t)
            self.circleSquareHole(3*t - door_clearance, h/2 + (2*big_radius + dial_spacing), 1.25 * t)
            self.rectangularHole(y/2 - door_clearance, h/2, t, handle_length / 2)
            
        self.rectangularWall(x, h, "seff", move="up only")
        self.moveTo(0, t/2)

        # lid
        with self.saved_context():
            #self.rectangularWall(y, x, "efff")
            self.edges["e"](y)
            self.corner(90)
            self.edges["f"](x)
            self.corner(90)
            self.edges["f"](y)
            self.corner(90)
            self.edges["f"](x)
            self.corner(90)
            
            self.circleSquareHole(y - 1.75*t, 1.75*t, 1.15*t)
            self.rectangularHole(y/2, x/2, slot_length, slot_width)
        self.rectangularWall(y, x, "efff", move="right only")

        # bottom
        with self.saved_context():
            #self.rectangularWall(y, x, "efff")
            #self.moveTo(1, 1)
            self.edges["e"](y)
            self.corner(90)
            self.edges["f"](x)
            self.corner(90)
            self.edges["f"](y)
            self.corner(90)
            self.edges["f"](x)
            self.corner(90)
            self.circleSquareHole(1.75*t, 1.75*t, 1.15*t)
        self.rectangularWall(y, x, "efff", move="right only")

        # locks
        with self.saved_context():
            self.circleSquareHole(big_radius, big_radius, big_radius)
            self.drawNumbers(big_radius, small_radius)
            self.moveTo(2 * big_radius + spacing, 0)
            self.circleSquareHole(big_radius, big_radius, big_radius)
            self.drawNumbers(big_radius, small_radius)
            self.moveTo(2 * big_radius + spacing, 0)
            self.circleSquareHole(big_radius, big_radius, big_radius)
            self.drawNumbers(big_radius, small_radius)
            self.moveTo(2 * big_radius + spacing, 0)
            self.circleSquareHole(big_radius, big_radius, big_radius, "D")
            self.moveTo(2 * 0.8 * big_radius + spacing, 0)
            self.circleSquareHole(big_radius, big_radius, big_radius, "D")
            self.moveTo(2 * 0.8 * big_radius + spacing, 0)
            self.circleSquareHole(big_radius, big_radius, big_radius, "D")
            self.moveTo(2 * 0.8 * big_radius + spacing, 0)

            self.circleSquareHole(small_radius, small_radius, small_radius)
            self.moveTo(2 * small_radius + spacing, 0)
            self.circleSquareHole(small_radius, small_radius, small_radius)
            self.moveTo(2 * small_radius + spacing, 0)
            self.circleSquareHole(small_radius, small_radius, small_radius)
            self.moveTo(2 * small_radius + spacing, 0)
            self.circleSquareHole(small_radius, small_radius, small_radius, "W")
            self.moveTo(2 * small_radius + spacing, 0)
            self.circleSquareHole(small_radius, small_radius, small_radius, "W")
            self.moveTo(2 * small_radius + spacing, 0)
            self.circleSquareHole(small_radius, small_radius, small_radius, "W")
        self.moveTo(0, 2 * big_radius + spacing)

        # lock pins
        with self.saved_context():
            self.rectangularWall(5*t, t, move="up")
            self.rectangularWall(5*t, t, move="up")
            self.rectangularWall(5*t, t, move="up")
        self.rectangularWall(5*t, t, move="right only")

        # handle
        handle_curve_radius = 0.2 * t
        self.moveTo(2 * handle_curve_radius,0)
        self.polyline(
            handle_length - 2 * handle_curve_radius,
            (90, handle_curve_radius),
            handle_clearance - handle_curve_radius,
            90,
            handle_length / 4,
            -90,
            t,
            90,
            handle_length / 2,
            90,
            t,
            -90,
            handle_length / 4,
            90,
            handle_clearance - handle_curve_radius,
            (90, handle_curve_radius))
