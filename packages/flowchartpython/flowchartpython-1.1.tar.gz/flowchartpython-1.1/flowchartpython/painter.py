# Flowchart Python
# Copyright (C) 2006-2007  Joshua Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from math import sin, cos, tan, pi, atan2
import time

import pygame
import pygame.locals as pgl
import keyboard

bkgColour = (255, 255, 255)
bdrColour = (224, 224, 224)
blkColour = (192, 192, 255)
ifColour =  (192, 255, 192)
psColour =  (255, 255, 192)
defColour = (192, 255, 255)
tryColour = (255, 232, 192)
escColour = (240, 192, 255)
esrColour = (192,   0, 255)
selColour = (  0,   0, 224)
insColour = (255,   0, 255)

mPtColour = (128, 128, 255)
mSlColour = (128, 224, 255)
mHlColour = (  0, 255, 128)

trcColour = (255,   0, 255)
fTxColour = (  0,   0, 224)
vTxColour = (  0,   0,   0)
tx4Colour = (240, 240, 255)
tEsColour = (255, 240, 255)   # Loop escape root text background
csrColour = (  0,   0,   0)
cmtColour = (255, 255, 192)   # Comment background
rnbColour = (192, 192, 192)   # Route name background

resolution = 5
maxSegments = 96

ibeam_strings = (               #sized 8x16
      "ooo ooo ",
      "   o    ",
      "   o    ",
      "   o    ",
      "   o    ",
      "   o    ",
      "   o    ",
      "   o    ",
      "   o    ",
      "   o    ",
      "   o    ",
      "   o    ",
      "   o    ",
      "   o    ",
      "   o    ",
      "ooo ooo ")

repeatLag = 0.2
repeatRate = 0.05

class RectType(object):
    Boundary = (bdrColour, None, 1)
    Border = ((0,0,0), None, 2)
    Solid = ((0,0,0), blkColour, 1)
    Pass = ((0,0,0), psColour, 1)
    If = ((0,0,0), ifColour, 1)
    Def = ((0,0,0), defColour, 1)
    Try = ((0,0,0), tryColour, 2)
    Hole = ((0,0,0), bkgColour, 2)
    Escape = ((0,0,0), escColour, 1)
    Selected = (selColour, None, 3)
    Insert = (None, insColour, 1)

