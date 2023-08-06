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

import sys, warnings, new, copy, string, os, time, stat
from math import pi, sin, cos, tan

from py_compile import marshal, MAGIC, wr_long

# The following number identifies the format of the save file.
fcpyMagicNumber = 3

class ContextError(Exception): pass
class EPrepBlockError(Exception): pass
class ECompileBlockError(Exception): pass
class WPrepBlockWarning(UserWarning): pass

#####################################
# for checking identifier validity
#####################################

class Identifier(object):
    firstChar = string.ascii_letters + '_'
    otherChars = string.ascii_letters + string.digits + '_'

    @classmethod
    def valid(cls, name):
        '''Checks whether name is a valid identifier name.'''
        # First do the compile test.
        try:
            compile(name, '', 'eval')
        except SyntaxError:
            return False

        if not isinstance(name, str):
            return False
        if name == '':
            return False
        if name[0] in cls.firstChar:
            for i in name[1:]:
                if not i in cls.otherChars:
                    return False
            return True
        return False

    @classmethod
    def preRouteNamesError(cls, routes):
        '''Checks whether the names in routes is valid names for routes which
        lead into an interface.

        If so, False is returned.
        If not, an explanation string is returned.'''

        for i in routes:
            # Must be a string.
            if not isinstance(i, str):
                return 'route name must be a string'
            if i != '':
                if not Identifier.valid(i):
                    # Check for question mark.
                    try:
                        if i[0] == '?':
                            # At pre-interface, any expression'll do.
                            try:
                                compile(i[1:],'','eval')
                            except:
                                pass
                            else:
                                continue
                    except:
                        pass

                    # Invalid.
                    return "invalid route name: '%s'" % i

        return False


    @classmethod
    def postRouteNamesError(cls, routes):
        '''Checks whether the names in routes is valid names for routes which
        lead out of an interface.

        If so, False is returned.
        If not, an explanation string is returned.'''

        hadQm = False
        for i in routes:
            # Check if we've had a question mark.
            if hadQm:
                return 'wildcard route must be last route'

            # Must be a string.
            if i != '':
                if not Identifier.valid(i):
                    # Check for question mark.
                    try:
                        test = i[0]
                    except TypeError:
                        test = ''

                    # '?something' is valid as the last entry.
                    if test == '?' and Identifier.valid(i[1:]):
                        hadQm = True
                        continue

                    # Invalid.
                    return "invalid route name: '%s'" % i

        return False

##################################
# mapping types
##################################

class Mapping(object):
    def __init__(self):
        self.numOutputs = 0
        self.numInputs = 0
        self.connections = []

    def __getitem__(self, index):
        value = self.connections[index]
        if value >= self.numOutputs:
            value = self.numOutputs - 1
        return value

    def __len__(self):
        return self.numInputs

    def isBroken(self):
        'error-checker.'
        if len(self.connections) < self.numInputs:
            print 'Mapping numInputs: %d, len connections: %d' % \
                  (self.numInputs, len(self.connections))
            return True
        return False

    def modifyInputs(self, insert, index):
        'internal'
        if insert:
            self.connections.insert(index, 0)
            self.numInputs = self.numInputs + 1
        else:
            self.connections.pop(index)
            self.numInputs = self.numInputs - 1

    def modifyOutputs(self, insert, index):
        'internal'
        # Adjust the pointers.
        adj = (insert and 1) or -1
        for i in range(len(self.connections)):
            j = self.connections[i]
            if j >= index:
                self.connections[i] = max(j + adj, 0)

        self.numOutputs = self.numOutputs + adj

    def setNumInputs(self, numInputs):
        'internal. Only used when numInputs suddenly changes.'
        i = numInputs - len(self.connections)
        self.numInputs = numInputs
        if i > 0:
            self.connections.extend([0]*i)

    def setNumOutputs(self, numOutputs):
        'internal. Only used when numOutputs suddenly changes.'
        self.numOutputs = numOutputs

    def reverseRoute(self, strandLabel, exit):
        '''reverseRoute(strandLabel, exit) - internal.
        Called in the process of labeling strands. Indicates that the
        strand which comes through the specified exit of this block should be
        labeled with the specified label.

        Arguments:

        strandLabel:    the label for the strand.
        exit:           the exit of this object through which the strand comes.

        Returns a list of the entries of this object through which the strand
        comes.
        '''

        return [i for i in range(self.numInputs) \
                if self[i] == exit]

    def straighten(self):
        '''straighten() - connects the routes in a sequential manner.'''
        n = 0
        for i in range(self.numInputs):
            self.connections[i] = n
            if n < self.numOutputs - 1:
                n = n + 1

class InterBlockMapping(Mapping):
    def __init__(self, prevBlock, nextBlock):
        assert prevBlock is not None
        assert nextBlock is not None
        super(InterBlockMapping, self).__init__()

        self.prevBlock = prevBlock
        self.nextBlock = nextBlock
        self.numOutputs = self.nextBlock.numInputs
        self.numInputs = self.prevBlock.numOutputs

        # By default everything's connected in order.
        for i in range(self.prevBlock.numOutputs):
            if i < self.numOutputs:
                self.connections.append(i)
            else:
                self.connections.append(self.numOutputs - 1)

    def isBroken(self):
        if super(InterBlockMapping, self).isBroken():
            return True
        if self.prevBlock.numOutputs != self.numInputs:
            print '  ib-map in: %d, prev out: %d' % (self.numInputs, \
                                                     self.prevBlock.numOutputs)
            return True
        if self.nextBlock.numInputs != self.numOutputs:
            print '  ib-map out: %d, next in: %d' % (self.numOutputs, \
                                                     self.nextBlock.numInputs)
            return True
        return False

    def splitBefore(self, midBlock):
        '''splitBefore(midBlock) - internal.
        Splits the mapping into two separated by the specified block.
        Returns the new mapping which must be inserted before this one.'''
        prevMap = InterBlockMapping(self.prevBlock, midBlock)
        self.prevBlock = midBlock
        numInputs = midBlock.numOutputs

        # Add connections if need be.
        if len(self.connections) < numInputs:
            self.connections.append([0] * (numInputs - \
                                           len(self.connections)))

        self.numInputs = numInputs

        return prevMap

    def splitAfter(self, midBlock):
        '''splitAfter(midBlock) - internal.
        Splits the mapping into two separated by the specified block.
        Returns the new mapping which must be inserted after this one.'''
        nextMap = InterBlockMapping(midBlock, self.nextBlock)
        self.nextBlock = midBlock
        self.numOutputs = midBlock.numInputs

        return nextMap

class CollapseMapping(Mapping):
    def __init__(self, prevBlock):
        super(CollapseMapping, self).__init__()

        self.prevBlock = prevBlock
        self.numOutputs = 1

        # Everything's connected to the one output.
        self.connections = [0] * self.prevBlock.numOutputs
        self.numInputs = self.prevBlock.numOutputs

    def isBroken(self):
        if super(CollapseMapping, self).isBroken():
            return True
        if self.prevBlock.numOutputs != self.numInputs:
            print 'CollapseMapping in: %d, prev out: %d' % \
                  (self.numInputs, self.prevBlock.numOutputs)
            return True
        return False

class LoopMapping(Mapping):
    '''LoopMapping(nextBlock, numInputs) - nextBlock is the main block of
    the loop, numInputs is the number of routes into the loop.'''

    def __init__(self, nextBlock, numInputs):
        super(LoopMapping, self).__init__()

        self.nextBlock = nextBlock
        self.numOutputs = self.nextBlock.numInputs
        self.numInputs = numInputs + self.nextBlock.numOutputs

        # By default everything's connected in order.
        for i in range(numInputs + self.nextBlock.numOutputs):
            if i < self.numOutputs:
                self.connections.append(i)
            else:
                self.connections.append(self.numOutputs - 1)

    def isBroken(self):
        if self.numOutputs != self.nextBlock.numInputs:
            print 'LoopMapping outputs: %d, block inputs: %d' % \
                  (self.numOutputs, self.nextBlock.numInputs)
            return True
        if self.numInputs <= self.nextBlock.numOutputs:
            print 'LoopMapping inputs: %d, block outputs: %d' % \
                  (self.numInputs, self.nextBlock.numOutputs)
            return True
        if super(LoopMapping, self).isBroken():
            return True
        return False

##################################
# base block types
##################################

class Block(object):
    def __init__(self, parent=None, nextLoop=None):
        '''base class for blocks.

        Arguments:

        parent:     this block's parent or None if this is the top-level block.
        nextLoop:   the next loop block which encapsulates this block - for use
                    when escapes(breaks) are used.
        '''

        self.parent = parent
        self.master = parent and parent.master
        self.nextLoop = nextLoop
        self.numInputs = 0
        self.numOutputs = 0
        self.maxInputs = 0
        self.bnLevel = 0        # Number of bottlenecks.
        self.passingEscapes = []
        self.lineNumbers = []

        # For graphics:
        self.g_desiredShape = 1.618     # Width / height
        self.g_modified = True
        self.g_sizeCutoff = None
        self.g_relPlacement = painter.RelativePlacement()
        self.g_loopPlacement = painter.RelativePlacement()
        self.g_cycle = None
        self.g_nonDrawn = False

    def __contains__(self, child):
        return False

    def isBroken(self):
        'error-checker'
        if self.parent and self not in self.parent:
            print 'Block not in parent.'
            return True
        return False

    @staticmethod
    def spacePoints(spacings, pt1, pt2):
        '''(spacings, pt1, pt2) - internal.
        Returns a list of points spaced between pt1 and pt2 with spacings
        proportional to the specified spacings, and with the stipulation that
        no spacing in the result be more than twice the size of any other.
        '''

        SSp = float(sum(spacings))
        spacings = [s / SSp for s in spacings]
        weights = [None] * len(spacings)

        while True:
            # 1. Fix items which are outside absolute bounds.
            while True:
                minSpace = 1. / (sum(w or 2. for w in weights) - 1.)
                maxSpace = 2. / (sum(w or 1. for w in weights) + 1.)

                modified = False
                for i in range(len(spacings)):
                    if weights[i] == None:
                        if spacings[i] < minSpace:
                            weights[i] = 1.
                            modified = True
                        elif spacings[i] > maxSpace:
                            weights[i] = 2.
                            modified = True
                if not modified:
                    break

            # Assign spacings for these weightings.
            num, denom = 1., 0.
            for i in range(len(spacings)):
                w = weights[i]
                if w:
                    denom = denom + w
                else:
                    num = num - spacings[i]
            if denom > 0.:
                smallSize = num / denom

            # Calculate current spacings.
            resultSpace = []
            for i in range(len(spacings)):
                if weights[i] == None:
                    resultSpace.append(spacings[i])
                else:
                    resultSpace.append(weights[i] * smallSize)

            # 2. Test for end condition.
            if max(resultSpace) <= 2. * min(resultSpace):
                break

            # 3. Correct the most extreme value.
            minIndex = maxIndex = -1
            minRes = 1.
            maxRes = 0.
            for i in range(len(spacings)):
                if weights[i] == None:
                    if spacings[i] < minRes:
                        minIndex = i
                        minRes = spacings[i]
                    if spacings[i] > maxRes:
                        maxIndex = i
                        maxRes = spacings[i]

            if minSpace - minRes > maxRes - maxSpace:
                # Correct the minimum value up.
                weights[minIndex] = 1.
            else:
                # Correct the maximum value down.
                weights[maxIndex] = 2.

        runningSpace = 0.
        result = []
        for space in resultSpace[:-1]:
            runningSpace = runningSpace + space
            result.append(tuple(pt1[j] + runningSpace * (pt2[j]-pt1[j]) for j \
                                in (0,1)))
        return result

    def setMaxInputs(self, maxInputs):
        '''setMaxInputs(maxInputs) - internal.
        Called by a parent block to tell this block how many inputs it
        can have. If the number of inputs excedes this maximum, the block
        will highlight the area and add itself to a list of attention-neededs.
        If this is set to 0 or None, any number of inputs can be had.
        '''
        self.maxInputs = maxInputs

        if maxInputs and maxInputs < self.numInputs:
            # TODO: draw attention to it.
            pass

    def childOutputsChanged(self, child, insert, index):
        '''childOutputsChanged(child, insert, index) - internal.
        Called by a child object when its number of outputs has changed.
        This procedure should tell its parent, and the child after the calling
        child of this fact.  Should be implemented by any block with children.

        Parameters:

        child:      the child whose outputs have changed.
        insert:     True if an output has been added, False otherwise.
        index:      the index of the deleted output route, or the index
                    before which the inserted route has been added.
        '''
        raise NotImplementedError

    def childInputsChanged(self, child, insert, index):
        '''childInputsChanged(child, insert, index) - internal.
        Called by a child object when its number of inputs has changed.
        This procedure should tell its parent, and the mapping before the
        calling child of this fact.  Should be implemented by any block with
        children.

        Parameters:

        child:      the child whose outputs have changed.
        insert:     True if an output has been added, False otherwise.
        index:      the index of the deleted output route, or the index
                    before which the inserted route has been added.

        Note that blocks are not allowed to have no inputs.
        '''
        raise NotImplementedError

    def childAddEscape(self, child, index):
        '''childAddEscape(child, index) - internal.
        Called by a child block when an escape has been added to its escapes
        list. An escape should be in the escapes list of all its ancestors up
        to the loop which it is escaping. This method call will be initiated
        by the escape itself, then passed from parent to parent until it
        reaches the loop.

        child:      the child who is calling.
        index:      the index of the newly added escape.
        '''
        raise NotImplementedError

    def childRemoveEscape(self, escape):
        '''childRemoveEscape(child, escape) - internal.
        Called by a child block when an escape has been removed from its
        escapes list.

        escape:     the escape block being removed from the list.
        '''

        # Remove the escape from my list and tell the parent.
        self.passingEscapes.remove(escape)
        if self.parent:
            self.parent.childRemoveEscape(escape)

    def swapChild(self, oldChild, newChild):
        '''swapChild(oldChild, newChild) - internal.
        Indicates that newChild should be substituted into this block in the
        place of oldChild.
        '''
        raise NotImplementedError

    def delChild(self, child):
        '''delChild(child) - internal.
        Indicates that a request has been made that the child block be deleted.
        This method should take appropriate action - by default it reverts and
        returns the new PassBlock object.
        Otherwise, it should call child.blankContext(), and return None.
        '''
        return child.revert()

    def duplicate(self):
        '''duplicate() - internal.
        Returns a block that's an exact deep copied duplicate of this block's
        contents (but not context).'''
        raise NotImplementedError

    def distil(self):
        '''distil() - internal.
        Distils the essence of this block down into a single object which can
        be accurately reproduced with repr().'''
        raise NotImplementedError

    @staticmethod
    def reconstitute(essence):
        '''reconstitute(essence) - internal.
        Restores a block from the specified distilled essence, and returns
        the block.

        Note that type(block).reconstitute(block.distil()) should be
        functionally equivalent to block.duplicate().
        '''
        raise NotImplementedError

    def reverseRoute(self, strandLabel, exit):
        '''reverseRoute(strandLabel, exit) - internal.
        Called in the process of labeling strands. Indicates that the
        strand which comes through the specified exit of this block should be
        labeled with the specified label.

        Arguments:

        strandLabel:    the label for the strand.
        exit:           the exit of this object through which the strand comes.

        Returns a list of the entries of this object through which the strand
        comes.
        '''
        # Compiler optimisation: tagging
        if self.numInputs == 1 >= self.numOutputs:
            self.tagLabel = strandLabel

        return [0]

    def labelStrand(self, strandLabel, child, entry):
        '''labelStrand(strandLabel, child, entry) - internal.
        Calling this method will label the strand which comes through the
        specified entry of the specified child block with the specified label.
        This method should be called during the prepBlock method of a
        strand-discriminating block which is the child of the current block.

        Arguments:

        strandLabel:    the label to give the strand in question.
        child:          the child block at which the strand terminates.
        entry:          the index of the entry of the child block through
                        which the strand comes.

        This method should be implemented by all block classes which have
        children.
        '''
        raise NotImplementedError

    def tagRoute(self, tagBlock, exit):
        '''tagRoute(tagBlock, exit) - internal.
        Called in the process of tagging strands. Indicates that the
        strand which comes through the specified exit of this block should
        have the specified block tagged on.
        '''
        # Default processing: ignore the tagging.
        return

    def tagStrand(self, tagBlock, child, entry):
        '''tagStrand(tagBlock, child, entry) - internal.
        Calling this method will attempt to tag the specified block onto the
        strand which comes through the specified entry of the specified child
        block.'''
        # Default processing is to ignore the tagging.
        return

    def compilesBlank(self):
        '''internal.
        Returns True if this block knows that it intends to compile as a
        blank.'''
        return self.beenParsed and not self.tagLabel

    def prepBlock(self):
        '''prepBlock() - internal.
        Called in the compilation process to tell this block to prepare
        itself for compilation. This method should be extended by all
        block classes which have children or are strand-discriminating.

        This method should:
        * Initialise any strand label variables.
        * Check that this block is valid and raise EPrepBlockError if it's not.
        * Call the prepBlock() method of any child blocks.
        * If this block is a strand-discriminating block, call the
          labelStrand() method of its parent block.
        * If this block might introduce integer consts into the code block,
          generate and return a list of all names which would be introduced.
        '''
        # Raise a warning if we have too many inputs.
        if self.maxInputs and self.numInputs > self.maxInputs:
            warnings.warn(WPrepBlockWarning((self, 'Too many entries.')))

        # We haven't yet been parsed.
        self.beenParsed = False

        # Check if we can be tagged.
        if self.numInputs == 1 >= self.numOutputs:
            self.parent.tagStrand(self, self, 0)
            self.tagLabel = None

        return []

    def parse(self, parser):
        '''parse(parser) - internal.
        Called in the process of compiling the code. This should be called
        after prepBlock() has been called on the whole program tree.

        parser:     the parser object assigned to parsing this block. This
                    method should perform the parsing by calling the
                    addLines(), addLine(), parseBlock(), indent(), dedent(),
                    newConst(), addLabel() and newParser() methods of the
                    parser object.
        '''
        raise NotImplementedError

    def setNumInputs(self, numInputs):
        '''internal. Only called when numInputs suddenly changes.'''
        if self.parent:
            if numInputs > self.numInputs:
                for i in range(self.numInputs, numInputs):
                    self.numInputs = self.numInputs + 1
                    self.parent.childInputsChanged(self, True, i)
            else:
                for i in range(numInputs, self.numInputs):
                    self.numInputs = self.numInputs - 1
                    self.parent.childInputsChanged(self, False, numInputs)
            assert self.numInputs == numInputs
        else:
            self.numInputs = numInputs

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def setNumOutputs(self, numOutputs):
        '''internal. Only called when numOutputs suddenly changes.'''
        oldOut = self.numOutputs
        if self.parent:
            if numOutputs > oldOut:
                for i in range(oldOut, numOutputs):
                    self.numOutputs = self.numOutputs + 1
                    self.parent.childOutputsChanged(self, True, i)
            else:
                for i in range(numOutputs, oldOut):
                    self.numOutputs = self.numOutputs - 1
                    self.parent.childOutputsChanged(self, False, numOutputs)

            assert self.numOutputs == numOutputs
        else:
            self.numOutputs = numOutputs

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def setContext(self, other):
        '''setContext(other) - internal.
        Called when this block is being substituted in the place of the other
        block. This block gets its context from the other block.
        '''
        # Copy my context from the other block.
        self.parent = other.parent
        self.maxInputs = other.maxInputs
        self.master = other.master
        self.setNextLoop(other.nextLoop)
        self.bnLevel = other.bnLevel
        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

        self.transmitContext()
        self.transmitLoopContext()

    def blankContext(self):
        '''blankContext() - internal.
        Called when this block or one of its ancestors is becoming free.
        Blanks this block's context.
        '''
        self.parent = None
        self.master = None
        self.setNextLoop(None)
        self.bnLevel = 0

        self.transmitContext()
        self.transmitLoopContext()

    def transmitContext(self):
        '''transmitContext() - internal.
        Transmits this block's context to its children. This should set all
        children's master members.
        Should be implemented by any block with children.
        '''
        pass

    def transmitLoopContext(self):
        '''transmitLoopContext() - internal.
        Transmits this block's context relating to loop nesting to its
        children. This should set all children's bnLevel members. It should
        also call the child's setNextLoop() method.
        This is a separate method from transmitContext because the loop context
        tree is not as deep.

        Should be implemented by any block with children.
        '''
        pass

    def setNextLoop(self, nextLoop):
        'internal.'
        self.nextLoop = nextLoop

    def g_addFeature(self, feature):
        'internal.'
        if feature.interactive:
            self.g_interactiveFeatures.append(feature)
        elif isinstance(feature, painter.Connection):
            self.g_connections.append(feature)
        else:
            self.g_features.append(feature)

    def g_addCutoffFeature(self, feature):
        'internal.'
        self.g_cutoffFeatures.append(feature)

    def g_drawChild(self, child):
        'internal. Draws the child in the place already specified.'

        if isinstance(self, LoopBlock):
            child.g_loopPlacement = child.g_relPlacement
        elif self.nextLoop:
            child.g_loopPlacement = self.g_loopPlacement.add( \
                child.g_relPlacement, self.nextLoop.g_relPlacement.area)
        child.g_draw()

    def g_addChild(self, child, area, shape, pos, angle=0.):
        'internal.'
        selfArea = self.g_relPlacement.area

        # If the child's shape has changed, it must be redrawn.
        pl = child.g_relPlacement
        if shape != pl.shape:
            child.g_modified = True

        # Set up the placement.
        pl.pos = pos
        pl.scale = area / selfArea
        pl.shape = shape
        pl.angle = angle

        if isinstance(self, LoopBlock):
            child.g_loopPlacement = pl
        elif self.nextLoop:
            child.g_loopPlacement = self.g_loopPlacement.add(pl, \
                                        self.nextLoop.g_relPlacement.area)

        self.g_children.append(child)
        child.g_nonDrawn = False
        child.g_draw()
        assert not child.g_modified

        assert len(child.g_rIn) == child.numInputs
        assert len(child.g_rOut) == child.numOutputs

        rIn = [pl.parentPoint(x, selfArea) for x in child.g_rIn]
        rOut = [pl.parentPoint(x, selfArea) for x in child.g_rOut]

        return rIn, rOut

    def g_clearBlock(self):
        'internal.'
        self.g_features = []
        self.g_cutoffFeatures = []
        self.g_interactiveFeatures = []
        self.g_connections = []
        self.g_children = []
        self.g_rIn = []
        self.g_rOut = []

    def g_draw(self):
        '''internal.
        Sets up this block's layout.
        Should be overridden by almost everything.'''

        if not self.g_modified or self.master == None:
            return
        self.g_modified = False

        # Default processing: draw a box.
        self.g_relPlacement.scaleDesired(self.g_desiredShape)
        self.g_clearBlock()
        self.g_border = painter.BlockBorder(self, 1.618, 1.0)
        self.g_addFeature(painter.Rectangle(self, 0.809, 0.5, RectType.Solid))
        self.g_addFeature(painter.Arrows(self, [(-.809, 0)]))

        self.g_rIn = [(-0.809, 0.)]
        self.g_rOut = [(0.809, 0.)]

        self.g_modified = False

    def g_childDesiredShapeChange(self, child):
        '''internal.
        Called when the desired shape of one of this block's children changes.
        Gives this block a chance to update its own desired shape.
        Should be overridden by blocks with children.'''
        pass

    def g_setDesiredShape(self, newShape):
        '''internal.
        Should be called by this block to set its own desired shape.'''
        if self.g_desiredShape == newShape:
            return
        self.g_desiredShape = newShape
        self.g_updateDesiredShape()

    def g_updateDesiredShape(self):
        '''internal.
        Informs the parent that this block's desired shape has changed.'''
        self.g_modified = True
        if self.parent:
            self.parent.g_childDesiredShapeChange(self)
        if self.master:
            self.master.g_treeModified = True

    def g_longDesiredShape(self):
        '''internal.
        Returns the desired shape when placed in a long block.'''
        return self.g_desiredShape

    def g_wideDesiredShape(self):
        '''internal.
        Returns the desired shape when placed in a wide block.'''
        return self.g_desiredShape

    def g_childRouteChange(self, child, inRoute):
        '''internal.
        Called when the input or output route positions of a child have
        inRoute should be True if an input route changed, False if an
        output route changed.'''
        # Default processing: just remember I've changed.
        self.g_modified = True

    def fixLineNumbers(self):
        '''internal.
        Fixes the line numbers so that this block knows encompases all its
        child line numbers.'''
        pass

    def getBlockFromLine(self, lineNumber):
        '''If this block or any of its descendants have the specified line
        number, returns the block in question, otherwise returns None.'''

        for i in range(0, len(self.lineNumbers), 2):
            small, big = self.lineNumbers[i:i+2]
            if lineNumber in xrange(small, big):
                return self
        return None

    def revert(self):
        '''revert(self) - revert the current block to a PassBlock, and returns
        the PassBlock.'''
        # Can't remove from context if there is no context.
        if not self.parent:
            return PassBlock()

        newBlock = PassBlock()

        # Remove escapes from my parent.
        for e in self.passingEscapes:
            self.parent.childRemoveEscape(e)

        # Copy my context into a new block.
        newBlock.setContext(self)
        self.parent.swapChild(self, newBlock)

        # I'm free.
        self.blankContext()

        # Error check.
        assert not self.isBroken()
        assert not newBlock.isBroken()
        assert not newBlock.parent.isBroken()

        if newBlock.master:
            newBlock.master.touch()

        return newBlock

    def delete(self):
        '''delete(self) - deletes the block from it's context, and if a
        new PassBlock is put in its place, returns that new block.
        '''
        # If it has no parent it's already deleted.
        if self.parent:
            if self.master:
                self.master.touch()

            parent = self.parent
            result = parent.delChild(self)
            if not result:
                self.blankContext()
            else:
                assert not result.isBroken()

            # Error check.
            assert not self.isBroken()
            assert not parent.isBroken()

            return result

    def insertChildSeq(self, child, after=True, newChild=None):
        '''insertChildSeq(child, after, [newChild]) - inserts a block before or
        after the specified child. If newChild is omitted, inserts and returns
        a new PassBlock. If after is True, inserts newChild after child,
        otherwise inserts it before.

        Note that insertChildSeq MUST be overridden by LongBlock
        or this definition will be recursive.'''

        if child not in self:
            raise KeyError, 'child does not belong to this block'

        # Creata a new long block.
        longBlock = LongBlock()
        # Remove child and put longBlock in its place.
        child.revert().mutate(longBlock)
        # Put child inside longBlock.
        longBlock.blocks[0].mutate(child)

        # tell longBlock to insert something before the child.
        result = longBlock.insertChildSeq_internal(child, after, newChild)

        # Error check.
        assert not self.isBroken()
        if result:
            assert not result.isBroken()
        assert not longBlock.isBroken()

        if self.master:
            self.master.touch()

        return result

    def insertBlockSeq(self, after=True, newObject=None):
        '''insertBlockSeq(after=True, newObject=None) inserts the specified
        block or a new PassBlock sequentially before or after the block.'''

        if not self.parent:
            raise ValueError('block does not have a context')

        if self.master:
            self.master.touch()

        return self.parent.insertChildSeq(self, after, newObject)

    def insertBlockPar(self, below=True, newObject=None):
        '''insertBlockPar(below=True, newObject=None) inserts the specified
        block or a new PassBlock in parallel with the block, either above
        it or below it as requested.'''

        if not self.parent:
            raise ValueError('block does not have a context')

        result = self.parent.insertParallelChild(self, below, newObject)

        if self.master:
            self.master.touch()

        return result

    def insertParallelChild(self, child, below=True, newChild=None):
        '''insertParallelChild(child, newChild, below) - inserts a block
        above or below the specified child. If newChild is omitted, inserts
        and returns a new PassBlock. If below is True, inserts newChild below
        child, otherwise inserts it above.

        This routine MUST be overridden by WideBlock.'''

        if child not in self:
            raise KeyError, 'child does not belong to this block'

        # Create a new wide block.
        wBlock = WideBlock()
        child.revert().mutate(wBlock)
        wBlock.blocks[0].mutate(child)

        assert not self.isBroken()
        assert not wBlock.isBroken()
        assert not child.isBroken()

        # Tell the wide block to do the real insertion.
        result = wBlock.insertParallelChild_internal(child, below, newChild)

        # Error check.
        assert not child.isBroken()
        assert not self.isBroken()
        assert not result.isBroken()
        assert not wBlock.isBroken()

        if self.master:
            self.master.touch()

        return result

    def enshroud(self, blockType):
        '''enshroud(blockType) - puts this block inside a new block of the
        specified type. The type specified must either implement the child
        member, or the blocks member. This method will first instantiate
        the specified class, then attempt to call newBlock.child.mutate(self),
        and failing that will call newBlock.blocks[0].mutate(self).

        Returns the enshrouding block.
        '''
        if not issubclass(blockType, Block):
            raise TypeError, 'specified block type must be a subclass of Block'

        newBlock = blockType()
        self.revert().mutate(newBlock)

        try:
            newBlock.child.mutate(self)
        except AttributeError:
            newBlock.blocks[0].mutate(self)

        if self.master:
            self.master.touch()

        return newBlock


