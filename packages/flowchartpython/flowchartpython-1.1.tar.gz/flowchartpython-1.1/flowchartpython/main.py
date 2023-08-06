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

import sys
import traceback

import pygame
import pygame.locals as pgl

# To start in dvorak keyboard layout, comment out the following line.
sys.argv = [sys.argv[0], "defaultKeymap=keyboard.QWERTY_MAP"]

defaultOptions = 0

# Choose an appropriate size.
import Tkinter
tk = Tkinter.Tk()
defaultSize = int(0.95*tk.winfo_screenwidth()), int(0.9*tk.winfo_screenheight())
tk.destroy()
del tk

# Keys to bind.
class Keys(object):
    Left, Right, Up, Down, In, Out = [object() for i in xrange(6)]
    Select, Cancel = [object() for i in xrange(2)]
    Add, Subtract, Add2, Subtract2 = [object() for i in xrange(4)]
    PanZoom, Mapping, Align, FindText = [object() for i in xrange(4)]
    Undo, Redo, Cut, Copy, Paste, Swap = [object() for i in xrange(6)]
    New, Save, SaveAs, Open, Run, Quit = [object() for i in xrange(6)]
    Enshroud, Insert, Delete, Revert, EnterExec, Mutate = \
                                        [object() for i in xrange(6)]
    Centre = object()
    MouseNavigate, MousePan = [object() for i in xrange(2)]
    Debug = object()

import sourceFile, actor, keyboard

# Default settings.
class Settings(object):
    keyLayouts = [('dvorak', keyboard.DVORAK_MAP), \
                  ('qwerty', keyboard.QWERTY_MAP)]
    defaultKeymap = keyboard.DVORAK_MAP

    keyBindings = {Keys.Left: pgl.K_s, Keys.Right: pgl.K_f, Keys.Up: pgl.K_e,
                   Keys.Down: pgl.K_d, Keys.In: pgl.K_r, Keys.Out: pgl.K_w,
                   Keys.Select: pgl.K_RETURN, Keys.Cancel: pgl.K_ESCAPE,
                   Keys.Add: pgl.K_v, Keys.Subtract: pgl.K_c,
                   Keys.Add2: pgl.K_x, Keys.Subtract2: pgl.K_z,
                # Mode keys...
                   Keys.PanZoom: pgl.K_SLASH, Keys.Mapping: pgl.K_m,
                   Keys.Align: pgl.K_a, Keys.FindText: pgl.K_k,
                # Edit menu keys...
                   Keys.Undo:  (pgl.K_z, pgl.KMOD_LCTRL),
                   Keys.Redo:  (pgl.K_z, pgl.KMOD_LCTRL|pgl.KMOD_LSHIFT),
                   Keys.Cut:   (pgl.K_x, pgl.KMOD_LCTRL),
                   Keys.Copy:  (pgl.K_c, pgl.KMOD_LCTRL),
                   Keys.Paste: (pgl.K_v, pgl.KMOD_LCTRL),
                   Keys.Swap:  (pgl.K_d, pgl.KMOD_LCTRL),
                # Modify menu keys...
                   Keys.Insert: pgl.K_g, Keys.Enshroud: pgl.K_SEMICOLON,
                   Keys.Delete: pgl.K_DELETE, Keys.EnterExec: pgl.K_RETURN,
                   Keys.Revert: (pgl.K_DELETE, pgl.KMOD_LCTRL),
                   Keys.Mutate: pgl.K_SEMICOLON,
                # File menu keys...
                   Keys.New: (pgl.K_l, pgl.KMOD_LCTRL),
                   Keys.Save: (pgl.K_SEMICOLON, pgl.KMOD_LCTRL),
                   Keys.SaveAs: (pgl.K_a, pgl.KMOD_LCTRL),
                   Keys.Open: pgl.K_F3,
                   Keys.Run:  pgl.K_F5,
                   Keys.Quit: (pgl.K_F4, pgl.KMOD_LALT),
                # Hidden menu keys...
                   Keys.Centre: pgl.K_SPACE,
                # Mouse keys...
                   Keys.MouseNavigate: pgl.K_LCTRL,
                   Keys.MousePan: pgl.K_LALT,
                # Block types...
                   sourceFile.IfBlock: pgl.K_g,
                   sourceFile.BottleneckBlock: pgl.K_n,
                   sourceFile.ExecBlock: pgl.K_b,
                   sourceFile.DefBlock: pgl.K_h,
                   sourceFile.ClassBlock: pgl.K_i,
                   sourceFile.ProcedureBlock: pgl.K_r,
                   sourceFile.ProcCallBlock: pgl.K_o,
                   sourceFile.TryBlock: pgl.K_k,
                   sourceFile.LoopBlock: pgl.K_p,
                   sourceFile.ForBlock: pgl.K_y,
                   sourceFile.EscapeBlock: pgl.K_d,
                   sourceFile.GroupingBlock: pgl.K_u,
                # Debug...
                   Keys.Debug: pgl.K_F12
              }