class Painter(object):
    zoomSpeed = 1.5
    panSpeed = 1.2

    def __init__(self, masterBlock, screen):
        self.masterBlock = masterBlock
        self.masterBlock.g_treeModified = True
        self.screenSize = screen.get_size()
        self.screen = pygame.Surface(self.screenSize)
        self.drawing = False

        # Default positioning.
        self.screenArea = 0.25 * self.screenSize[0] * self.screenSize[1]
        self.drawBlock = self.masterBlock   # Smallest encapsulating block.
        self.drawingPlacement = RelativePlacement(scale=0.667, shape=1.618,
                                                  pos=(self.screenSize[0]/2.,
                                                       self.screenSize[1]/2.),
                                                  area=1.618)

        self.cycle = 0
        self.updateTime = time.time()
        self.focusing = False

    def reset(self, masterBlock=None):
        'resets the view'
        if masterBlock:
            self.masterBlock = masterBlock
        self.masterBlock.g_treeModified = True

        # Default positioning.
        self.screenArea = 0.25 * self.screenSize[0] * self.screenSize[1]
        self.drawBlock = self.masterBlock   # Smallest encapsulating block.
        self.drawingPlacement = RelativePlacement(scale=0.667, shape=1.618,
                                                  pos=(self.screenSize[0]/2.,
                                                       self.screenSize[1]/2.),
                                                  area=1.618)

        self.focusing = False

    def drawChild(self, block, absPlacement):
        '''internal.
        area is (xy)_child
        shape is x_child / y_child

        absPlacement will become the block's g_absPlacement.
        '''
        block.g_cycle = self.cycle
        block.g_absPlacement = absPlacement

        # Check if this block encapsulates the screen.
        if self.checkDrawBlockCandidate(block):
            # Block is completely off the screen. Don't draw.
            return

        # Draw the border.
        block.g_border.draw(self.screen)

        # Check for size cutoff.
        if block.g_sizeCutoff != None and \
                   absPlacement.scale < block.g_sizeCutoff:
            for f in block.g_cutoffFeatures:
                f.draw(self.screen)
        else:
            # Draw the features.
            for f in block.g_features:
                f.draw(self.screen)

            # Draw the children.
            for ch in block.g_children:
                # Set new settings.
                newPlacement = absPlacement.add(ch.g_relPlacement,
                                                self.screenArea)

                self.drawChild(ch, newPlacement)

            # Draw the connections.
            for f in block.g_connections:
                f.draw(self.screen)
            for f in block.g_interactiveFeatures:
                f.draw(self.screen)

    def addFeature(self, feature):
        '''internal.
        Adds the specified interactive feature to the block's layout.'''
        # Add it.
        self.nodeStack[-1][2].append(feature)
        # Draw it.
        feature.draw(self)

    def lineIntersectsScreenEdge(self, p1, p2):
        '''internal.
        Tests whether the specified line segment intersects any of the edges
        of the screen.'''
        X, Y = self.screenSize

        # 1. Test for both off the same side.
        if (p1[0] < 0 and p2[0] < 0) or (p1[1] < 0 and p2[1] < 0):
            return False
        if (p1[0] > X and p2[0] > X) or (p1[1] > Y and p2[1] > Y):
            return False

        # 2. Test for intersecting top or bottom.
        if p1[1] != p2[1]:
            c = p2[0] - p2[1]*(p2[0]-p1[0]+0.)/(p2[1]-p1[1])
            if c > 0 and c < X:
                return True
            c = p2[0] - (p2[1]-Y)*(p2[0]-p1[0]+0.)/(p2[1]-p1[1])
            if c > 0 and c < X:
                return True

        # 3. Test for intersecting left or right.
        if p1[0] != p2[0]:
            c = p2[1] - p2[0]*(p2[1]-p1[1]+0.)/(p2[0]-p1[0])
            if c > 0 and c < Y:
                return True
            c = p2[1] - (p2[0]-X)*(p2[1]-p1[1]+0.)/(p2[0]-p1[0])
            if c > 0 and c < Y:
                return True

        return False

    def getLineScreenFlags(self, p1, p2):
        '''internal.
        Tests whether the specified line segment intersects any of the edges
        of the screen, and returns a set of flags indicating which sides of
        the screen they cross.'''
        X, Y = self.screenSize

        # 1. Test for both off the same side.
        if (p1[0] < 0 and p2[0] < 0):
            if (p1[1] > 0 and p1[1] < Y) or (p2[1] > 0 and p2[1] < Y):
                return set('L')     # Crosses left side.
            if (p1[1] < 0 and p2[1] > Y) or (p2[1] < 0 and p1[1] > Y):
                return set('L')
            return set()
        if (p1[1] < 0 and p2[1] < 0):
            if (p1[0] > 0 and p1[0] < X) or (p2[0] > 0 and p2[0] < X):
                return set('T')     # Crosses top.
            if (p1[0] < 0 and p2[0] > X) or (p2[0] < 0 and p1[0] > X):
                return set('T')
            return set()
        if (p1[0] > X and p2[0] > X):
            if (p1[1] > 0 and p1[1] < Y) or (p2[1] > 0 and p2[1] < Y):
                return set('R')     # Crosses right side.
            if (p1[1] < 0 and p2[1] > Y) or (p2[1] < 0 and p1[1] > Y):
                return set('R')
            return set()
        if (p1[1] > Y and p2[1] > Y):
            if (p1[0] > 0 and p1[0] < X) or (p2[0] > 0 and p2[0] < X):
                return set('B')     # Crosses bottom.
            if (p1[0] < 0 and p2[0] > X) or (p2[0] < 0 and p1[0] > X):
                return set('B')
            return set()

        # 2. Test for intersecting top or bottom.
        result = set()
        if p1[1] != p2[1]:
            c1 = p2[0] - p2[1]*(p2[0]-p1[0]+0.)/(p2[1]-p1[1])
            if c1 > 0 and c1 < X:
                return None
            c2 = p2[0] - (p2[1]-Y)*(p2[0]-p1[0]+0.)/(p2[1]-p1[1])
            if c2 > 0 and c2 < X:
                return None
            if c1 < 0 and c2 < 0:
                result.add('L')
            elif c1 > X and c2 > X:
                result.add('R')
            else:
                return None

        # 3. Test for intersecting left or right.
        if p1[0] != p2[0]:
            c1 = p2[1] - p2[0]*(p2[1]-p1[1]+0.)/(p2[0]-p1[0])
            if c1 > 0 and c1 < Y:
                return None
            c2 = p2[1] - (p2[0]-X)*(p2[1]-p1[1]+0.)/(p2[0]-p1[0])
            if c2 > 0 and c2 < Y:
                return None
            if c1 < 0 and c2 < 0:
                result.add('T')
            elif c1 > Y and c2 > Y:
                result.add('B')
            else:
                return None

        return result

    def checkDrawBlock(self):
        '''internal.
        Checks whether the current drawBlock does actually encapsulate the
        screen area, and fixes it if not.'''
        W, H = self.screenSize

        # We can't possibly look further out than the master block.
        if self.drawBlock == self.masterBlock:
            return

        shape = self.drawingPlacement.shape
        area = self.drawingPlacement.area
        width = (shape * area) ** 0.5
        height = (area / shape) ** 0.5
        pts = []
        for p in ((-width,height),(-width,-height),(width,-height),(width,height)):
            q = self.drawingPlacement.parentPoint(p, self.screenArea)
            pts.append(q)
            # Check if the point lies within the screen area.
            if q[0]>0 and q[0]<W and q[1]>0 and q[1]<H:
                break
        else:
            # Go through lines and check for intersection.
            for i in range(4):
                if self.lineIntersectsScreenEdge(pts[-i], pts[-i-1]):
                    break
            else:
                # Block encapsulates screen. No problem.
                return

        # Block does not encapsulate screen. Look at parent.
        if self.drawBlock.parent.g_nonDrawn:
            blockParent = self.drawBlock.parent.parent
        else:
            blockParent = self.drawBlock.parent

        # Check for errors.
        if not hasattr(blockParent, 'g_absPlacement'):
            self.reset()
            return

        newArea = blockParent.g_relPlacement.area
        newAngle = (self.drawingPlacement.angle - \
                    self.drawBlock.g_relPlacement.angle)%(2*pi)
        newShape = blockParent.g_relPlacement.shape
        newScale = self.drawingPlacement.scale / \
                   self.drawBlock.g_relPlacement.scale

        # It is important we get the scale right before calcing offset.
        blockParent.g_absPlacement.scale = newScale
        deltaPos = blockParent.g_absPlacement.parentDisplacement( \
                        self.drawBlock.g_relPlacement.pos, self.screenArea)
        newPos = [self.drawingPlacement.pos[i] - deltaPos[i] for i in (0,1)]

        self.drawingPlacement = RelativePlacement(pos=newPos, angle=newAngle, \
                                scale=newScale, shape=newShape, area=newArea)
        self.drawBlock = blockParent
        blockParent.g_absPlacement  = self.drawingPlacement

        self.masterBlock.g_treeModified = True

        # Recurse.
        self.checkDrawBlock()

    def checkDrawBlockCandidate(self, block):
        '''internal.
        Checks whether the block currently being drawn is a good candidate for
        being _the_ drawing block. If so updates the drawing block.
        Also returns True if the block is completely off the screen and false
        otherwise.'''

        if block is self.drawBlock:
            return

        W, H = self.screenSize

        shape = block.g_absPlacement.shape
        area = block.g_absPlacement.area
        width = (shape * area) ** 0.5
        height = (area / shape) ** 0.5
        pts = []
        for p in ((-width,height),(-width,-height),(width,-height),
                  (width,height)):
            q = block.g_absPlacement.parentPoint(p, self.screenArea)
            pts.append(q)

            # Check if the point lies within the screen area.
            if q[0]>0 and q[0]<W and q[1]>0 and q[1]<H:
                return False

        # Go through lines and check for intersection.
        flags = set()
        for i in range(4):
            r = self.getLineScreenFlags(pts[-i], pts[-i-1])
            if r == None:
                # Line intersects an edge.
                return False
            flags.update(r)

        # For this block to encapsulate the screen, we need all 4 flags.
        if len(flags) != 4:
            # Block is completely off the screen.
            return True

        # Block encapsulates screen. Remember.
        self.drawingPlacement = block.g_absPlacement
        self.drawBlock = block

        return False

    def maybeNav(self):
        '''internal.
        Checks if we need to zoom and pan the screen towards a target and if
        so, does it.'''

        # Get the time interval.
        t = time.time()
        dTime = t - self.updateTime
        self.updateTime = t
        dTime = 0.1

        # First check if we're moving the view.
        if self.focusing == 2:
            # Phase 1: zoom out till we get to an ancestor of the target.
            if self.drawBlock in self.focusTargets:
                # Phase is over. We've arrived.
                self.focusing = 3
                i = self.focusTargets.index(self.drawBlock)
                self.focusTargets = self.focusTargets[:i+1]
            else:
                # Do the zooming.
                self.zoom(8 ** (-self.zoomSpeed * dTime))
        elif self.focusing == 3:
            # Phase 2: zoom out and pan until this block's child is in view.

            # Check if we're there yet.
            try:
                b = self.focusTargets[-2]
            except IndexError:
                self.focusing = True
            else:
                # We stop when the child we're interested in is on screen.
                if b.g_cycle != self.cycle:
                    self.focusing = True
                else:
                    pt = b.g_absPlacement.parentPoint((0.,0.), self.screenArea)
                    if (0 < pt[0] < self.screenSize[0]) and \
                           (0 < pt[1] < self.screenSize[1]):
                        self.focusing = True

            if self.focusing == 3:
                pt = b.g_absPlacement.pos

                # Pan that block towards the screen centre.
                scC = [0.5*i for i in self.screenSize]

                # Zoom out
                relAmount = dTime * self.zoomSpeed
                relScale = 8 ** -relAmount
                self.zoom(relScale) #, tuple(scC[i]-pt[i] for i in (0,1)))
        elif self.focusing:
            # Phase 3: Focus on the correct block.

            # First check what's the smallest visible block.
            while len(self.focusTargets) > 1 and \
                  self.focusTargets[-2].g_cycle == self.cycle:
                self.focusTargets.pop()

            # Now pan and zoom the block towards the centre of the screen.
            pt = self.focusTargets[-1].g_absPlacement.pos
            finished = 0

            # Pan towards the screen centre.
            scC = [0.5*i for i in self.screenSize]
            dist = dTime * self.panSpeed * (self.screenArea ** 0.5)
            dPos = tuple(scC[i] - pt[i] for i in (0,1))
            targetDist = (dPos[0]**2 + dPos[1]**2) ** 0.5
            if dist < targetDist:
                # Doesn't reach the exact centre.
                ratio = dist / targetDist
                dPos = tuple(i * ratio for i in dPos)
            else:
                finished = 1
            self.pan(dPos)
            pt = tuple(pt[i] + dPos[i] for i in (0,1))

            # 2. Zoom component.
            sc = self.focusTargets[-1].g_absPlacement.scale
            relAmount = dTime * self.zoomSpeed
            if sc < 0.7:
                # Going in.
                relScale = 8 ** relAmount
                if sc * relScale >= 0.7:
                    relScale = 0.7 / sc
                    finished = finished + 1
            else:
                # Going out.
                relScale = 8 ** -relAmount
                if sc * relScale <= 0.7:
                    relScale = 0.7 / sc
                    finished = finished + 1
                pt = scC  # tuple(scC[i]-pt[i] for i in (0,1))
            self.zoom(relScale, pt)

            # Check if we're there yet.
            if finished >= 2 and len(self.focusTargets) == 1:
                self.focusing = False


    def draw(self):
        '''Draws the current view to the screen.'''

        if self.drawing:
            return

        self.maybeNav()

        # Check if it's been modified.
        if not self.masterBlock.g_treeModified:
            return

        self.drawing = True

        # Check if we need to reset the view.
        if self.drawBlock.master != self.masterBlock:
            self.reset()


        # Fill the background.
        self.screen.fill(bkgColour)

        # Make sure that everything's correctly laid out.
        self.drawBlock.g_nonDrawn = False
        self.drawBlock.g_draw()

        # Draw the block.
        self.cycle = (self.cycle + 1) % 2147000000
        self.drawChild(self.drawBlock, self.drawingPlacement)

        self.masterBlock.g_treeModified = False
        self.drawing = False

    def pan(self, amount):
        '''Pans the view by the specified amount.'''
        if self.drawing:
            return

        self.masterBlock.g_treeModified = True
        self.drawingPlacement.pos = [self.drawingPlacement.pos[i] + \
                                     amount[i] for i in (0,1)]
        self.checkDrawBlock()

    def zoom(self, relScale, centre=None):
        '''Zooms the view by the specified amount.'''
        if self.drawing:
            return

        self.drawingPlacement.scale = self.drawingPlacement.scale * relScale

        # Keep the screen centre fixed.
        if centre == None:
            centre = [0.5*i for i in self.screenSize]

        self.drawingPlacement.pos = [centre[i]+(self.drawingPlacement.pos[i]- \
                                centre[i])*(relScale ** 0.5) for i in (0,1)]

        self.checkDrawBlock()
        self.masterBlock.g_treeModified = True

    def navigate(self, point, amount):
        '''(point, amount) - Navigates the view as if the user had clicked on
        point and dragged the mouse by amount. Returns the new position of the
        point where the user clicked. Horizontal motion moves the point along
        the line joining the point to the centre of the screen. Vertical motion
        zooms towards or away from the point.'''

        if self.drawing:
            return

        # 1. Pan component.
        scC = [0.5*i for i in self.screenSize]
        if abs(point[1] - scC[1]) < 3 * abs(point[0] - scC[0]):
            dPos = (amount[0], amount[0] * (point[1] - scC[1]) / \
                    (point[0] - scC[0]))
            self.pan(dPos)
            point = tuple(point[i] + dPos[i] for i in (0,1))

        # 2. Zoom component.
        self.masterBlock.g_treeModified = True
        relAmount = amount[1] / (self.screenArea ** 0.5)
        relScale = 8 ** relAmount
        self.zoom(relScale, point)

        return point

    def focusView(self, block):
        '''(block) - starts the view moving towards the specified block.
        If the view is already moving, the view will jump instantly to the
        specified block.'''

        # If we're already moving, jump to the block.
        if self.focusing:
            scC = [0.5*i for i in self.screenSize]

            # Make sure that every intermediate block's been drawn right.
            b = block
            trail = []
            while b.g_cycle != self.cycle:
                trail.insert(0, b)
                b = b.parent
                if b.g_nonDrawn:
                    b = b.parent
            for b2 in trail:
                b2.g_absPlacement = b.g_absPlacement.add(b2.g_relPlacement,
                                                         self.screenArea)
                b = b2
            angle = block.g_absPlacement.angle

            # Jump to it.
            self.drawBlock = block
            self.drawingPlacement = RelativePlacement(scC, 0.7, \
                        block.g_relPlacement.shape, block.g_relPlacement.area, \
                        angle)
            self.masterBlock.g_treeModified = True

            self.focusing = False
        else:
            self.focusing = 2       # Indicates that we're zooming out.

            ft = []
            while True:
                if not block.g_nonDrawn:
                    ft.append(block)
                if block == self.masterBlock:
                    break
                block = block.parent
            self.focusTargets = ft

    def setFocusParent(self, block):
        '''internal.'''
        fp = []
        while True:
            fp.append(block)
            if block == self.masterBlock:
                break
            block = block.parent
        self.focusParents = fp

class RelativePlacement(object):
    __slots__ = ['pos', 'scale', 'shape', 'area', 'angle']
    # Area parameter controls internal scaling.
    def __init__(self, pos=(0.,0.), scale=1., shape=1.618, area=1., angle=0.):
        self.pos = pos
        self.scale = scale
        self.shape = shape
        self.area = area
        self.angle = angle

    def scaleToWidth(self):
        '''internal.
        Scales the drawer object so that the allowed drawing area is from
        (-1, -y) to (1, y) and returns y.'''

        self.area = 1. / self.shape
        return self.area

    def scaleToHeight(self):
        '''internal.
        Scales the drawer object so that the allowed drawing area is from
        (-x, -1) to (x, 1) and returns x.'''

        self.area = self.shape
        return self.area

    def scaleDesired(self, desiredShape):
        '''internal.
        Scales so that everything in (-desiredShape, -1.) to (desiredShape, 1.)
        is in the view.'''

        self.area = max(desiredShape**2 / self.shape, self.shape)

    def parentPoint(self, point, parentArea):
        '''Translates a point from this placement to a parent placement.'''
        u, v = point

        # Translate to offset from the parent's origin.
        m = (self.scale * parentArea / self.area) ** 0.5
        theta = self.angle
        U = self.pos[0] + m*(u*cos(theta) - v*sin(theta))
        V = self.pos[1] + m*(u*sin(theta) + v*cos(theta))

        return U, V

    def parentLength(self, x, parentArea):
        '''Tranlates a length from this placement to parent placement.'''
        m = (self.scale * parentArea / self.area) ** 0.5
        return m * x

    def parentDisplacement(self, s, parentArea):
        '''Tranlates a length from this placement to parent placement.'''
        u, v = s

        m = (self.scale * parentArea / self.area) ** 0.5
        theta = self.angle
        U = m*(u*cos(theta) - v*sin(theta))
        V = m*(+u*sin(theta) + v*cos(theta))
        return U, V

    def parentAngle(self, theta):
        '''Translates an angle from this placement to parent placement.'''
        return theta + self.angle

    def pointFromParent(self, point, parentArea):
        '''Translates a point from the parent placement to this one.'''

        # Translate to offset from this origin.
        X, Y = (point[i] - self.pos[i] for i in (0, 1))

        # Translate into local co-ordinates.
        m = (self.area / self.scale / parentArea) ** 0.5
        theta = self.angle
        u = m*(X*cos(theta) + Y*sin(theta))
        v = m*(-X*sin(theta) + Y*cos(theta))

        return u, v

    def add(self, other, parentArea):
        '''Combines the the two placements.'''
        angle = self.angle + other.angle
        area = other.area
        shape = other.shape
        scale = self.scale * other.scale
        pos = self.parentPoint(other.pos, parentArea)

        return RelativePlacement(pos=pos, scale=scale, shape=shape, area=area,
                                 angle=angle)

