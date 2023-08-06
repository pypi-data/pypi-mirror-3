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

import main, painter, sourceFile, keyboard

import sys
import time
import pygame
import pygame.locals as pgl

import Tkinter, tkFileDialog, Dialog

menuColour = (192, 192, 255)
textColour = (0, 0, 0)
selMenuColour = (0, 0, 224)
selTextColour = (255, 255, 255)

class SysMode(object):
    Standard, PanZoom, Mapping, Align, FindText, Text = \
              [object() for i in range(6)]

#####################################
# Menu definitions.
#####################################

class MenuItem(object):
    def __init__(self, caption, shortcut, function, args=[], kwargs={}):
        self.caption = caption
        self.function = function
        self.args = args
        self.kwargs = kwargs

        self.shortcut = shortcut

        # Translate shortcut to keys.
        try:
            sh = main.Settings.keyBindings[shortcut]
        except KeyError:
            self.shortcutKeys = None
        else:
            if isinstance(sh, tuple):
                k, mod = sh
            else:
                k, mod = sh, 0
            self.shortcutKeys = k, mod

    def __call__(self):
        if self.function != None:
            self.function(*self.args, **self.kwargs)

class Menu(object):
    def __init__(self, *items):
        self.items = []
        self.itemsByShortcut = {}
        for item in items:
            self.items.append(item)
            if item.function and item.shortcutKeys:
                k, mod = item.shortcutKeys
                self.itemsByShortcut.setdefault(k, []).append((mod, item))

    def __len__(self):
        return len(self.items)
    def __iter__(self):
        return iter(self.items)

    def getItemFromShortcut(self, key, mods):
        '''Returns the menu item specified by a given shortcut.'''
        # Go through possibilities and check modifiers.
        mods = mods & (pgl.KMOD_CTRL|pgl.KMOD_ALT|pgl.KMOD_SHIFT|pgl.KMOD_META)
        for m, i in self.itemsByShortcut.get(key, []):
            if mods == m:
                return i

#####################################
# Actor class.
#####################################