class Main(object):
    def __init__(self, size=defaultSize, options=defaultOptions):
        '''Initialises the program.'''

        pygame.init()
        pygame.display.set_caption('Flowchart Python')

        self.screen = pygame.display.set_mode(size, options)
        self.masterBlock = sourceFile.MasterBlock()
        self.actor = actor.Actor(self)

    def run(self):
        '''Runs the program.'''
        self.running = True
        while self.running:
            self.Try(self.actor.draw, 0.5)
            pygame.display.flip()
            self.Try(self.actor.processEvents)

    def Try(self, function, weight=1, fault=[0]):
        try:
            function()
        except:
            traceback.print_exc()

            fault[0] = fault[0] + weight
            if fault[0] >= 3:
                print >> sys.stderr, 'Triple-faulted. Quitting.'
                self.running = False
        else:
            fault[0] = max(fault[0] - weight, 0)

    def finalise(self):
        pygame.display.quit()
        pygame.quit()

#####################################
# Main routines.
#####################################

def main():
    # Translate settings.
    settingsString = ' '.join(sys.argv[1:])
    for k,v in eval('dict(%s)' % settingsString, \
                    {'keyboard': keyboard}).iteritems():
        setattr(Settings, k, v)

    keyboard.KEY_MAPPING = Settings.defaultKeymap

    mainObj = Main()

##    # Create a block design.
##    a = mainObj.masterBlock
##    b = a.child.mutate(sourceFile.IfBlock('a'))
##    b2 = b.insertBlockSeq().mutate(sourceFile.WideBlock)
##    b2.insertParallelChild(None)
##    b.parent.maps[0].connections = [0, 1]
##
##    c = b2.blocks[0].mutate(sourceFile.IfBlock('b'))
##    c2 = c.insertBlockSeq().mutate(sourceFile.WideBlock)
##    c2.insertParallelChild(None)
##    c.parent.maps[0].connections = [0, 1]
##
##    d = c2.blocks[1].mutate(sourceFile.IfBlock('c'))
##    e = b.parent.enshroud(sourceFile.TryBlock)
##    g = b.parent.enshroud(sourceFile.ForBlock)
##
##    c2.blocks[0].mutate(sourceFile.EscapeBlock)
##
##    bCopy = b.parent.duplicate()
##
##    f = b2.insertBlockSeq().mutate(sourceFile.BottleneckBlock)
##    f.setNumRoutes(4)
##    b.parent.maps[1].connections = [0,1,2,3]
##    f.child.mutate(sourceFile.ExecBlock)
##
##    f.insertBlockSeq().mutate(bCopy)
##    bCopy.unnest()
##    e.insertBlockPar()
##    e.parent.insertBlockSeq()
##
    try:
        mainObj.run()
    finally:
        mainObj.finalise()

    return mainObj.masterBlock

def test():
    try:
        main()
    except:
        pass

if __name__ == '__main__':
    mb = main()
##    import profile
##    profile.run('test()')
