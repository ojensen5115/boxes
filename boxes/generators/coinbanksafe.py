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

    description = "Assembly note: make sure you keep all of the circle cutouts from the doors, they are all needed as spacers or hinges."
    
    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "h")
        self.argparser.add_argument(
            "--slotlength", action="store", type=float, default=35,
            help="Length of the coin slot in mm")
        self.argparser.add_argument(
            "--slotwidth", action="store", type=float, default=5,
            help="Width of the coin slot in mm")
        self.argparser.add_argument(
            "--handlelength", action="store", type=float, default=6,
            help="Length of handle in multiples of thickness")
    
    def circleSquareHole(self, x, y, radius, variant=False):
        t = self.thickness
        with self.saved_context():
            self.rectangularHole(x, y, t, t)
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


    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        slot_length = self.slotlength
        slot_width = self.slotwidth

        handle_length = self.handlelength * t

        # lock parameters
        big_radius = 2.25 * t
        small_radius = 1.4 * t
        spacing = 1

        # side walls
        with self.saved_context():
            self.rectangularWall(x, h, "seFf", move="mirror right")
            self.rectangularWall(y, h, "sFFF", move="right")
            self.rectangularWall(x-2*t, h, "sfFh", ignore_widths=[3,4,7,8], move="mirror right")
            # locking bar
            with self.saved_context():
                self.moveTo(0, 4*t)
                self.rectangularWall(1.5*t, h, "eeef", move="right")
            self.rectangularWall(1.5*t, h, "eeef", move="right only")
            # door
            self.moveTo(1, 1+t*4)
            self.polyline(
                (y - 2.25*t), -90, t, 90, t, 90, t, -90, 1.25*t, 90,
                h, 90,
                1.25*t, -90, t, 90, t, 90, t, -90, (y - 2.25*t), 90,
                h, 90)
            num_dials = 3
            space_under_dials = 6*big_radius
            space_not_under_dials = h - space_under_dials
            dial_spacing = space_not_under_dials / (num_dials + 1)
            if dial_spacing < 1 :
                min_height = 6*big_radius + 4
                raise ValueError(f"With thickness {t}, h must be at least {min_height} to fit the dials.")

            self.circleSquareHole(3*t, h/2, 1.25 * t)
            self.circleSquareHole(3*t, h/2 - (2*big_radius + dial_spacing), 1.25 * t)
            self.circleSquareHole(3*t, h/2 + (2*big_radius + dial_spacing), 1.25 * t)
            self.rectangularHole(y/2, h/2, t, handle_length - 2.4*t)
            
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
            
            self.circleSquareHole(y - 1.75*t, 1.75*t, t)
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
            self.circleSquareHole(1.75*t, 1.75*t, t)
        self.rectangularWall(y, x, "efff", move="right only")

        # locks
        with self.saved_context():
            self.circleSquareHole(big_radius, big_radius, big_radius)
            self.moveTo(2 * big_radius + spacing, 0)
            self.circleSquareHole(big_radius, big_radius, big_radius)
            self.moveTo(2 * big_radius + spacing, 0)
            self.circleSquareHole(big_radius, big_radius, big_radius)
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
        self.moveTo(0.4*t,0)
        self.polyline(
            handle_length - 0.4*t,
            (90, 0.2*t),
            1.3 * t,
            90,
            1.2 * t,
            -90,
            t,
            90,
            handle_length - 2.4*t,
            90,
            t,
            -90,
            1.2 * t,
            90,
            1.3*t,
            (90, 0.2*t))