class Actor(object):
    '''Performs actions on a block.'''

    menuWidth = 150
    menuItemHeight = 20
    menuMaxGrowSpeed = 1000
    menuGrowAcc = 1500

    panSpeed = 1
    zoomSpeed = 1

    trackKeys = [main.Keys.MouseNavigate, main.Keys.MousePan, main.Keys.Up, \
                 main.Keys.Down, main.Keys.Left, main.Keys.Right, \
                 main.Keys.In, main.Keys.Out]

    def debug(self):
        assert not self.selection.isBroken()

    def initMenus(self):
        class Menus(object):
            pass
        self.Menus = Menus

        # Submenus.
        self.Menus.Insert = Menu( \
            MenuItem('Above', main.Keys.Up, self.insertPar, [False]), \
            MenuItem('Below', main.Keys.Down, self.insertPar, [True]), \
            MenuItem('Left', main.Keys.Left, self.insertSeq, [False]), \
            MenuItem('Right', main.Keys.Right, self.insertSeq, [True]))

        self.Menus.Enshroud = Menu( \
            MenuItem('Loop', sourceFile.LoopBlock, self.enshroud, \
                     [sourceFile.LoopBlock]), \
            MenuItem('For Loop', sourceFile.ForBlock, self.enshroud, \
                     [sourceFile.ForBlock]), \
            MenuItem('Function Def', sourceFile.DefBlock, self.enshroud, \
                     [sourceFile.DefBlock]), \
            MenuItem('Class', sourceFile.ClassBlock, self.enshroud, \
                     [sourceFile.ClassBlock]), \
            MenuItem('Procedure', sourceFile.ProcedureBlock, self.enshroud, \
                     [sourceFile.ProcedureBlock]), \
            MenuItem('Try', sourceFile.TryBlock, self.enshroud, \
                     [sourceFile.TryBlock]), \
            MenuItem('Bottleneck', sourceFile.BottleneckBlock, self.enshroud, \
                     [sourceFile.BottleneckBlock]), \
            MenuItem('Group', sourceFile.GroupingBlock, self.enshroud, \
                     [sourceFile.GroupingBlock]))

        self.Menus.Mutate = Menu( \
            MenuItem('Execute', sourceFile.ExecBlock, self.mutate, \
                     [sourceFile.ExecBlock]), \
            MenuItem('If', sourceFile.IfBlock, self.mutate, \
                     [sourceFile.IfBlock]), \
            MenuItem('Loop', sourceFile.LoopBlock, self.mutate, \
                     [sourceFile.LoopBlock]), \
            MenuItem('For Loop', sourceFile.ForBlock, self.mutate, \
                     [sourceFile.ForBlock]), \
            MenuItem('Loop Escape', sourceFile.EscapeBlock, self.mutate, \
                     [sourceFile.EscapeBlock]), \
            MenuItem('Function Def', sourceFile.DefBlock, self.mutate, \
                     [sourceFile.DefBlock]), \
            MenuItem('Class', sourceFile.ClassBlock, self.mutate, \
                     [sourceFile.ClassBlock]), \
            MenuItem('Procedure', sourceFile.ProcedureBlock, self.mutate, \
                     [sourceFile.ProcedureBlock]), \
            MenuItem('Procedure Call', sourceFile.ProcCallBlock, self.mutate,\
                     [sourceFile.ProcCallBlock]), \
            MenuItem('Try', sourceFile.TryBlock, self.mutate, \
                     [sourceFile.TryBlock]), \
            MenuItem('Bottleneck', sourceFile.BottleneckBlock, self.mutate, \
                     [sourceFile.BottleneckBlock]), \
            MenuItem('Group', sourceFile.GroupingBlock, self.mutate, \
                     [sourceFile.GroupingBlock]))

        self.Menus.InMapping = Menu( \
            MenuItem('Add Route', main.Keys.Add, self.addRoute), \
            MenuItem('Remove Route', main.Keys.Subtract, self.delRoute))

        # Main menus.
        self.Menus.Edit = Menu( \
##                MenuItem('Undo',  main.Keys.Undo,  self.undo), \
##                MenuItem('Redo',  main.Keys.Redo,  self.redo), \
                MenuItem('Cut',   main.Keys.Cut,   self.cut), \
                MenuItem('Copy',  main.Keys.Copy,  self.copy), \
                MenuItem('Paste', main.Keys.Paste, self.paste), \
                MenuItem('Swap',  main.Keys.Swap, self.swap), \
            )
        self.Menus.File = Menu( \
                MenuItem('New', main.Keys.New, self.new), \
                MenuItem('Open...', main.Keys.Open, self.load), \
                MenuItem('Save', main.Keys.Save, self.save), \
                MenuItem('Save As...', main.Keys.SaveAs, self.saveAs), \
                MenuItem('Run', main.Keys.Run, self.run), \
                MenuItem('Quit', main.Keys.Quit, self.quit) \
            )
        self.Menus.Mode = Menu( \
                MenuItem('Pan/Zoom', main.Keys.PanZoom, self.setMode, \
                         [SysMode.PanZoom]), \
                MenuItem('Mappings', main.Keys.Mapping, self.setMode, \
                         [SysMode.Mapping]), \
                MenuItem('Alignment', main.Keys.Align, self.setMode, \
                         [SysMode.Align]), \
                MenuItem('Text Elements', main.Keys.FindText, self.setMode, \
                         [SysMode.FindText])
            )
        self.Menus.Modify = { \
            sourceFile.PassBlock: Menu( \
                MenuItem('Substitute', main.Keys.Mutate, self.subMenu, \
                         [self.Menus.Mutate]), \
                MenuItem('Insert', main.Keys.Insert, self.subMenu, \
                         [self.Menus.Insert]), \
                MenuItem('Delete', main.Keys.Delete, self.delete)), \
            sourceFile.BottleneckBlock: Menu( \
                MenuItem('Add Route', main.Keys.Add, self.addRoute), \
                MenuItem('Remove Route', main.Keys.Subtract, self.delRoute), \
                MenuItem('Enshroud', main.Keys.Enshroud, self.subMenu, \
                         [self.Menus.Enshroud]),\
                MenuItem('Insert', main.Keys.Insert, self.subMenu, \
                         [self.Menus.Insert]), \
                MenuItem('Delete', main.Keys.Delete, self.delete), \
                MenuItem('Revert', main.Keys.Revert, self.revert)),
            sourceFile.ExecBlock: Menu( \
                MenuItem('Enter', main.Keys.EnterExec, self.enterExec),\
                MenuItem('Enshroud', main.Keys.Enshroud, self.subMenu, \
                         [self.Menus.Enshroud]),\
                MenuItem('Insert', main.Keys.Insert, self.subMenu, \
                         [self.Menus.Insert]), \
                MenuItem('Delete', main.Keys.Delete, self.delete), \
                MenuItem('Revert', main.Keys.Revert, self.revert)),
            sourceFile.LoopBlock: Menu( \
                MenuItem('Add Entry', main.Keys.Add, self.addEntry), \
                MenuItem('Remove Entry', main.Keys.Subtract, self.delEntry), \
                MenuItem('Enshroud', main.Keys.Enshroud, self.subMenu, \
                         [self.Menus.Enshroud]),\
                MenuItem('Insert', main.Keys.Insert, self.subMenu, \
                         [self.Menus.Insert]), \
                MenuItem('Delete', main.Keys.Delete, self.delete), \
                MenuItem('Revert', main.Keys.Revert, self.revert)),
            sourceFile.DefBlock: Menu( \
                MenuItem('Add Return', main.Keys.Add, self.addDefReturn), \
                MenuItem('Remove Return', main.Keys.Subtract, self.delDefReturn), \
                MenuItem('Enshroud', main.Keys.Enshroud, self.subMenu, \
                         [self.Menus.Enshroud]),\
                MenuItem('Insert', main.Keys.Insert, self.subMenu, \
                         [self.Menus.Insert]), \
                MenuItem('Delete', main.Keys.Delete, self.delete), \
                MenuItem('Revert', main.Keys.Revert, self.revert)),
            sourceFile.ProcedureBlock: Menu( \
                MenuItem('Add Exit Route', main.Keys.Add, self.addProcExit), \
                MenuItem('Remove Exit Route', main.Keys.Subtract, self.delProcExit), \
                MenuItem('Enshroud', main.Keys.Enshroud, self.subMenu, \
                         [self.Menus.Enshroud]),\
                MenuItem('Insert', main.Keys.Insert, self.subMenu, \
                         [self.Menus.Insert]), \
                MenuItem('Delete', main.Keys.Delete, self.delete), \
                MenuItem('Revert', main.Keys.Revert, self.revert)),
            sourceFile.ProcCallBlock: Menu( \
                MenuItem('Add Entry Route', main.Keys.Add, self.addProcEntry), \
                MenuItem('Remove Entry Route', main.Keys.Subtract, self.delProcEntry), \
                MenuItem('Add Exit Route', main.Keys.Add2, self.addProcExit), \
                MenuItem('Remove Exit Route', main.Keys.Subtract2, self.delProcExit), \
                MenuItem('Enshroud', main.Keys.Enshroud, self.subMenu, \
                         [self.Menus.Enshroud]),\
                MenuItem('Insert', main.Keys.Insert, self.subMenu, \
                         [self.Menus.Insert]), \
                MenuItem('Delete', main.Keys.Delete, self.delete), \
                MenuItem('Revert', main.Keys.Revert, self.revert)),
            sourceFile.MasterBlock: Menu(),
            # Default:
            None: Menu( \
                MenuItem('Enshroud', main.Keys.Enshroud, self.subMenu, \
                         [self.Menus.Enshroud]),\
                MenuItem('Insert', main.Keys.Insert, self.subMenu, \
                         [self.Menus.Insert]), \
                MenuItem('Delete', main.Keys.Delete, self.delete), \
                MenuItem('Revert', main.Keys.Revert, self.revert))}

        self.Menus.HiddenNav = Menu(
            MenuItem('Centre', main.Keys.Centre, self.centreView))

        self.Menus.Hidden = Menu( \
            MenuItem('Cancel', main.Keys.Cancel, self.cancel), \
            MenuItem('Debug', main.Keys.Debug, self.debug), \
            MenuItem('New', main.Keys.New, self.new), \
            MenuItem('Save', main.Keys.Save, self.save), \
            MenuItem('Save As...', main.Keys.SaveAs, self.saveAs), \
            MenuItem('Open...', main.Keys.Open, self.load), \
            MenuItem('Run', main.Keys.Run, self.run), \
            MenuItem('Quit', main.Keys.Quit, self.quit))

        self.Menus.FullNav = Menu( \
            MenuItem('Up', main.Keys.Up, None),
            MenuItem('Down', main.Keys.Down, None),
            MenuItem('Left', main.Keys.Left, None),
            MenuItem('Right', main.Keys.Right, None),
            MenuItem('In', main.Keys.In, None),
            MenuItem('Out', main.Keys.Out, None))

        self.Menus.Nav = { \
            SysMode.Standard: Menu( \
                MenuItem('Up', main.Keys.Up, self.selUp),
                MenuItem('Down', main.Keys.Down, self.selDown),
                MenuItem('Left', main.Keys.Left, self.selLeft),
                MenuItem('Right', main.Keys.Right, self.selRight),
                MenuItem('In', main.Keys.In, self.selIn),
                MenuItem('Out', main.Keys.Out, self.selOut)),
            SysMode.Mapping: Menu( \
                MenuItem('Up', main.Keys.Up, self.mapUp),
                MenuItem('Down', main.Keys.Down, self.mapDown),
                MenuItem('Left', main.Keys.Left, self.mapLeft),
                MenuItem('Right', main.Keys.Right, self.mapRight),
                MenuItem('Select', main.Keys.Select, self.mapSelect)),
            SysMode.FindText: Menu( \
                MenuItem('Up', main.Keys.Up, self.fTxtLeft),
                MenuItem('Down', main.Keys.Down, self.fTxtRight),
                MenuItem('Left', main.Keys.Left, self.fTxtLeft),
                MenuItem('Right', main.Keys.Right, self.fTxtRight),
                MenuItem('Select', main.Keys.Select, self.fTxtSelect)),
            SysMode.Align: Menu( \
                MenuItem('Up', main.Keys.Up, self.alnUp),
                MenuItem('Down', main.Keys.Down, self.alnDown),
                MenuItem('Left', main.Keys.Left, self.alnLeft),
                MenuItem('Right', main.Keys.Right, self.alnRight)),
            SysMode.Text: Menu( \
                MenuItem('Done', None, self.txtDone)),
            None: Menu()}


    def __init__(self, mainObject):
        self.initMenus()

        self.defaultCursor = pygame.mouse.get_cursor()

        self.mainObject = mainObject
        self.masterBlock = mainObject.masterBlock
        self.painter = painter.Painter(self.masterBlock, mainObject.screen)
        self.screen = mainObject.screen
        self.screenSize = self.screen.get_size()

        self.keys = set()
        self.clicking = False
        self.targetPoint = (0,0)
        self.clipBoard = None

        self.menuFont = pygame.font.Font(None, 16)
        self.primaryMenu = PrimaryMenu(self, self.menuFont, self.screenSize)
        self.mode = None
        self.setSelection(mainObject.masterBlock)

        self.lastRefreshTime = time.time()
        self.setMode(SysMode.Standard)

        self.clickItem = None

    ### Selection

    def setSelection(self, selection):
        '''Sets the selection.
        If we are in mapping mode, this MUST reevaluate selMappings.
        '''
        assert selection is not None

        if self.mode == SysMode.Text:
            # Can't change selection while in text mode.
            self.setMode(SysMode.Standard)

        if selection.g_nonDrawn:
            selection = selection.parent

        self.selection = selection

        # Special processing.
        if self.mode == SysMode.Standard:
            self.primaryMenu.menu = None
        elif self.mode == SysMode.Mapping:
            if self.calculateSelFeatures(painter.MapFeature):
                self.selFeatures[0].enter(True)
        elif self.mode == SysMode.FindText:
            if self.calculateSelFeatures((painter.InteractiveText, \
                                          painter.MultilineText)):
                # If there's only one text element, automatically enter it.
                if len(self.selFeatures) == 1:
                    self.setMode(SysMode.Text)

        # Set the menu.
        self.primaryMenu.selectionIs(self.selection)

    def calculateSelFeatures(self, featureType):
        '''internal.
        Used to calculate a list of the features of a given type.'''

        # Find the mappings we can access.
        selFeatures = [f for f in self.selection.g_interactiveFeatures if \
                       isinstance(f, featureType)]
        if len(selFeatures) == 0:
            if not self.selection.parent:
                self.setMode(SysMode.Standard)
                return False

            newSel = self.selection.parent
            if newSel.g_nonDrawn:
                newSel = newSel.parent
            selFeatures = [f for f in newSel.g_interactiveFeatures if \
                           isinstance(f, featureType)]
            if len(selFeatures) > 0:
                self.setSelection(newSel)
            else:
                self.setMode(SysMode.Standard)
                return False

        self.selFeatures = selFeatures
        self.selIndex = 0
        return True

    ### Mode Selection

    def setMode(self, mode):
        # Unset the old mode
        if self.mode != SysMode.Standard:
            self.primaryMenu.menu = None
            self.primaryMenu.menuChanged()
        if self.mode == SysMode.Text:
            # Notify text element of save.
            self.selFeatures[self.selIndex].save()

        # Set the new mode
        oldMode = self.mode
        self.mode = mode
        self.navMenu = self.Menus.Nav.get(mode, self.Menus.Nav[None])

        # Set the menu.
        if self.mode == SysMode.PanZoom:
            self.primaryMenu.menu = self.Menus.FullNav
            self.primaryMenu.menuChanged()
        elif self.mode != SysMode.Standard:
            self.primaryMenu.menu = self.navMenu
            self.primaryMenu.menuChanged()

        # Set special settings.
        if self.mode == SysMode.Mapping:
            # Only recalculate everything if it's changed.
            if oldMode != SysMode.Mapping:
                self.setSelection(self.selection)
        elif self.mode == SysMode.FindText:
            if oldMode != SysMode.FindText:
                self.setSelection(self.selection)
        elif self.mode == SysMode.Text:
            # Tell the text element it's being entered.
            self.selFeatures[self.selIndex].beginEdit()

    ### Menu Navigation

    def subMenu(self, menu):
        self.primaryMenu.menu = menu
        self.primaryMenu.menuChanged()

    def cancel(self):
        if self.mode is SysMode.Mapping:
            self.selFeatures[self.selIndex].cancel() or \
                    self.setMode(SysMode.Standard)
        elif self.mode is SysMode.Text:
            # If there's more than one element, drop back to findText mode.
            if len(self.selFeatures) > 1:
                i = self.selIndex
                self.setMode(SysMode.FindText)
                self.selIndex = i
            else:
                self.setMode(SysMode.Standard)
        elif self.mode is not SysMode.Standard:
            self.setMode(SysMode.Standard)
        elif self.primaryMenu.menu:
            self.primaryMenu.menu = None
            self.primaryMenu.menuChanged()

    ### Edit Menu

    def undo(self):
        pass
        # TODO: Undo and redo.
    def redo(self):
        pass

    def cut(self):
        self.clipBoard = self.selection
        self.setSelection(self.selection.revert())

    def copy(self):
        self.clipBoard = self.selection.duplicate()

    def paste(self):
        if self.clipBoard:
            self.setSelection(self.selection.revert().mutate(self.clipBoard))
            self.clipBoard = self.selection.duplicate()
            self.combineBlock(self.selection)

    def swap(self):
        if self.clipBoard:
            sel = self.selection
            self.setSelection(self.selection.revert().mutate(self.clipBoard))
            self.clipBoard = sel
            self.combineBlock(self.selection)

    ### File Menu

    def new(self):
        if self.confirmDestroy():
            self.masterBlock = sourceFile.MasterBlock()
            self.mainObject.masterBlock = self.masterBlock
            self.painter.reset(self.masterBlock)
            self.setSelection(self.masterBlock)
            self.setMode(SysMode.Standard)

    def save(self, tk=None):
        # Check if it's been saved before.
        if self.masterBlock.filename == '':
            self.saveAs(tk)
        else:
            self.masterBlock.save()

    def confirmDestroy(self, tk=None):
        '''Asks the user if they want to save, and saves if they say yes.
        Returns True unless they choose cancel.'''
        if not self.masterBlock.modified:
            return True

        myTk = tk == None
        if myTk:
            tk = Tkinter.Tk()
            tk.withdraw()
        result = Dialog.Dialog(tk,
                    title = 'Question', \
                    text = 'File has been modified. Save it now?', \
                    default = 2, \
                    strings = ('Yes, save now.', 'No, don\'t save.', 'Cancel'), \
                    bitmap = 'question').num
        pygame.event.post(pygame.event.Event(pgl.MOUSEBUTTONUP, pos=(0,0), \
                                             button=1))
        if result == 0:
            self.save(tk)
        if myTk:
            tk.destroy()
        return result != 2

    def saveAs(self, tk=None):
        myTk = tk == None
        if myTk:
            tk = Tkinter.Tk()
            tk.withdraw()

        filename = tkFileDialog.asksaveasfilename(parent=tk, \
                    defaultextension='fcpy', \
                    filetypes=[('Flowchart Python program', '*.fcpy')])

        if filename:
            self.masterBlock.filename = filename
            self.masterBlock.save()

        if myTk:
            tk.destroy()
        pygame.event.post(pygame.event.Event(pgl.MOUSEBUTTONUP, \
                                             pos=(0,0), \
                                             button=1))

    def load(self):
        tk = Tkinter.Tk()
        tk.withdraw()
        if not self.confirmDestroy(tk):
            tk.destroy()
            return
        filename = tkFileDialog.askopenfilename(parent=tk, \
                        defaultextension='fcpy', \
                        filetypes=[('Flowchart Python program', '*.fcpy')])
        tk.destroy()

        if filename:
            self.masterBlock = sourceFile.MasterBlock.load(filename)
            self.mainObject.masterBlock = self.masterBlock
            self.painter.reset(self.masterBlock)
            self.setSelection(self.masterBlock)
            self.setMode(SysMode.Standard)

        pygame.event.post(pygame.event.Event(pgl.MOUSEBUTTONUP, \
                                             pos=(0,0), \
                                             button=1))

    def run(self):
        # TODO: Pretty this up.
        print '================================= RUNNING ================================'
        try:
            t = sourceFile.compileBlock(self.masterBlock)
        except (sourceFile.EPrepBlockError, sourceFile.ECompileBlockError):
            args = sys.exc_info()[1].args
            a, b = args
            print >> sys.stderr, b
            self.setSelection(a)
            return

        try:
            exec t in {}
        except:
            tp, error, traceback = sys.exc_info()
            tb = traceback
            print >> sys.stderr, 'Traceback (most recent call last):'
            while tb:
                lineNum = tb.tb_lineno
                print >> sys.stderr, '  File "%s", line %s in %s' % \
                  (tb.tb_frame.f_code.co_filename, lineNum, \
                   tb.tb_frame.f_code.co_name)
                tb = tb.tb_next
            print >> sys.stderr, error

            block = self.masterBlock.getBlockFromLine(lineNum)
            if block:
                self.setSelection(block)
            del traceback, tb

        print '================================ FINISHED ================================'
        print

    def quit(self):
        self.setMode(SysMode.Standard)
        if self.confirmDestroy():
            self.mainObject.running = False

    ### Modify Menu

    def mutate(self, blockType):
        self.setSelection(self.selection.mutate(blockType))
        self.cancel()

    def addRoute(self):
        self.selection.setNumRoutes(self.selection.numInputs + 1)

    def delRoute(self):
        if self.selection.numInputs > 1:
            self.selection.setNumRoutes(self.selection.numInputs - 1)

    def enshroud(self, blockType):
        self.selection.enshroud(blockType)
        self.setSelection(self.selection.parent)
        self.cancel()

    def insertPar(self, below):
        result = self.selection.insertBlockPar(below)
        if isinstance(self.selection, sourceFile.WideBlock):
            self.selection.unnest()
        self.setSelection(result)
        self.cancel()

    def insertSeq(self, after):
        # Create a WideBlock full of PassBlocks.
        if after:
            num = self.selection.numOutputs
        else:
            num = self.selection.numInputs

        if num > 1:
            newBlock = sourceFile.WideBlock()
            while len(newBlock.blocks) < num:
                newBlock.insertParallelChild(None)
        else:
            newBlock = sourceFile.PassBlock()

        assert not newBlock.isBroken()

        result = self.selection.insertBlockSeq(after, newBlock)
        if isinstance(self.selection, sourceFile.LongBlock):
            self.selection.unnest()
        self.setSelection(result)
        self.cancel()

    def delete(self):
        parent = self.selection.parent
        sel = self.selection.delete()
        if sel == None:
            self.setSelection(parent)
        else:
            self.setSelection(sel)
        self.combineBlock(parent)

    def revert(self):
        self.setSelection(self.selection.revert())

    def enterExec(self):
        # TODO
        pass

    def addEntry(self):
        self.selection.setNumEntries(self.selection.numInputs + 1)

    def delEntry(self):
        if self.selection.numInputs > 1:
            self.selection.setNumEntries(self.selection.numInputs - 1)

    def addProcExit(self):
        self.selection.modifyOutputRoutes(True, len(self.selection.routesOut))

    def delProcExit(self):
        if len(self.selection.routesOut) > 1:
            self.selection.modifyOutputRoutes(False, -1)

    def addProcEntry(self):
        self.selection.modifyInputRoutes(True, len(self.selection.routesIn))

    def delProcEntry(self):
        if len(self.selection.routesIn) > 1:
            self.selection.modifyInputRoutes(False, -1)

    def addDefReturn(self):
        self.selection.modifyReturnExpressions(True, \
                                    len(self.selection.returnExpressions))

    def delDefReturn(self):
        if len(self.selection.returnExpressions) > 1:
            self.selection.modifyReturnExpressions(False, -1)

    ### Hidden Menu

    def centreView(self):
        # Start the view moving to the selected block.
        self.painter.focusView(self.selection)

    ### Navigation: Standard mode.

    def selUp(self):
        ch = self.selection
        if ch is self.masterBlock:
            return

        p = ch.parent
        if isinstance(p, sourceFile.WideBlock):
            i = p.blocks.index(ch)
            i = p.blocks.index(ch)
            if i > 0:
                self.setSelection(p.blocks[i - 1])
                return
        self.setSelection(p)

    def selDown(self):
        ch = self.selection
        if ch is self.masterBlock:
            return

        p = ch.parent
        if isinstance(p, sourceFile.WideBlock):
            i = p.blocks.index(ch)
            if i < len(p.blocks) - 1:
                self.setSelection(p.blocks[i + 1])
                return
        self.setSelection(p)

    def selLeft(self):
        ch = self.selection
        if ch is self.masterBlock:
            return

        p = ch.parent
        if isinstance(p, sourceFile.LongBlock):
            i = p.blocks.index(ch)
            if i > 0:
                self.setSelection(p.blocks[i - 1])
                return
        self.setSelection(p)

    def selRight(self):
        ch = self.selection
        if ch is self.masterBlock:
            return

        p = ch.parent
        if isinstance(p, sourceFile.LongBlock):
            i = p.blocks.index(ch)
            if i < len(p.blocks) - 1:
                self.setSelection(p.blocks[i + 1])
                return
        self.setSelection(p)

    def selIn(self):
        try:
            b = self.selection.g_children[0]
        except IndexError:
            pass
        else:
            self.setSelection(b)

    def selOut(self):
        if self.selection != self.masterBlock:
            if self.selection.parent.g_nonDrawn:
                self.setSelection(self.selection.parent.parent)
            else:
                self.setSelection(self.selection.parent)

    ### Navigation: Mapping mode.

    def mapUp(self):
        self.selFeatures[self.selIndex].up()

    def mapDown(self):
        self.selFeatures[self.selIndex].down()

    def mapLeft(self):
        self.selFeatures[self.selIndex].left() or self.mapLeaveLeft()

    def mapRight(self):
        self.selFeatures[self.selIndex].right() or self.mapLeaveRight()

    def mapSelect(self):
        if self.selFeatures[self.selIndex].select():
            self.masterBlock.g_treeModified = True

    def mapLeaveLeft(self):
        if self.selIndex > 0:
            self.selIndex = self.selIndex - 1
            self.selFeatures[self.selIndex].enter(False)

    def mapLeaveRight(self):
        if self.selIndex < len(self.selFeatures) - 1:
            self.selIndex = self.selIndex + 1
            self.selFeatures[self.selIndex].enter(True)

    def mapClick(self, map):
        '''Called when a mapping item is clicked on.'''

        if self.mode == SysMode.Mapping and \
                   self.selFeatures[self.selIndex] == map:
            return

        # Select the appropriate block.
        newSel = map.block
        if newSel.g_nonDrawn:
            newSel = newSel.parent
        if newSel != self.selection:
            self.setSelection(newSel)

        self.setMode(SysMode.Mapping)

        # Select the appropriate mapping.
        self.selIndex = self.selFeatures.index(map)

    ### Navigation: Alignment mode.

    def alnUp(self):
        pass
    def alnDown(self):
        pass
    def alnLeft(self):
        pass
    def alnRight(self):
        pass

    ### Navigation: Find text mode.

    def fTxtLeft(self):
        if self.selIndex > 0:
            self.selIndex = self.selIndex - 1

    def fTxtRight(self):
        if self.selIndex < len(self.selFeatures) - 1:
            self.selIndex = self.selIndex + 1

    def fTxtSelect(self):
        self.setMode(SysMode.Text)

    def txtClick(self, txt):
        '''Called when a text element is clicked on.'''

        if self.mode == SysMode.Text and \
                   self.selFeatures[self.selIndex] == txt:
            return

        # It is best to do selecting in standard mode.
        self.setMode(SysMode.Standard)

        # Select the appropriate block.
        newSel = txt.block
        if newSel.g_nonDrawn:
            newSel = newSel.parent
        if newSel != self.selection:
            self.setSelection(newSel)

        self.setMode(SysMode.FindText)

        # Select the appropriate text block.
        try:
            self.selIndex = self.selFeatures.index(txt)
        except ValueError:
            print >> sys.stderr, 'Text element not in list.'
            self.selIndex = 0

        self.setMode(SysMode.Text)

    def txtDone(self):
        '''Called when editing of text element is complete.'''
        # 1. Cancel the mode - this also saves the edit.
        self.cancel()

    ### Managing the system.

    def combineBlock(self, block):
        '''internal.
        If appropriate, unnests or vanishes the current block.'''

        if isinstance(block, (sourceFile.WideBlock, sourceFile.LongBlock)):
            if type(block.parent) == type(block):
                newBlock = block.unnest()
            elif len(block.blocks) == 1:
                newBlock = block.vanish()
            else:
                return

            if self.selection == block:
                self.setSelection(newBlock)

    ### Interface with mainObject

    def processEvents(self):
        trackKeys = set([main.Settings.keyBindings[i] for i in self.trackKeys])

        # Give tick event to selection.
        self.tick()

        # Process the events in the queue.
        for event in pygame.event.get():
            if event.type == pgl.QUIT:
                self.quit()
            elif event.type == pgl.KEYDOWN:
                if event.key in trackKeys:
                    self.keys.add(event.key)
                # Process the key press.
                self.processKeypress(event)
            elif event.type == pgl.KEYUP:
                if event.key in trackKeys:
                    self.keys.discard(event.key)
                # Process the key up.
                self.processKeyup(event)
            elif event.type == pgl.MOUSEBUTTONDOWN:
                # Right-button is cancel.
                if event.button == 3:
                    self.cancel()
                else:
                    self.clicking = True
                    self.targetPoint = event.pos
                    if not self.keys.intersection(trackKeys):
                        # Process the click.
                        self.processClick(event)
            elif event.type == pgl.MOUSEBUTTONUP:
                self.clicking = False
            elif event.type == pgl.MOUSEMOTION:
                if self.clicking:
                    # Click and drag.
                    if main.Settings.keyBindings[main.Keys.MouseNavigate] in \
                       self.keys:
                        # Navigate (combination zoom and pan).
                        self.targetPoint = \
                            self.painter.navigate(self.targetPoint, event.rel)
                    elif main.Settings.keyBindings[main.Keys.MousePan] in self.keys:
                        # Pan view.
                        self.painter.pan(event.rel)
                    elif self.mode == SysMode.Text:
                        # Drag can also be processed by text elements.
                        self.selFeatures[self.selIndex].mouseDrag(event)

        if not self.clicking:
            # Must process mouse position every refresh.
            self.processMousemove()

    def tick(self):
        if self.mode == SysMode.Text:
            self.selFeatures[self.selIndex].tick()

    def processKeypress(self, event):
        if self.primaryMenu.menu:
            menus = [self.primaryMenu.menu]
        else:
            mod = self.Menus.Modify
            menus = [mod.get(type(self.selection), mod[None]), \
                     self.Menus.Edit, self.Menus.Mode, self.Menus.File]

        menus.append(self.navMenu)
        menus.append(self.Menus.Hidden)

        if self.mode != SysMode.Text:
            menus.append(self.Menus.HiddenNav)

        # Go through in order looking for shortcut.
        for m in menus:
            i = m.getItemFromShortcut(event.key, event.mod)
            if i:
                i()
                return

        # Not a shortcut key. Selection may wish to process it.
        if self.mode == SysMode.Text:
            self.selFeatures[self.selIndex].keyPress(event, self)

    def processKeyup(self, event):
        if self.mode == SysMode.Text:
            self.selFeatures[self.selIndex].keyUp(event, self)

    def processMousemove(self):
        pos = pygame.mouse.get_pos()
        scArea = 0.25*self.screenSize[0]*self.screenSize[1]

        selBlock = None
        # Test for mouse over menu.
        if self.primaryMenu.checkMouseHover(pos):
            selBlock = self.primaryMenu
        else:
            # Locate the block I'm hovering over.
            block = self.painter.drawBlock
            escaping = False
            while True:
                noGood = False
                if block.g_cycle != self.painter.cycle:
                    noGood = True
                else:
                    rPos = block.g_absPlacement.pointFromParent(pos, scArea)

                    # Test against block border.
                    if not block.g_border.pointWithin(rPos):
                        noGood = True

                if not noGood:
                    blockCutoff = block.g_sizeCutoff != None and \
                              block.g_absPlacement.scale < block.g_sizeCutoff

                    # Test for active features.
                    if not blockCutoff:
                        for i in range(len(block.g_interactiveFeatures)):
                            f = block.g_interactiveFeatures[-i]
                            if f.checkMouseHover(rPos):
                                # Clicking here will activate feature.
                                selBlock = f
                                escaping = True
                                break
                        if escaping:
                            break

                    # Test for hover near border.
                    if block.g_border.checkMouseHover(rPos):
                        selBlock = block.g_border
                        break

                    # Remember that a click here could select.
                    selBlock = block

                    # Check children.
                    if (not blockCutoff) and len(block.g_children) > 0:
                        block = block.g_children[0]
                        childIndex = 0
                    else:
                        break
                else:
                    # No luck. Look at next child of parent.
                    if not selBlock:
                        # First block failed.
                        break

                    childIndex = childIndex + 1
                    if childIndex >= len(selBlock.g_children):
                        # No more children.
                        break

                    # Try next child.
                    block = selBlock.g_children[childIndex]

        # Now remember the selection.
        self.clickItem = selBlock

        # And update the cursor.
        pygame.mouse.set_cursor(*getattr(selBlock, 'cursor', \
                                         self.defaultCursor))

    def processClick(self, event):
        if isinstance(self.clickItem, sourceFile.Block):
            self.setMode(SysMode.Standard)
            self.setSelection(self.clickItem)
        elif isinstance(self.clickItem, painter.Feature) or \
                 self.clickItem == self.primaryMenu:
            self.clickItem.mouseClick(self)

    def draw(self):
        # Check for outside interference.
        if self.selection.master != self.masterBlock:
            self.setSelection(self.masterBlock)
            self.primaryMenu.menu = None
            self.primaryMenu.menuChanged()

        # Time is used for a few things.
        now = time.time()
        dTime = now - self.lastRefreshTime
        self.lastRefreshTime = now

        # Shift the view if we're in pan/zoom mode.
        if self.mode == SysMode.PanZoom:
            panSp = self.panSpeed * self.painter.screenArea ** 0.5
            panAmount = [0, 0]
            if main.Settings.keyBindings[main.Keys.Left] in self.keys:
                panAmount[0] += panSp * dTime
            if main.Settings.keyBindings[main.Keys.Right] in self.keys:
                panAmount[0] -= panSp * dTime
            if main.Settings.keyBindings[main.Keys.Up] in self.keys:
                panAmount[1] += panSp * dTime
            if main.Settings.keyBindings[main.Keys.Down] in self.keys:
                panAmount[1] -= panSp * dTime

            if panAmount != [0, 0]:
                self.painter.pan(panAmount)

            zoomAmount = 0
            if main.Settings.keyBindings[main.Keys.In] in self.keys:
                zoomAmount = zoomAmount + self.zoomSpeed * dTime
            if main.Settings.keyBindings[main.Keys.Out] in self.keys:
                zoomAmount = zoomAmount - self.zoomSpeed * dTime

            if zoomAmount != 0:
                self.painter.zoom(8 ** zoomAmount)

        # Paint the layout if needed.
        self.painter.draw()
        self.screen.blit(self.painter.screen, (0,0))

        # Draw the selection (depends on mode).
        if self.mode in (SysMode.Mapping, SysMode.Text):
            self.selFeatures[self.selIndex].drawSelected(self.screen)
        elif self.mode == SysMode.FindText:
            self.selFeatures[self.selIndex].drawFinding(self.screen)
        else:
            # Draw the selected block.
            if self.selection.g_cycle == self.painter.cycle:
                self.selection.g_border.drawSelected(self.screen)



        # Highlight what we're pointing at.
        if isinstance(self.clickItem, painter.Feature):
            self.clickItem.mouseHover(self.screen)

        # Draw the menu.
        self.primaryMenu.draw(self.screen)

        if self.clickItem == self.primaryMenu:
            self.clickItem.mouseHover(self.screen)