class Feature(object):
    '''Defines a feature of a block.'''
    interactive = False
    def draw(self, painter):
        '''Draws the feature.'''
        raise NotImplementedError

class InteractiveFeature(Feature):
    '''Defines an interactive feature of a block.'''
    interactive = True
    def checkMouseHover(self, point):
        '''Checks if the mouse is over this item and returns True or False
        accordingly.'''
        raise NotImplementedError

    def mouseHover(self, screen):
        '''Called when the mouse is over this item.'''
        raise NotImplementedError

    def mouseClick(self, actor):
        '''Performs the relevant action when the mouse is clicked over this
        item.'''
        raise NotImplementedError

class Rectangle(Feature):
    __slots__ = ['block', 'halfWidth', 'halfHeight', 'type', 'pt']
    def __init__(self, block, halfWidth, halfHeight, type=RectType.Boundary, \
                 pt=(0.,0.)):
        self.block = block
        self.halfWidth = halfWidth
        self.halfHeight = halfHeight
        self.type = type
        self.pt = pt

    def draw(self, screen):
        pl = self.block.g_absPlacement
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0] * scsz[1]

        halfWidth, halfHeight = self.halfWidth, self.halfHeight
        x0,y0 = self.pt
        x1,y1 = pl.parentPoint((x0-halfWidth, y0-halfHeight), scArea)
        x2,y2 = pl.parentPoint((x0+halfWidth, y0-halfHeight), scArea)
        x3,y3 = pl.parentPoint((x0+halfWidth, y0+halfHeight), scArea)
        x4,y4 = pl.parentPoint((x0-halfWidth, y0+halfHeight), scArea)
        polygon = [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]

        borderColour, fillColour, thickness = self.type

        if fillColour:
            pygame.draw.polygon(screen, fillColour, polygon)
        if borderColour:
            pygame.draw.polygon(screen, borderColour, polygon, thickness)

class Diamond(Feature):
    '''Draws a square diamond with semi-axis of size.'''
    __slots__ = ['block', 'pos', 'size']
    def __init__(self, block, pos, size):
        self.block = block
        self.pos = pos
        self.size = size

    def draw(self, screen):
        pl = self.block.g_absPlacement
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0]  * scsz[1]

        pos, size = self.pos, self.size
        x1,y1 = pl.parentPoint((pos[0], pos[1]-size), scArea)
        x2,y2 = pl.parentPoint((pos[0]+size, pos[1]), scArea)
        x3,y3 = pl.parentPoint((pos[0], pos[1]+size), scArea)
        x4,y4 = pl.parentPoint((pos[0]-size, pos[1]), scArea)
        polygon = [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]

        pygame.draw.polygon(screen, ifColour, polygon)
        pygame.draw.polygon(screen, (0,0,0), polygon, 1)

class Connection(Feature):
    '''Connects the two points.'''
    __slots__ = ['block', 'pos1', 'pos2', 'theta1', 'theta2', 'colour']
    def __init__(self, block, pos1, pos2, theta1=0., theta2=0., colour=(0,0,0)):
        self.block = block
        self.pos1 = pos1
        self.pos2 = pos2
        self.theta1 = theta1
        self.theta2 = theta2
        self.colour = colour

    def drawArc(self, pts, centre, radius, theta1, gamma, thickness):
        '''internal.
        Draws an arc with the given screen coordinates.'''
        hTh = min(thickness/2., abs(radius))

        # Calculate the arc length and how many pieces to chop it into.
        arcLen = abs(radius * gamma)
        n = min(int(arcLen / resolution) + 1, maxSegments)
        dGamma = gamma / n

        # Calculate a list of points.
        if radius * gamma > 0:
            r1 = radius + hTh
            r2 = radius - hTh
        else:
            r1 = radius - hTh
            r2 = radius + hTh

        theta = theta1
        for i in range(n+1):
            cosTheta = cos(theta)
            sinTheta = sin(theta)
            pts.append(   (centre[0] + r1*cosTheta, centre[1] + r1*sinTheta))
            pts.insert(0, (centre[0] + r2*cosTheta, centre[1] + r2*sinTheta))
            theta = theta + dGamma

    def draw(self, screen):
        '''Draws a smooth connecting line between the two points.'''
        pl = self.block.g_absPlacement
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0]  * scsz[1]

        pos1, pos2, theta1, theta2 = self.pos1, self.pos2, self.theta1, \
                                     self.theta2

        # Transform to screen coordinates.
        pos1 = pl.parentPoint(pos1, scArea)
        pos2 = pl.parentPoint(pos2, scArea)
        theta1 = pl.parentAngle(theta1)
        theta2 = pl.parentAngle(theta2)

        p1off = p2off = False
        # If both points are off the screen, don't draw.
        if not (pos1[0] > 0 < pos1[1] and pos1[0] < scsz[0] and \
                pos1[1] < scsz[1]):
            p1off = True
        if not (pos2[0] > 0 < pos2[1] and pos2[0] < scsz[0] and \
                pos2[1] < scsz[1]):
            p2off = True
        if p1off and p2off:
            return

        # Calculate line width.
        lw = min(3, int(4 * self.block.g_absPlacement.scale + 1))

        # Calculate projection length based on separation.
        pLen = 0.5 * ((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)**0.5

        wholeAngle = atan2(pos2[1]-pos1[1],pos2[0]-pos1[0])
        w1 = cos(theta1 - wholeAngle) ** 2 + 0.1
        w2 = cos(theta2 + pi - wholeAngle) ** 2 + 0.1
        W = w1 + w2
        pLen1 = pLen * w1 / W
        pLen2 = pLen * w2 / W

        # Project to find target points.
        pos1a = [pos1[0] + pLen1 * cos(theta1),
                 pos1[1] + pLen1 * sin(theta1)]
        pos2a = [pos2[0] - pLen2 * cos(theta2),
                 pos2[1] - pLen2 * sin(theta2)]

        # Find angle of second target point from first.
        alpha = atan2(pos2a[1]-pos1a[1],pos2a[0]-pos1a[0]) % (2*pi)

        # Projected along line between target points.
        pos1b = [pos1a[0] + pLen1 * cos(alpha),
                 pos1a[1] + pLen1 * sin(alpha)]
        pos2b = [pos2a[0] - pLen2 * cos(alpha),
                 pos2a[1] - pLen2 * sin(alpha)]

        # Find the angles between points at target points.
        phi1 = (theta1 - alpha) % (2*pi) - pi
        phi2 = (alpha - theta2) % (2*pi) - pi

        points = []
        # Firt curve - check for off-screen.
        if p1off and not (pos1b[0] > 0 < pos1b[1] and pos1b[0] < scsz[0] and \
                          pos1b[1] < scsz[1]):
            # Off-screen - add the mid-point.
            points.append((pos1b[0] + 0.5*lw*sin(theta1), \
                           pos1b[1] - 0.5*lw*cos(theta1)))
            points.insert(0, (pos1b[0] - 0.5*lw*sin(theta1), \
                              pos1b[1] + 0.5*lw*cos(theta1)))
        # Now check for straight.
        elif abs(phi1 % (2.*pi) - pi) < 0.1:
            # Straight - add the end-point.
            points.append((pos1[0] + 0.5*lw*sin(theta1), \
                           pos1[1] - 0.5*lw*cos(theta1)))
            points.insert(0, (pos1[0] - 0.5*lw*sin(theta1), \
                              pos1[1] + 0.5*lw*cos(theta1)))
        elif abs((phi1+pi) % (.2*pi) - pi) < 0.1:
            # Reverse - add the end-point upside down.
            points.append((pos1[0] - 0.5*lw*sin(theta1), \
                           pos1[1] + 0.5*lw*cos(theta1)))
            points.insert(0, (pos1[0] + 0.5*lw*sin(theta1), \
                              pos1[1] - 0.5*lw*cos(theta1)))
        else:
            # Calculate radius of curvature.
            r1 = pLen1 * tan(phi1 / 2.)

            # Calculate centre of curvature.
            c1 = [pos1[0] + r1 * cos(theta1 + pi/2.),
                  pos1[1] + r1 * sin(theta1 + pi/2.)]

            # Draw the curve.
            self.drawArc(points, c1, r1, theta1-pi/2., pi-phi1%(2*pi), lw)

        # Second curve - check for off-screen.
        if p2off and not (pos2b[0] > 0 < pos2b[1] and pos2b[0] < scsz[0] and \
                          pos2b[1] < scsz[1]):
            # Off-screen - add the mid-point.
            points.append((pos2b[0] + 0.5*lw*sin(theta2), \
                           pos2b[1] - 0.5*lw*cos(theta2)))
            points.insert(0, (pos2b[0] - 0.5*lw*sin(theta2), \
                              pos2b[1] + 0.5*lw*cos(theta2)))
        # Now check for straight.
        elif abs(phi2%(2.*pi) - pi) < 0.1:
            # Straight - add the end-point.
            points.append((pos2[0] + 0.5*lw*sin(theta2), \
                           pos2[1] - 0.5*lw*cos(theta2)))
            points.insert(0, (pos2[0] - 0.5*lw*sin(theta2), \
                              pos2[1] + 0.5*lw*cos(theta2)))
        elif abs((phi2+pi) % (2.*pi) - pi) < 0.1:
            # Reverse - add the end-point upside down.
            points.append((pos2[0] - 0.5*lw*sin(theta2), \
                           pos2[1] + 0.5*lw*cos(theta2)))
            points.insert(0, (pos2[0] + 0.5*lw*sin(theta2), \
                              pos2[1] - 0.5*lw*cos(theta2)))
        else:
            # Calculate radius of curvature.
            r2 = -pLen2 * tan(phi2 / 2.)

            # Calculate centre of curvature.
            c2 = [pos2[0] + r2 * cos(theta2 - pi/2.),
                  pos2[1] + r2 * sin(theta2 - pi/2.)]

            # Draw the curve.
            self.drawArc(points, c2, r2, theta2+phi2-pi/2., pi-phi2%(2*pi), lw)

        # Do the actual drawing.
        pygame.draw.polygon(screen, self.colour, points)

class EscapeRoute(Connection):
    def __init__(self, block, pos1, pos2, theta1, theta2 = -0.25*pi):
        '''Joins the two points as an escape route ONLY if both points are on
        the screen.'''
        super(EscapeRoute, self).__init__(block, pos1, pos2, theta1, \
                                          theta2=theta2, colour=esrColour)

    def draw(self, screen):
        pl = self.block.g_absPlacement
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0]  * scsz[1]

        sp1 = pl.parentPoint(self.pos1, scArea)
        sp2 = pl.parentPoint(self.pos2, scArea)
        if not (sp1[0] > 0 < sp2[0] and sp1[0] < scsz[0] > sp2[0] \
           and sp1[1] > 0 < sp2[1] and sp1[1] < scsz[1] > sp2[1]):
            return

        super(EscapeRoute, self).draw(screen)