class OneChildBlock(Block):
    def __init__(self, parent=None, nextLoop=None):
        super(OneChildBlock, self).__init__(parent, nextLoop)
        self.child = PassBlock(parent=self, nextLoop=nextLoop)

    def __contains__(self, child):
        return self.child is child

    def childAddEscape(self, child, index):
        # Insert the escape into my list.
        self.passingEscapes.insert(index, child.passingEscapes[index])
        # Notify parent.
        if self.parent:
            self.parent.childAddEscape(self, index)

    def swapChild(self, child, newChild):
        self.child = newChild
        self.g_modified = True

    def transmitContext(self):
        self.child.master = self.master
        self.child.transmitContext()

    def transmitLoopContext(self):
        self.child.setNextLoop(self.nextLoop)
        self.child.bnLevel = self.bnLevel
        self.child.transmitLoopContext()

    def fixLineNumbers(self):
        # First fix the child's numbers.
        self.child.fixLineNumbers()
        # Then fix mine.
        for i in range(0, len(self.child.lineNumbers), 2):
            l1, l2 = self.child.lineNumbers[i:i+2]
            # Check that I encompass this.
            for j in range(0, len(self.lineNumbers), 2):
                m1, m2 = self.lineNumbers[j:j+2]
                if m1 <= l1 <= l2 <= m2:
                    # Everything's ok.
                    break
            else:
                # We're missing it.
                self.lineNumbers.extend([l1, l2])
        # Now go through and connect any consecutive blocks.
        i = 0
        while i < len(self.lineNumbers):
            l1, l2 = self.lineNumbers[i:i+2]
            for j in range(i + 2, len(self.lineNumbers), 2):
                m1, m2 = self.lineNumbers[j:j+2]
                if l2 == m1:
                    self.lineNumbers[i+1] = m2
                    self.lineNumbers.pop(j)
                    self.lineNumbers.pop(j)
                    break
                elif l1 == m2:
                    self.lineNumbers[i] = m1
                    self.lineNumbers.pop(j)
                    self.lineNumbers.pop(j)
                    break
            i = i + 2

    def getBlockFromLine(self, lineNumber):
        result = super(OneChildBlock, self).getBlockFromLine(lineNumber)
        if result != None:
            chRes = self.child.getBlockFromLine(lineNumber)
            if chRes != None:
                return chRes
        return result

class MultiChildBlock(Block):
    def __init__(self, parent=None, nextLoop=None):
        super(MultiChildBlock, self).__init__(parent, nextLoop)
        self.blocks = []

    def __contains__(self, child):
        return child in self.blocks

    def isBroken(self):
        if super(MultiChildBlock, self).isBroken():
            return True
        for b in self.blocks:
            if b.parent is not self:
                print 'MultiChildBlock has child who disowns it:', b
                return True
        return False

    def childAddEscape(self, child, index):
        # Find the correct position and insert it there.
        i = self.blocks.index(child)
        newIndex = sum(len(b.passingEscapes) for b in self.blocks[:i]) + index
        self.passingEscapes.insert(newIndex, child.passingEscapes[index])
        # Notify parent.
        if self.parent:
            self.parent.childAddEscape(self, newIndex)

    def swapChild(self, child, newChild):
        self.blocks[self.blocks.index(child)] = newChild
        self.g_modified = True

    def transmitContext(self):
        for b in self.blocks:
            b.master = self.master
            b.transmitContext()

    def transmitLoopContext(self):
        for b in self.blocks:
            b.setNextLoop(self.nextLoop)
            b.bnLevel = self.bnLevel
            b.transmitLoopContext()

    def fixLineNumbers(self):
        for b in self.blocks:
            b.fixLineNumbers()
            for i in range(0, len(b.lineNumbers), 2):
                l1, l2 = b.lineNumbers[i:i+2]
                # Check that I encompass this.
                for j in range(0, len(self.lineNumbers), 2):
                    m1, m2 = self.lineNumbers[j:j+2]
                    if m1 <= l1 <= l2 <= m2:
                        # Everything's ok.
                        break
                else:
                    # We're missing it.
                    self.lineNumbers.extend([l1, l2])
        # Now go through and connect any consecutive blocks.
        i = 0
        while i < len(self.lineNumbers):
            l1, l2 = self.lineNumbers[i:i+2]
            for j in range(i + 2, len(self.lineNumbers), 2):
                m1, m2 = self.lineNumbers[j:j+2]
                if l2 == m1:
                    self.lineNumbers[i+1] = m2
                    self.lineNumbers.pop(j)
                    self.lineNumbers.pop(j)
                    break
                elif l1 == m2:
                    self.lineNumbers[i] = m1
                    self.lineNumbers.pop(j)
                    self.lineNumbers.pop(j)
                    break
            i = i + 2

    def getBlockFromLine(self, lineNumber):
        result = super(MultiChildBlock, self).getBlockFromLine(lineNumber)
        if result != None:
            for b in self.blocks:
                chRes = b.getBlockFromLine(lineNumber)
                if chRes != None:
                    return chRes
        return result

##################################
# specific block types
##################################

class PassBlock(Block):
    '''PassBlock(numRoutes=1, parent=None, nextLoop=None) -
    Class representing pass blocks. A pass block has any number of inputs
    and the same number of outputs and does nothing.'''

    def __init__(self, parent=None, nextLoop=None):
        super(PassBlock, self).__init__(parent=parent, nextLoop=nextLoop)
        self.numOutputs = self.numInputs = 1

        if self.parent:
            self.bnLevel = self.parent.bnLevel

        self.g_desiredShape = 1.

    def isBroken(self):
        if super(PassBlock, self).isBroken():
            return True
        return self.numInputs != self.numOutputs

    def duplicate(self):
        result = PassBlock()
        assert not result.isBroken()
        return result

    def distil(self):
        return [self.lineNumbers]

    @staticmethod
    def reconstitute(essence):
        [lineNums] = essence
        result = PassBlock()
        result.lineNumbers = lineNums
        assert not result.isBroken()
        return result

    def reverseRoute(self, strandLabel, exit):
        # Catch label.
        self.tagLabel = strandLabel
        return []

    def tagRoute(self, tagBlock, exit):
        # Pass straight through.
        if self.parent:
            self.parent.tagStrand(tagBlock, self, exit)

    def parse(self, parser):
        # Does nothing
        parser.addLabel(self.tagLabel)

    def g_draw(self):
        if self.master == None:
            return

        width = self.g_relPlacement.scaleToHeight()
        sqSize = 0.2 * min(1., width)
        self.g_clearBlock()
        self.g_border = painter.BlockBorder(self, width, 1.0)
        self.g_addFeature(painter.Rectangle(self, sqSize, sqSize, RectType.Pass))

        self.g_rIn = [(-sqSize, 0.)]
        self.g_rOut = [(sqSize, 0.)]

        self.g_modified = False

    def g_wideDesiredShape(self):
        for b in self.parent.blocks:
            if not isinstance(b, PassBlock):
                return 3.
        return self.g_desiredShape

    def g_longDesiredShape(self):
        for b in self.parent.blocks:
            if not isinstance(b, PassBlock):
                return 0.25
        return self.g_desiredShape

    # A PassBlock can mutate into any kind of block.
    def mutate(self, targetBlock):
        '''mutate(targetBlock) - inserts targetBlock into the flowchart in
        place of this PassBlock. Returns the resulting block.

        targetBlock must be a free block.'''
        if not self.parent:
            return

        if isinstance(targetBlock, type):
            targetBlock = targetBlock()
        elif targetBlock.parent != None:
            raise ValueError('targetBlock must be a free block')

        # Remove escapes from my parent.
        for e in self.passingEscapes:
            self.parent.childRemoveEscape(e)

        # Copy my context into the target block.
        targetBlock.setContext(self)
        self.parent.swapChild(self, targetBlock)

        # I'm now a free block.
        self.blankContext()

        # Pass escapes on to new block.
        for i in range(len(targetBlock.passingEscapes)):
            targetBlock.parent.childAddEscape(targetBlock, i)

        # Error check
        assert not self.isBroken()
        assert not targetBlock.isBroken()
        assert not targetBlock.parent.isBroken()

        if targetBlock.master:
            targetBlock.master.touch()

        return targetBlock