#####################################
# Glyph classes.
#####################################

class PrimaryMenu(object):
    menuWidth = 150
    menuItemHeight = 20
    menuMaxGrowSpeed = 1000
    menuGrowAcc = 1500

    def __init__(self, actor, font, screenSize):
        self.actor = actor
        self.Menus = actor.Menus
        self.menuFont = font

        self.lastRefreshTime = time.time()

        self.menu = None
        self.realMenu = None
        self.mainMenuTab = 0
        self.menuHeight = 0
        self.menuGrowSpeed = 0
        self.screenSize = screenSize

    def draw(self, screen):
        now = time.time()
        dTime = now - self.lastRefreshTime
        self.lastRefreshTime = now

        # Move the menu.
        vel = dTime * self.menuGrowAcc
        dist = self.menuTargetHeight - self.menuHeight
        if dist > 0:
            self.menuGrowSpeed = min(self.menuGrowSpeed + vel, \
                                     self.menuMaxGrowSpeed, \
                                     (2 * self.menuGrowAcc * dist)**0.5)
            self.menuHeight = min(self.menuTargetHeight, \
                            self.menuHeight + self.menuGrowSpeed * dTime)
        elif dist < 0:
            self.menuGrowSpeed = max(self.menuGrowSpeed - vel, \
                                     -self.menuMaxGrowSpeed, \
                                     -(-2 * self.menuGrowAcc * dist)**0.5)
            self.menuHeight = max(self.menuTargetHeight, \
                            self.menuHeight + self.menuGrowSpeed * dTime)
        else:
            self.menuGrowSpeed = 0

        # Draw the menu
        pos = (self.screenSize[0] - self.menuWidth, \
               self.screenSize[1] - self.menuHeight)
        screen.blit(self.menuCanvas, pos)

    def checkMouseHover(self, pos):
        menuPos = (self.screenSize[0] - self.menuWidth, \
                   self.screenSize[1] - self.menuHeight)
        x, y = (pos[i] - menuPos[i] for i in (0,1))

        # Tell the system that we're not over the menu.
        if x < 0 or x > self.menuWidth or y < 0 or y > self.menuTargetHeight:
            return False

        # If it's the main menu, check for tabs.
        if self.menu == None:
            y = y - self.menuItemHeight
            if y < 0.:
                # Test for which tab.
                t = 0
                for tabX in self.tabLocs:
                    if x < tabX:
                        break
                    t = t - 1
                self.hoverIndex = t

                return True

        # Remember which item's being pointed to.
        self.hoverIndex = int(y // self.menuItemHeight)

        return True

    def mouseClick(self, actor):
        if self.hoverIndex < 0:
            # Select the tab which is pointed to.
            self.mainMenuTab = -1 - self.hoverIndex
            self.menuChanged()
        else:
            try:
                i = self.realMenu.items[self.hoverIndex]
            except IndexError:
                # Cancel was clicked.
                self.actor.cancel()
            else:
                # Activate the pointed-to item.
                i()

    def mouseHover(self, screen):
        if self.hoverIndex < 0:
            # Hover over tab.
            i = -1 - self.hoverIndex
            xPos = self.screenSize[0] - self.menuWidth + self.tabLocs[i]
            yPos = self.screenSize[1] - self.menuHeight + \
                   0.5 * self.menuItemHeight

            t = ('Modify','Edit','Mode','File')[i]
            cText = self.menuFont.render(t, True, selTextColour, menuColour)
            w, h = cText.get_size()
            screen.blit(cText, (xPos + 5., yPos - 0.5*h))
            return

        try:
            i = self.realMenu.items[self.hoverIndex]
        except IndexError:
            # Hover over cancel item.

            # 1. Rect.
            r = pygame.Rect((self.screenSize[0] - self.menuWidth, \
                             self.screenSize[1] - self.menuHeight + \
                             self.menuTargetHeight - self.menuItemHeight), \
                            (self.menuWidth, self.menuItemHeight))

            screen.fill(selMenuColour, r)

            # 2. Text.
            cText = self.menuFont.render('Cancel', True, selTextColour,
                                         selMenuColour)
            w, h = cText.get_size()

            pt = (self.screenSize[0] - 0.5*(self.menuWidth + w), \
                  self.screenSize[1] - self.menuHeight + self.menuTargetHeight \
                  - 0.5 * (self.menuItemHeight + h))
            screen.blit(cText, pt)
        else:
            # Check for tabs at the top.
            if self.menu == None:
                y = self.hoverIndex + 1
            else:
                y = self.hoverIndex
            pt = [self.screenSize[0] - self.menuWidth, \
                  self.screenSize[1] - self.menuHeight + \
                  y * self.menuItemHeight]

            screen.blit(self.drawItem(i, selTextColour, selMenuColour), pt)

    def menuChanged(self):
        # Decide which menu.
        if self.menu == None:
            # Main menu. Check which tab.
            if self.mainMenuTab == 0:
                # Modify tab - depends on selection type.
                menu = self.modifyMenu
            elif self.mainMenuTab == 1:
                menu = self.Menus.Edit
            elif self.mainMenuTab == 2:
                menu = self.Menus.Mode
            else:
                menu = self.Menus.File
        else:
            menu = self.menu
        self.realMenu = menu

        # Now draw the menu.
        canvas = pygame.Surface((self.menuWidth, self.menuItemHeight * \
                                 (len(menu)+1)))
        canvas.fill(menuColour)
        yPos = 0.

        # If it's a main menu, put the tabs across the top.
        if self.menu == None:
            yPos = 0.5 * self.menuItemHeight
            xPos = 0.
            i = 0
            self.tabLocs = []
            for t in ('Modify','Edit','Mode','File'):
                self.tabLocs.append(xPos)

                cText = self.menuFont.render(t, True, textColour, menuColour)
                w, h = cText.get_size()
                canvas.blit(cText, (xPos + 5., yPos - 0.5*h))
                xPos2 = xPos + w + 10.

                if i == self.mainMenuTab:
                    pygame.draw.line(canvas, textColour, (xPos, 0.), \
                                     (xPos, self.menuItemHeight), 2)
                    pygame.draw.line(canvas, textColour, (xPos2, 0.), \
                                     (xPos2, self.menuItemHeight), 2)
                    pygame.draw.line(canvas, textColour, (xPos, 0.), \
                                     (xPos2, 0.), 2)
                    pygame.draw.line(canvas, textColour, \
                                     (0., self.menuItemHeight), \
                                     (xPos, self.menuItemHeight), 2)
                    pygame.draw.line(canvas, textColour, \
                                     (xPos2, self.menuItemHeight), \
                                     (self.menuWidth, self.menuItemHeight), 2)

                xPos = xPos2
                i = i + 1

            yPos = yPos + 0.5 * self.menuItemHeight

        # Now draw the items.
        for item in menu:
            itemCanvas = self.drawItem(item, textColour, menuColour)
            itemCanvas.set_colorkey(menuColour)
            canvas.blit(itemCanvas, (0., yPos))
            yPos = yPos + self.menuItemHeight

        # If it's not main menu, add a cancel item.
        if self.menu != None:
            cText = self.menuFont.render('Cancel', True, textColour,
                                         menuColour)
            w, h = cText.get_size()
            canvas.blit(cText, (0.5*(self.menuWidth - w), \
                                yPos+0.5*(self.menuItemHeight-h)))

        self.menuCanvas = canvas
        self.menuTargetHeight = canvas.get_height()

    def drawItem(self, item, fgColour, bkgColour):
        canvas = pygame.Surface((self.menuWidth, self.menuItemHeight))
        canvas.fill(bkgColour)

        cText = self.menuFont.render(item.caption, True, fgColour, bkgColour)

        if item.shortcutKeys != None:
            scText = self.menuFont.render(keyboard.shortcutName( \
                *item.shortcutKeys), True, fgColour, bkgColour)

            # Place the texts on the canvas.
            w, h = scText.get_size()
            canvas.blit(scText, (self.menuWidth - 3 - w, \
                                 0.5 * (self.menuItemHeight - h)))

        canvas.blit(cText, (3, 0.5*(self.menuItemHeight-cText.get_height())))
        return canvas

    def selectionIs(self, selection):
        mod = self.Menus.Modify
        menu = mod.get(type(selection), mod[None])
        self.modifyMenu = menu

        self.menuChanged()

if __name__ == '__main__':
    mb = main.main()