class Text(Feature):
    __slots__ = ['block', 'text', 'pt', 'font', 'radius', 'bkgColour']
    def __init__(self, block, text, radius, pt=(0,0), bkgColour=None, \
                 font=None):
        '''Draws the specified text at the specified position.'''
        self.block = block
        self.text = text
        self.radius = radius
        self.pt = pt
        self.bkgColour = bkgColour

        if font == None:
            try:
                self.font = Text.defaultFont
            except:
                self.font = Text.defaultFont = pygame.font.Font(None, 24)
        else:
            self.font = font

    def draw(self, screen):
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0]  * scsz[1]

        # 1. Render the text.
        if self.bkgColour:
            surface = self.font.render(self.text, True, (0,0,0), \
                                       self.bkgColour).convert()
        else:
            surface = self.font.render(self.text, False, (0,0,0)).convert()
        sz = surface.get_size()

        # Don't draw it if it's too small.
        if 2. * sz[0] * sz[1] / scArea > self.block.g_absPlacement.scale:
            return

        # Find the position.
        pt = self.block.g_absPlacement.parentPoint(self.pt, scArea)
        r = self.block.g_absPlacement.parentLength(self.radius, scArea)

        # 3. Check if it needs to be scaled.
        self.sFactor = sFactor = 2. * r / sz[0]

        # Cutoff - don't draw.
        if sFactor > 0.3:
            # Scale it if needed.
            if sFactor < 1.:
                sz = [int(round(i * sFactor)) for i in sz]
                surface = pygame.transform.scale(surface, sz)

            # 4. Put the text.
            screen.blit(surface, [pt[i] - 0.5* sz[i] for i in (0,1)])

class EscapeText(Text):
    interactive = True
    def __init__(self, block, escapeBlock, radius, pt, font=None):
        super(EscapeText, self).__init__(block, '', radius, pt, tEsColour, font)
        self.escapeBlock = escapeBlock

    def draw(self, screen):
        # Update the text from the escape route.
        self.text = self.escapeBlock.comment
        super(EscapeText, self).draw(screen)

    def checkMouseHover(self, pt):
        return False

class Arrows(Feature):
    __slots__ = ['block', 'pts']
    def __init__(self, block, pts):
        '''Draws right-facing arrow heads at the specified points.'''
        self.block = block
        self.pts = pts

    def draw(self, screen):
        pl = self.block.g_absPlacement
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0]  * scsz[1]

        a = 0.07
        for x,y in self.pts:
            x1,y1 = pl.parentPoint((x-a, y-a), scArea)
            x2,y2 = pl.parentPoint((x,y), scArea)
            x3,y3 = pl.parentPoint((x-a,y+a), scArea)
            pygame.draw.polygon(screen, (0,0,0), [(x1,y1),(x2,y2), (x3,y3)])

class BlockBorder(Rectangle):
    '''Defines the border of a block.'''

    def __init__(self, block, halfWidth, halfHeight, pt = (0., 0.)):
        super(BlockBorder, self).__init__(block, halfWidth, halfHeight, pt=pt)
        self.hoverEdge = None
        self.hoverRange = (halfWidth * halfHeight / 161.8) ** 0.5
        self.highlightWidth = self.hoverRange / 6.

    def draw(self, screen):
        # Draw the bounding rectangle.
        super(BlockBorder, self).draw(screen)

        # Also draw any escapes passing through this block.
        escChilds = [ch for ch in self.block.g_children if \
                     len([e for e in ch.passingEscapes if \
                          e in self.block.passingEscapes])]

        if len(escChilds):
            if self.block.g_absPlacement.scale >= self.block.g_sizeCutoff:
                x0,y0 = self.pt
                pos2 = (x0+self.halfWidth, y0-self.halfHeight)

                # Create one escape route and reuse it.
                route = EscapeRoute(self.block, pos2, pos2, 0.)

                for ch in escChilds:
                    x0, y0 = ch.g_border.pt
                    pos1 = (x0+ch.g_border.halfWidth, y0-ch.g_border.halfHeight)
                    pl = ch.g_relPlacement
                    pos1 = pl.parentPoint(pos1, self.block.g_absPlacement.area)
                    ang = pl.parentAngle(-0.25 * pi)

                    route.pos1 = pos1
                    route.theta1 = ang
                    route.draw(screen)

        self.drawn = True

    def drawSelected(self, screen):
        self.type = RectType.Selected
        self.draw(screen)
        self.type = RectType.Boundary

    def pointWithin(self, point):
        '''(point) - Checks if the specified point lies within the border.'''
        return abs(point[0]) <= self.halfWidth and \
               abs(point[1]) <= self.halfHeight

    def checkMouseHover(self, point):
        '''(point, screen)'''

        if isinstance(self.block, sourceFile.MasterBlock):
            return False

        if not self.pointWithin(point):
            return False

        # Check the different borders.
        if point[1] + self.halfHeight < self.hoverRange:
            self.hoverEdge = 0
            return True
        if point[1] - self.halfHeight > -self.hoverRange:
            self.hoverEdge = 1
            return True
        if point[0] + self.halfWidth < self.hoverRange:
            self.hoverEdge = 2
            return True
        if point[0] - self.halfWidth > -self.hoverRange:
            self.hoverEdge = 3
            return True
        return False

    def mouseHover(self, screen):
        hd = self.highlightWidth
        if self.hoverEdge == 0:
            Rectangle(self.block, self.halfWidth, hd, \
                      RectType.Insert, (0., -self.halfHeight+hd)).draw(screen)
        elif self.hoverEdge == 1:
            Rectangle(self.block, self.halfWidth, hd, \
                      RectType.Insert, (0., self.halfHeight-hd)).draw(screen)
        elif self.hoverEdge == 2:
            Rectangle(self.block, hd, self.halfHeight, \
                      RectType.Insert, (-self.halfWidth+hd, 0.)).draw(screen)
        elif self.hoverEdge == 3:
            Rectangle(self.block, hd, self.halfHeight, \
                      RectType.Insert, (self.halfWidth-hd, 0.)).draw(screen)

    def mouseClick(self, actor):
        # Set the mode.
        actor.setMode(SysMode.Standard)

        # Set the selection.
        actor.setSelection(self.block)

        # Insert a new block.
        if self.hoverEdge == 0:
            actor.insertPar(False)
        elif self.hoverEdge == 1:
            actor.insertPar(True)
        elif self.hoverEdge == 2:
            actor.insertSeq(False)
        elif self.hoverEdge == 3:
            actor.insertSeq(True)

class MapFeature(InteractiveFeature):
    pathColours = ((  0,   0, 128),
                   (  0, 128,   0),
                   (128,   0,   0),
                   (  0, 128, 128),
                   (128,   0, 128),
                   (128, 128,   0),
                   (  0,  64, 128),
                   ( 64, 128,   0),
                   (128,   0,  64),
                   (  0, 128,  64),
                   (128,  64,   0),
                   ( 64,   0, 128))

    def __init__(self, block, ht, inputs, outputs, mapping):
        if len(inputs) != mapping.numInputs:
            raise ValueError, 'mapping and inputs have different sizes'
        elif len(outputs) != mapping.numOutputs:
            raise ValueError, 'mapping and outputs have different sizes'

        self.block = block
        self.inputs = inputs
        self.outputs = outputs
        self.mapping = mapping
        self.height = ht

        self.highlight = [True, 0]
        self.selected = None
        self.hideHighlight = False
        self.hoverIn = None
        self.radius = 0.15 *self.height/max(len(self.inputs),len(self.outputs))

    def draw(self, screen):
        pl = self.block.g_absPlacement
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0]  * scsz[1]

        self.radius = self.height*(0.03 + 0.05 / max(len(self.inputs), \
                                                     len(self.outputs)))
        r = int(round(pl.parentLength(self.radius, scArea)))

        # Draw the connections.
        clrIndex = 0
        for i in range(len(self.mapping)):
            j = self.mapping[i]
            p1, a1 = self.inputs[i]
            p2, a2 = self.outputs[j]
            c = Connection(self.block, p1, p2, a1, a2, self.pathColours[clrIndex])
            c.draw(screen)

            clrIndex = (clrIndex + 1) % len(self.pathColours)

        # Draw the input circles.
        for pt, angle in self.inputs:
            pt = tuple(int(i) for i in pl.parentPoint(pt, scArea))
            pygame.draw.circle(screen, mPtColour, pt, r)

        # Draw the output circles.
        for pt, angle in self.outputs:
            pt = tuple(int(i) for i in pl.parentPoint(pt, scArea))
            pygame.draw.circle(screen, mPtColour, pt, r)

    def checkMouseHover(self, pos):
        r2 = self.radius ** 2

        # Check for hover over input circles.
        self.hoverIn = True
        for i in range(len(self.inputs)):
            pt, angle = self.inputs[i]
            if sum((pos[i] - pt[i]) ** 2 for i in (0,1)) <= r2 * 1.6:
                self.hoverIndex = i
                return True

        # Check for hover over output circles.
        self.hoverIn = False
        for i in range(len(self.outputs)):
            pt, angle = self.outputs[i]
            if sum((pos[i] - pt[i]) ** 2 for i in (0,1)) <= r2 * 1.6:
                self.hoverIndex = i
                return True

        self.hoverIn = None
        return False

    def mouseHover(self, screen):
        pl = self.block.g_absPlacement
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0]  * scsz[1]

        r = int(round(pl.parentLength(self.radius, scArea)))

        if self.hoverIn:
            # Highlight an input circle.
            pt, angle = self.inputs[self.hoverIndex]
        else:
            # Highlight an output circle.
            pt, angle = self.outputs[self.hoverIndex]

        pt = tuple(int(i) for i in pl.parentPoint(pt, scArea))
        pygame.draw.circle(screen, mHlColour, pt, r)

        # Hide the keyboard highlight.
        self.hideHighlight = True

    def mouseClick(self, actor):
        # Make sure that this mapping's selected.
        actor.mapClick(self)

        # Process the click.
        oldHighlight = self.highlight
        self.highlight = [self.hoverIn, self.hoverIndex]
        if self.select():
            actor.masterBlock.g_treeModified = True
        self.highlight = oldHighlight

    def enter(self, leftSide):
        '''Called when the mapping is entered in mapping mode.'''
        self.highlight[0] = leftSide
        self.selected = None
        if not self.fixHighlight():
            self.highlight[0] = not leftSide
            self.fixHighlight()

    def fixHighlight(self):
        'internal.'
        if self.highlight[0]:
            if len(self.inputs) == 0:
                return False
            self.highlight[1] = min(self.highlight[1], len(self.inputs)-1)
        else:
            self.highlight[1] = min(self.highlight[1], len(self.outputs)-1)

        return True

    def drawSelected(self, screen):
        '''Called when the mapping is selected to draw selection.'''
        pl = self.block.g_absPlacement
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0]  * scsz[1]

        r = int(round(pl.parentLength(self.radius, scArea)))

        # Calculate highlight.
        leftSide1, index = self.highlight
        if leftSide1:
            # Highlight an input circle.
            pt1, angle = self.inputs[index]
        else:
            # Highlight an output circle.
            pt1, angle = self.outputs[index]
        pt1 = tuple(int(i) for i in pl.parentPoint(pt1, scArea))

        if self.selected:
            # Calculate selection
            leftSide2, index = self.selected
            if leftSide2:
                # Highlight an input circle.
                pt2, angle = self.inputs[index]
            else:
                # Highlight an output circle.
                pt2, angle = self.outputs[index]

            pt2 = tuple(int(i) for i in pl.parentPoint(pt2, scArea))

            # Check for mouse-hovering line.
            if self.hoverIn != None:
                if self.hoverIn:
                    pt3, angle = self.inputs[self.hoverIndex]
                else:
                    pt3, angle = self.outputs[self.hoverIndex]
                pt3 = tuple(int(i) for i in pl.parentPoint(pt3, scArea))
                leftSide1 = self.hoverIn
            else:
                pt3 = pt1
                if self.hideHighlight:
                    leftSide1 = leftSide2

            # Check for necessity of joining line.
            if leftSide1 != leftSide2:
                # Join two points with a line.
                pygame.draw.line(screen, trcColour, pt3, pt2)

            # Actually draw selection.
            pygame.draw.circle(screen, mSlColour, pt2, r)

        # Actually draw highlight.
        if not self.hideHighlight:
            pygame.draw.circle(screen, mHlColour, pt1, r)

    def up(self):
        if self.highlight[1] > 0:
            self.highlight[1] = self.highlight[1] - 1
        self.hideHighlight = False

    def down(self):
        self.highlight[1] = self.highlight[1] + 1
        self.fixHighlight()
        self.hideHighlight = False

    def left(self):
        self.hideHighlight = False
        if self.highlight[0]:
            return False
        else:
            self.highlight[0] = True
            if not self.fixHighlight():
                return False
        return True

    def right(self):
        self.hideHighlight = False
        if self.highlight[0]:
            self.highlight[0] = False
            self.fixHighlight()
            return True
        return False

    def select(self):
        'Returns True if the block has changed.'
        if self.selected and self.selected[0] != self.highlight[0]:
            # Connect the points.
            if self.selected[0]:
                i,j = self.selected[1], self.highlight[1]
                self.selected = None
            else:
                j,i = self.selected[1], self.highlight[1]

            self.mapping.connections[i] = j
            return True
        else:
            self.selected = list(self.highlight)
            return False

    def cancel(self):
        'Returns True if the cancel has been processed.'
        if self.selected:
            self.selected = None
            return True
        return False