class IfBlock(Block):
    '''IfBlock(condition='', parent=None, nextLoop=None) - Class
    representing if blocks.'''

    def __init__(self, condition='', parent=None, nextLoop=None):
        '''condition is the condition of the if statement.'''
        super(IfBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        self.numInputs = 1
        self.numOutputs = 2
        self.condition = condition
        self.yesFirst = True

        self.branchLabels = [None, None]
        self.g_desiredShape = 0.75

    def isBroken(self):
        if super(IfBlock, self).isBroken():
            return True
        if self.numInputs != 1:
            return True
        if self.numOutputs != 2:
            return True
        return False

    def duplicate(self):
        result = IfBlock(self.condition)
        result.yesFirst = self.yesFirst
        assert not result.isBroken()

        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [self.lineNumbers, self.condition, int(self.yesFirst)]

    @staticmethod
    def reconstitute(essence):
        lineNums, condition, yesFirst = essence
        result = IfBlock(condition)
        result.yesFirst = bool(yesFirst)
        result.lineNumbers = lineNums

        assert not result.isBroken()
        return result

    def reverseRoute(self, strandLabel, exit):
        # Check which branch to save it on.
        self.branchLabels[exit] = strandLabel

        return []

    def tagRoute(self, tagBlock, exit):
        # Check which branch to put it on.
        self.tags[exit] = tagBlock

    def prepBlock(self):
        badConsts = super(IfBlock, self).prepBlock()

        # Initialise any strand label variables.
        self.branchLabels = [None, None]
        self.tags = [None, None]

        # Check that this block is valid and raise EPrepBlockError if it's not.
        try:
            c = compile('if %s: pass\n' % self.condition, '', 'exec')
            # Save the constants.
            badConsts.extend(c.co_consts)
        except:
            raise EPrepBlockError, (self, 'invalid if condition')

        return badConsts

    def parse(self, parser):
        parser.addLine('if %s:' % self.condition)

        if self.yesFirst: i = 0
        else: i = 1

        # Put the first label and tag.
        parser.indent()
        parser.addTag(self, self.tags[i])
        parser.addLabel(self.branchLabels[i])
        parser.dedent()

        parser.addLine('else:')

        if self.yesFirst: i = 1
        else: i = 0

        # Put the second label and tag.
        parser.indent()
        parser.addTag(self, self.tags[i])
        parser.addLabel(self.branchLabels[i])
        parser.dedent()

    def g_draw(self):
        if self.master == None:
            return
        if not self.g_modified:
            return
        self.g_modified = False

        self.g_clearBlock()
        self.g_relPlacement.scaleDesired(0.75)
        width = (self.g_relPlacement.shape * self.g_relPlacement.area) ** 0.5
        height = (self.g_relPlacement.area / self.g_relPlacement.shape)** 0.5

        # Size cutoff.
        self.g_clearBlock()
        self.g_sizeCutoff = 0.001
        self.g_border = painter.BlockBorder(self, width, height)
        self.g_addCutoffFeature(painter.Rectangle(self, 0.75, 1., \
                                                  RectType.If))

        # Draw the if diamond.
        self.g_addFeature(painter.Diamond(self, (0., 0.), 0.5))

        # Draw the text.
        self.g_addFeature(painter.InteractiveText(self, [''], ['?'], \
                    [self.condition], 0.5, self.textCallback, (0., 0.)))
        if self.yesFirst:
            self.g_addFeature(painter.Text(self, 'Yes', 0.25, (-0.25, -0.75)))
            self.g_addFeature(painter.Text(self, 'No', 0.25, (-0.25, 0.75)))
        else:
            self.g_addFeature(painter.Text(self, 'No', 0.25, (-0.25, -0.75)))
            self.g_addFeature(painter.Text(self, 'Yes', 0.25, (-0.25, 0.75)))

        # Draw the input route.
        self.g_addFeature(painter.Connection(self, (-width, 0.), (-0.5, 0.)))
        self.g_rIn = [(-width, 0.)]

        # Draw the output routes.
        self.g_rOut = []
        for i in (-1, 1):
            p2 = (0.4*width, 0.7*i)
            self.g_addFeature(painter.Connection(self, (0., i*0.5), p2, \
                                                 i*pi/3.))
            self.g_addFeature(painter.Connection(self, p2, (width, i*0.5)))
            self.g_rOut.append((width, i*0.5))

        # Draw the in arrow.
        self.g_addFeature(painter.Arrows(self, [(-0.5, 0.)]))
        self.g_addCutoffFeature(painter.Arrows(self, self.g_rIn))

        self.g_modified = False

    def textCallback(self, values):
        '''internal - callback function for TextFeature to change the
        condition of this if statement.'''
        self.condition = values[0]

        if self.master:
            self.master.touch()

    def changeCondition(self, condition):
        '''(condition) - changes the condition of this if statement.'''
        self.condition = condition
        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

        if self.master:
            self.master.touch()

class BottleneckBlock(OneChildBlock):
    '''BottleneckBlock(parent=None, nextLoop=None) - Class
    representing bottleneck blocks.'''

    def __init__(self, parent=None, nextLoop=None):
        super(BottleneckBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        self.numOutputs = self.numInputs = 1

        # Create one child block.
        self.child.setMaxInputs(1)
        self.label = None

    def isBroken(self):
        if super(BottleneckBlock, self).isBroken():
            return True
        return self.numInputs != self.numOutputs

    def duplicate(self):
        result = BottleneckBlock()
        result.child.mutate(self.child.duplicate())
        result.setNumRoutes(self.numInputs)
        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [self.lineNumbers, \
                self.numInputs, approvedBlockTypes.index(type(self.child)), \
                self.child.distil()]

    @staticmethod
    def reconstitute(essence):
        lineNums, numInputs, a, b = essence
        result = BottleneckBlock()
        result.child.mutate(approvedBlockTypes[a].reconstitute(b))
        result.setNumRoutes(numInputs)
        result.lineNumbers = lineNums

        assert not result.isBroken()
        return result

    def childOutputsChanged(self, child, insert, index):
        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def childInputsChanged(self, child, insert, index):
        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def setNumRoutes(self, numRoutes):
        '''setNumRoutes(numRoutes) - sets the number of routes going through
        this block.'''
        self.setNumInputs(numRoutes)
        self.setNumOutputs(numRoutes)
        assert not self.isBroken()

        if self.master:
            self.master.touch()

    def swapChild(self, child, newChild):
        super(BottleneckBlock, self).swapChild(child, newChild)
        newChild.setMaxInputs(1)
        self.g_childDesiredShapeChange(newChild)

    def reverseRoute(self, strandLabel, exit):
        # Compiler optimisation: tagging
        if self.numInputs == 1 >= self.numOutputs:
            self.tagLabel = strandLabel

        # Nothing traps the labels.
        return [exit]

    def prepBlock(self):
        badConsts = super(BottleneckBlock, self).prepBlock()

        # Initialise any strand label variables.
        self.label = None

        # Call the prepBlock() method of any child blocks.
        badConsts.extend(self.child.prepBlock())

        return badConsts

    def labelStrand(self, strandLabel, child, entry):
        # Catch the label.
        if entry == 0:
            self.label = strandLabel

    def parse(self, parser):
        parser.addLine('__strand_stack__.append(__strand__)')

        # Insert label if required.
        parser.addLabel(self.label)

        # Get the child's parsed form.
        parser.parseBlock(self.child, 0)

        # Now pop the old strand.
        parser.addLine('__strand__ = __strand_stack__.pop()')

    def transmitLoopContext(self):
        self.bnLevel = self.bnLevel + 1
        super(BottleneckBlock, self).transmitLoopContext()

    def g_childDesiredShapeChange(self, child):
        self.g_setDesiredShape((6. + 5. * child.g_desiredShape) / 6.)

    def g_draw(self):
        if self.master == None:
            return
        if not self.g_modified:
            self.g_drawChild(self.child)
            if not self.g_modified:
                return

        self.g_clearBlock()
        maxHeight = self.g_relPlacement.scaleToWidth()
        blockHeight = min(maxHeight, 1. / self.g_desiredShape)
        a = blockHeight / 12.

        # First calculate route locations.
        delta = 2 * blockHeight / (self.numInputs + 1)
        rIn = []
        rOut = []
        for i in range(self.numInputs):
            y = -blockHeight + (i+1) * delta
            rIn.append((-1., y))
            rOut.append((1., y))
        self.g_rIn, self.g_rOut = rIn, rOut

        self.g_border = painter.BlockBorder(self, 1., maxHeight)

        # Size cutoff.
        self.g_sizeCutoff = 0.001
        self.g_addCutoffFeature(painter.Rectangle(self, 1., maxHeight, \
                                                  RectType.Solid))
        self.g_addCutoffFeature(painter.Arrows(self, rIn))

        chX = 1. - 6. * a
        chY = blockHeight - a

        # Draw the child block.
        chIn, chOut = self.g_addChild(self.child, chX*chY, chX/chY, \
                                      (-4.*a, 0.))

        # Lines to the child.
        for pt in rIn:
            self.g_addFeature(painter.Connection(self, pt, chIn[0]))

        # From the child.
        focus = (1.-4.*a, 0.)
        for x,y in chOut:
            self.g_addFeature(painter.Connection(self, (x, y), focus))
        for pt in rOut:
            self.g_addFeature(painter.Connection(self, focus, pt))

        # Draw the border.
        self.g_addFeature(painter.Rectangle(self, 1., blockHeight, \
                                            RectType.Border))

        self.g_modified = False

class ExecBlock(Block):
    '''ExecBlock(lines=[], parent=None, nextLoop=None) - Class
    representing execution blocks.'''

    def __init__(self, lines=None, parent=None, nextLoop=None):
        super(ExecBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        self.numOutputs = self.numInputs = 1
        if lines == None:
            lines = ['pass']
        self.lines = lines
        self.g_desiredShape = 1.

    def isBroken(self):
        if super(ExecBlock, self).isBroken():
            return True
        return self.numInputs != 1 or self.numOutputs != 1

    def duplicate(self):
        result = ExecBlock(list(self.lines))
        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [self.lineNumbers] + list(self.lines)

    @staticmethod
    def reconstitute(essence):
        lines = list(essence)
        lineNums = lines.pop(0)
        result = ExecBlock(lines)
        result.lineNumbers = lineNums
        assert not result.isBroken()
        return result

    def reverseRoute(self, label, exit):
        # Compiler optimisation: tagging
        self.tagLabel = label

        self.label = label
        return []

    def tagRoute(self, tagBlock, exit):
        self.tag = tagBlock

    def prepBlock(self):
        bc = super(ExecBlock, self).prepBlock()
        self.tag = None
        self.label = None
        return bc

    def parse(self, parser):
        # Create a new parser for this little block.
        newParser = parser.newParser(self)
        newParser.addLines([l for l in self.lines])
        try:
            codeObj = newParser.compile()
        except:
            val = sys.exc_info()[1]
            raise ECompileBlockError, (self, (str(val), val))

        # Add the block into the program.
        parser.addLine('exec %s' % parser.newConst(codeObj))
        parser.addTag(self, self.tag)
        parser.addLabel(self.label)

    def g_draw(self):
        if not self.g_modified or self.master == None:
            return
        self.g_modified = False

        # Default processing: draw a box.
        self.g_relPlacement.scaleDesired(self.g_desiredShape)
        self.g_clearBlock()
        self.g_border = painter.BlockBorder(self, 1.0, 1.0)
        self.g_addFeature(painter.Rectangle(self, 0.9, 0.9, RectType.Solid))
        self.g_addFeature(painter.Arrows(self, [(-.9, 0)]))

        self.g_rIn = [(-0.9, 0.)]
        self.g_rOut = [(0.9, 0.)]

        self.g_addFeature(painter.MultilineText(self, self.lines[:], .9, \
                            self.textCallback, minWrapWidth=300, \
                            followText='... '))

    def textCallback(self, vals):
        self.lines = vals[:]

        if self.master:
            self.master.touch()

class DefBlock(OneChildBlock):
    '''DefBlock(fnName='', params='', parent=None, nextLoop=None, comment=None)
    - Class representing function definition blocks.'''

    def __init__(self, fnName='', params='', parent=None, nextLoop=None,
                 comment=None):
        super(DefBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        if comment == None:
            self.comment = ['<description>']
        else:
            self.comment = comment

        self.numOutputs = self.numInputs = 1
        self.fnName = fnName
        self.params = params
        self.label = None
        self.child.setMaxInputs(1)
        self.returnExpressions = ['']
        self.map = CollapseMapping(self.child)

        self.g_desiredShape = 2.236

    def isBroken(self):
        if super(DefBlock, self).isBroken():
            return True
        if self.numInputs != 1 or self.numOutputs != 1:
            print 'DefBlock in: %d, out: %d' % (self.numInputs, self.numOutputs)
            return True
        if self.map.prevBlock is not self.child:
            print 'DefBlock map prev is not child.'
            return True
        if self.map.isBroken():
            print 'DefBlock map broken.'
            return True
        return False

    def duplicate(self):
        result = DefBlock(self.fnName, self.params, comment=self.comment[:])
        for i in range(len(self.returnExpressions)-1):
            result.modifyReturnExpressions(True, 0)
        result.child.mutate(self.child.duplicate())
        result.map.connections = list(self.map.connections)

        result.returnExpressions = list(self.returnExpressions)
        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [self.lineNumbers, \
                self.fnName, self.params, self.comment[:], \
                approvedBlockTypes.index(type(self.child)), \
                self.child.distil(), list(self.map), \
                list(self.returnExpressions)]

    @staticmethod
    def reconstitute(essence):
        lineNums, fnName, params, comment, a, b, connections, ret = essence
        result = DefBlock(fnName, params, comment=comment[:])
        for i in range(len(ret)-1):
            result.modifyReturnExpressions(True, 0)
        result.child.mutate(approvedBlockTypes[a].reconstitute(b))
        result.map.connections = list(connections)
        result.lineNumbers = lineNums
        result.returnExpressions = list(ret)
        assert not result.isBroken()
        return result

    def childInputsChanged(self, child, insert, index):

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def childOutputsChanged(self, child, insert, index):
        # Update the map.
        self.map.modifyInputs(insert, index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def swapChild(self, child, newChild):
        super(DefBlock, self).swapChild(child, newChild)
        newChild.setMaxInputs(1)
        self.map.prevBlock = newChild
        self.map.setNumInputs(newChild.numOutputs)

    def reverseRoute(self, label, exit):
        # Compiler optimisation: tagging
        if self.numInputs == 1 >= self.numOutputs:
            self.tagLabel = label

        self.postLabel = label
        return []

    def labelStrand(self, label, child, entry):
        # Child is wanting to label the strand.
        if entry == 0:
            self.label = label

    def tagRoute(self, tagBlock, exit):
        self.tag = tagBlock

    def prepBlock(self):
        badConsts = super(DefBlock, self).prepBlock()

        # Init label.
        self.label = None
        self.tag = None
        self.postLabel = None

        # Check validity of name.
        try:
            compile('def %s(): pass\n' % self.fnName, '', 'exec')
        except SyntaxError:
            raise EPrepBlockError, (self, 'invalid function name')

        # Check validity of parameters.
        try:
            code = compile('def foo(%s): pass\n' % self.params, '', 'exec')
            # Save constants.
            badConsts.extend(code.co_consts)
        except SyntaxError:
            raise EPrepBlockError, (self, 'invalid parameter list')

        # Check validity of output expressions.
        for exp in self.returnExpressions:
            if exp != '':
                try:
                    code = compile('%s\n' % exp, '', 'eval')
                    # Save constants.
                    badConsts.extend(code.co_consts)
                except SyntaxError:
                    raise EPrepBlockError, (self, 'invalid return expression')

        # Don't prepBlock the child until we need its badConsts

        # Return constants used.
        return badConsts

    def parse(self, parser):
        # Prep the child block and get its bad constants.
        badConsts = self.child.prepBlock()

        # Trace back return routes
        for i in range(len(self.returnExpressions)):
            lbl = self.returnExpressions[i]
            if lbl == '':
                lbl = 'None'
            routes = self.map.reverseRoute(lbl, i)

            newRoutes = []
            for r in routes:
                newRoutes.extend(self.child.reverseRoute(lbl, r))
            if len(newRoutes) > 0:
                self.label = lbl

        # Note that we need to parse the contents separately and insert them
        #  because otherwise we cannot substitute constants within the
        #  body of the function.

        # Parse the inside of the block with a new parser.
        newParser = DefBlockParser(parser, self, self.fnName, \
                                   badConsts=badConsts)

        newParser.addLine('def %s(%s):' % (self.fnName, self.params))
        newParser.indent()
        if self.comment:
            newParser.addLine(newParser.newConst('\n'.join(self.comment)))
        newParser.addLine('__strand_stack__ = []')
        newParser.addLabel(self.label)
        newParser.parseBlock(self.child, 0)

        # Add the return values.
        newParser.addLine('return eval(__strand__)')

        # Extract the code object from compiled code.
        codeObj = newParser.compile()

        # Add dummy function code to the parser and link with code object.
        parser.addLine('def %s(%s): pass' % (self.fnName, self.params))
        parser.addNamedCodeObject(self.fnName, codeObj)

        # Add a tag.
        parser.addTag(self, self.tag)
        parser.addLabel(self.postLabel)

    def transmitLoopContext(self):
        # Loop context does not enter funtions or classes.
        self.child.setNextLoop(None)
        self.child.bnLevel = self.bnLevel
        self.child.transmitLoopContext()

    def g_draw(self):
        if self.master == None:
            return
        if not self.g_modified:
            self.g_drawChild(self.child)
            if not self.g_modified:
                return

        self.g_clearBlock()
        self.g_relPlacement.scaleDesired(self.g_desiredShape)

        self.g_border = painter.BlockBorder(self, 2.236, 1.)
        self.g_sizeCutoff = 0.3

        # Size cutoff shape.
        self.g_addCutoffFeature(painter.Rectangle(self, 2.236, 1.0, \
                                                  RectType.Def))
        self.g_addCutoffFeature(painter.Arrows(self, [(-2.236, 0.)]))
        self.cutoffs = []
        self.cutoffs.append(painter.InteractiveText(self, ['def ', '('], \
                             ['', ')'], [self.fnName, self.params], \
                             1., self.textCallback, (-1.236, 0.)))
        self.cutoffs.append(painter.MultilineText(self, self.comment, \
                             1., self.commentCallback, (1., 0.), \
                             painter.cmtColour))
        for c in self.cutoffs:
            self.g_addCutoffFeature(c)

        # Standard shape.
        self.g_addFeature(painter.Rectangle(self, 2.236, 1.0, RectType.Border))

        rIn, rChOut = self.g_addChild(self.child, .81, 1., (0.,0.))
        self.g_addFeature(painter.InteractiveText(self, ['def ','('], \
                          ['', ')'], [self.fnName, self.params], \
                          0.382, self.textCallback, (-1.568, -0.618)))
        self.g_addFeature(painter.MultilineText(self, self.comment, \
                          0.618, self.commentCallback, (-1.568, 0.382), \
                          painter.cmtColour))

        # Draw route in.
        self.g_addFeature(painter.Connection(self, (-1.618, 0), rIn[0]))

        # Calc positions of returns and draw returnexpressions.
        rOut = []
        delta = 2. / (1. + self.map.numOutputs)
        for i in range(self.map.numOutputs):
            y = -1. + (i+1) * delta
            rOut.append((1.5, y))
            self.g_addFeature(painter.InteractiveText(self, ['return '], [''], \
                        [self.returnExpressions[i]], min(0.5*delta, 0.309), \
                        (self.returnExpCallback, [i]), (1.927, y)))

        # Draw the map to the returns.
        spacings = [rChOut[0][1] + 1.] + \
                   [rChOut[j+1][1] - rChOut[j][1] for j in range(len(rChOut)-1)] \
                   + [1. - rChOut[-1][1]]
        ptIn = self.spacePoints(spacings, (.95, -1.), (.95, 1.))
        for j in range(self.map.numInputs):
            self.g_addFeature(painter.Connection(self, rChOut[j], ptIn[j]))

        ptIn = [(ptIn[j], 0.) for j in range(self.map.numInputs)]
        ptOut = [(n, 0.) for n in rOut]
        self.g_addFeature(painter.MapFeature(self, 1., \
                                             ptIn, ptOut, self.map))

        # Draw arrow heads.
        self.g_addFeature(painter.Arrows(self, [(1.618, y) for x,y in rOut]))
        self.g_addFeature(painter.Arrows(self, [(-2.236, 0.)]))
        self.g_addCutoffFeature(painter.Arrows(self, [(-2.236, 0.)]))

        self.g_rIn, self.g_rOut = [(-2.236, 0.)], [(2.236, 0.)]

        self.g_modified = False

    def textCallback(self, values):
        'internal.'
        self.fnName, self.params = values
        self.cutoffs[0].setValues(list(values))

        if self.master:
            self.master.touch()

    def commentCallback(self, values):
        'internal.'
        self.comment = list(values)
        self.cutoffs[1].setValues(list(values))

        if self.master:
            self.master.touch()

    def returnExpCallback(self, values, index):
        [self.returnExpressions[index]] = values

        if self.master:
            self.master.touch()

    def setReturnExpression(self, index, expression):
        '''setReturnExpression(index, expression) - sets the return expression
        with the given index to the given expression.'''

        self.returnExpressions[index] = expression
        assert not self.isBroken()

        if self.master:
            self.master.touch()

    def modifyReturnExpressions(self, insert, index):
        '''Adds or removes a return expression from the list of return values.
        '''

        if insert:
            self.returnExpressions.insert(index, '')
        else:
            self.returnExpressions.pop(index)

        # Tell the mapping.
        self.map.modifyOutputs(insert, index)
        if self.parent:
            self.parent.childOutputsChanged(self, insert, index)

        assert not self.isBroken()

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True
            self.master.touch()

class ClassBlock(OneChildBlock):
    '''ClassBlock(clsName='', inherit='', parent==None, nextLoop=None) -
    Class representing class definition blocks. A class block can have
    any number of inputs and any number of outputs.'''

    def __init__(self, clsName='', inherit='object', parent=None,
                 nextLoop=None, comment=None):
        super(ClassBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        if comment == None:
            self.comment = ['<description>']
        else:
            self.comment = comment

        self.numOutputs = self.numInputs = 1
        self.clsName = clsName
        self.inherit = inherit
        self.label = None

        self.g_desiredShape = 1.618

    def isBroken(self):
        if super(ClassBlock, self).isBroken():
            return True
        return self.numInputs != self.child.numInputs or \
               self.numOutputs != self.child.numOutputs

    def duplicate(self):
        result = ClassBlock(self.clsName, self.inherit, comment=self.comment[:])
        result.child.mutate(self.child.duplicate())
        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [self.lineNumbers, \
                self.clsName, self.inherit, self.comment[:], \
                approvedBlockTypes.index(type(self.child)), self.child.distil()]

    @staticmethod
    def reconstitute(essence):
        lineNums, clsName, inherit, comment, a, b = essence
        result = ClassBlock(clsName, inherit, comment = comment[:])
        result.child.mutate(approvedBlockTypes[a].reconstitute(b))
        result.lineNumbers = lineNums
        assert not result.isBroken()
        return result

    def setMaxInputs(self, maxInputs):
        # Child can only have as many inputs as me.
        super(ClassBlock, self).setMaxInputs(maxInputs)
        self.child.setMaxInputs(maxInputs)

    def childOutputsChanged(self, child, insert, index):
        self.numOutputs = child.numOutputs
        if self.parent:
            self.parent.childOutputsChanged(self, insert, index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def childInputsChanged(self, child, insert, index):
        self.numInputs = child.numInputs
        if self.parent:
            self.parent.childInputsChanged(self, insert, index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def swapChild(self, child, newChild):
        super(ClassBlock, self).swapChild(child, newChild)
        self.setNumInputs(newChild.numInputs)
        self.setNumOutputs(newChild.numOutputs)

    def prepBlock(self):
        badConsts = super(ClassBlock, self).prepBlock()

        # Init label.
        self.label = None

        # Check validity of name.
        try:
            compile('class %s(object): pass\n' % self.clsName, '', 'exec')
        except SyntaxError:
            raise EPrepBlockError, (self, 'invalid class name')

        # Check validity of parameters.
        try:
            compile('class foo(%s): pass\n' % self.inherit, '', 'exec')
        except SyntaxError:
            raise EPrepBlockError, (self, 'invalid inheritance list')

        # Don't prepBlock the child until we need its badConsts

        # Return constants used.
        return badConsts

    def reverseRoute(self, label, exit):
        # Compiler optimisation: tagging
        if self.numInputs == 1 >= self.numOutputs:
            self.tagLabel = label

        # All routes go straight into the single block.
        return self.child.reverseRoute(label, exit)

    def labelStrand(self, label, child, entry):
        # Child is wanting to label the strand.
        if entry == 0:
            self.label = label

    def parse(self, parser):
        # Prep the child block and get its bad constants.
        badConsts = self.child.prepBlock()

        # Parse the inside of the block with a new parser.
        newParser = DefBlockParser(parser, self, self.clsName, \
                                   badConsts=badConsts)

        newParser.addLine('class %s(%s):' % (self.clsName, self.inherit))
        newParser.indent()
        if self.comment:
            newParser.addLine(newParser.newConst('\n'.join(self.comment)))
        newParser.parseBlock(self.child, 0)
        newParser.dedent()

        # Extract the code object from compiled code.
        codeObj = newParser.compile()

        # Add dummy function code to the parser and link with code object.
        parser.addLabel(self.label)
        parser.addLine('class %s(%s): pass' % (self.clsName, self.inherit))
        parser.addNamedCodeObject(self.clsName, codeObj)

    def transmitLoopContext(self):
        # Loop context does not enter funtions or classes.
        self.child.setNextLoop(None)
        self.child.bnLevel = self.bnLevel
        self.child.transmitLoopContext()

    def g_draw(self):
        if self.master == None:
            return
        if not self.g_modified:
            self.g_drawChild(self.child)
            if not self.g_modified:
                return

        self.g_clearBlock()
        self.g_relPlacement.scaleDesired(self.g_desiredShape)
        self.g_border = painter.BlockBorder(self, 1.618, 1.)
        self.g_sizeCutoff = 0.3

        # Size cutoff shape.
        self.g_addCutoffFeature(painter.Rectangle(self, 1.618, 1.0, \
                                                  RectType.Def))
        self.g_addCutoffFeature(painter.Arrows(self, [(-1.618, 0.)]))
        self.cutoffs = []
        self.cutoffs.append(painter.InteractiveText(self, ['class ', '('], \
                            ['', ')'], [self.clsName, self.inherit], \
                            0.618, self.textCallback, (-1., 0.)))
        self.cutoffs.append(painter.MultilineText(self, self.comment, \
                            1., self.commentCallback, (.618, 0.), \
                            painter.cmtColour))
        for c in self.cutoffs:
            self.g_addCutoffFeature(c)

        # Standard shape.
        self.g_addFeature(painter.Rectangle(self, 1.618, 1.0, RectType.Border))

        rIn, rOut = self.g_addChild(self.child, .81, 1., (.618,0.))
        self.g_addFeature(painter.InteractiveText(self, ['class ','('], \
                          ['', ')'], [self.clsName, self.inherit], \
                          0.382, self.textCallback, (-.95, -0.618)))
        self.g_addFeature(painter.MultilineText(self, self.comment, \
                          0.618, self.commentCallback, (-.95, 0.382), \
                          painter.cmtColour))


        # Extend input and output routes.
        for i in range(len(rIn)):
            p2 = (-1.618, rIn[i][1])
            self.g_addFeature(painter.Connection(self, p2, rIn[i]))
            rIn[i] = p2
        self.g_addCutoffFeature(painter.Arrows(self, rIn))
        for i in range(len(rOut)):
            p2 = (1.618, rOut[i][1])
            self.g_addFeature(painter.Connection(self, rOut[i], p2))
            rOut[i] = p2

        self.g_rIn, self.g_rOut = rIn, rOut

        self.g_modified = False

    def textCallback(self, values):
        'internal.'
        self.clsName, self.inherit = values
        self.cutoffs[0].setValues(list(values))

        if self.master:
            self.master.touch()

    def commentCallback(self, values):
        'internal.'
        self.comment = list(values)
        self.cutoffs[1].setValues(list(values))

        if self.master:
            self.master.touch()

class ProcedureBlock(OneChildBlock):
    '''ProcedureBlock(prName='', params='', parent=None, nextLoop=None,
    comment=None)'''

    def __init__(self, prName='', params='', parent=None, nextLoop=None,
                 comment=None):
        super(ProcedureBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        if comment == None:
            self.comment = ['<description>']
        else:
            self.comment = comment

        self.numInputs = 1
        self.numOutputs = 1
        self.routesIn = ['']
        self.routesOut = ['']

        self.prName = prName
        self.params = params
        self.labels = None
        self.child.setMaxInputs(0)
        self.map = CollapseMapping(self.child)
        self.g_desiredShape = 2.545

    def isBroken(self):
        if super(ProcedureBlock, self).isBroken():
            return True
        if self.numInputs != 1 or self.numOutputs != 1:
            print 'ProcedureBlock in: %d, out: %d' % (self.numInputs, \
                                                      self.numOutputs)
            return True
        if self.map.numOutputs != len(self.routesOut):
            print 'ProcedureBlock map out: %d, routes out: %s' % \
                  (self.map.numOutputs, str(self.routesOut))
            return True
        if self.map.numInputs != self.child.numOutputs:
            print 'ProcedureBlock map in: %d, child out: %d' % \
                  (self.map.numInputs, self.child.numOutputs)
            return True
        if self.child.numInputs != len(self.routesIn):
            print 'ProcedureBlock child in: %d, routes in: %s' % \
                  (self.child.numInputs, str(self.routesIn))
            return True
        if self.map.isBroken():
            print 'ProcedureBlock map broken'
            return True
        return False

    def duplicate(self):
        result = ProcedureBlock(self.prName, self.params, \
                                comment=self.comment[:])
        result.child.mutate(self.child.duplicate())
        result.map.connections = list(self.map.connections)
        result.routesIn = self.routesIn
        result.routesOut = self.routesOut
        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [self.lineNumbers, \
                self.prName, self.params, self.comment[:], \
                approvedBlockTypes.index(type(self.child)), \
                self.child.distil(), list(self.map), \
                list(self.routesIn), list(self.routesOut)]

    @staticmethod
    def reconstitute(essence):
        lineNums, prName, params, comment, a, b, connections, rIn, rOut = essence
        result = ProcedureBlock(prName, params, comment=comment[:])
        result.child.mutate(approvedBlockTypes[a].reconstitute(b))
        result.map.numOutputs = len(rOut)
        result.map.connections = list(connections)
        result.lineNumbers = lineNums
        result.routesIn = rIn
        result.routesOut = rOut
        assert not result.isBroken()

        return result

    def childOutputsChanged(self, child, insert, index):
        # Fix up the mapping.
        self.map.modifyInputs(insert, index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def childInputsChanged(self, child, insert, index):
        # Fix up the routes list.
        if insert:
            self.routesIn.insert(index, '')
        else:
            self.routesIn.pop(index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def swapChild(self, child, newChild):
        super(ProcedureBlock, self).swapChild(child, newChild)
        self.map.prevBlock = newChild
        self.map.setNumInputs(newChild.numOutputs)
        newChild.setMaxInputs(None)

    def prepBlock(self):
        badConsts = super(ProcedureBlock, self).prepBlock()

        # Init labels.
        self.labels = [None] * self.child.numInputs
        self.tag = None
        self.postLabel = None

        # Check validity of name.
        try:
            compile('def %s(): pass\n' % self.prName, '', 'exec')
        except SyntaxError:
            raise EPrepBlockError, (self, 'invalid procedure name')

        # Check validity of parameters.
        try:
            code = compile('def foo(%s): pass\n' % self.params, '', 'exec')
            # Save constants.
            badConsts.extend(code.co_consts)
        except SyntaxError:
            raise EPrepBlockError, (self, 'invalid parameter list')

        # If it's in a class, check that it's got 1 non-keyword argument.
        if isinstance(self.parent, ClassBlock):
            # There must be no equals before first comma.
            commaPos = self.params.find(',')
            if commaPos < 0:
                arg1 = self.params
            else:
                arg1 = self.params[:commaPos]

            if arg1.find('=') >= 0:
                raise EPrepBlockError, (self, 'needs at least one non-keyword argument')

        # Check validity of routesIn and routesOut.
        error = Identifier.preRouteNamesError(self.routesOut)
        error = error or Identifier.postRouteNamesError(self.routesIn)
        if error:
            raise EPrepBlockError, (self, error)

        # Don't prepBlock the child until we need its badConsts

        # Return constants used.
        return badConsts

    def reverseRoute(self, label, exit):
        # Compiler optimisation: tagging
        self.tagLabel = label

        self.postLabel = label
        return []

    def labelStrand(self, label, child, entry):
        # Child is wanting to label the strand.
        self.labels[entry] = label

    def tagRoute(self, tagBlock, exit):
        self.tag = tagBlock

    def parse(self, parser):
        '''parse(parser) - internal.
        A procedure is simply a function which takes an extra argument for
        route, and returns a route.
        '''

        # Prep the child block and get its bad constants.
        badConsts = self.child.prepBlock()

        # Tell the child what the different routes mean.
        for i in range(self.map.numOutputs):
            label = self.routesOut[i]
            if label == '':
                # No label - strand is labeled with (index, None).
                label = (i, None)
            elif label[0] == '?':
                # Wildcard label - strand is labeled with expression to eval.
                label = label[1:]
            else:
                # Standard label - strand is labeled with index and label.
                label = (i, label)

            for j in self.map.reverseRoute(label, i):
                for k in self.child.reverseRoute(label, j):
                    # Got right through mapping and block.
                    self.labels[k] = label

        # Parse the inside of the block with a new parser.
        newParser = DefBlockParser(parser, self, self.prName, \
                                   badConsts=badConsts)

        # Generate the definition line.
        p = self.parent
        while not isinstance(p, ClassBlock):
            if isinstance(p, (WideBlock, LongBlock, GroupingBlock)):
                p = p.parent
            else:
                # It's not in a class.
                defLine = 'def %s(__strand__, %s):' % (self.prName, self.params)
                break
        else:
            # If it's in a class we must leave a space for self.
            cPos = self.params.find(',')
            if cPos == -1:
                defLine = 'def %s(%s, __strand__):' % (self.prName, \
                                                       self.params)
            else:
                defLine = 'def %s(%s, __strand__%s):' % \
                          (self.prName, self.params[:cPos], self.params[cPos:])

        newParser.addLine(defLine)
        newParser.indent(1)
        if self.comment:
            newParser.addLine(newParser.newConst('\n'.join(self.comment)))
        newParser.addLine('__strand_stack__ = []')

        # Code to translate route received.
        if self.routesIn[-1] != '' and self.routesIn[-1][0] == '?':
            wildcardCode = compile('%s = __strand__' % self.routesIn[-1][1:], \
                                   '', 'exec')
            allRoutes = tuple(self.labels[:-1])
        else:
            wildcardCode = None
            allRoutes = tuple(self.labels)

        # First translate any ints.
        newParser.addLine('if isinstance(__strand__, int) and __strand__ in xrange(%s):' % \
                          newParser.newConst(len(allRoutes)))
        newParser.addLine(' __strand__ = (%s)[__strand__]' % \
                       newParser.newConst(allRoutes))
        # Then translate strings.
        for i in range(len(allRoutes)):
            r = self.routesIn[i]
            if r != '':
                newParser.addLine("elif __strand__ == %s:" % newParser.newConst(r))
                newParser.addLine(' __strand__ = %s' % \
                               newParser.newConst(self.labels[i]))

        # Then catch any leftovers.
        newParser.addLine('else:')
        if wildcardCode:
            newParser.addLine(' exec %s' % newParser.newConst(wildcardCode))
            newParser.addLine(' __strand__ = %s' % \
                           newParser.newConst(self.labels[-1]))
        else:
            newParser.addLine(' raise ValueError(%s %% repr(__strand__))' % parser.newConst( \
                    'procedure has no entry route %s'))

        # Now parse the contents.
        newParser.parseBlock(self.child, 0)

        # Now we need to dereference labels if need be.

        # Check if we have any wildcards.
        hasWildcards = False
        for r in self.routesOut:
            if r != '' and r[0] == '?':
                hasWildcards = True
                break

        # Insert code to translate wildcards.
        if hasWildcards:
            newParser.addLine("if isinstance(__strand__, str):")
            newParser.addLine(' __strand__ = (eval(__strand__),)*2')

        # Return the result.
        newParser.addLine('return __strand__')

        # Extract the code object from compiled code.
        codeObj = newParser.compile()

        # Add dummy function code to the parser and link with code object.
        parser.addLine('%s pass' % defLine)
        parser.addNamedCodeObject(self.prName, codeObj)

        # Add the tag.
        parser.addTag(self, self.tag)
        parser.addLabel(self.postLabel)

    def transmitLoopContext(self):
        # Loop context does not enter funtions or classes.
        self.child.setNextLoop(None)
        self.child.bnLevel = self.bnLevel
        self.child.transmitLoopContext()

    def g_draw(self):
        if self.master == None:
            return
        if not self.g_modified:
            self.g_drawChild(self.child)
            if not self.g_modified:
                return

        self.g_clearBlock()
        self.g_relPlacement.scaleDesired(self.g_desiredShape)
        self.g_border = painter.BlockBorder(self, 2.545, 1.)
        self.g_sizeCutoff = 0.3

        # Size cutoff shape.
        self.g_addCutoffFeature(painter.Rectangle(self, 2.545, 1.0, \
                                                  RectType.Def))
        self.g_addCutoffFeature(painter.Arrows(self, [(-2.545, 0.)]))
        self.cutoffs = []
        self.cutoffs.append(painter.InteractiveText(self, ['proc ', '('], \
                             ['', ')'], [self.prName, self.params], \
                             1., self.textCallback, (-1.545, 0.)))
        self.cutoffs.append(painter.MultilineText(self, self.comment, \
                             1., self.commentCallback, (1., 0.), \
                             painter.cmtColour))
        for c in self.cutoffs:
            self.g_addCutoffFeature(c)

        # Standard shape.
        self.g_addFeature(painter.Rectangle(self, 2.545, 1.0, RectType.Border))

        rChIn, rChOut = self.g_addChild(self.child, .81, 1., (.309,0.))
        self.g_addFeature(painter.InteractiveText(self, ['proc ','('], \
                          ['', ')'], [self.prName, self.params], \
                          0.382, self.textCallback, (-1.877, -0.618)))
        self.g_addFeature(painter.MultilineText(self, self.comment, \
                          0.618, self.commentCallback, (-1.877, 0.382), \
                          painter.cmtColour))

        # Draw routes in and input expressions.
        rIn = []
        delta = 2. / (1. + self.child.numInputs)
        for i in range(self.child.numInputs):
            y = -1. + (i+1) * delta
            rIn.append((-0.691, y))
            self.g_addFeature(painter.InteractiveText(self, [' '], [' '], \
                        [self.routesIn[i]], min(0.5*delta, 0.309), \
                        (self.routeInCallback, [i]), (-1., y)))
            self.g_addFeature(painter.Connection(self, rIn[i], rChIn[i]))

        # Calc positions of routes out and draw output expressions.
        rOut = []
        delta = 2. / (1. + self.map.numOutputs)
        for i in range(self.map.numOutputs):
            y = -1. + (i+1) * delta
            rOut.append((1.8, y))
            self.g_addFeature(painter.InteractiveText(self, [' '], [' '], \
                        [self.routesOut[i]], min(0.5*delta, 0.309), \
                        (self.routeOutCallback, [i]), (2.236, y)))

        # Draw the map to the routes out.
        spacings = [rChOut[0][1] + 1.] + \
                   [rChOut[j+1][1] - rChOut[j][1] for j in range(len(rChOut)-1)] \
                   + [1. - rChOut[-1][1]]
        ptIn = self.spacePoints(spacings, (1.309, -1.), (1.309, 1.))
        for j in range(self.map.numInputs):
            self.g_addFeature(painter.Connection(self, rChOut[j], ptIn[j]))

        ptIn = [(ptIn[j], 0.) for j in range(self.map.numInputs)]
        ptOut = [(n, 0.) for n in rOut]
        self.g_addFeature(painter.MapFeature(self, 1., \
                                             ptIn, ptOut, self.map))

        self.g_addFeature(painter.Arrows(self, [(1.927, y) for x,y in rOut]))
        self.g_addFeature(painter.Arrows(self, [(-2.545, 0.)]))
        self.g_addCutoffFeature(painter.Arrows(self, [(-2.545, 0.)]))

        self.g_rIn, self.g_rOut = [(-2.545, 0.)], [(2.545, 0.)]

        self.g_modified = False

    def textCallback(self, values):
        'internal.'
        self.prName, self.params = values
        self.cutoffs[0].setValues(list(values))

        if self.master:
            self.master.touch()

    def commentCallback(self, values):
        'internal.'
        self.comment = list(values)
        self.cutoffs[1].setValues(list(values))

        if self.master:
            self.master.touch()

    def routeOutCallback(self, values, index):
        'internal.'
        [self.routesOut[index]] = values

        if self.master:
            self.master.touch()

    def routeInCallback(self, values, index):
        'internal.'
        [self.routesIn[index]] = values

        if self.master:
            self.master.touch()

    def modifyOutputRoutes(self, insert, index):
        '''Adds or removes an output route.'''
        # Fix the map.
        self.map.modifyOutputs(insert, index)

        # And the list.
        if insert:
            self.routesOut.insert(index, '')
        else:
            self.routesOut.pop(index)

        assert not self.isBroken()

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True
            self.master.touch()

    # TODO: Add methods for changing route names and modifying input routes.

class ProcCallBlock(Block):
    '''ProcCallBlock(nameExpression='', params='', parent=None, nextLoop=None)
    - Represents a call to a procedure.'''

    def __init__(self, nameExpression='', params='', parent=None,
                 nextLoop=None):
        super(ProcCallBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        self.numInputs = 1
        self.numOutputs = 1
        self.routesIn = ['']
        self.routesOut = ['']

        self.nameExpression = nameExpression
        self.params = params
        self.labels = [None]

    def isBroken(self):
        if super(ProcCallBlock, self).isBroken():
            return True
        if self.numInputs != len(self.routesIn):
            print 'ProcCall inputs: %d, len(routesIn): %d' % (self.numInputs, \
                                                        len(self.routesIn))
            return True
        if self.numOutputs != len(self.routesOut):
            print 'ProcCall outputs: %d, len(routesOut): %d' % \
                  (self.numOutputs, len(self.routesOut))
            return True
        return False

    def duplicate(self):
        result = ProcCallBlock(self.nameExpression, self.params)
        result.routesIn = list(self.routesIn)
        result.routesOut = list(self.routesOut)
        result.numInputs = len(self.routesIn)
        result.numOutputs = len(self.routesOut)
        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [self.lineNumbers, \
                self.nameExpression, self.params, list(self.routesIn), \
                list(self.routesOut)]

    @staticmethod
    def reconstitute(essence):
        lineNums, nameExp, params, routesIn, routesOut = essence
        result = ProcCallBlock(nameExp, params)
        result.routesIn = list(routesIn)
        result.routesOut = list(routesOut)
        result.numInputs = len(routesIn)
        result.numOutputs = len(routesOut)
        result.lineNumbers = lineNums
        assert not result.isBroken()

        return result

    def reverseRoute(self, label, exit):
        # Compiler optimisation: tagging
        if self.numInputs == 1 >= self.numOutputs:
            self.tagLabel = label

        # Catch the label.
        self.labels[exit] = label
        return []

    def prepBlock(self):
        badConsts = super(ProcCallBlock, self).prepBlock()

        # Init labels.
        self.labels = [None] * self.numOutputs

        # Check validity of routesIn and routesOut.
        error = Identifier.preRouteNamesError(self.routesIn)
        error = error or Identifier.postRouteNamesError(self.routesOut)
        if error:
            raise EPrepBlockError, (self, error)

        # Check validity of name.
        try:
            c = compile('%s\n' % self.nameExpression, '', 'eval')
            # Save the bad constants.
            badConsts.extend(c.co_consts)
        except SyntaxError:
            raise EPrepBlockError, (self, 'invalid expression')

        # Check validity of parameters.
        try:
            code = compile('foo(%s)\n' % self.params, '', 'eval')
            badConsts.extend(code.co_consts)
        except SyntaxError:
            raise EPrepBlockError, (self, 'invalid parameter expression')

        # Label the strands which come to this point.
        for i in range(self.numInputs):
            label = self.routesIn[i]
            if label == '':
                label = i

            if self.parent:
                self.parent.labelStrand(label, self, i)

        return badConsts

    def parse(self, parser):
        # Check if we have any wildcards.
        hasWildcards = False
        hasInts = False
        for r in self.routesIn:
            if r == '':
                hasInts = True
            elif r[0] == '?':
                hasWildcards = True

        # Insert code to translate wildcards.
        if hasWildcards:
            if hasInts:
                parser.addLine("if isinstance(__strand__, str) and __strand__[%s] == %s:" \
                               % (parser.newConst(0), parser.newConst('?')))
            else:
                parser.addLine("if __strand__[%s] == %s:" \
                               % (parser.newConst(0), parser.newConst('?')))
            parser.addLine(' __strand__ = eval(__strand__[%s:])' % \
                           parser.newConst(1))

        # Code to call function.
        parser.addLine('__strand__ = %s(__strand__, %s)' % \
                        (self.nameExpression, self.params))

        # Code to translate route back - return route is (index, label).
        if self.routesOut[-1] != '' and self.routesOut[-1][0] == '?':
            wildcardCode = compile('%s = __strand__' % self.routesOut[-1][1:], \
                                   '', 'exec')
            allRoutes = tuple(self.labels[:-1])
        else:
            wildcardCode = None
            allRoutes = tuple(self.labels)

        # First translate labels.
        el = ''
        for i in range(len(allRoutes)):
            r = self.routesOut[i]
            if r != '':
                parser.addLine('%sif __strand__[%s] == %s:' % (el, \
                                    parser.newConst(1), parser.newConst(r)))
                parser.addLine(' __strand__ = %s' % \
                               parser.newConst(self.labels[i]))
                el = 'el'

        # Now translate index.
        zero = parser.newConst(0)
        parser.addLine('%sif isinstance(__strand__[%s], int) and __strand__[%s] in xrange(%s):' % \
                       (el, zero, zero, parser.newConst(len(allRoutes))))
        parser.addLine(' __strand__ = (%s)[__strand__[%s]]' % \
                       (parser.newConst(allRoutes), parser.newConst(0)))

        # Then catch any leftovers.
        parser.addLine('else:')
        if wildcardCode:
            parser.addLine(' exec %s' % parser.newConst(wildcardCode))
            parser.addLine(' __strand__ = %s' % \
                           parser.newConst(self.labels[-1]))
        else:
            parser.addLine(' raise ValueError(%s %% repr(__strand__))' % parser.newConst( \
                       'procedure returned unknown route: %s'))

    def g_draw(self):
        if not self.g_modified or self.master == None:
            return
        self.g_modified = False

        # Default processing: draw a box.
        self.g_relPlacement.scaleDesired(self.g_desiredShape)
        self.g_clearBlock()
        self.g_border = painter.BlockBorder(self, 1.618, 1.0)
        self.g_addFeature(painter.Rectangle(self, 1., 0.618, RectType.Solid))

        # Fix up input routes.
        delta = 1.236 / (1. + self.numInputs)
        arrowPts = []
        rIn = []
        for i in range(self.numInputs):
            y = -.618 + (i+1) * delta
            rIn.append((-1.618, y))
            arrowPts.append((-1., y))
            self.g_addFeature(painter.Connection(self, (-1.618, y), (-1., y)))
            self.g_addFeature(painter.InteractiveText(self, [' '], [' '], \
                              [self.routesIn[i]], min(delta/2.,0.309), \
                              (self.inCallback, [i]), (-1.309, y), \
                              painter.rnbColour))

        self.g_addFeature(painter.Arrows(self, arrowPts))

        # This text goes between input and output.
        self.g_addFeature(painter.InteractiveText(self, ['call ','('], \
                          ['', ')'], [self.nameExpression, self.params], \
                          0.618, self.textCallback, (0., 0.)))

        # And output routes.
        delta = 1.236 / (1. + self.numOutputs)
        rOut = []
        for i in range(self.numOutputs):
            y = -.618 + (i+1) * delta
            rOut.append((1.618, y))
            self.g_addFeature(painter.Connection(self, (1., y), (1.618, y)))
            self.g_addFeature(painter.InteractiveText(self, [' '], [' '], \
                              [self.routesOut[i]], min(delta/2., 0.309), \
                              (self.outCallback, [i]), (1.309, y), \
                              painter.rnbColour))

        self.g_rIn, self.g_rOut = rIn, rOut

    def textCallback(self, values):
        'internal.'
        self.nameExpression, self.params = values

        if self.master:
            self.master.touch()

    def inCallback(self, values, index):
        'internal.'
        [self.routesIn[index]] = values

        if self.master:
            self.master.touch()

    def outCallback(self, values, index):
        'internal.'
        [self.routesOut[index]] = values

        if self.master:
            self.master.touch()

    def modifyInputRoutes(self, insert, index):
        '''Adds or removes an input route.'''
        # Fix the list.
        if insert:
            self.routesIn.insert(index, '')
            self.numInputs = self.numInputs + 1
        else:
            self.routesIn.pop(index)
            self.numInputs = self.numInputs - 1

        if self.parent:
            self.parent.childInputsChanged(self, insert, index)

        assert not self.isBroken()

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True
            self.master.touch()

    def modifyOutputRoutes(self, insert, index):
        '''Adds or removes an output route.'''
        # Fix the list.
        if insert:
            self.routesOut.insert(index, '')
            self.numOutputs = self.numOutputs + 1
        else:
            self.routesOut.pop(index)
            self.numOutputs = self.numOutputs - 1

        if self.parent:
            self.parent.childOutputsChanged(self, insert, index)

        assert not self.isBroken()

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True
            self.master.touch()

class TryBlock(OneChildBlock):
    '''TryBlock(excVar='', parent=None, nextLoop=None)
    Represents a try block.'''

    def __init__(self, excVar='excValue', excTrace='', parent=None, \
                 nextLoop=None):
        super(TryBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        self.numInputs = 1
        self.numOutputs = 2
        self.excVar = excVar
        self.excTrace = excTrace

        self.child = PassBlock(parent=self, nextLoop=nextLoop)

        self.label = None
        self.g_desiredShape = (6. * self.child.g_desiredShape + 1.5) / 8.5

    def isBroken(self):
        if super(TryBlock, self).isBroken():
            return True
        if self.numInputs != self.child.numInputs:
            return True
        if self.numOutputs != self.child.numOutputs + 1:
            return True
        return False

    def duplicate(self):
        result = TryBlock(self.excVar, self.excTrace)
        result.child.mutate(self.child.duplicate())

        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [self.lineNumbers, \
                self.excVar, self.excTrace, \
                approvedBlockTypes.index(type(self.child)), \
                self.child.distil()]

    @staticmethod
    def reconstitute(essence):
        lineNums, excVar, excTrace, a, b = essence
        result = TryBlock(excVar, excTrace)
        result.child.mutate(approvedBlockTypes[a].reconstitute(b))
        result.lineNumbers = lineNums
        assert not result.isBroken()

        return result

    def setMaxInputs(self, maxInputs):
        # Tell child.
        super(TryBlock, self).setMaxInputs(maxInputs)
        self.child.setMaxInputs(maxInputs)

    def childOutputsChanged(self, child, insert, index):
        # Tell the parent.
        self.numOutputs = child.numOutputs + 1
        if self.parent:
            self.parent.childOutputsChanged(self, insert, index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def childInputsChanged(self, child, insert, index):
        # Tell parent.
        self.numInputs = child.numInputs
        if self.parent:
            self.parent.childInputsChanged(self, insert, index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def swapChild(self, child, newChild):
        self.g_modified = True

        self.child = newChild
        newChild.setMaxInputs(0)

        # Adjust my number of outputs.
        self.setNumOutputs(newChild.numOutputs + 1)
        self.setNumInputs(newChild.numInputs)

        # Adjust shape
        self.g_childDesiredShapeChange(None)

    def setNumOutputs(self, numOutputs):
        # Special function takes into account the error strand.
        if self.parent:
            if numOutputs > self.numOutputs:
                for i in range(self.numOutputs-1, numOutputs-1):
                    self.numOutputs = self.numOutputs + 1
                    self.parent.childOutputsChanged(self, True, i)
            else:
                for i in range(numOutputs-1, self.numOutputs-1):
                    self.numOutputs = self.numOutputs - 1
                    self.parent.childOutputsChanged(self, False, numOutputs)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def reverseRoute(self, label, exit):
        # Compiler optimisation: tagging
        if self.numInputs == 1 >= self.numOutputs:
            self.tagLabel = label

        # If it's going to the last one, I catch it.
        if exit >= self.numOutputs - 1:
            self.label = label
            return []

        # Check the child block.
        return self.child.reverseRoute(label, exit)

    def labelStrand(self, label, child, entry):
        # Pass the label on to parent.
        if self.parent:
            self.parent.labelStrand(label, self, entry)

    def tagRoute(self, tagBlock, exit):
        # Only catch it on the except case.
        if exit == self.numOutputs - 1:
            self.tag = tagBlock

    def prepBlock(self):
        badConsts = super(TryBlock, self).prepBlock()

        # Init label.
        self.label = None
        self.tag = None

        # Check validity of names.
        if not Identifier.valid(self.excVar):
            raise EPrepBlockError, (self, 'invalid identifier: %s' % self.excVar)
        if self.excTrace != '' and not Identifier.valid(self.excTrace):
            raise EPrepBlockError, (self, 'invalid identifier: %s' % self.excTrace)

        # Call prepBlock of children.
        badConsts.extend(self.child.prepBlock())

        # Return bad consts.
        return badConsts

    def parse(self, parser):
        parser.addLine('try:')
        parser.parseBlock(self.child)
        parser.addLine('except:')
        parser.indent()
        if self.excTrace:
            parser.addLine('%s, %s = sys.exc_info()[1:]' % \
                           (self.excVar, self.excTrace))
        else:
            parser.addLine('%s = sys.exc_info()[1]' % self.excVar)
        parser.addTag(self,self.tag)
        parser.addLabel(self.label)
        parser.dedent()

    def g_childDesiredShapeChange(self, child):
        self.g_setDesiredShape(max((6. * self.child.g_desiredShape + 1.5) / 8.5, \
                                   7. / 16.))

    def g_draw(self):
        if self.master == None:
            return
        if not self.g_modified:
            self.g_drawChild(self.child)
            if not self.g_modified:
                return

        self.g_clearBlock()
        maxHeight = self.g_relPlacement.scaleToWidth()
        blockHeight = min(maxHeight, 1. / self.g_desiredShape)
        a = blockHeight / 16.

        self.g_sizeCutoff = 0.001

        self.g_border = painter.BlockBorder(self, 1., maxHeight)
        self.g_addCutoffFeature(painter.Rectangle(self, 1., maxHeight, \
                                                  RectType.Try))

        # Draw an orange box.
        self.g_addFeature(painter.Rectangle(self, 1., blockHeight, \
                                            RectType.Try))

        # Calculate the child shapes.
        chY = blockHeight * 0.75 - 0.5*a
        chX = 1. - 1.5*a

        # Draw the child blocks.
        self.g_addFeature(painter.Rectangle(self, chX+0.5*a, chY+0.5*a, \
                                            RectType.Hole, (0., -a)))
        rIn0, rOut0 = self.g_addChild(self.child, chX*chY, \
                                      chX/chY, (0., -a))

        # Extend output routes to the side.
        rOut = []
        for p in rOut0:
            p2 = (1., p[1])
            self.g_addFeature(painter.Connection(self, p, p2))
            rOut.append(p2)

        # Error output.
        # TODO: Draw skull and cross-bones.
        self.g_addFeature(painter.Connection(self, (1.-a, blockHeight-1.5*a), \
                                             (1., blockHeight-1.5*a)))
        rOut.append((1., blockHeight-1.5*a))
        self.g_addFeature(painter.InteractiveText(self, \
                    ['Except: ','Trace: '], ['', ''], \
                    [self.excVar, self.excTrace], 1.5*a, self.textCallback, \
                    (1.-2.5*a, blockHeight-1.5*a)))

        # Extend input routes.
        for i in range(len(rIn0)):
            x,y = rIn0[i]
            p1 = (-1., y)
            self.g_addFeature(painter.Connection(self, p1, (x,y)))
            rIn0[i] = p1

        self.g_addCutoffFeature(painter.Arrows(self, rIn0))
        self.g_rIn, self.g_rOut = rIn0, rOut

        self.g_modified = False

    def g_childRouteChange(self, child, inRoute):
        self.g_modified = True
        if self.parent:
            self.parent.g_childRouteChange(self, inRoute)

    def textCallback(self, values):
        '''internal.'''
        self.excVar, self.excTrace = values

        if self.master:
            self.master.touch()

    def setExcVar(self, varname):
        '''setExcVar(varname) - sets the name of the variable which this
        try block will put an error in if it is raised.'''
        if not isinstance(varname, str):
            raise TypeError, 'varname must be a string'

        self.excVar = varname
        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

class LongBlock(MultiChildBlock):
    '''LongBlock(parent,nextLoop) - Represents a block made up of
    a number of consecutive blocks.'''

    edgeGap = 0.1
    mapGap = 1.

    def __init__(self, parent=None, nextLoop=None):
        super(LongBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        self.numInputs = 1
        self.numOutputs = 1

        self.blocks = [PassBlock(parent=self, nextLoop=nextLoop)]
        self.maps = []

        self.g_desiredShape = self.edgeGap + (1-self.edgeGap) * \
                              self.blocks[0].g_longDesiredShape()

    def isBroken(self):
        if super(LongBlock, self).isBroken():
            return True
        if len(self.maps) != len(self.blocks) - 1:
            print 'LongBlock blocks: %d, maps: %d' % (len(self.blocks),
                                                      len(self.maps))
            return True
        for i in range(len(self.maps)):
            m = self.maps[i]
            if m.prevBlock != self.blocks[i]:
                print 'LongBlock\'s map prev points to wrong thing.'
                return True
            if m.nextBlock != self.blocks[i+1]:
                print 'LongBlock\'s map next points to wrong block:', \
                      str(m.nextBlock), str(self.blocks[i+1])
                return True
            if m.isBroken():
                print 'LongBlock\'s mapping is broken.'
                return True
        if self.numInputs != self.blocks[0].numInputs:
            print 'LongBlock\'s in: %d, first block in: %d' % \
                  (self.numInputs, self.blocks[0].numInputs)
            return True
        if self.numOutputs != self.blocks[-1].numOutputs:
            print 'LongBlock\'s out: %d, last block out: %d' % \
                  (self.numOutputs, self.blocks[-1].numOutputs)
            return True
        return False

    def duplicate(self):
        result = LongBlock()

        lastBlock = result.blocks[0]
        for b in self.blocks:
            result.insertChildSeq_internal(lastBlock, False,
                                           b.duplicate())
        lastBlock.delete()

        for i in range(len(self.maps)):
            result.maps[i].connections = list(self.maps[i].connections)

        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        result = [self.lineNumbers]
        for i in range(len(self.blocks)):
            b = self.blocks[i]
            result.append(approvedBlockTypes.index(type(b)))
            result.append(b.distil())

            if i >= len(self.blocks) - 1:
                break
            result.append(list(self.maps[i]))
        return result

    @staticmethod
    def reconstitute(essence):
        lineNums = essence.pop(0)
        assert len(essence) % 3 == 2

        result = LongBlock()
        result.lineNumbers = lineNums

        lastBlock = result.blocks[0]
        i = 0
        oldMap = None
        while i < len(essence):
            a, b = essence[i:i+2]
            result.insertChildSeq_internal(lastBlock, False, \
                                    approvedBlockTypes[a].reconstitute(b))

            if oldMap:
                result.maps[-2].connections = list(oldMap)

            i = i + 2
            if i >= len(essence):
                break
            oldMap = essence[i]
            i = i + 1

        lastBlock.delete()

        assert not result.isBroken()
        return result

    def setMaxInputs(self, maxInputs):
        # Tell first child.
        super(LongBlock, self).setMaxInputs(maxInputs)
        self.blocks[0].setMaxInputs(maxInputs)

    def childOutputsChanged(self, child, insert, index):
        i = self.blocks.index(child)
        if i < len(self.maps):
            self.maps[i].modifyInputs(insert, index)
            self.blocks[i+1].setMaxInputs(child.numOutputs)
        else:
            # Last block - changes my output count, and tell parent.
            self.numOutputs = child.numOutputs
            if self.parent:
                self.parent.childOutputsChanged(self, insert, index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def childInputsChanged(self, child, insert, index):
        i = self.blocks.index(child)
        if i == 0:
            # First block - tell parent.
            self.numInputs = child.numInputs
            if self.parent:
                self.parent.childInputsChanged(self, insert, index)
        else:
            self.maps[i-1].modifyOutputs(insert, index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def swapChild(self, child, newChild):
        self.g_modified = True
        i = self.blocks.index(child)
        self.blocks[i] = newChild
        if i == 0:
            newChild.setMaxInputs(self.maxInputs)
            self.setNumInputs(newChild.numInputs)
            if self.parent:
                self.parent.g_childRouteChange(self, True)
        else:
            self.maps[i-1].nextBlock = newChild
            self.maps[i-1].setNumOutputs(newChild.numInputs)

        if i == len(self.maps):
            newChild.setMaxInputs(self.blocks[i-1].numOutputs)
            self.setNumOutputs(newChild.numOutputs)
            if self.parent:
                self.parent.g_childRouteChange(self, False)
        else:
            self.maps[i].prevBlock = newChild
            self.maps[i].setNumInputs(newChild.numOutputs)
            self.blocks[i+1].setMaxInputs(newChild.numOutputs)

        self.g_fixDesiredShape()

    def delChild(self, child):
        # If we only have one child, blank it.
        if len(self.blocks) == 1:
            return child.revert()

        # Remove escapes from me.
        for e in child.passingEscapes:
            self.childRemoveEscape(e)

        # More than 1: delete it.
        i = self.blocks.index(child)
        self.blocks.pop(i)
        if i == 0:
            # Remove mapping, set NumInputs.
            self.maps.pop(0)
            self.setNumInputs(self.blocks[0].numInputs)
        elif i < len(self.maps):
            # Remove the second mapping.
            self.maps.pop(i)

            # Adjust the first
            self.maps[i-1].nextBlock = self.blocks[i]
            self.maps[i-1].setNumOutputs(self.blocks[i].numInputs)
        else:
            # Deleting the last block - remove mapping, set NumOutputs.
            self.maps.pop(-1)
            self.setNumOutputs(self.blocks[-1].numOutputs)

        # Update shape of block.
        self.g_fixDesiredShape()

    def reverseRoute(self, label, exit):
        # Compiler optimisation: tagging
        if self.numInputs == 1 >= self.numOutputs:
            self.tagLabel = label

        newRoutes = routes = [exit]
        i = len(self.blocks) - 1
        # Filter backwards through the blocks.
        while i >= 0:
            newRoutes = []
            for r in routes:
                newRoutes.extend(self.blocks[i].reverseRoute(label, r))
            if len(newRoutes) == 0:
                return []

            i -= 1
            if i < 0:
                break

            # And through the mapping.
            routes = []
            for r in newRoutes:
                routes.extend(self.maps[i].reverseRoute(label, r))
            if routes == []:
                return []

        return newRoutes

    def tagRoute(self, tagBlock, exit):
        i = len(self.blocks) - 1
        # Filter backwards through blocks.
        while i >= 0:
            exit = self.blocks[i].tagRoute(tagBlock, exit)
            if exit == None:
                return
            i -= 1
            if i == 0:
                break

            # And through the mapping.
            exit = self.maps[i].reverseRoute(tagBlock, exit)
            if len(exit) != 1:
                return
            exit = exit[0]

        if self.parent:
            self.parent.tagStrand(tagBlock, self, exit)

    def labelStrand(self, label, child, entry):
        i = self.blocks.index(child) - 1
        routes = [entry]
        while i >= 0:
            newRoutes = []
            # Filter it through the mapping.
            for r in routes:
                newRoutes.extend(self.maps[i].reverseRoute(label, r))
            if newRoutes == []:
                return

            # Now filter it through the next block.
            routes = []
            for r in newRoutes:
                routes.extend(self.blocks[i].reverseRoute(label, r))
            if routes == []:
                return
            i -= 1

        # Now anything that's left goes to the parent.
        if self.parent:
            for r in routes:
                self.parent.labelStrand(label, self, r)

    def tagStrand(self, tagBlock, child, entry):
        i = self.blocks.index(child) - 1
        while i >= 0:
            entry = self.maps[i].reverseRoute(tagBlock, entry)
            if len(entry) != 1:
                return
            entry = entry[0]
            entry = self.blocks[i].tagRoute(tagBlock, entry)
            if entry == None:
                return
        # Tell the parent.
        if self.parent:
            self.parent.tagStrand(tagBlock, self, entry)

    def prepBlock(self):
        badConsts = super(LongBlock, self).prepBlock()

        # Call prepBlock() for each child.
        for b in self.blocks:
            badConsts.extend(b.prepBlock())

        # Return badConsts
        return badConsts

    def parse(self, parser):
        # Parse all the separate children.
        for b in self.blocks:
            parser.parseBlock(b, 0)

    def g_childDesiredShapeChange(self, child):
        self.g_fixDesiredShape()

    def g_fixDesiredShape(self):
        'internal.'
        self.g_setDesiredShape(self.edgeGap + (1 - self.edgeGap)* \
                               sum(b.g_longDesiredShape() for b in self.blocks) + \
                               0.5 * self.mapGap * (len(self.blocks) - 1.))

    def g_draw(self):
        if self.master == None:
            return
        if not self.g_modified:
            for ch in self.blocks:
                self.g_drawChild(ch)
            if not self.g_modified:
                return

        self.g_clearBlock()
        maxHeight = self.g_relPlacement.scaleToWidth()
        childFactor = (1. - self.edgeGap)

        # Size cutoff.
        self.g_sizeCutoff = 0.001
        self.g_border = painter.BlockBorder(self, 1., maxHeight)
        self.g_addCutoffFeature(painter.Rectangle(self, 1., maxHeight, \
                                                  RectType.Solid))


        blockHeight = min(maxHeight, 1. / self.g_desiredShape)
        if len(self.blocks) > 1:
            mapWidth = (2.-2.*blockHeight*childFactor*\
                        sum(b.g_longDesiredShape() for b \
                            in self.blocks) - 2.*self.edgeGap) \
                            / (len(self.blocks) - 1.)
            mapBorder = 0.2 * mapWidth
        else:
            mapWidth = 0

        # Draw the first block.
        x = -1. + self.edgeGap
        b = self.blocks[0]
        bDesShape = b.g_longDesiredShape()
        bHeight = childFactor * blockHeight
        bWidth = bHeight * bDesShape
        x = x + bWidth
        rIn0, rOut = self.g_addChild(b, bHeight * bWidth, \
                                      bWidth / bHeight, (x, 0))

        i = 1
        while i < len(self.blocks):
            xm1 = x + bWidth + mapBorder
            x = x + bWidth + mapWidth
            xm2 = x - mapBorder

            # Draw the next block.
            b = self.blocks[i]

            bDesShape = b.g_longDesiredShape()
            bWidth = bHeight * bDesShape
            x = x + bWidth
            rIn, rOut2 = self.g_addChild(b, bHeight*bWidth, \
                                          bWidth / bHeight, (x, 0))

            # Draw the previous map.
            if len(rOut) == 0:
                ptIn = []
            else:
                spacings = [rOut[0][1] + bHeight] + \
                           [rOut[j+1][1] - rOut[j][1] for j in range(len(rOut)-1)] \
                           + [bHeight - rOut[-1][1]]
                ptIn = self.spacePoints(spacings, (xm1, -bHeight), \
                                        (xm1, bHeight))
                for j in range(len(rOut)):
                    self.g_addFeature(painter.Connection(self, rOut[j], ptIn[j]))

            if len(rIn) == 0:
                ptOut = []
                raise Exception, 'Mapping can\'t have zero outputs.'
            else:
                spacings = [rIn[0][1] + bHeight] + \
                           [rIn[j+1][1] - rIn[j][1] for j in range(len(rIn)-1)] \
                           + [bHeight - rIn[-1][1]]
                ptOut = self.spacePoints(spacings, (xm2, -bHeight), \
                                         (xm2, bHeight))
                for j in range(len(rIn)):
                    self.g_addFeature(painter.Connection(self, ptOut[j], rIn[j]))

            m = self.maps[i-1]
            ptIn = [(n, 0.) for n in ptIn]
            ptOut = [(n, 0.) for n in ptOut]
            self.g_addFeature(painter.MapFeature(self, bHeight, \
                                                 ptIn, ptOut, m))

            i = i + 1
            rOut = rOut2

        assert len(rIn0) == self.numInputs
        assert len(rOut) == self.numOutputs

        # Extend input and output routes.
        for x,y in rIn0:
            pt = (-1., y)
            self.g_addFeature(painter.Connection(self, pt, (x,y)))
            self.g_rIn.append(pt)
        for x,y in rOut:
            pt = (1., y)
            self.g_addFeature(painter.Connection(self, (x,y), pt))
            self.g_rOut.append(pt)

        self.g_addCutoffFeature(painter.Arrows(self, self.g_rIn))

        self.g_modified = False

    def g_childRouteChange(self, child, inRoute):
        self.g_modified = True
        if self.parent:
            if inRoute:
                if child is self.blocks[0]:
                    self.parent.g_childRouteChange(self, True)
            else:
                if child is self.blocks[-1]:
                    self.parent.g_childRouteChange(self, False)

    def insertChildSeq_internal(self, child, after=True, blockToAdd=None):
        '''(child, after, [newChild]) - internal.'''

        if child is None:
            # Translate None calls.
            if after:
                index = 0
                after = False
            else:
                index = len(self.maps)
                after = True
            child = self.blocks[index]
        else:
            index = self.blocks.index(child)

        newBlock = PassBlock(parent=self, nextLoop=self.nextLoop)
        newBlock.setMaxInputs(self.maxInputs)
        # First insert a new PassBlock
        if after:
            if index >= len(self.maps):
                # Add a block at the end.
                self.blocks.append(newBlock)
                self.maps.append(InterBlockMapping(child, newBlock))
                self.setNumOutputs(newBlock.numOutputs)
            else:
                self.blocks.insert(index+1, newBlock)
                self.maps.insert(index, self.maps[index].splitBefore(newBlock))
        else:
            if index == 0:
                # Add a block at the start.
                self.blocks.insert(0, newBlock)
                # Add a mapping at the start.
                self.maps.insert(0, InterBlockMapping(newBlock, child))
                self.setNumInputs(newBlock.numInputs)
            else:
                self.maps.insert(index, self.maps[index-1].splitAfter(newBlock))
                self.blocks.insert(index, newBlock)

        # Update the shape of this block.
        self.g_fixDesiredShape()

        if blockToAdd:
            newBlock.mutate(blockToAdd)
            newBlock = blockToAdd

        # Fix the mapping.
        self.maps[index].straighten()

        return newBlock

    def insertChildSeq(self, child, after=True, blockToAdd=None):
        '''insertChildSeq(child, after, [newChild]) - inserts a block before or
        after the specified child. If newChild is omitted, inserts and returns
        a new PassBlock. If after is True, inserts newChild after child,
        otherwise inserts it before.

        If child is None, inserts a block at the begining or end.
        '''

        if child is not None and child not in self:
            raise KeyError, 'child does not belong to this block'

        result = self.insertChildSeq_internal(child, after, blockToAdd)
        assert not self.isBroken()
        assert not result.isBroken()

        if self.master:
            self.master.touch()

        return result

    def divide(self, child, after=True):
        '''divide(child, after) - after calling this method, this long block
        will contain exactly two blocks. Everything before the specified child
        block will be in the first half, and everything after it will be in
        the second half. The value of after determines whether the split occurs
        before or after child.

        If the request specifies to split at the very end, this routine will
        create a new PassBlock to go in one half.'''

        if child not in self:
            raise KeyError, 'child does not belong to this block'

        i = self.blocks.index(child)
        i = (after and i+1) or i

        # Create first half.
        if i == 0:
            block1 = self.insertChildSeq_internal(None)
            i = 1
        elif i == 1:
            block1 = self.blocks[0]
        else:
            block1 = LongBlock(parent=self, nextLoop=self.nextLoop)
            block1.blocks = self.blocks[:i]
            block1.maps = self.maps[:i-1]

            block1.numInputs = self.numInputs
            block1.numOutputs = self.blocks[i-2].numOutputs

            for b in block1.blocks:
                b.parent = block1
                assert not b.isBroken()

        # Create second half.
        if i == len(self.blocks):
            block2 = self.insertChildSeq_internal(None, after=False)
        elif i == len(self.blocks) - 1:
            block2 = self.blocks[-1]
        else:
            block2 = LongBlock(parent=self, nextLoop=self.nextLoop)
            block2.blocks = self.blocks[i:]
            block2.maps = self.maps[i:]

            block2.numInputs = self.blocks[i].numInputs
            block2.numOutputs = self.numOutputs

            for b in block2.blocks:
                b.parent = block2
                assert not b.isBroken()

        # Join the two together
        self.blocks = [block1, block2]
        newMap = InterBlockMapping(block1, block2)
        newMap.connections = self.maps[i-1].connections
        newMap.numInputs = self.maps[i-1].numInputs
        self.maps = [newMap]

        self.g_fixDesiredShape()

        assert not self.isBroken()
        assert not block1.isBroken()
        assert not block2.isBroken()

        if self.master:
            self.master.touch()

    def unnest(self):
        '''unnest() - if this long block is a child of a long block, combines
        this block into that block.'''

        if not self.parent:
            raise ValueError('cannot unnest free block')
        if not isinstance(self.parent, LongBlock):
            raise ValueError('LongBlock parent is not in a LongBlock')

        parent = self.parent
        # Remember the map just before me.
        j = parent.blocks.index(self)
        if j > 0:
            oldMap = parent.maps[j-1].connections
        else:
            oldMap = None
        # Go through blocks and transfer them to parent
        for i in range(len(self.blocks)-1):
            # Remember my first map.
            curMap = self.maps[0].connections
            # Move my first block.
            pBlock = parent.insertChildSeq_internal(self, after=False)
            block = self.blocks[0]
            block.delete()
            pBlock.mutate(block)
            # Restore the mapping.
            if oldMap != None:
                parent.maps[j-1].connections = oldMap
            oldMap = curMap
            j = j + 1

        # Remember the map following me.
        try:
            curMap = parent.maps[j].connections
        except IndexError:
            curMap = None

        # Handle the last block separately.
        block = self.blocks[0]
        block.revert()

        # Revert me and put my last block in my place.
        assert not parent.isBroken()
        self.revert().mutate(block)

        # Put the maps back.
        if oldMap != None:
            parent.maps[j-1].connections = oldMap
        if curMap != None:
            parent.maps[j].connections = curMap

        assert not self.isBroken()
        assert not block.isBroken()

        if self.master:
            self.master.touch()

        return parent

    def vanish(self):
        '''vanish() - if this block has only one child, this block will be
        replaced with its child.'''

        if len(self.blocks) > 1:
            raise ValueError, 'block must have only one child'

        if not self.parent:
            self.blocks[0].delete()
            return self
        else:
            a = self.blocks[0]
            a.revert()
            b = self.revert()
            b.mutate(a)
            assert not a.isBroken()

            if self.master:
                self.master.touch()
            return a

    def alignChildren(self):
        '''alignChildren() - realigns the contents of this block.
        This method inserts a division in the mapping joining two WideBlocks.

        When calling this method:
        * this LongBlock should have exactly two children which should either
            both be WideBlocks.
        * these two child blocks should have the same number of children.

        After calling this method:
        * this block will be replaced with a single WideBlock.
        * the WideBlock's children will all be LongBlocks.
        * each of these LongBlocks will have exactly two children.
        * these children will be the original children of the original
            WideBlocks.
        * the execution structure will not have changed.

        Note that by separating the wide blocks, this routine may have to
        cut some strands in a mapping.
        '''
        # Error check.
        if len(self.blocks) != 2:
            raise ValueError, 'block should have exactly two children'
        if not isinstance(self.blocks[0], WideBlock):
            raise TypeError, 'first child must be a WideBlock'
        if not isinstance(self.blocks[1], WideBlock):
            raise TypeError, 'second child should be a WideBlock'
        if len(self.blocks[0].blocks) != len(self.blocks[1].blocks):
            raise ValueError, 'both child blocks must have the same number of children'

        # Save my mapping.
        m = self.maps[0].connections

        # Replace self with first block.
        block0, block1 = self.blocks
        block0.revert()
        self.revert().mutate(block0)

        # Make all children of block0 LongBlocks.
        offset = 0
        for i in range(len(block0.blocks)):
            ch = block0.blocks[i]
            lb = ch.enshroud(LongBlock)

            # Man the long blocks.
            b = block1.blocks[i]
            b.revert()
            lb.insertChildSeq_internal(None, False, b)

            # Fix the mappings.
            numIns, numOuts = lb.maps[0].numInputs, lb.maps[0].numOutputs
            for i in range(numIns):
                route = min(max(0, m[i - offset]), numOuts)
                lb.maps[0].connections[i] = route
            offset = offset + numOuts

        assert not self.isBroken()
        assert not block0.isBroken()

        if self.master:
            self.master.touch()

        return block0

class WideBlock(MultiChildBlock):
    '''WideBlock() - creates a block which can contain a number of parallel
    blocks.'''

    edgeGap = 0.07

    def __init__(self, parent=None, nextLoop=None):
        super(WideBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        self.numInputs = 1
        self.numOutputs = 1

        self.blocks = [PassBlock(parent=self, nextLoop=nextLoop)]
        self.labels = None
        self.inputTally = [0, 1]
        self.outputTally = [0, 1]

        self.g_desiredShape = 1./ ((1.-self.edgeGap)*\
                                1./self.blocks[0].g_wideDesiredShape() \
                                + self.edgeGap)

    def isBroken(self):
        if super(WideBlock, self).isBroken():
            return True
        if self.numInputs != sum(i.numInputs for i in self.blocks):
            print 'WideBlock inputs: %d, child inputs: %s' % \
                  (self.numInputs, str([i.numInputs for i in self.blocks]))
            return True
        if self.numOutputs != sum(i.numOutputs for i in self.blocks):
            print 'WideBlock outputs: %d, child outputs: %s' % \
                  (self.numOutputs, str([i.numOutputs for i in self.blocks]))
            return True
        if len(self.inputTally) != len(self.blocks) + 1:
            print 'WideBlock input tally: %d, blocks: %d' % (len(self.inputTally),
                                                             len(self.blocks))
            return True
        if len(self.outputTally) != len(self.blocks) + 1:
            print 'WideBlock output tally: %d, blocks: %d' % (len(self.outputTally),
                                                              len(self.blocks))
            return True
        if self.outputTally[0] != 0:
            print 'WideBlock outputTally[0] =', self.outputTally[0]
            return True
        n = 0
        for i in range(len(self.blocks)):
            n = n + self.blocks[i].numOutputs
            if self.outputTally[i+1] != n:
                print 'WideBlock outputTally[%d] = %d, should be %d' % \
                      (i+1, self.outputTally[i+1], n)
                return True
        if self.inputTally[0] != 0:
            print 'WideBlock inputTally[0] =', self.inputTally[0]
            return True
        n = 0
        for i in range(len(self.blocks)):
            n = n + self.blocks[i].numInputs
            if self.inputTally[i+1] != n:
                print 'WideBlock inputTally[%d] = %d, should be %d' % \
                      (i+1, self.inputTally[i+1], n)
                return True
        return False

    def duplicate(self):
        result = WideBlock()

        lastBlock = result.blocks[0]
        for b in self.blocks:
            result.insertParallelChild_internal(lastBlock, False, b.duplicate())
        lastBlock.delete()

        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        result = [self.lineNumbers]

        for b in self.blocks:
            result.append(approvedBlockTypes.index(type(b)))
            result.append(b.distil())
        return result

    @staticmethod
    def reconstitute(essence):
        lineNums = essence.pop(0)
        assert len(essence) % 2 == 0
        result = WideBlock()
        result.lineNumbers = lineNums

        lastBlock = result.blocks[0]
        i = 0
        while i < len(essence):
            a, b = essence[i:i+2]
            i = i + 2
            result.insertParallelChild_internal(lastBlock, False, \
                                approvedBlockTypes[a].reconstitute(b))
        lastBlock.delete()

        assert not result.isBroken()
        return result



    def setMaxInputs(self, maxInputs):
        super(WideBlock, self).setMaxInputs(maxInputs)
        # Tell every child this number.
        for b in self.blocks:
            b.setMaxInputs(maxInputs)

    def childOutputsChanged(self, child, insert, index):
        i = self.blocks.index(child)
        outIndex = index + self.outputTally[i]

        dTally = (insert and 1) or -1

        # Adjust our running tally.
        for j in range(i+1, len(self.outputTally)):
            self.outputTally[j] += dTally

        self.numOutputs += dTally
        if self.parent:
            self.parent.childOutputsChanged(self, insert, outIndex)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def childInputsChanged(self, child, insert, index):
        i = self.blocks.index(child)
        inIndex = index - self.inputTally[i]

        dTally = (insert and 1) or -1

        for j in range(i+1, len(self.inputTally)):
            self.inputTally[j] += dTally

        self.numInputs = self.numInputs + dTally
        if self.parent:
            self.parent.childInputsChanged(self, insert, inIndex)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def swapChild(self, child, newChild):
        self.g_modified = True
        if self.parent:
            self.parent.g_childRouteChange(self, True)
            self.parent.g_childRouteChange(self, False)

        i = self.blocks.index(child)
        self.blocks[i] = newChild

        # Update tally counts.
        diTally = newChild.numInputs - child.numInputs
        doTally = newChild.numOutputs - child.numOutputs
        for j in range(i+1, len(self.inputTally)):
            self.inputTally[j] += diTally
            self.outputTally[j] += doTally

        # Update numInputs and numOutputs.
        if diTally > 0:
            for j in range(self.inputTally[i] + child.numInputs,
                           self.inputTally[i+1]):
                self.numInputs = self.numInputs + 1
                if self.parent:
                    self.parent.childInputsChanged(self, True, j)
        else:
            for j in range(-diTally):
                self.numInputs = self.numInputs - 1
                if self.parent:
                    self.parent.childInputsChanged(self, False,
                                    self.inputTally[i] + newChild.numInputs)

        if doTally > 0:
            for j in range(self.outputTally[i] + child.numOutputs,
                           self.outputTally[i+1]):
                self.numOutputs = self.numOutputs + 1
                if self.parent:
                    self.parent.childOutputsChanged(self, True, j)
        else:
            for j in range(-doTally):
                self.numOutputs = self.numOutputs - 1
                if self.parent:
                    self.parent.childOutputsChanged(self, False,
                                    self.outputTally[i] + newChild.numOutputs)

        self.g_fixDesiredShape()

    def delChild(self, child):
        # If there's only one child, revert it.
        if len(self.blocks) == 1:
            return child.revert()

        # Remove escapes from me.
        for e in child.passingEscapes:
            self.childRemoveEscape(e)

        # Unlink this child.
        i = self.blocks.index(child)
        self.blocks.pop(i)

        # Update the tally counts.
        self.inputTally.pop(i+1)
        self.outputTally.pop(i+1)
        diTally = child.numInputs
        doTally = child.numOutputs
        for j in range(i+1, len(self.inputTally)):
            self.inputTally[j] -= diTally
            self.outputTally[j] -= doTally

        # Update my input and output counts.
        iPos = self.inputTally[i]
        for j in range(diTally):
            self.numInputs -= 1
            if self.parent:
                self.parent.childInputsChanged(self, False, iPos)

        oPos = self.outputTally[i]
        for j in range(doTally):
            self.numOutputs -= 1
            if self.parent:
                self.parent.childOutputsChanged(self,False, oPos)

        self.g_fixDesiredShape()

    def reverseRoute(self, label, exit):
        # Compiler optimisation: tagging
        if self.numInputs == 1 >= self.numOutputs:
            self.tagLabel = label

        # Find which block it needs to be directed to.
        for j in range(1, len(self.outputTally)):
            if exit < self.outputTally[j]:
                # We've found the object, find the index.
                i = exit - self.outputTally[j-1]
                routes = self.blocks[j-1].reverseRoute(label, i)
                # Catch leftover labels.
                for route in routes:
                    self.labelStrand(label, self.blocks[j-1], route)
                break
        return []

    def labelStrand(self, label, child, entry):
        # Find what position it needs to be directed to.
        index = entry + self.inputTally[self.blocks.index(child)]
        # Save the label.
        self.labels[index] = label

    def tagRoute(self, tagBlock, exit):
        # Find which block it needs to be directed to.
        for j in range(1, len(self.outputTally)):
            if exit < self.outputTally[j]:
                # We've found the object, find the index.
                #i = exit - self.outputTally[j-1]
                exit = self.blocks[j-1].tagRoute(tagBlock, exit)
                # Catch leftover tags.
                if exit != None:
                    self.tagStrand(tagBlock, self.blocks[j-1], exit)
                break

    def tagStrand(self, tagBlock, child, entry):
        # Find what position it needs to be directed to.
        index = entry + self.inputTally[self.blocks.index(child)]
        # Pass on the tag.
        if self.parent:
            self.parent.tagStrand(tagBlock, self, index)

    def prepBlock(self):
        badConsts = super(WideBlock, self).prepBlock()

        # Initialise labels.
        self.labels = [None] * self.numInputs

        # Prep children.
        for b in self.blocks:
            badConsts.extend(b.prepBlock())

        # Label each input strand with its index.
        if self.parent:
            for i in range(self.numInputs):
                self.parent.labelStrand(i, self, i)

        # Return badConsts
        return badConsts

    def getParsingStrings(self, parser, i, first):
        # a = 'el' only for non-zero first.
        a = (not first and 'el') or ''

        # b is the test condition, c is the label-setter.
        if self.blocks[i].numInputs == 1:
            b = '== %d' % self.inputTally[i]
            lbl = self.labels[self.inputTally[i]]
            if lbl is None:
                c = None
            else:
                c = ' __strand__ = %s' % parser.newConst(repr(lbl))
        else:
            # More than one input to this block.
            xr = xrange(self.inputTally[i], self.inputTally[i+1])
            b = 'in %d' % tuple(xr)

            # Check for no labelling.
            for i in xr:
                if self.labels[i] != None:
                    break
            else:
                return a,b, ''

            c = ' __strand__ = (%s)[__strand__-%s]' % \
                    (tuple(repr(self.labels[i]) for i in xr), \
                     parser.newConst(self.inputTally[i]))
        return a, b, c

    def parse(self, parser):
        firstTime = True
        for i in range(len(self.blocks)):
            if not self.blocks[i].compilesBlank():
                a, b, c = self.getParsingStrings(parser, i, firstTime)
                parser.addLine('%sif __strand__ %s:' % (a,b))
                parser.indent()
                if c:
                    parser.addLine(c)
                parser.parseBlock(self.blocks[i], 0)
                parser.dedent()

                firstTime = False

    def g_childDesiredShapeChange(self, child):
        self.g_fixDesiredShape()

    def g_fixDesiredShape(self):
        'internal.'
        self.g_setDesiredShape(1./ ((1.-self.edgeGap)*\
                                sum(1./self.blocks[0].g_wideDesiredShape() \
                                    for b in self.blocks) \
                                + (len(self.blocks)+1.)*0.5*self.edgeGap))
        self.g_updateDesiredShape()

    def g_draw(self):
        if self.master == None:
            return
        if not self.g_modified:
            for b in self.blocks:
                self.g_drawChild(b)
            if not self.g_modified:
                return

        self.g_clearBlock()
        maxWidth = self.g_relPlacement.scaleToHeight()
        self.g_border = painter.BlockBorder(self, maxWidth, 1.)

        # Size cutoff.
        self.g_sizeCutoff = 0.001
        self.g_addCutoffFeature(painter.Rectangle(self, maxWidth, 1., \
                                                  RectType.Solid))

        # Calculate child heights.
        chY = [1./ch.g_wideDesiredShape() for ch in self.blocks]
        factor = (1.-0.5*(len(self.blocks)+1)*self.edgeGap) / sum(chY)
        chY = [i * factor for i in chY]
        chX = maxWidth - self.edgeGap

        # Draw the child blocks.
        rOut = []
        rIn = []
        yPos = -1.
        for i in range(len(self.blocks)):
            yPos = yPos + self.edgeGap + chY[i]
            cIn, cOut = self.g_addChild(self.blocks[i], chX*chY[i], \
                                        chX/chY[i], (0., yPos))
            rIn.extend(cIn)
            rOut.extend(cOut)
            yPos = yPos + chY[i]

        # Extend input and output routes to border.
        for i in range(len(rIn)):
            x,y = rIn[i]
            self.g_addFeature(painter.Connection(self, (-maxWidth,y), (x, y)))
            rIn[i] = (-maxWidth, y)
        for i in range(len(rOut)):
            x,y = rOut[i]
            self.g_addFeature(painter.Connection(self, (x, y), (maxWidth, y)))
            rOut[i] = (maxWidth, y)

        self.g_rIn, self.g_rOut = rIn, rOut
        self.g_modified = False

    def g_childRouteChange(self, child, inRoute):
        self.g_modified = True
        if self.parent:
            self.parent.g_childRouteChange(self, inRoute)

    def insertParallelChild_internal(self, child, below=True, newChild=None):
        '(child, below, newChild) - internal.'

        if child is None:
            # Translate None calls.
            if below:
                i = 0
            else:
                i = len(self.blocks)
        else:
            i = self.blocks.index(child)
            i = (below and i+1) or i

        if newChild == None:
            newChild = PassBlock(parent=self, nextLoop=self.nextLoop)
        else:
            newChild.setContext(self.blocks[0])

        # Insert it into the list of blocks.
        self.blocks.insert(i, newChild)

        # Duplicate entries in the tallies.
        self.inputTally.insert(i, self.inputTally[i])
        self.outputTally.insert(i, self.outputTally[i])

        # Update the tallies.
        deltaI = newChild.numInputs
        deltaO = newChild.numOutputs
        for j in range(i+1, len(self.inputTally)):
            self.inputTally[j] = self.inputTally[j] + deltaI
            self.outputTally[j] = self.outputTally[j] + deltaO

        # Update my number of inputs and outputs.
        iPos = self.inputTally[i]
        oPos = self.outputTally[i]
        for j in range(deltaI):
            self.numInputs += 1
            if self.parent:
                self.parent.childInputsChanged(self, True, iPos)

        for j in range(deltaO):
            self.numOutputs += 1
            if self.parent:
                self.parent.childOutputsChanged(self,True, oPos)

        self.g_fixDesiredShape()

        # Update escapes list.
        for i in range(len(newChild.passingEscapes)):
            self.childAddEscape(newChild, i)

        return newChild

    def insertParallelChild(self, child, below=True, newChild=None):
        '''insertParallelChild(child, below, newChild) - inserts a block
        above or below the specified child. If newChild is omitted, inserts
        and returns a new PassBlock. If below is True, inserts newChild below
        child, otherwise inserts it above.

        If child is None, inserts new block at the top or bottom.
        '''

        if child is not None and child not in self:
            raise KeyError, 'child does not belong to this block'

        result = self.insertParallelChild_internal(child,below,newChild)

        assert not self.isBroken()
        assert not result.isBroken()

        return result

    def divide(self, child, below=True):
        '''divide(child, after) - after calling this method, this wide block
        will contain exactly two blocks. Everything before the specified child
        block will be in the top half, and everything after it will be in
        the other half. The value of below determines whether the split occurs
        above or below child.
        '''

        if child not in self:
            raise KeyError, 'child does not belong to this block'

        i = self.blocks.index(child)
        i = (below and i+1) or i

        # Create first half.
        if i == 0:
            block1 = self.insertParallelChild_internal(None)
            i = 1
        elif i == 1:
            block1 = self.blocks[0]
        else:
            block1 = WideBlock(parent=self, nextLoop=self.nextLoop)
            block1.blocks = self.blocks[:i]

            block1.numInputs = sum(b.numInputs for b in block1.blocks)
            block1.numOutputs = sum(b.numOutputs for b in block1.blocks)

            block1.inputTally = self.inputTally[:i+1]
            block1.outputTally = self.outputTally[:i+1]

            for b in block1.blocks:
                b.parent = block1
                assert not b.isBroken()

        # Create second half.
        if i == len(self.blocks):
            block2 = self.insertParallelChild_internal(None, below=False)
        elif i == len(self.blocks) - 1:
            block2 = self.blocks[-1]
        else:
            block2 = WideBlock(parent=self, nextLoop=self.nextLoop)
            block2.blocks = self.blocks[i:]

            block2.numInputs = sum(b.numInputs for b in block2.blocks)
            block2.numOutputs = sum(b.numOutputs for b in block2.blocks)

            tStart = self.inputTally[i]
            block2.inputTally = [j-tStart for j in self.inputTally[i:]]
            tStart = self.outputTally[i]
            block2.outputTally = [j-tStart for j in self.outputTally[i:]]

            for b in block2.blocks:
                b.parent = block2
                assert not b.isBroken()

        # Join the two together
        self.blocks = [block1, block2]
        self.inputTally = [0,self.inputTally[i],self.inputTally[-1]]
        self.outputTally = [0,self.outputTally[i],self.outputTally[-1]]

        assert not self.isBroken()
        assert not block1.isBroken()
        assert not block2.isBroken()

    def unnest(self):
        '''unnest() - if this wide block is a child of a wide block, combines
        this block into that block.'''

        if not self.parent:
            raise ValueError('cannot unnest free block')
        if not isinstance(self.parent, WideBlock):
            raise ValueError('WideBlock is not in a WideBlock')

        # Go through blocks and transfer them to parent.
        parent = self.parent
        for i in range(len(self.blocks)):
            pBlock = parent.insertParallelChild_internal(self, below=False)
            block = self.blocks[0]
            block.delete()
            pBlock.mutate(block)

        # Remove me with my one remaining PassBlock
        self.delete()

        assert not self.isBroken()

        if self.master:
            self.master.touch()

        return parent

    def vanish(self):
        '''vanish() - if this block has only one children, this block will be
        replaced with its child.'''

        if len(self.blocks) > 1:
            raise ValueError, 'block must have only one child'

        if not self.parent:
            self.blocks[0].delete()
            return self
        else:
            a = self.blocks[0]
            a.revert()
            self.revert().mutate(a)
            return a

        assert not self.isBroken()

        if self.master:
            self.master.touch()

    def alignChildren(self):
        '''alignChildren() - realigns this block's children.

        This method is only a valid call if:
        * every one of this block's children are LongBlocks.
        * every one of this block's children has exactly two children

        After calling this method:
        * this block will be replaced by a single LongBlock
        * the LongBlock will contain exactly two WideBlocks
        * these WideBlocks will contain the original children of the
            children of the original LongBlocks.
        * the program flow will remain unchanged.

        This method will return the new LongBlock.
        '''

        # Error check.
        for b in self.blocks:
            if not isinstance(b, LongBlock):
                raise TypeError, 'every child must be a LongBlock instance'
            if len(b.blocks) != 2:
                raise ValueError, 'LongBlocks must have exactly two children'

        # Create the new long block and give it two wide blocks.
        result = LongBlock()
        result.blocks[0].mutate(WideBlock())
        result.insertChildSeq_internal(result.blocks[0], True, WideBlock())

        # Populate blocks with their current equivalents.
        maps = []
        for lb in self.blocks:
            # Save the mappings.
            maps.append(lb.maps[0])

            for i in (0, 1):
                # Free and add to wide blocks.
                block = lb.blocks[i]
                block.revert()
                result.blocks[i].insertParallelChild_internal(None, False, \
                                                              block)

        for b in result.blocks:
            # Delete the leftover PassBlock.
            b.blocks[0].delete()

        # Now translate the mappings to one big mapping.
        finalMap = []
        offset = 0
        for m in maps:
            for i in m:
                finalMap.append(offset + i)
            offset = offset + m.numOutputs

        result.maps[0].connections = finalMap
        assert not result.maps[0].isBroken()

        # Replace self with result.
        self.revert().mutate(result)
        assert not self.isBroken()
        assert not result.isBroken()

        if self.master:
            self.master.touch()

        return result

class MasterBlock(OneChildBlock):
    '''MasterBlock(filename, comment) - represents an entire executable
    program. A MasterBlock cannot be a child block of any other block.'''

    def __init__(self, filename='', comment=None):
        super(MasterBlock, self).__init__(parent=None, nextLoop=None)

        if comment == None:
            self.comment = ['<description>']
        else:
            self.comment = comment

        self.master = self
        self.filename = filename
        self.timestamp = time.time()
        self.modified = False
        self.numInputs = 0
        self.numOutputs = 0

        self.child.setMaxInputs(1)
        self.child.master = self

        self.label = None

    def duplicate(self):
        result = MasterBlock(self.filename, comment=self.comment[:])
        result.child.mutate(self.child.duplicate())
        result.timestamp = self.timestamp
        result.modified = self.modified

        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [fcpyMagicNumber, self.lineNumbers, \
                self.comment[:], approvedBlockTypes.index(type(self.child)), \
                self.child.distil(), self.timestamp]

    @staticmethod
    def reconstitute(essence):
        magicNum, lineNums, comment, a, b, timestamp = essence
        if magicNum != fcpyMagicNumber:
            raise ValueError, 'invalid file format'
        result = MasterBlock(comment=comment[:])
        result.child.mutate(approvedBlockTypes[a].reconstitute(b))
        result.timestamp = timestamp
        result.modified = False
        result.lineNumbers = lineNums

        assert not result.isBroken()
        return result

    def childOutputsChanged(self, child, insert, index):
        self.g_modified = True
        self.g_treeModified = True

    def childInputsChanged(self, child, insert, index):
        self.g_modified = True
        self.g_treeModified = True

    def swapChild(self, child, newChild):
        super(MasterBlock, self).swapChild(child, newChild)
        newChild.setMaxInputs(1)

    def reverseRoute(self, strandLabel, exit):
        return []

    def labelStrand(self, label, child, entry):
        if entry == 0:
            self.label = label

    def prepBlock(self):
        badConsts = super(MasterBlock, self).prepBlock()

        # Init label.
        self.label = None

        # Prep child.
        badConsts.extend(self.child.prepBlock())

        # Return badConsts
        return badConsts

    def parse(self, parser):
        if self.comment:
            parser.addLine(parser.newConst('\n'.join(self.comment)))
        parser.addLines(['__strand_stack__ = []',
                         'import sys'])
        parser.addLabel(self.label)
        parser.parseBlock(self.child, 0)

    def g_draw(self):
        if not self.g_modified:
            self.child.g_draw()
            return
        self.g_modified = False

        self.g_relPlacement.scaleDesired(self.g_desiredShape)
        self.g_clearBlock()

        self.g_border = painter.BlockBorder(self, 1.618, 1.)
        self.g_sizeCutoff = 0.001

        if self.filename:
            fName = os.path.basename(self.filename)
        else:
            fName = '< new file >'

        # Size cutoff shape.
        self.g_addCutoffFeature(painter.Rectangle(self, 1.618, 1.0, \
                                                  RectType.Solid))
        self.g_addCutoffFeature(painter.Text(self, fName, \
                                             1., (0.,0.)))

        # Standard shape.
        self.g_addFeature(painter.Rectangle(self, 1.618, 1.0, RectType.Border))

        rIn, rOut = self.g_addChild(self.child, .81, 1., (.618,0.))
        self.g_addFeature(painter.Text(self, fName, \
                                       0.618, (-.95, -0.618)))
        self.g_addFeature(painter.MultilineText(self, self.comment, \
                          0.618, self.commentCallback, (-.95, 0.382), \
                          painter.cmtColour))

        # Draw routes in and out.
        self.g_addFeature(painter.Connection(self, (-.382, 0), rIn[0]))
        for r in rOut:
            self.g_addFeature(painter.Connection(self, r, (1.618, r[1])))

        self.g_rIn = []
        self.g_rOut = []

    def g_childDesiredShapeChange(self, child):
        self.g_modified = True
        self.g_treeModified = True

    def commentCallback(self, values):
        'internal.'
        self.comment = list(values)

        if self.master:
            self.master.touch()

    def touch(self):
        'internal. Updates my timestamp and my modified flag.'
        self.timestamp = time.time()
        self.modified = True

    @staticmethod
    def load(filename):
        'load() - creates and returns a new MasterBlock from a file.'
        f = file(filename)
        essence = f.read()
        f.close()

        result = MasterBlock.reconstitute(eval(essence))
        result.filename = filename
        return result

    def save(self):
        'save() - saves the block to its filename.'
        essence = self.distil()

        f = file(self.filename, 'w')
        f.write(repr(essence))
        f.close()

class LoopBlock(OneChildBlock):
    def __init__(self, parent=None, nextLoop=None):
        super(LoopBlock, self).__init__(parent=parent, nextLoop=nextLoop)
        self.child.nextLoop = self

        self.numInputs = 1
        self.numOutputs = 0
        # Loop block passes no escapes, but maintains a list of caught ones.
        self.escapes = []
        self.map = LoopMapping(self.child, self.numInputs)
        self.g_desiredShape = 2./3. * (self.child.g_desiredShape + 1)
        self.g_lastDraw1Member = True
        assert not LoopBlock.isBroken(self)

    def isBroken(self):
        if super(LoopBlock, self).isBroken():
            return True
        if self.map.isBroken():
            return True
        if self.map.numInputs != self.child.numOutputs + self.numInputs:
            return True
        if self.numOutputs != len(self.escapes):
            return True
        return False

    def duplicate(self):
        result = LoopBlock()
        result.child.mutate(self.child.duplicate())
        result.map.connections = list(self.map.connections)
        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [self.lineNumbers, \
                approvedBlockTypes.index(type(self.child)), \
                self.child.distil(), list(self.map)]

    @staticmethod
    def reconstitute(essence):
        lineNums, a, b, connections = essence
        result = LoopBlock()
        result.child.mutate(approvedBlockTypes[a].reconstitute(b))
        result.map.connections = list(connections)
        result.lineNumbers = lineNums
        assert not result.isBroken()

        return result

    def childOutputsChanged(self, child, insert, index):
        # Tell the map.
        self.map.modifyInputs(insert, index + self.numInputs)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def childInputsChanged(self, child, insert, index):
        # Tell the map.
        self.map.modifyOutputs(insert, index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def childAddEscape(self, child, index):
        # Insert the escape into my list.
        self.escapes.insert(index, child.passingEscapes[index])

        # Don't notify parent though.

        self.numOutputs = self.numOutputs + 1
        if self.parent:
            self.parent.childOutputsChanged(self, True, index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

        assert not self.isBroken()

    def childRemoveEscape(self, escape):
        i = self.escapes.index(escape)
        self.escapes.pop(i)
        self.numOutputs = self.numOutputs - 1

        if self.parent:
            self.parent.childOutputsChanged(self, False, i)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

        assert not self.isBroken()

    def swapChild(self, child, newChild):
        super(LoopBlock, self).swapChild(child, newChild)
        self.child.setMaxInputs(0)
        self.map.setNumOutputs(newChild.numInputs)
        self.map.setNumInputs(newChild.numOutputs + self.numInputs)
        self.map.nextBlock = newChild

        if self.parent:
            # It might change my input locations.
            self.parent.g_childRouteChange(self, True)
        self.g_childDesiredShapeChange(newChild)

    def reverseRoute(self, label, exit):
        # Compiler optimisation: tagging
        if self.numInputs == 1 >= self.numOutputs:
            self.tagLabel = label

        # Send any reverse routes back to the escapes.
        return self.escapes[exit].reverseRoute(label, 0)

    def labelStrand(self, label, child, entry):
        # Strands can go in circles! How exciting!
        routes = [entry]
        while len(routes) > 0:
            # Send it through the mapping.
            newRoutes = []
            for r in routes:
                newRoutes.extend(self.map.reverseRoute(label, r))
            if len(newRoutes) == 0:
                break

            # Send it through the block or back to parent.
            routes = []
            for r in newRoutes:
                # Check if it leaves the loop.
                if r < self.numInputs:
                    if self.parent:
                        self.parent.labelStrand(label, self, r)
                else:
                    r = r - self.numInputs
                    routes.extend(self.child.reverseRoute(label, r))

    def prepBlock(self):
        badConsts = super(LoopBlock, self).prepBlock()

        # Prep child.
        badConsts.extend(self.child.prepBlock())

        # return bad consts.
        return badConsts

    def parse(self, parser):
        parser.addLine('while True:')
        parser.parseBlock(self.child)

    def g_childDesiredShapeChange(self, child):
        if isinstance(self.child, LongBlock) and len(self.child.blocks) > 1:
            self.g_setDesiredShape(1.618)
        else:
            self.g_setDesiredShape(0.6*self.child.g_desiredShape + 1.2)

    def g_draw(self):
        if self.master == None:
            return

        if not self.g_modified and not self.child.g_modified:
            for ch in self.g_children:
                self.g_drawChild(ch)
            if not self.g_modified and not self.child.g_modified:
                return

        self.g_clearBlock()
        self.g_sizeCutoff = 0.001

        if (not isinstance(self.child, LongBlock)) or \
                   (len(self.child.blocks) == 1):
            if not self.g_lastDraw1Member:
                if self.parent:
                    self.parent.g_childRouteChange(self, True)
                    self.parent.g_childRouteChange(self, False)
                self.g_lastDraw1Member = True

            # Non-long-block child: draw child with arrows going around.
            maxHeight = self.g_relPlacement.scaleToWidth()
            blockHeight = min(maxHeight, 1./self.g_desiredShape)

            delta = 0.8*blockHeight / (self.numInputs + 1.)
            rIn = [(-1., -0.8*blockHeight + (i+1)*delta) for i in range(self.numInputs)]
            delta = blockHeight / (self.numOutputs + 1.)
            rOut = [(1., (i+1)*delta-blockHeight) for i in range(self.numOutputs)]
            rEsc = [(1.-0.6*blockHeight, y) for x,y in rOut]
            self.escTextRadius = min(0.5 * delta, 0.3*blockHeight)

            a = blockHeight * 0.3

            # Draw border.
            self.g_border = painter.BlockBorder(self, 1., blockHeight)

            # Draw child.
            chX = 1. - 4. * a
            chY = 0.9 * blockHeight - a
            chIn, chOut = self.g_addChild(self.child, chX*chY, chX/chY, \
                                          (-2.*a, -a+0.1*blockHeight))

            # Connect child's outputs around.
            guides = [i / (len(chOut) + 1.) for i in range(1, 1+len(chOut))]
            newIn = []
            for i in range(len(chOut)):
                p1 = (1. - 3.*a - 2.*a*guides[i], a)
                p2 = (-2.*a, blockHeight - 2.*a*guides[i])
                p3 = (-1. + 1.8*a*guides[i], a)
                newIn.append(p3)
                self.g_addFeature(painter.Connection(self, chOut[i], p1, 0., \
                                                     0.5*pi))
                self.g_addFeature(painter.Connection(self, p1, p2, 0.5*pi, pi))
                self.g_addFeature(painter.Connection(self, p2, p3, pi, -0.5*pi))

            # Space the map outputs.
            spacings = [chIn[0][1] + blockHeight] + \
                       [chIn[j+1][1] - chIn[j][1] for j in range(len(chIn)-1)] \
                       + [blockHeight-2*a-chIn[-1][1]]
            xm1 = -1. + 1.8*a
            ptOut = self.spacePoints(spacings, (xm1, -blockHeight), \
                                     (xm1, blockHeight - 2. * a))
            for j in range(len(ptOut)):
                self.g_addFeature(painter.Connection(self, ptOut[j], chIn[j]))

            # Draw the map.
            mapIn = rIn + newIn
            mAng = [0.] * len(rIn) + [-0.5*pi] * len(newIn)
            ptIn = [(mapIn[j], mAng[j]) for j in range(self.map.numInputs)]
            ptOut = [(n, 0.) for n in ptOut]
            self.g_addFeature(painter.MapFeature(self, blockHeight, \
                                                 ptIn, ptOut, self.map))

            forPt = (-1. + a, -.4 * blockHeight)
            forRad = a
        else:
            if self.g_lastDraw1Member:
                if self.parent:
                    self.parent.g_childRouteChange(self, True)
                    self.parent.g_childRouteChange(self, False)
                self.g_lastDraw1Member = False

            # Long block child: draw everything in circular formation.
            maxHeight = self.g_relPlacement.scaleDesired(self.g_desiredShape)
            ch = self.child
            ch.g_nonDrawn = True
            ch.g_modified = False

            # Draw boundary.
            self.g_border = painter.BlockBorder(self, 1.618, 1.)

            # 1. Calculate inner radius.
            chDesSh = sum(b.g_longDesiredShape() for b in ch.blocks) + \
                      0.25*(len(ch.blocks)-1.) + .5
            r = chDesSh / (2*pi + chDesSh)

            # 2. Go through and draw blocks.
            mapTheta = 0.5*pi/chDesSh
            pMapTheta = 1.*pi/chDesSh
            theta = -pi + 0.5*pMapTheta

            # Calculate position of for block text.
            l = 1. - r * cos(0.5*pMapTheta)
            h = r * sin(0.5*pMapTheta)
            forRad = 0.5 * (l + h ** 2 / l)
            forPt = (-1.618 + forRad, 0.)

            # Define how to draw a block.
            def drawBlock(b, theta):
                bDesSh = b.g_longDesiredShape()
                dTheta = 2*pi*bDesSh/chDesSh

                # Find corner positions and block dimensions.
                p0m = (cos(theta), sin(theta))
                p1m = (cos(theta+dTheta), sin(theta+dTheta))
                p0, p1 = [(-.618+r*x, r*y) for x,y in (p0m, p1m)]
                p0m, p1m = [(-.618+x, y) for x,y in (p0m, p1m)]
                bX = ((p0[0]-p1[0])**2 + (p0[1]-p1[1])**2) ** 0.5 / 2.
                bY = bX / bDesSh

                # Find centre of base and centre of block.
                theta = theta + 0.5*dTheta
                p2 = tuple(0.5*(p0[i]+p1[i]) for i in (0,1))
                p3 = (p2[0] + bY*cos(theta), p2[1] + bY*sin(theta))

                # Draw block.
                blockAngle = theta + pi/2.
                res = self.g_addChild(b, bX * bY, bX / bY, p3, blockAngle)

                theta = theta + 0.5*dTheta + mapTheta

                return res + (theta, blockAngle, p0, p0m, p1, p1m)

            # First block.
            rIn0, rOut1, theta, bAngle1, pi0a, pi0b, po1a, po1b = \
                  drawBlock(ch.blocks[0], theta)
            bAngle0 = bAngle1

            for i in range(1, len(ch.blocks)):
                oldTheta = theta + 0.5*pi

                # Each subsequent block.
                rIn2, rOut2, theta, bAngle2, pi2a, pi2b, po2a, po2b = \
                      drawBlock(ch.blocks[i], theta)

                # Space map inputs.
                if len(rOut1) == 0:
                    ptIn = []
                else:
                    spacings = [1. - (rOut1[0][0]**2 + rOut1[0][1]**2)**0.5] + \
                               [((rOut1[j+1][0] - rOut1[j][0]) ** 2 + \
                                 (rOut1[j+1][1] - rOut1[j][1]) ** 2) ** 0.5 \
                                for j in range(len(rOut1) - 1)] + \
                               [(rOut1[-1][0]**2 + rOut1[-1][1]**2)**0.5 - r]
                    ptIn = self.spacePoints(spacings, po1b, po1a)

                    for j in range(len(ptIn)):
                        self.g_addFeature(painter.Connection(self, rOut1[j], \
                                    ptIn[j], bAngle1, oldTheta-mapTheta))

                # Space map outputs.
                spacings = [1. - (rIn2[0][0]**2 + rIn2[0][1]**2)**0.5] + \
                           [((rIn2[j+1][0] - rIn2[j][0]) ** 2 + \
                             (rIn2[j+1][1] - rIn2[j][1]) ** 2) ** 0.5 \
                            for j in range(len(rIn2) - 1)] + \
                           [(rIn2[-1][0]**2 + rIn2[-1][1]**2)**0.5 - r]
                ptOut = self.spacePoints(spacings, pi2b, pi2a)

                for j in range(len(ptOut)):
                    self.g_addFeature(painter.Connection(self, ptOut[j], \
                                rIn2[j], oldTheta, bAngle2))

                # Previous mapping.
                m = ch.maps[i-1]
                ptIn = [(n, oldTheta-mapTheta) for n in ptIn]
                ptOut = [(n, oldTheta) for n in ptOut]
                self.g_addFeature(painter.MapFeature(self, 1. - r, \
                                                     ptIn, ptOut, m))
                rOut1, bAngle1 = rOut2, bAngle2
                po1a, po1b = po2a, po2b

            # Calculate borders of first mapping.
            map0y = tan(0.5 * pMapTheta)

            # Calculate entry and exit routes.
            delta = 2. * map0y / (self.numInputs + 1.)
            rIn = [(-1.618, -map0y + (i+1)*delta) for i in range(self.numInputs)]
            delta = 2. / (self.numOutputs + 1.)
            rOut = [(1.618, (i+1)*delta-1.) for i in range(self.numOutputs)]
            rEsc = [(1., y) for x,y in rOut]
            self.escTextRadius = min(0.5 * delta, 0.309)

            # Primary map - space inputs.
            if len(rOut2) == 0:
                rMapIn = rIn
            else:
                spacings = [1. - (rOut2[0][0]**2 + rOut2[0][1]**2)**0.5] + \
                           [((rOut2[j+1][0] - rOut2[j][0]) ** 2 + \
                             (rOut2[j+1][1] - rOut2[j][1]) ** 2) ** 0.5 \
                            for j in range(len(rOut2) - 1)] + \
                           [(rOut2[-1][0]**2 + rOut2[-1][1]**2)**0.5 - r]
                ptIn = self.spacePoints(spacings, po2b, po2a)

                for j in range(len(ptIn)):
                    self.g_addFeature(painter.Connection(self, rOut2[j], \
                                ptIn[j], bAngle2, theta-mapTheta+0.5*pi))
                rMapIn = rIn + ptIn

            # Space outputs.
            spacings = [1. - (rIn0[0][0]**2 + rIn0[0][1]**2)**0.5] + \
                       [((rIn0[j+1][0] - rIn0[j][0]) ** 2 + \
                         (rIn0[j+1][1] - rIn0[j][1]) ** 2) ** 0.5 \
                        for j in range(len(rIn0) - 1)] + \
                       [(rIn0[-1][0]**2 + rIn0[-1][1]**2)**0.5 - r]
            ptOut = self.spacePoints(spacings, pi0b, pi0a)

            for j in range(len(ptOut)):
                self.g_addFeature(painter.Connection(self, ptOut[j], \
                            rIn0[j], 0.5*(pMapTheta-pi), bAngle0))

            # Draw primary map.
            rAngle = [0.] * len(rIn) + [theta-mapTheta+0.5*pi] * len(rOut2)
            ptIn = [(rMapIn[j], rAngle[j]) for j in range(self.map.numInputs)]
            ptOut = [(n, 0.5*(pMapTheta-pi)) for n in ptOut]
            self.g_addFeature(painter.MapFeature(self, 1. - r, \
                                                 ptIn, ptOut, self.map))

        # Draw escapes.
        childIndex = -1
        i = -1
        while -i <= len(self.escapes):
            # Go through in reverse order to accomodate for for loops.
            ch = self.g_children[childIndex]
            if self.escapes[i] in ch.passingEscapes:
                # We have the block and the escape.
                x0, y0 = ch.g_border.pt
                pos1 = (x0+ch.g_border.halfWidth, y0-ch.g_border.halfHeight)
                pl = ch.g_relPlacement
                pos1 = pl.parentPoint(pos1, self.g_relPlacement.area)
                ang = pl.parentAngle(-0.25 * pi)

                pos2 = rEsc[i]
                self.g_addFeature(painter.EscapeRoute(self, pos1, pos2, ang,0.))
                pos2b = tuple(0.5*(rOut[i][j] + pos2[j]) for j in (0,1))
                self.g_addFeature(painter.EscapeText(self, self.escapes[i], \
                                                     self.escTextRadius, pos2b))
                i = i - 1
            else:
                childIndex = childIndex - 1

        self.g_addFeature(painter.Arrows(self, rEsc))

        # Save info for for block drawing.
        if isinstance(self, ForBlock):
            donePt = (0.5*(rOut[0][0]+rEsc[0][0]), rOut[0][1])
            self.g_forBlockSave = forPt, forRad, donePt

        # The shape with size cutoff.
        width = self.g_border.halfWidth
        height = self.g_border.halfHeight
        self.g_addCutoffFeature(painter.Rectangle(self, width, height, \
                                                  RectType.Solid))
        self.g_addCutoffFeature(painter.Arrows(self, rIn))

        self.g_rIn, self.g_rOut = rIn, rOut
        self.g_modified = False

    def transmitContext(self):
        self.child.master = self.master
        self.child.transmitContext()

    def transmitLoopContext(self):
        # Loop context is transmitted no further.
        pass

    def setNumEntries(self, numInputs):
        '''Sets the number of entry routes to this loop.'''
        delta = numInputs - self.numInputs
        if delta > 0:
            pos = self.numInputs - self.child.numOutputs
            for i in range(delta):
                self.map.modifyInputs(True, pos)
        if self.numInputs > numInputs:
            pos = numInputs - self.child.numOutputs
            for i in range(-delta):
                self.map.modifyInputs(False, pos)
        self.setNumInputs(numInputs)

        if self.master:
            self.master.touch()

class ForBlock(LoopBlock):
    def __init__(self, indexExpression='', inExpression='',
                 parent=None, nextLoop=None):
        super(ForBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        self.indexExpression = indexExpression
        self.inExpression = inExpression
        self.label = None

        # For-loop has exactly one standard exit. (non-escape)
        self.numOutputs = 1

    def isBroken(self):
        if Block.isBroken(self):
            return True
        if self.map.isBroken():
            print 'ForBlock map is broken.'
            return True
        if self.map.numInputs != self.child.numOutputs + self.numInputs:
            print 'ForBlock map inputs: %d, child outputs: %d, my inputs: %d' % \
                  (self.map.numInputs, self.child.numOutputs, self.numInputs)
            return True
        if self.numOutputs != len(self.escapes) + 1:
            print 'ForBlock outputs: %d, num escapes: %d' % (self.numOutputs,
                                                        len(self.escapes))
            return True
        return False

    def duplicate(self):
        result = ForBlock(self.indexExpression, self.inExpression)
        result.child.mutate(self.child.duplicate())
        result.map.connections = list(self.map.connections)
        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [self.lineNumbers, \
                self.indexExpression, self.inExpression, \
                approvedBlockTypes.index(type(self.child)), \
                self.child.distil(), list(self.map)]

    @staticmethod
    def reconstitute(essence):
        lineNums, idxExp, inExp, a, b, connections = essence
        result = ForBlock(idxExp, inExp)
        result.child.mutate(approvedBlockTypes[a].reconstitute(b))
        result.map.connections = list(connections)
        result.lineNumbers = lineNums

        assert not result.isBroken()
        return result

    def reverseRoute(self, label, exit):
        # Compiler optimisation: tagging
        if self.numInputs == 1 >= self.numOutputs:
            self.tagLabel = label

        # Catch any reverse routes to the standard exit.
        if exit == 0:
            self.label = label
            return []
        else:
            # Send any reverse routes back to the escapes.
            return self.escapes[exit - 1].reverseRoute(label, 0)

    def tagRoute(self, tagBlock, exit):
        # Only catch the else strand.
        if exit == 0:
            self.tag = tagBlock

    def prepBlock(self):
        badConsts = super(LoopBlock, self).prepBlock()

        # Init label.
        self.labels = None
        self.tag = None

        # Prep child.
        badConsts.extend(self.child.prepBlock())

        # Check validity.
        try:
            code = compile('for %s in %s: pass\n' % (self.indexExpression,
                                                     self.inExpression),
                           '', 'exec')
            badConsts.append(code.co_consts)
        except SyntaxError, err:
            raise EPrepBlockError, (self, err.msg)

        # return bad consts.
        return badConsts

    def parse(self, parser):
        parser.addLine('for %s in %s:' % (self.indexExpression,
                                          self.inExpression))
        parser.parseBlock(self.child)
        if self.label is not None:
            parser.addLine('else:')
            parser.indent()
            parser.addTag(self, self.tag)
            parser.addLabel(self.label)
            parser.dedent()

    def g_draw(self):
        if self.master == None:
            return

        if not self.g_modified and not self.child.g_modified:
            for ch in self.g_children:
                self.g_drawChild(ch)
            if not self.g_modified and not self.child.g_modified:
                return

        # First draw the loop itself.
        super(ForBlock, self).g_draw()

        # Decide where to put the for condition.
        #width = self.g_relPlacement.shape * self.g_relPlacement.area
        #height = self.g_relPlacement.area / self.g_relPlacement.shape
        donePt = self.g_rOut[0]
        forPt, r, donePt = self.g_forBlockSave

        # Now put the for condition on it.
        self.g_addFeature(painter.InteractiveText(self, ['for ',''], \
                [' in',''], [self.indexExpression, self.inExpression], \
                r, self.textCallback, forPt, painter.tx4Colour))

        # And add a 'done' text.
        self.g_addFeature(painter.Text(self, 'done', self.escTextRadius, \
                                       donePt, painter.rnbColour))

        self.g_modified = False

    def textCallback(self, values):
        'internal.'
        self.indexExpression, self.inExpression = values

        if self.master:
            self.master.touch()

class EscapeBlock(Block):
    def __init__(self, parent=None, nextLoop=None, comment=''):
        super(EscapeBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        self.comment = comment
        self.numInputs = 1
        self.numOutputs = 0
        self.label = None
        self.passingEscapes = [self]

        if self.nextLoop and self.parent:
            self.parent.childAddEscape(self, 0)

        self.g_desiredShape = 1.

    def duplicate(self):
        result = EscapeBlock(comment=self.comment)
        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [self.lineNumbers, self.comment]

    @staticmethod
    def reconstitute(essence):
        lineNums, comment = essence
        result = EscapeBlock(comment=comment)
        result.lineNumbers = lineNums
        assert not result.isBroken()
        return result

    def reverseRoute(self, label, exit):
        # If we get a label, keep it.
        self.label = label
        return []

    def prepBlock(self):
        badConsts = super(EscapeBlock, self).prepBlock()

        # Check for bounding loop.
        if not self.nextLoop:
            raise EPrepBlockError, (self, 'escape must be within loop')

        return badConsts

    def parse(self, parser):
        # If we're inside any bottleneck's, undo the damage.
        if self.bnLevel > 0:
            parser.addLine('__strand_stack__ = __strand_stack__[:%s]' % \
                           parser.newConst(-self.bnLevel))
        parser.addLabel(self.label)
        parser.addLine('break')

    def g_draw(self):
        if self.master == None:
            return

        if not self.g_modified:
            return
        self.g_modified = False

        self.g_relPlacement.scaleDesired(self.g_desiredShape)
        self.g_clearBlock()

        # Box
        self.g_border = painter.BlockBorder(self, 1., 1.)
        self.g_addFeature(painter.Rectangle(self, 0.8, 0.8, RectType.Escape))
        self.g_addFeature(painter.Arrows(self, [(-.8, 0)]))

        # Escape-route to top-right corner.
        self.g_addFeature(painter.EscapeRoute(self, (0.8, -0.8), \
                                              (1., -1.), -0.25*pi))

        # Draw the text.
        self.g_addFeature(painter.InteractiveText(self, [' '], [' '], \
                        [self.comment], 0.8, self.textCallback))

        self.g_rIn, self.g_rOut = [(-.8, 0.)], []

    def textCallback(self, values):
        'internal.'
        self.comment = values[0]

        if self.master:
            self.master.touch()

class GroupingBlock(OneChildBlock):
    def __init__(self, parent=None, nextLoop=None, comment=None):
        super(GroupingBlock, self).__init__(parent=parent, nextLoop=nextLoop)

        if comment == None:
            self.comment = ['<description>']
        else:
            self.comment = comment

        self.numInputs = 1
        self.numOutputs = 1

        self.g_desiredShape = 1.618

    def isBroken(self):
        if super(GroupingBlock, self).isBroken():
            return True
        return self.numInputs != self.child.numInputs or \
               self.numOutputs != self.child.numOutputs

    def duplicate(self):
        result = GroupingBlock(comment=self.comment[:])
        result.child.mutate(self.child.duplicate())
        assert not result.isBroken()
        assert self.numInputs == result.numInputs
        assert self.numOutputs == result.numOutputs
        return result

    def distil(self):
        return [self.lineNumbers, \
                self.comment, approvedBlockTypes.index(type(self.child)), \
                self.child.distil()]

    @staticmethod
    def reconstitute(essence):
        lineNums, comment, a, b = essence
        result = GroupingBlock(comment=comment)
        result.child.mutate(approvedBlockTypes[a].reconstitute(b))
        result.lineNumbers = lineNums
        assert not result.isBroken()
        return result

    def setMaxInputs(self, maxInputs):
        # Child can only have as many inputs as me.
        super(GroupingBlock, self).setMaxInputs(maxInputs)
        self.child.setMaxInputs(maxInputs)

    def childOutputsChanged(self, child, insert, index):
        self.numOutputs = child.numOutputs
        if self.parent:
            self.parent.childOutputsChanged(self, insert, index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def childInputsChanged(self, child, insert, index):
        self.numInputs = child.numInputs
        if self.parent:
            self.parent.childInputsChanged(self, insert, index)

        self.g_modified = True
        if self.master:
            self.master.g_treeModified = True

    def swapChild(self, child, newChild):
        super(GroupingBlock, self).swapChild(child, newChild)
        self.setNumInputs(newChild.numInputs)
        self.setNumOutputs(newChild.numOutputs)

    def reverseRoute(self, label, exit):
        # Compiler optimisation: tagging
        if self.numInputs == 1 >= self.numOutputs:
            self.tagLabel = label

        return self.child.reverseRoute(label, exit)

    def labelStrand(self, label, child, entry):
        assert child is self.child
        return self.parent.labelStrand(label, self, entry)

    def tagRoute(self, tagBlock, exit):
        self.child.tagRoute(tagBlock, exit)

    def tagStrand(self, tagBlock, child, entry):
        assert child is self.child
        self.parent.tagStrand(tagBlock, self, entry)

    def prepBlock(self):
        badConsts = super(GroupingBlock, self).prepBlock()
        badConsts.extend(self.child.prepBlock())

        return badConsts

    def parse(self, parser):
        parser.parseBlock(self.child, 0)

    def g_draw(self):
        if self.master == None:
            return
        if not self.g_modified:
            self.g_drawChild(self.child)
            if not self.g_modified:
                return

        self.g_clearBlock()
        assert self.g_desiredShape == 1.618
        self.g_relPlacement.scaleDesired(self.g_desiredShape)
        self.g_border = painter.BlockBorder(self, 1.618, 1.)

        self.g_sizeCutoff = 0.3

        # Size cutoff shape.
        self.g_addCutoffFeature(painter.Rectangle(self, 1.618, 1.0, \
                                                  RectType.Solid))
        self.g_addCutoffFeature(painter.Arrows(self, [(-1.618, 0.)]))
        self.cutoff = painter.MultilineText(self, self.comment, \
                            1., self.commentCallback, (0., 0.), \
                            painter.cmtColour)
        self.g_addCutoffFeature(self.cutoff)

        # Standard shape.
        self.g_addFeature(painter.Rectangle(self, 1.618, 1.0, RectType.Border))

        rIn, rOut = self.g_addChild(self.child, .81, 1., (.618,0.))
        self.g_addFeature(painter.MultilineText(self, self.comment, \
                          0.618, self.commentCallback, (-.95, 0.), \
                          painter.cmtColour))

        # Extend inputs and outputs.
        for x,y in rIn:
            pt = (-1.618, y)
            self.g_addFeature(painter.Connection(self, pt, (x,y)))
            self.g_rIn.append(pt)
        for x,y in rOut:
            pt = (1.618, y)
            self.g_addFeature(painter.Connection(self, (x,y), pt))
            self.g_rOut.append(pt)

        self.g_addCutoffFeature(painter.Arrows(self, self.g_rIn))

        self.g_modified = False

    def g_childRouteChange(self, child, inRoute):
        self.g_modified = True
        if self.parent:
            self.parent.g_childRouteChange(self, inRoute)

    def commentCallback(self, values):
        'internal.'
        self.comment = list(values)
        self.cutoff.setValues(list(values))

        if self.master:
            self.master.touch()


# The following list is used to identify block types for loading and saving.
approvedBlockTypes = [PassBlock, IfBlock, BottleneckBlock, ExecBlock, \
                      DefBlock, ClassBlock, ProcedureBlock, ProcCallBlock, \
                      TryBlock, LongBlock, WideBlock, LoopBlock, ForBlock, \
                      EscapeBlock, GroupingBlock]

##################################
# classes to parse code tree
##################################

def compileBlock(block):
    '''Compiles the specified block to a code object. If at the time of
    compilation, there is a .pyc file with a name corresponding to the
    block's filename, then timestamps are used to decide whether to simply
    load from the file, or compile.

    block:      the block to compile.
    filename:   the filename to use as a reference.

    Returns a code object of the compiled block.
    '''
    fcCode = FlowchartCode(block)
    fcCode.compile()
    return fcCode.codeObject

class FlowchartCode(object):
    def __init__(self, block):
        '''Compiles the specified block to a code object. If at the time of
        compilation, there is a .pyc file with a name corresponding to the
        block's filename, then timestamps are used to decide whether to simply
        load from the file, or compile.

        block:      the block to compile.
        filename:   the filename to use as a reference.
        '''
        # So traceback never gets line 1 of the source file.
        self.nextLineNo = 2
        self.compiled = False
        self.blockLines = {}

        # Check if it's a MasterBlock - if not, make one.
        if isinstance(block, MasterBlock):
            self.block = block
        else:
            # If it's already bound we can't compile it.
            if block.parent is not None:
                raise ValueError, "can't compile bound Block"

            # Create a MasterBlock to house it.
            newBlock = MasterBlock(filename='<flowchart>')
            newBlock.child.mutate(block)
            self.block = newBlock

        self.filename = self.block.filename

    def compile(self):
        '''Actually performs the compilation. This is not in the init routine
        because if an exception occured there you would not get the
        FlowchartCode object back, and you need it to pinpoint the error's
        location.'''

        if self.compiled:
            return

        # Look for an existing pyc file.
        if self.block.filename:
            base, ext = os.path.splitext(self.block.filename)
            pycName = base + '.pyc'

            # Check if such a file exists and get timestamp.
            try:
                pycTime = os.stat(pycName)[stat.ST_MTIME]
            except OSError:
                pass
            else:
                # Compare the timestamp to the block's timestamp.
                if pycTime > self.block.timestamp:
                    # pyc file's more recent.
                    self.loadPyc(pycName)
                    self.compiled = True
                    return
        else:
            pycName = None

        # Prep the block.
        consts = self.block.prepBlock()

        # Parse the block.
        parser = BlockParser(self, self.block, consts)
        parser.parseAll()
        self.codeObject = parser.compile()
        self.updateLineNumbers()

        self.compiled = True

        # If the file is named, save a .pyc
        if pycName:
            self.savePyc(pycName, time.time())

    def registerCompile(self, parser):
        '''Called during compilation by parsers belonging to this code block.
        Indicates that the parser is about to compile it's code and wants to
        know what filename and first linenumber to use.'''

        result = self.filename, self.nextLineNo
        parser.firstLineNumber = self.nextLineNo
        self.nextLineNo = self.nextLineNo + len(parser.lines)

        return result

    def setBlockLines(self, parser, block, lines):
        '''Called during compilation by parsers belonging to this code block.
        Indicates that the specified block used the specified line numbers
        within the specified parser.'''

        # Update our list of block line numbers.
        assert len(lines) == 2
        bl = self.blockLines.setdefault(block, [])
        bl.append((True, parser, lines))

    def unsetBlockLines(self, parser, block, lines):
        '''Called during compilation by parsers belonging to this code block.
        Indicates that the specified block did not use the specified line
        numbers within the specified parser, even though the line numbers
        are within a range which would be attributed to this block. This is
        required because tagging optimisation moves some blocks around.'''

        # Update our list of block line numbers.
        assert len(lines) == 2
        bl = self.blockLines.setdefault(block, [])
        bl.append((False, parser, lines))

    def updateLineNumbers(self):
        '''Updates the line numbers in the blocks based on the compilation
        that's just occurred.'''

        for b, chunks in self.blockLines.iteritems():
            lines = []
            # Add the things.
            for p,l in [(p, l) for add, p, l in chunks if add]:
                lines.extend([i + p.firstLineNumber for i in l])

            # Remove the others.
            unLines = [(p,l) for add, p, l in chunks if not add]
            i = 0
            assert len(lines) % 2 == 0
            while i < len(lines):
                m1,m2 = lines[i:i+2]
                for p,l in unLines:
                    l1,l2 = [j + p.firstLineNumber for j in l]
                    if l1 <= m1 <= m2 <= l2:
                        lines.pop(i)
                        lines.pop(i)
                        i = i - 2
                        break
                    elif l1 <= m1 < l2 < m2:
                        m1 = l2
                        lines[i] = m1
                    elif m1 < l1 < m2 <= l2:
                        m2 = l1
                        lines[i+1] = m2
                    elif m1 < l1 <= l2 < m2:
                        lines.extend([l2, m2])
                        m2 = l1
                        lines[i+1] = m2
                i = i + 2

            b.lineNumbers = lines

        self.block.fixLineNumbers()
        self.block.touch()

    def execute(self, globals=None, locals=None):
        '''execute(globals[, locals]) - executes the code in this object.
        '''
        if not self.compiled:
            self.compile()

        if globals == None:
            globals = {}
        if locals == None:
            locals = globals

        exec self.codeObject in globals, locals

    def savePyc(self, cfile, timestamp):
        """Save a Byte-compiled Python code object to a .pyc or .pyo file.

        Arguments:

        codeobject:     the code object to save.
        cfile:          target filename; usually this would be the name of the
                        source file with an extension of .pyc normally or .pyo
                        in optimising mode.
        timestamp:      the timestamp to put in the compiled file. This should
                        be the time of last modification of the code object
                        from which it's created.

        To decide whether to use a .pyc or .pyo extension, you may wish to use the
        idiom: basename + (__debug__ and 'c' or 'o')

        If the file exists it is the responsibility of the caller to check the
        timestamp of the file and only overwrite it if changes have been made to
        the code object since the file was written.

        The code in this routine is copied from the bottom of the compile()
        function in the file lib/py_compile.py. That is where developers should
        look for updates.
        """

        if not self.compiled:
            self.compile()
        codeobject = self.codeObject

        fc = open(cfile, 'wb')
        fc.write('\0\0\0\0')
        wr_long(fc, long(timestamp))
        marshal.dump(codeobject, fc)
        fc.flush()
        fc.seek(0, 0)
        fc.write(MAGIC)
        fc.close()

    def loadPyc(self, filename):
        'Load a Byte-compiled Python code object from a .pyc or .pyo file.'

        fc = open(filename, 'rb')
        a = fc.read(4)
        assert a == MAGIC

        # Read another 4 bytes of timestamp.
        fc.read(4)

        # Get the rest of the data.
        data = fc.read()
        self.codeObject = marshal.loads(data)

        fc.close()

class BlockParser(object):
    firstConst = -11

    def __init__(self, fcCode, block, badConsts=[]):
        self.fcCode = fcCode
        self.block = block
        self.badConsts = []
        self.lines = []
        self.indentLevel = 0
        self.substitutions = {}
        self.nextConst = self.firstConst
        self.nameIndex = 0
        self.nameBindings = {}
        self.pendingLabel = None

    def parseAll(self):
        'Parses the block it was set up for.'
        self.parseBlock(self.block, 0)

    def newConst(self, value):
        '''Returns a string representing a unique constant to be uned in
        place of code objects during parsing. Insert the return value of this
        function into the parsed text exactly where you want a representation
        of value and the BlockParser will guarantee that in the final code
        object it will be treated as value.'''

        # To ease readability of generated python code:
        if isinstance(value, str) or (isinstance(value, int) and \
                                      value > self.firstConst) or \
                                      value == None:
            return repr(value)

        self.nextConst -= 1
        while self.nextConst in self.badConsts:
            self.nextConst -= 1
        result = self.nextConst

        self.substitutions[result] = value
        return str(result)

    def addLine(self, text):
        self.noChange = False

        self.putLabel()
        self.lines.append(' ' * self.indentLevel + text)

    def addLabel(self, label):
        '''If label is None, does nothing, otherwise, adds the line
        __strand__ = label to the python code.
        '''

        # Label isn't put immediately in case of two consecutive addLabel()s
        #  (consequence of the tagging optimisation)
        self.pendingLabel = label

    def putLabel(self):
        '''internal. If there's a label waiting to be put, puts it.'''
        if self.pendingLabel is not None:
            label = self.pendingLabel
            self.pendingLabel = None
            self.addLine('__strand__ = %s' % repr(label))

    def addTag(self, block, tag):
        '''If tag is None, does nothing, otherwise tags the specified block
        along at the current position in the code.'''
        # Parse block here.
        if tag is not None:
            firstLine = len(self.lines)
            tag.parse(self)
            tag.beenParsed = True
            lastLine = len(self.lines)
            self.fcCode.setBlockLines(self, tag, (firstLine, lastLine))
            self.fcCode.unsetBlockLines(self, block, (firstLine, lastLine))

    def addLines(self, lines):
        '''Adds the specified lines of Python code to the program at the
        current indentation level.'''

        if len(lines) > 0:
            self.noChange = False
            self.putLabel()
            indent = ' ' * self.indentLevel
            for l in lines:
                self.lines.append(indent + l)

    def parseBlock(self, block, levels=1):
        '''Indents, then parses the specified block, then returns to the
        current indentation.'''
        iLvl = self.indentLevel
        if levels > 0:
            self.indent(levels)

        firstLineNum = len(self.lines)
        if block.beenParsed:
            # It's been parsed. Just insert it's label here.
            self.addLabel(block.tagLabel)
        else:
            block.parse(self)

        if levels > 0:
            self.dedent()           # Takes care of 'pass' and noChange
        self.indentLevel = iLvl

        # Save the line numbers.
        lastLineNum = len(self.lines)
        self.fcCode.setBlockLines(self, block, (firstLineNum, lastLineNum))

    def indent(self, levels=1):
        '''Indents by the specified number of levels (or 1 if no level is
        given).'''
        self.putLabel()

        self.indentLevel += levels
        self.noChange = True

    def dedent(self, levels=1):
        '''Dedents by the specified number of levels (or 1 if no level is
        given). If there has been no change to the text since the indent
        was called, writes 'pass' before dedenting.'''
        self.putLabel()

        if self.noChange:
            self.addLine('pass')
            self.noChange = False

        self.indentLevel -= levels

    def newParser(self, block):
        '''Generates a new parser for use when compiling sub-sections of the
        code tree.'''
        return BlockParser(self.fcCode, block)

    def compile_internal(self):
        '''Compiles python code without substitutions and returns the code
        object. This can be overridden if, for example, the code block we
        want is actually nested within the main code block.'''
        return compile('\n'.join(self.lines), '', 'exec')

    def compile(self, fnName=None):
        '''Compiles the python code as it currently is, performs the necessary
        constant substitutions and returns a code object. Should only be
        called by the creator of the BlockParser.'''

        # First check if we're still indented and if so do processing.
        if self.indentLevel:
            self.dedent(self.indentLevel)

        self.lines.append('')

        # Give our block everything.
        self.fcCode.setBlockLines(self, self.block, (0, len(self.lines)))

        # Register that we're compiling the code.
        fileName, firstLineNum = self.fcCode.registerCompile(self)

        # Debug - print what we've compiled.
##        print '======= begins line %d ======' % firstLineNum
##        for l in self.lines: print l

        # Compile
        result = self.compile_internal()

        # Create new constants list.
        varsToSub = self.substitutions.keys()
        nameBindings = copy.deepcopy(self.nameBindings)
        consts = []
        for i in result.co_consts:
            # Check for substitution.
            try:
                # Perform substitution.
                j = self.substitutions[i]
                # Remove it from list.
                try:
                    varsToSub.remove(i)
                except:
                    pass
                i = j
            except KeyError:
                if i.__class__ == new.code:
                    # Check for name substitutions.
                    try:
                        # Perform substitution.
                        iName = i.co_name
                        iList = nameBindings[iName]

                        # Pop the code object.
                        i = iList.pop(0)
                        if len(iList) == 0:
                            del nameBindings[iName]
                    except KeyError:
                        pass
            consts.append(i)

        # Check for any non-substituted consts or names.
        if len(varsToSub) > 0:
            for l in self.lines: print l
            print 'unsubstituted:', varsToSub
            raise Exception, 'Unsubstituted const!'
        if len(nameBindings) > 0:
            print self.lines
            raise Exception, 'Unsubstituted code object!'

        if fnName == None:
            fnName = result.co_name
        # Create and return the code object.
        result= new.code(result.co_argcount,
                        result.co_nlocals,
                        result.co_stacksize,
                        result.co_flags,
                        result.co_code,
                        tuple(consts),
                        result.co_names,
                        result.co_varnames,
                        str(fileName),
                        fnName,
                        firstLineNum,
                        result.co_lnotab)

        return result

    def addNamedCodeObject(self, name, codeObject):
        '''Adds an entry into the substitution queue so that the first code
        block of the given name found when compiling will be replaced with the
        specified code object.'''

        # Lists are maintained so that it will correctly treat two def blocks
        # of the same name in the same code object.
        try:
            nameList = self.nameBindings[name]
            nameList.append(codeObject)
        except KeyError:
            self.nameBindings[name] = [codeObject]

class DefBlockParser(BlockParser):
    def __init__(self, parser, block, fnName, badConsts=[]):
        super(DefBlockParser, self).__init__(parser.fcCode, block, \
                                             badConsts=badConsts)

        self.fnName = fnName

    def compile_internal(self):
        # Read the parsed block and extract the code object.
        codeObj = compile('\n'.join(self.lines), '', 'exec')

        for i in codeObj.co_consts:
            if i.__class__ == new.code:
                return i

def test1():
    a = MasterBlock()
    a.child.mutate(ExecBlock(['a=input("Enter a number: ")']))
    a.insertChildSeq(a.child, True, ClassBlock('b','object'))
    a.child.insertChildSeq(a.child.blocks[-1], True, ExecBlock(['d=b()','print d.c(a)']))
    a.child.blocks[1].child.mutate(DefBlock('c','self, blah'))
    a.child.blocks[1].child.child.mutate(ExecBlock(['print self,blah']))
    a.child.blocks[1].child.returnExpressions[0] = '7'

    namespace={}
    exec compileBlock(a) in namespace

def test2():
    a = MasterBlock()
    b = DefBlock('a','blah')
    a.child.mutate(b)
    c = ExecBlock(['print a(17)'])
    b.parent.insertChildSeq(b, True, c)

    d = ExecBlock(['b=input("Enter a number: ")'])
    b.child.mutate(d)
    e = IfBlock('b > blah')
    d.parent.insertChildSeq(d, True, e)
    b.modifyReturnExpressions(True, 0)
    b.setReturnExpression(0, "'small'")
    b.setReturnExpression(1, "'big'")
    b.map.connections[1] = 0

    print b.map.connections

    namespace={}
    exec compileBlock(a) in namespace

def test3():
    a = MasterBlock()
    b = ExecBlock(['a=input("Please enter a number: ")'])
    c = ExecBlock(['print "ok"'])
    d = ExecBlock(['b=3/0'])
    e = ExecBlock(['print "m"'])
    f = ExecBlock(['b=z'])
    g = [ExecBlock(['print %d' % i]) for i in range(1,5)]
    h = IfBlock('a in (1,3)')
    i = IfBlock('a in (2,3)')
    j = TryBlock('abc')
    k = WideBlock()
    l = WideBlock()
    m = WideBlock()

    m.blocks[0].mutate(e)
    m.insertParallelChild(None, False, f)
    l.blocks[0].mutate(c)
    l.insertParallelChild(None, False, d)

    j.child.mutate(h)

    j1 = TryBlock('defg')
    j2 = j1.child.mutate(BottleneckBlock)
    j2.setNumRoutes(2)
    h.insertBlockSeq(True, j1)
    j2.child.mutate(i)

    h.insertBlockSeq().mutate(l)
    i.insertBlockSeq().mutate(m)
    print '**C**'

    k.blocks[0].mutate(g[0])
    for z in g[1:]:
        k.insertParallelChild(None, False, z)
    print '**B**'

    a.child.mutate(b)
    b.parent.insertChildSeq(b, True, j)
    print k.numInputs
    j.parent.insertChildSeq(j, True, k)
    print k.numInputs
    print '**A**'


    print a.child.maps[0].connections, a.child.maps[1].connections

    namespace={}
    r = compileBlock(a)
    exec r in namespace
    return a,r

def test4():
    a = MasterBlock()
    b = ForBlock('i', 'range(3)')
    assert not b.isBroken()

    a.child.mutate(b)
    assert b.parent is a
    c = IfBlock('input("Go 2? ")')
    b.child.mutate(c)
    assert c.parent is b
    assert c.nextLoop is b
    assert b.numOutputs == 1
    assert not b.isBroken()
    print b.map.numOutputs, b.map.connections

    d = EscapeBlock()
    print ' === 1A ==='
    c.insertBlockSeq().mutate(d)
    d.insertBlockPar()

    assert d.nextLoop is b
    print b.numOutputs
    assert b.numOutputs == 2
    assert not b.isBroken()

    print ' === 1B ==='

    e = IfBlock('input("Go 3? ")')
    assert b.numOutputs == 2
    assert not b.isBroken()
    x=d.parent.insertBlockSeq()
    print b.numOutputs
    assert b.numOutputs == 2
    assert not b.isBroken()
    x.mutate(e)
    assert b.numOutputs == 2
    assert e.parent is c.parent
    assert e.nextLoop is b
    assert not b.isBroken()
    print ' === 1C ==='
    f = EscapeBlock()
    assert b.numOutputs == 2
    assert not b.isBroken()
    print ' === 1D ==='
    e.insertBlockSeq().mutate(f)
    f.insertBlockPar()
    assert f.nextLoop is b
    assert b.numOutputs == 3
    assert not b.isBroken()
    print ' === 1E ==='

    g = ExecBlock(['print i'])
    f.parent.insertBlockSeq().mutate(g)
    assert e.parent is g.parent
    assert g.nextLoop is b
    assert not b.isBroken()

    h = ExecBlock(['print 1'])
    i = ExecBlock(['print 2'])
    j = ExecBlock(['print 3'])
    print ' === 2A ==='
    b.insertBlockSeq().mutate(h)
    print ' === 2B ==='
    assert b.parent is h.parent
    h.insertBlockPar().mutate(i)
    print ' === 3A ==='
    i.insertBlockPar().mutate(j)
    print ' === 3B ==='

    assert h.parent is i.parent is j.parent

    print b.parent.maps[0].numOutputs, h.parent.numInputs
    assert b.parent.maps[0].numOutputs == 3
    print b.numOutputs, b.parent.maps[0].numInputs
    assert b.parent.maps[0].numInputs == 3
    b.parent.maps[0].connections = [0,1,2]

    result = compileBlock(a)
    return a, result

def test5():
    a = MasterBlock()
    a.child.mutate(IfBlock('input("True/False? ")'))
    b = LoopBlock()
    a.child.insertBlockSeq().mutate(b)
    c = ExecBlock(['print 1'])
    b.child.mutate(c)
    d = BottleneckBlock()
    c.insertBlockSeq().mutate(d)
    d.setNumRoutes(3)
    e = IfBlock('input("Exit? ")')
    d.child.mutate(e)
    assert d.child is e
    print ' === A ==='
    e2 = e.insertBlockSeq().mutate(WideBlock)
    e2.insertParallelChild(None).mutate(EscapeBlock)
    e.parent.maps[0].connections = [0, 1]

    print ' === B ==='
    c.insertBlockPar().mutate(ExecBlock(['print 3']))
    print ' === C ==='
    c.insertBlockPar().mutate(ExecBlock(['print 2']))

    b.setNumEntries(2)

    # Rearrange the mappings.
    assert b.map.numInputs == 5
    assert b.map.numOutputs == 3
    b.map.connections = [0,1,1,2,0]
    assert b.child.maps[0].numInputs == 3
    assert b.child.maps[0].numOutputs == 3
    b.child.maps[0].connections = [0,1,2]
    assert a.child.maps[0].numInputs == 2
    assert a.child.maps[0].numOutputs == 2
    a.child.maps[0].connections = [0, 1]

    result = compileBlock(a)
    return result

def test6():
    a = MasterBlock('file1')
    b = a.child.mutate(ProcedureBlock('xyz'))
    b.child.mutate(ExecBlock(['print 1']))
    b.child.insertBlockPar().mutate(ExecBlock(['print 2']))
    b.child.blocks[1].insertBlockPar().mutate(ExecBlock(['print 3']))
    b.modifyOutputRoutes(True, 1)

    assert b.map.numInputs == 3

    b.map.connections = [1,0,1]

    r = compileBlock(a)

    a = MasterBlock('file2')
    b = a.child.mutate(ExecBlock(['entry=input("Enter by: ")']))
    c = ProcCallBlock('xyz')
    b.insertBlockSeq().mutate(c)
    c.modifyOutputRoutes(True, 1)
    c.routesIn[0] = '?entry'
    t = compileBlock(a)

    return r, t

def test7():
    a = MasterBlock()
    a.child.mutate(IfBlock())
    a.child.insertBlockSeq()
    a.child.blocks[1].insertBlockPar()
    a.child.maps[0].connections = [0, 1]
    l = []
    for b in a.child.blocks[1].blocks:
        b=b.mutate(IfBlock())
        b2 = b.insertBlockSeq()
        b2.insertBlockPar()
        b.parent.maps[0].connections = [0, 1]
        for c in b.parent.blocks[1].blocks:
            l2 = [c]
            for i in range(2):
                l2.insert(i,c.insertBlockSeq(False))
            l.append(l2)
    return a, l

def test8():
    a = MasterBlock()
    b = a.child.mutate(ExecBlock(["a = input('True/False? ')"]))
    b = b.insertBlockSeq().mutate(IfBlock('a'))
    b = b.insertBlockSeq().mutate(WideBlock)
    c = b.blocks[0].mutate(ExecBlock(["print 'hi'"]))
    c.insertBlockPar().mutate(ExecBlock(["print 'good'"]))
    b = b.insertBlockSeq().mutate(WideBlock)
    c = b.blocks[0].mutate(ExecBlock(["print 'bye'"]))
    c.insertBlockPar().mutate(ExecBlock(["print 'there'"]))

    assert len(a.child.maps[1]) == 2 == len(a.child.maps[2])
    a.child.maps[1].connections = [0,1]
    a.child.maps[2].connections = [1,0]

    t = compileBlock(a)

    return a, t

import painter
from painter import RectType


if __name__ == '__main__':
    import main
    mb = main.main()