class InteractiveText(InteractiveFeature):
    def __init__(self, block, pretext, posttext, values, radius, callback, \
                 pt=(0.,0.), bkgColour=None, font=None):
        '''(block, pretext, posttext, values, radius, callback, point, font)
        - defines an interactive text element.

        block:      the block to which this element belongs.
        pretext:    a list of fixed text strings which will appear at the start
                    of each line of text.
        posttext:   a list of fixed text strings which will appear at the end
                    of each line of text.
        values:     a list of the editable pieces of text, which is wedged
                    between the pretext and posttext of each line.
        radius:     the radius of the circle within which the entire feature
                    must remain.
        callback:   a callback function which will be called with the values
                    list as its argument when the text changes. Can also be
                    a tuple containing a callback function and a list, in
                    which case, fn(values, *list) is called.
        pt:         the position of the text. Defaults to (0,0).
        bkgColour:  if specified, fills in the area behind the text with the
                    given colour.
        '''
        self.block = block
        self.pretext = pretext
        self.posttext = posttext
        self.values = list(values)
        self.callback = callback
        self.pt = pt
        self.radius = radius
        self.bkgColour = bkgColour
        self.textSz = None

        assert len(values) == len(pretext) == len(posttext)

        self.cursorPos = [0, 0]
        self.selStart = 0
        self.selLength = 0
        self.highlightMotion = False
        self.keyEvent = None

        if font == None:
            try:
                self.font = Text.defaultFont
            except AttributeError:
                self.font = Text.defaultFont = pygame.font.Font(None, 24)
        else:
            self.font = font

        try:
            InteractiveText.cursor
        except AttributeError:
            InteractiveText.cursor = ((len(ibeam_strings[0]),len(ibeam_strings)),\
                                      (3, 7)) + \
                                      pygame.cursors.compile(ibeam_strings)

    def tick(self):
        if self.keyEvent:
            # Repeated keypress processing.
            if time.time() >= self.repeatTime:
                self.processKeystroke(self.keyEvent)
                self.repeatTime = time.time() + repeatRate
                self.block.g_treeModified = True

    def draw(self, screen):
        scsz = screen.get_size()
        self.scArea = scArea = 0.25 * scsz[0]  * scsz[1]

        # 1. Render the text.
        lineSize = self.font.get_linesize()
        height = width = 0
        surfaces = []
        for i in range(len(self.values)):
            s1 = self.font.render(self.pretext[i], False, fTxColour).convert()
            s2 = self.font.render(self.values[i], False, vTxColour).convert()
            s3 = self.font.render(self.posttext[i], False, fTxColour).convert()

            surfaces.append((s1,s2,s3))
            height = height + lineSize
            width = max(width, s1.get_width()+s2.get_width()+s3.get_width())
            lastHeight = max(s1.get_height(), s2.get_height(), s3.get_height())

        # Adjust for hanging characters in the last line.
        if lastHeight > lineSize:
            height = height + lastHeight - lineSize

        # 2. Piece it all together.
        surface = pygame.Surface((width, height)).convert()
        if self.bkgColour:
            surface.fill(self.bkgColour)
        else:
            surface.fill(bkgColour)
            surface.set_colorkey(bkgColour)
        y = 0.
        for s1,s2,s3 in surfaces:
            x1,x2,x3 = (s.get_width() for s in (s1,s2,s3))
            x = 0.5 * (width - x1 - x2 - x3)
            surface.blit(s1, (x, y))
            x = x + x1
            surface.blit(s2, (x, y))
            x = x + x2
            surface.blit(s3, (x, y))
            y = y + lineSize

        # Find the position.
        pt = self.block.g_absPlacement.parentPoint(self.pt, scArea)
        r = self.block.g_absPlacement.parentLength(self.radius, scArea)

        # 3. Check if it needs to be scaled.
        self.sFactor = sFactor = 2. * r / (width ** 2 + height ** 2) ** 0.5

        # Cutoff - don't draw.
        if sFactor > 0.3:
            # Scale it if needed.
            if sFactor < 1.:
                width = int(round(width * sFactor))
                height = int(round(height * sFactor))
                surface = pygame.transform.scale(surface, (width, height))

            # 4. Put the text.
            putPos = (pt[0] - 0.5*width, pt[1] - 0.5*height)
            screen.blit(surface, putPos)
            self.textSz = (0.5*width, 0.5*height)

            # Draw a fine border.
            pygame.draw.rect(screen, bdrColour, \
                             pygame.Rect(putPos, (width, height)), 1)
        else:
            self.textSz = None

    def drawFinding(self, screen):
        '''Draws this block when the cursors resting on it but it hasn't yet
        been entered.'''
        if self.textSz == None:
            return

        pl = self.block.g_absPlacement
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0] * scsz[1]

        halfWidth, halfHeight = self.textSz
        x0,y0 = pl.parentPoint(self.pt, scArea)
        x1,y1 = (x0-halfWidth, y0-halfHeight)
        x2,y2 = (x0+halfWidth, y0-halfHeight)
        x3,y3 = (x0+halfWidth, y0+halfHeight)
        x4,y4 = (x0-halfWidth, y0+halfHeight)
        polygon = [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]

        borderColour, fillColour, thickness = RectType.Selected

        if fillColour:
            pygame.draw.polygon(screen, fillColour, polygon)
        if borderColour:
            pygame.draw.polygon(screen, borderColour, polygon, thickness)

    def drawSelected(self, screen):
        if self.textSz == None:
            return

        pl = self.block.g_absPlacement
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0] * scsz[1]
        x0, y0 = pl.parentPoint(self.pt, scArea)

        # Choose the appropriate line.
        n, m = self.cursorPos
        lineSize = self.font.get_linesize()
        y = lineSize * n

        if self.selLength != 0:
            m = self.selStart

        # Get the sizes of the different sections.
        s1 = self.font.size(self.pretext[n])[0]
        s2a = self.font.size(self.values[n][:m])[0]
        s2b = self.font.size(self.values[n][m:])[0]
        s3 = self.font.size(self.posttext[n])[0]

        # Draw a cursor line.
        x = 0.5 * (s1 + s2a - s2b - s3)
        if self.sFactor < 1.:
            x = x * self.sFactor
            y = y * self.sFactor
            lineSize = lineSize * self.sFactor

        pt0 = (x0 + x, y0 - self.textSz[1] + y)

        if self.selLength == 0:
            pt1 = (x0 + x, y0 - self.textSz[1] + y + lineSize)
            pygame.draw.line(screen, csrColour, pt0, pt1)
        else:
            # Create a surface of the selected text.
            m2 = m + self.selLength
            s = self.font.render(self.values[n][m:m2], False, \
                                 tuple(255-i for i in csrColour), csrColour)
            s.set_colorkey(None)

            if self.sFactor < 1.:
                width, height = s.get_size()
                width = int(round(width * self.sFactor))
                height = int(round(height * self.sFactor))
                s = pygame.transform.scale(s, (width, height))
            screen.blit(s, pt0)

    def checkMouseHover(self, pos):
        # Check for text not showing.
        if self.textSz == None:
            return False

        # Now check for hover over text.
        mPt = self.block.g_absPlacement.parentPoint(pos, self.scArea)
        tPt = self.block.g_absPlacement.parentPoint(self.pt, self.scArea)

        if tPt[0] - self.textSz[0] < mPt[0] < tPt[0] + self.textSz[0]:
            if tPt[1] - self.textSz[1] < mPt[1] < tPt[1] + self.textSz[1]:
                self.hoverPos = mPt
                return True
        return False

    def mouseHover(self, screen):
        # Do nothing special on a hover.
        pass

    def mouseClick(self, actor):
        # Make sure that this text's selected.
        actor.txtClick(self)

        # Set the cursor position.
        self.highlightMotion = False
        self.moveCursor(self.getClickPoint(self.hoverPos))

    def mouseDrag(self, event):
        self.highlightMotion = True
        self.moveCursor(self.getClickPoint(event.pos))

    def getClickPoint(self, point):
        '''internal. Returns the coordinates of the specified screen position.
        '''

        pl = self.block.g_absPlacement
        x0, y0 = pl.parentPoint(self.pt, self.scArea)

        # First find the correct row for the cursor.
        x = point[0] - x0
        y = point[1] - y0 + self.textSz[1]

        lineSize = self.font.get_linesize()
        if self.sFactor < 1.:
            lineSize = lineSize * self.sFactor
            x = x / self.sFactor

        if self.highlightMotion:
            n = self.cursorPos[0]
        else:
            n = min(int(y // lineSize), len(self.values) - 1)

        # Now find the correct column.
        s1 = self.font.size(self.pretext[n])[0]
        s2 = self.font.size(self.values[n])[0]
        s3 = self.font.size(self.posttext[n])[0]

        # 1. Guess the position.
        if x <= 0.5 * (s1 - s2 - s3):
            m = 0
        elif x >= 0.5 * (s1 + s2 - s3):
            m = len(self.values[n])
        else:
            dist = (0.5*(s2 + s3 - s1) + x)
            m = int(round(len(self.values[n]) * dist / s2))

            # 2. Refine the guess.
            gDist = self.font.size(self.values[n][:m])[0]

            if gDist < dist:
                # We guessed too low.
                while gDist < dist:
                    diff = dist - gDist
                    m = m + 1
                    gDist = self.font.size(self.values[n][:m])[0]

                # We found the turning point.
                if diff < gDist - dist:
                    m = m - 1
            elif gDist > dist:
                # We guessed too high.
                while gDist > dist:
                    diff = gDist - dist
                    m = m - 1
                    gDist = self.font.size(self.values[n][:m])[0]

                # Found the turning point.
                if diff < dist - gDist:
                    m = m + 1

        # 3. Return the value.
        return [n, m]

    def moveCursor(self, pt):
        'internal. Moves the cursor within a row.'
        newY, newX = pt
        if newY != self.cursorPos[0]:
            self.cursorPos = pt
            self.selLength = 0
        elif not self.highlightMotion:
            self.cursorPos[1] = newX
            self.selLength = 0
        else:
            if not self.selLength:
                selEnd = self.cursorPos[1]
            elif self.selStart == self.cursorPos[1]:
                selEnd = self.selStart + self.selLength
            else:
                selEnd = self.selStart

            if newX < selEnd:
                self.selLength = selEnd - newX
                self.selStart = newX
            else:
                self.selLength = newX - selEnd
                self.selStart = selEnd

            self.cursorPos[1] = newX

        self.block.master.g_treeModified = True

    def blankSelection(self):
        'internal. Blanks the selection. Returns True if there was one.'
        if not self.selLength:
            return False
        n,m = self.cursorPos[0], self.selStart
        self.values[n] = self.values[n][:m] + self.values[n][m+self.selLength:]
        self.selLength = 0
        self.cursorPos[1] = self.selStart
        return True

    def keyUp(self, event, actor):
        'internal. A key has been released.'
        if self.keyEvent and event.key == self.keyEvent.key:
            self.keyEvent = None

    def keyPress(self, event, actor):
        'internal. A key has been pressed.'
        self.keyEvent = event
        self.actor = actor
        self.processKeystroke(event)
        self.repeatTime = time.time() + repeatLag

    def processKeystroke(self, event):
        'internal. Process a keystroke.'

        char = keyboard.charPressed(event.key, event.mod)
        if isinstance(char, str):
            # Translates to a char.
            self.blankSelection()
            n,m = self.cursorPos
            self.values[n] = self.values[n][:m] + char + \
                             self.values[n][m:]
            self.cursorPos[1] = m + 1
        else:
            key, mod = char
            self.highlightMotion = mod & pgl.KMOD_SHIFT
            mod = mod & ~ pgl.KMOD_SHIFT
            n,m = self.cursorPos

            if mod == 0:
                if key == keyboard.Return:
                    # Enter.
                    self.actor.txtDone()
                elif key == keyboard.Left:
                    # Left arrow.
                    self.moveCursor([n, max(0, m - 1)])
                elif key == keyboard.Right:
                    # Right arrow.
                    self.moveCursor([n, min(m + 1, len(self.values[n]))])
                elif key == keyboard.Up:
                    # Up arrow.
                    self.cursorPos[0] = max(0, n - 1)
                    self.cursorPos[1] = min(self.cursorPos[1],
                                            len(self.values[self.cursorPos[0]]))
                    self.selLength = 0
                elif key == keyboard.Down:
                    # Down arrow.
                    self.cursorPos[0] = min(n + 1, len(self.values) - 1)
                    self.cursorPos[1] = min(self.cursorPos[1],
                                            len(self.values[self.cursorPos[0]]))
                    self.selLength = 0
                elif key == keyboard.Home:
                    # Home key.
                    self.moveCursor([n, 0])
                elif key == keyboard.End:
                    # End key.
                    self.moveCursor([n, len(self.values[n])])
                elif key == keyboard.Backspace:
                    # Backspace.
                    if not self.blankSelection():
                        n,m = self.cursorPos
                        if m > 0:
                            self.values[n] = self.values[n][:m-1] + self.values[n][m:]
                            self.cursorPos[1] = m - 1
                        else:
                            return
                elif key == keyboard.Delete:
                    # Delete.
                    if not self.blankSelection():
                        n,m = self.cursorPos
                        if m < len(self.values[n]):
                            self.values[n] = self.values[n][:m] + \
                                             self.values[n][m+1:]
                        else:
                            return
                else:
                    return
            elif mod == pgl.KMOD_LCTRL:
                if key == keyboard.Left:
                    # Move left one word.
                    n1, m1 = n, m
                    wordStarted = False
                    while True:
                        if m1 == 0:
                            if n1 == 0:
                                break
                            n1 = n1 - 1
                            m1 = len(self.values[n1]) - 1
                        else:
                            m1 = m1 - 1
                        if self.values[n1][m1] == ' ':
                            if wordStarted:
                                break
                        else:
                            wordStarted = True

                        n, m = n1, m1
                    self.moveCursor([n, m])
                elif key == keyboard.Right:
                    # Move right one word.
                    n1, m1 = n, m
                    wordStarted = False
                    while True:
                        if m1 == len(self.values[n1]) - 1:
                            if n1 == len(self.values) - 1:
                                break
                            n1 = n1 + 1
                            m1 = 0
                        else:
                            m1 = m1 + 1
                        if self.values[n1][m1] == ' ':
                            if wordStarted:
                                break
                        else:
                            wordStarted = True
                        n, m = n1, m1
                    self.moveCursor([n, m + 1])
                elif key == keyboard.Home:
                    # Move to the top of the feature.
                    self.moveCursor([0, 0])
                elif key == keyboard.End:
                    # Move to the end of the feature.
                    self.moveCursor([len(self.values)-1,
                                     len(self.values[-1])])
                else:
                    return
            else:
                return

        self.block.master.g_treeModified = True

    def setValues(self, values):
        self.values = values

        n, m = self.cursorPos
        if n > len(self.values):
            n = len(self.values)
        if m > len(self.values[n]):
            m = 0
        self.cursorPos = [n, m]

    def save(self):
        'Calls the notify function about the changes.'
        if isinstance(self.callback, tuple):
            fn, args = self.callback
            fn(self.values, *args)
        else:
            self.callback(self.values)

        self.block.master.g_treeModified = True

        n,m = self.cursorPos
        if m > len(self.values[n]):
            self.cursorPos[1] = 0

        self.keyEvent = None

    def beginEdit(self):
        'Called when this element\'s first entered.'
        # Select the whole first line of text.
        self.cursorPos = [0, 0]
        self.selStart = 0
        self.selLength = len(self.values[0])

class MultilineText(InteractiveFeature):
    def __init__(self, block, values, radius, callback, \
                 pt=(0.,0.), bkgColour=None, minWrapWidth=150, \
                 followText='', font=None):
        '''(block, values, radius, callback, point, font)
        - defines a multiline text element.

        block:      the block to which this element belongs.
        values:     a list of the lines of text.
        radius:     the radius of the circle within which the entire feature
                    must remain.
        callback:   a callback function which will be called with the values
                    list as its argument when the text changes. May also be
                    a tuple of the form (fn, args), in which case the callback
                    will execute fn(values, *args).
        pt:         the position of the text. Defaults to (0,0).
        bkgColour:  if specified, fills in the area behind the text with the
                    given colour.
        minWrapWidth: the minimum width to which text will be wrapped in
                    pixels.
        followText: a string of text to put at the start of any wrapped line.
        '''
        self.block = block
        self.values = list(values)
        self.callback = callback
        self.pt = pt
        self.radius = radius
        self.bkgColour = bkgColour
        self.textSz = None
        self.minWrapWidth = minWrapWidth

        self.cursorPos = [0, 0]
        self.selStart = [0, 0]
        self.selLength = 0
        self.selLines = 0

        self.highlightMotion = False
        self.keyEvent = None

        if font == None:
            try:
                self.font = Text.defaultFont
            except AttributeError:
                self.font = Text.defaultFont = pygame.font.Font(None, 24)
        else:
            self.font = font

        self.followText = followText
        self.followSurface = self.font.render(followText, False, fTxColour)
        self.followWidth = self.followSurface.get_width()
        self.screenWidth = 1024
        self.wordWrap()

        try:
            MultilineText.cursor
        except AttributeError:
            try:
                InteractiveText.cursor
            except AttributeError:
                InteractiveText.cursor = ((len(ibeam_strings[0]),len(ibeam_strings)),\
                                          (3, 7)) + \
                                          pygame.cursors.compile(ibeam_strings)
            MultilineText.cursor = InteractiveText.cursor

    def wordWrap(self):
        'Recalculates the position of line breaks due to word wrapping.'

        # Find the height and width of the non-wrapped text.
        # Take into account a minimum wrap width.
        lineSize = self.font.get_linesize()
        numValues = len(self.values)
        assert len(self.values) > 0
        small = max(lineSize * numValues, self.minWrapWidth)
        big = min(max(self.font.size(l)[0] for l in self.values), \
                  self.screenWidth)

        if small >= big:
            # Height is greater than width. Line wrapping to maximum width.
            self.wrappedLines, self.lines = self.wrapToWidth(self.screenWidth)
            return

        # 5 iterations of algorithm.
        for n in range(5):
            a = (big * small) ** 0.5
            wrappedLines, lines = self.wrapToWidth(a)
            b = lineSize * (len(wrappedLines) + numValues)

            # Update our big and small guesses.
            if a > b:
                big = min(a, big)
                small = max(b, small)
            else:
                big = min(b, big)
                small = max(a, small)

            if small >= big:
                break

        self.wrappedLines = wrappedLines
        self.lines = lines

    def wrapToWidth(self, width):
        '''Wraps the line breaks to a maximum line width of width.
        Returns (wrappedLines, lines) where lines is a list lines with this
        wrapping, and wrappedLines is a list of which lines terminate in
        artificial line breaks.'''

        i = 0
        follow = 0
        lines = list(self.values)
        wrappedLines = []
        while i < len(lines):
            l = lines[i]

            lWidth = self.font.size(l)[0] + follow
            if lWidth < width:
                # No splitting required.
                i = i + 1
                follow = 0
                continue

            # Guess where to split the line.
            m = int(round(width * len(l) / lWidth))

            # Move until we hit the right point.
            lWidth = self.font.size(l[:m])[0] + follow
            if lWidth >= width:
                while lWidth > width:
                    m = m - 1
                    lWidth = self.font.size(l[:m])[0] + follow
            else:
                lWidth = self.font.size(l[:m+1])[0] + follow
                while lWidth < width:
                    m = m + 1
                    lWidth = self.font.size(l[:m+1])[0] + follow

            startM = max(1, m)

            # Now count backwards until we hit a space.
            while m > 0:
                if l[m-1] == ' ':
                    # Found the right point. Split here.
                    break
                m = m - 1
            else:
                # Run out of line. Split where we thought at first.
                m = startM

            # Perform split.
            wrappedLines.append(i)
            lines.insert(i+1, l[m:])
            lines[i] = l[:m]
            follow = self.followWidth
            i = i + 1

        # Return the result.
        return wrappedLines, lines

    def screenPos(self, pt):
        '''internal. Convert from actual co-ordinates to displayed co-ordinates
        based on word wrap positions.'''

        n,m = pt

        # Get vertical position.
        for i in self.wrappedLines:
            if i == n:
                # Get horizontal position.
                if m <= len(self.lines[n]):
                    break
                m = m - len(self.lines[n])
            elif i > n:
                break
            n = n + 1

        return [n, m]

    def actualPos(self, pt):
        '''internal. Convert from displayed co-ordinates to actual co-ordinates
        based on word wrap.'''

        n, m = pt
        if n == 0:
            return [n, m]

        # Get horizontal position.
        x = n - 1
        while x >= 0:
            if x not in self.wrappedLines:
                break
            m = m + len(self.lines[x])
            x = x - 1

        # Get vertical position.
        x = n
        for i in self.wrappedLines:
            if i >= x:
                break
            n = n - 1

        return [n, m]

    def tick(self):
        if self.keyEvent:
            # Repeated keypress processing.
            if time.time() >= self.repeatTime:
                self.processKeystroke(self.keyEvent)
                self.repeatTime = time.time() + repeatRate
                self.block.g_treeModified = True

    def draw(self, screen):
        scsz = screen.get_size()
        self.scArea = scArea = 0.25 * scsz[0]  * scsz[1]

        # Fix for unknown screen width.
        if scsz[0] != self.screenWidth and self.selLength == 0 == self.selLines:
            self.screenWidth = scsz[0]
            pt = self.actualPos(self.cursorPos)
            self.wordWrap()
            self.cursorPos = self.screenPos(pt)

        # 1. Render the text.
        lineSize = self.font.get_linesize()
        height = width = 0
        surfaces = []
        for i in range(len(self.lines)):
            s = self.font.render(self.lines[i], False, vTxColour).convert()

            surfaces.append(s)
            height = height + lineSize
            w = s.get_width()
            if (i-1) in self.wrappedLines:
                w = w + self.followWidth
            width = max(width, w)
            lastHeight = s.get_height()

        # Adjust for hanging characters in the last line.
        if lastHeight > lineSize:
            height = height + lastHeight - lineSize

        # 2. Piece it all together.
        surface = pygame.Surface((width, height)).convert()
        if self.bkgColour:
            surface.fill(self.bkgColour)
        else:
            surface.fill(bkgColour)
            surface.set_colorkey(bkgColour)

        y = 0.
        for i in range(len(surfaces)):
            s = surfaces[i]
            x = 0

            if (i-1) in self.wrappedLines:
                # Indicate that line is wrapped
                surface.blit(self.followSurface, (x, y))
                x = x + self.followWidth

            surface.blit(s, (x, y))
            y = y + lineSize

        # Find the position.
        pt = self.block.g_absPlacement.parentPoint(self.pt, scArea)
        r = self.block.g_absPlacement.parentLength(self.radius, scArea)

        # 3. Check if it needs to be scaled.
        self.sFactor = sFactor = 2. * r / (width ** 2 + height ** 2) ** 0.5

        # Cutoff - don't draw.
        if sFactor > 0.3:
            # Scale it if needed.
            if sFactor < 1.:
                width = int(round(width * sFactor))
                height = int(round(height * sFactor))
                surface = pygame.transform.scale(surface, (width, height))

            # 4. Put the text.
            putPos = (pt[0] - 0.5*width, pt[1] - 0.5*height)
            screen.blit(surface, putPos)
            self.textSz = (0.5*width, 0.5*height)

            # Draw a fine border.
            pygame.draw.rect(screen, bdrColour, \
                             pygame.Rect(putPos, (width+8, height)), 1)
        else:
            self.textSz = None

    def drawFinding(self, screen):
        '''Draws this block when the cursors resting on it but it hasn't yet
        been entered.'''
        if self.textSz == None:
            return

        pl = self.block.g_absPlacement
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0] * scsz[1]

        halfWidth, halfHeight = self.textSz
        x0,y0 = pl.parentPoint(self.pt, scArea)
        x1,y1 = (x0-halfWidth, y0-halfHeight)
        x2,y2 = (x0+halfWidth+8, y0-halfHeight)
        x3,y3 = (x0+halfWidth+8, y0+halfHeight)
        x4,y4 = (x0-halfWidth, y0+halfHeight)
        polygon = [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]

        borderColour, fillColour, thickness = RectType.Selected

        if fillColour:
            pygame.draw.polygon(screen, fillColour, polygon)
        if borderColour:
            pygame.draw.polygon(screen, borderColour, polygon, thickness)

    def drawSelected(self, screen):
        if self.textSz == None:
            return

        pl = self.block.g_absPlacement
        scsz = screen.get_size()
        scArea = 0.25 * scsz[0] * scsz[1]
        x0, y0 = pl.parentPoint(self.pt, scArea)

        # Choose the appropriate line.
        if self.selLength == 0 == self.selLines:
            n, m = self.cursorPos
        else:
            n, m = self.selStart
        lineSize = self.font.get_linesize()
        y = lineSize * n

        # Get the sizes of the different sections.
        sa = self.font.size(self.lines[n][:m])[0]

        # Draw a cursor line.
        if (n-1) in self.wrappedLines:
            x = sa + self.followWidth
        else:
            x = sa

        if self.sFactor < 1.:
            x = x * self.sFactor
            y = y * self.sFactor
            lineSize = lineSize * self.sFactor

        pt0 = (x0 -self.textSz[0] + x, y0 - self.textSz[1] + y)

        if self.selLength == 0 == self.selLines:
            # No selection. Just draw cursor.
            pt1 = (x0 - self.textSz[0] + x, y0 - self.textSz[1] + y + lineSize)
            pygame.draw.line(screen, csrColour, pt0, pt1)
        elif self.selLines == 0:
            # Create a surface of the selected text.
            m2 = m + self.selLength
            s = self.font.render(self.lines[n][m:m2], False, \
                                 tuple(255-i for i in csrColour), csrColour)
            s.set_colorkey(None)

            if self.sFactor < 1.:
                width, height = s.get_size()
                width = int(round(width * self.sFactor))
                height = int(round(height * self.sFactor))
                s = pygame.transform.scale(s, (width, height))
            screen.blit(s, pt0)
        else:
            # Multiline selection.

            # Create a surface of this line of the selected text.
            if m < len(self.lines[n]):
                text = self.lines[n][m:]
                if len(text) > 0:
                    s = self.font.render(text, False, \
                                         tuple(255-i for i in csrColour), csrColour)
                    s.set_colorkey(None)

                    if self.sFactor < 1.:
                        width, height = s.get_size()
                        width = int(round(width * self.sFactor))
                        height = int(round(height * self.sFactor))
                        s = pygame.transform.scale(s, (width, height))
                    screen.blit(s, pt0)

            # Central section.
            for i in range(n + 1, n + self.selLines):
                if (i-1) in self.wrappedLines:
                    x = x0 - self.textSz[0] + self.followWidth
                else:
                    x = x0 - self.textSz[0]
                pt0 = (x, pt0[1] + lineSize)

                if self.lines[i] == '':
                    # Single vertical bar.
                    pygame.draw.line(screen, csrColour, pt0, \
                                     (pt0[0], pt0[1]+lineSize))
                else:
                    s = self.font.render(self.lines[i], False, \
                                         tuple(255-i for i in csrColour), csrColour)
                    s.set_colorkey(None)
                    if self.sFactor < 1.:
                        width, height = s.get_size()
                        width = int(round(width * self.sFactor))
                        height = int(round(height * self.sFactor))
                        s = pygame.transform.scale(s, (width, height))
                    screen.blit(s, pt0)

            # Last line.
            i = n + self.selLines
            if (i-1) in self.wrappedLines:
                x = x0 - self.textSz[0] + self.followWidth
            else:
                x = x0 - self.textSz[0]
            pt0 = (x, pt0[1] + lineSize)
            text = self.lines[i][:self.selLength]
            if text != '':
                s = self.font.render(text,\
                            False, tuple(255-i for i in csrColour), csrColour)
                s.set_colorkey(None)

                if self.sFactor < 1.:
                    width, height = s.get_size()
                    width = int(round(width * self.sFactor))
                    height = int(round(height * self.sFactor))
                    s = pygame.transform.scale(s, (width, height))
                screen.blit(s, pt0)

    def checkMouseHover(self, pos):
        # Check for text not showing.
        if self.textSz == None:
            return False

        # Now check for hover over text.
        mPt = self.block.g_absPlacement.parentPoint(pos, self.scArea)
        tPt = self.block.g_absPlacement.parentPoint(self.pt, self.scArea)

        # 8-pixel padding on each side where you can still click.
        if tPt[0] - self.textSz[0] - 8 < mPt[0] < tPt[0] + self.textSz[0] + 8:
            if tPt[1] - self.textSz[1] < mPt[1] < tPt[1] + self.textSz[1]:
                self.hoverPos = mPt
                return True
        return False

    def mouseHover(self, screen):
        # Do nothing special on a hover.
        pass

    def mouseClick(self, actor):
        # Make sure that this text's selected.
        actor.txtClick(self)

        # Set the cursor position.
        self.highlightMotion = False
        self.moveCursor(self.getClickPoint(self.hoverPos))

    def mouseDrag(self, event):
        self.highlightMotion = True
        self.moveCursor(self.getClickPoint(event.pos))

    def getClickPoint(self, point):
        '''internal. Returns the coordinates of the specified screen position.
        '''

        pl = self.block.g_absPlacement
        x0, y0 = pl.parentPoint(self.pt, self.scArea)

        # First find the correct row for the cursor.
        x = point[0] - x0 + self.textSz[0]
        y = point[1] - y0 + self.textSz[1]

        lineSize = self.font.get_linesize()
        if self.sFactor < 1.:
            lineSize = lineSize * self.sFactor
            x = x / self.sFactor

        n = max(0, min(int(y // lineSize), len(self.lines) - 1))

        return [n, self.getClickPointInternal(x, n)]

    def getClickPointInternal(self, x, n):
        '''internal. Returns the x-coordinates taken from the specified offset
        from the left side of this block after scaling. n is the line
        number.'''

        # Now find the correct column.
        if n-1 in self.wrappedLines:
            s0 = self.followWidth
        else:
            s0 = 0
        s = self.font.size(self.lines[n])[0]

        # 1. Guess the position.
        if x <= s0:
            m = 0
        elif x >= s0 + s:
            m = len(self.lines[n])
        else:
            m = int(round(len(self.lines[n]) * (x-s0) / s))

            # 2. Refine the guess.
            gDist = self.font.size(self.lines[n][:m])[0] + s0

            if gDist < x:
                # We guessed too low.
                while gDist < x:
                    diff = x - gDist
                    m = m + 1
                    gDist = self.font.size(self.lines[n][:m])[0] + s0

                # We found the turning point.
                if diff < gDist - x:
                    m = m - 1
            elif gDist > x:
                # We guessed too high.
                while gDist > x:
                    diff = gDist - x
                    m = m - 1
                    gDist = self.font.size(self.lines[n][:m])[0] + s0

                # Found the turning point.
                if diff < x - gDist:
                    m = m + 1

        # 3. Return the value.
        return m

    def moveCursor(self, pt):
        'internal. Moves the cursor to a new point.'
        newY, newX = pt
        if not self.highlightMotion:
            self.cursorPos = [newY, newX]
            self.selLength = 0
            self.selLines = 0
        else:
            if not (self.selLength or self.selLines):
                selEnd = self.cursorPos
            elif self.selStart == self.cursorPos:
                selEnd = self.selEnd()
            else:
                selEnd = self.selStart

            if newY < selEnd[0] or (newY == selEnd[0] and newX < selEnd[1]):
                self.selLines = selEnd[0] - newY
                if self.selLines == 0:
                    self.selLength = selEnd[1] - newX
                else:
                    self.selLength = selEnd[1]
                self.selStart = [newY, newX]
            else:
                self.selLines = newY - selEnd[0]
                self.selStart = selEnd
                if self.selLines == 0:
                    self.selLength = newX - selEnd[1]
                else:
                    self.selLength = newX

            self.cursorPos = [newY, newX]

    def blankBetween(self, start, end):
        '''internal. Blanks between the two specified positions, which are
        positions in the displayed text.'''
        pos1 = self.actualPos(start)
        pos2 = self.actualPos(end)

        if pos1[0] == pos2[0]:
            # All on the same (actual) line.
            x = self.values[pos1[0]]
            self.values[pos1[0]] = x[:pos1[1]] + x[pos2[1]:]
        else:
            # Split across multiple lines.
            for i in range(pos2[0] - pos1[0]-1):
                self.values.pop(pos1[0]+1)
            self.values[pos1[0]] = self.values[pos1[0]][:pos1[1]] + \
                                   self.values.pop(pos1[0]+1)[pos2[1]:]

    def selEnd(self):
        '''internal. Returns the position of the end of the selection in the
        displayed text.'''
        if not (self.selLength or self.selLines):
            return self.selStart
        if self.selLines:
            return [self.selStart[0] + self.selLines,
                      self.selLength]
        else:
            return [self.selStart[0], self.selStart[1] + \
                      self.selLength]

    def blankSelection(self):
        'internal. Blanks the selection. Returns True if there was one.'
        if not (self.selLength or self.selLines):
            return False
        savedPos = self.actualPos(self.selStart)
        self.blankBetween(self.selStart, self.selEnd())

        self.selLength = 0
        self.selLines = 0
        self.cursorPos = self.screenPos(savedPos)

        self.wordWrap()
        return True

    def keyUp(self, event, actor):
        'internal. A key has been released.'
        if self.keyEvent and event.key == self.keyEvent.key:
            self.keyEvent = None

    def keyPress(self, event, actor):
        'internal. A key has been pressed.'
        self.keyEvent = event
        self.actor = actor
        self.processKeystroke(event)
        self.repeatTime = time.time() + repeatLag

    def processKeystroke(self, event):
        'internal. Process a keystroke.'

        char = keyboard.charPressed(event.key, event.mod)
        if isinstance(char, str):
            # Translates to a char.
            self.blankSelection()
            n, m = self.actualPos(self.cursorPos)
            self.values[n] = self.values[n][:m] + char + \
                             self.values[n][m:]
            self.wordWrap()
            self.cursorPos = self.screenPos([n, m + 1])
        else:
            key, mod = char
            self.highlightMotion = mod & pgl.KMOD_SHIFT
            mod = mod & ~ pgl.KMOD_SHIFT
            n,m = self.cursorPos

            if mod == 0:
                if key == keyboard.Return:
                    # Enter.
                    self.blankSelection()
                    n, m = self.actualPos(self.cursorPos)

                    # Split the line at this point.
                    self.values.insert(n + 1, self.values[n][m:])
                    self.values[n] = self.values[n][:m]
                    self.wordWrap()
                    self.cursorPos = self.screenPos([n + 1, 0])
                elif key == keyboard.Left:
                    # Left arrow.
                    if m == 0:
                        if n != 0:
                            self.moveCursor([n-1, len(self.lines[n-1])])
                    else:
                        self.moveCursor([n, m - 1])
                elif key == keyboard.Right:
                    # Right arrow.
                    if m < len(self.lines[n]):
                        self.moveCursor([n, m + 1])
                    elif n < len(self.lines) - 1:
                        self.moveCursor([n+1, 0])
                elif key == keyboard.Up:
                    # Up arrow.
                    if n == 0:
                        return
                    xPos = self.font.size(self.lines[n][:m])[0]
                    if (n-1) in self.wrappedLines:
                        xPos = xPos + self.followWidth
                    n = n - 1
                    m = self.getClickPointInternal(xPos, n)
                    self.moveCursor([n, m])
                elif key == keyboard.Down:
                    # Down arrow.
                    if n == len(self.lines) - 1:
                        return
                    xPos = self.font.size(self.lines[n][:m])[0]
                    if (n-1) in self.wrappedLines:
                        xPos = xPos + self.followWidth
                    n = n + 1
                    m = self.getClickPointInternal(xPos, n)
                    self.moveCursor([n, m])
                elif key == keyboard.Home:
                    # Home key.
                    self.moveCursor([n, 0])
                elif key == keyboard.End:
                    # End key.
                    self.moveCursor([n, len(self.lines[n])])
                elif key == keyboard.Backspace:
                    # Backspace.
                    if not self.blankSelection():
                        n,m = self.actualPos(self.cursorPos)
                        if m > 0:
                            self.values[n] = self.values[n][:m-1] + self.values[n][m:]
                            m = m - 1
                        else:
                            # Combine this line with the previous.
                            if n > 0:
                                m = len(self.values[n-1])
                                self.values[n-1] = self.values[n-1] + \
                                                 self.values.pop(n)
                                n = n-1
                            else:
                                return
                        self.wordWrap()
                        self.cursorPos = self.screenPos([n, m])
                elif key == keyboard.Delete:
                    # Delete.
                    if not self.blankSelection():
                        n,m = self.actualPos(self.cursorPos)
                        if m < len(self.values[n]):
                            self.values[n] = self.values[n][:m] + \
                                             self.values[n][m+1:]
                        else:
                            # Combine line with next.
                            if n < len(self.values) - 1:
                                self.values[n] = self.values[n] + \
                                                 self.values.pop(n+1)
                            else:
                                return
                        self.wordWrap()
                        self.cursorPos = self.screenPos([n, m])
                else:
                    return
            elif mod == pgl.KMOD_LCTRL:
                if key == keyboard.Left:
                    # Move left one word.
                    n1, m1 = n, m
                    wordStarted = False
                    while True:
                        if m1 == 0:
                            if n1 == 0:
                                break
                            if wordStarted:
                                break
                            n1 = n1 - 1
                            m1 = len(self.lines[n1]) - 1
                        else:
                            m1 = m1 - 1
                        if self.lines[n1][m1] == ' ':
                            if wordStarted:
                                break
                        else:
                            wordStarted = True

                        n, m = n1, m1
                    self.moveCursor([n, m])
                elif key == keyboard.Right:
                    # Move right one word.
                    n1, m1 = n, m
                    if m == len(self.lines[n]):
                        m = m - 1
                    wordStarted = False
                    while True:
                        if m1 >= len(self.lines[n1]) - 1:
                            if n1 == len(self.lines) - 1:
                                break
                            if wordStarted:
                                break
                            n1 = n1 + 1
                            m1 = 0
                        else:
                            m1 = m1 + 1
                        if self.lines[n1][m1] == ' ':
                            if wordStarted:
                                break
                        else:
                            wordStarted = True
                        n, m = n1, m1
                    self.moveCursor([n, m + 1])
                elif key == keyboard.Home:
                    # Move to the top of the feature.
                    self.moveCursor([0, 0])
                elif key == keyboard.End:
                    # Move to the end of the feature.
                    self.moveCursor([len(self.lines)-1,
                                     len(self.lines[-1])])
                else:
                    return
            else:
                return

        self.block.master.g_treeModified = True

    def setValues(self, values):
        self.values = values
        self.wordWrap()

        n, m = self.cursorPos
        if n > len(self.lines):
            n = len(self.lines)
        if m > len(self.lines[n]):
            m = 0
        self.cursorPos = [n, m]

    def save(self):
        'Calls the notify function about the changes.'
        if isinstance(self.callback, tuple):
            fn, args = self.callback
            fn(self.values, *args)
        else:
            self.callback(self.values)

        self.block.master.g_treeModified = True

        n,m = self.cursorPos
        if m > len(self.lines[n]):
            self.cursorPos[1] = 0

        self.keyEvent = None

    def beginEdit(self):
        'Called when this element\'s first entered.'
        # Select the whole first line of text.
        self.cursorPos = [0, 0]
        self.selStart = [0, 0]
        self.selLines = len(self.lines) - 1
        self.selLength = len(self.lines[-1])

import sourceFile
from actor import SysMode

if __name__ == '__main__':
    import main
    mb = main.main()
