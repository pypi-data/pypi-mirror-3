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

import pygame.locals as pgl

# 1. We want to be able to represent a shortcut as a string.
def shortcutName(key, modifiers):
    try:
        k = KEY_MAPPING[key]
    except KeyError:
        # Unmapped key.
        return

    # Test if it's a named key.
    try:
        name = NAMED[k]
    except KeyError:
        try:
            name = TYPABLE[k][0]
        except KeyError:
            return ''

    # Add the modifiers.
    modString = ''
    for kmod, modName in KMOD_NAMES:
        if modifiers & kmod:
            modString = '%s%s+' % (modString, modName)

    return '%s%s' % (modString, name)

# 2. We want to be able to translate a keypress into a char.
def charPressed(key, modifiers):
    '''(key, modifiers) - returns the character typed, or if the character
    is not typable, returns key, modifiers where key is the virtual key (as
    opposed to the physical key).'''

    # First translate to virtual key.
    try:
        k = KEY_MAPPING[key]
    except KeyError:
        return

    # Now translate keypad items.
    done = False
    if modifiers & pgl.KMOD_NUM:
        try:
            k = NUMLOCKED[k]
            done = True
        except KeyError:
            pass
        modifiers = modifiers & ~ pgl.KMOD_NUM
    if not done:
        try:
            k = NUMUNLOCKED[k]
        except KeyError:
            pass

    # Now translate any right modifiers (shift, ctrl, alt) to left.
    if modifiers & pgl.KMOD_RSHIFT:
        modifiers = modifiers | pgl.KMOD_LSHIFT & ~ pgl.KMOD_RSHIFT
    if modifiers & pgl.KMOD_RCTRL:
        modifiers = modifiers | pgl.KMOD_LCTRL & ~ pgl.KMOD_RCTRL
    if modifiers & pgl.KMOD_RALT:
        modifiers = modifiers | pgl.KMOD_LALT & ~ pgl.KMOD_RALT
    if modifiers & pgl.KMOD_RMETA:
        modifiers = modifiers | pgl.KMOD_LMETA & ~ pgl.KMOD_RMETA

    # Test for anything except shift, caps and numlock.
    if modifiers & ~(pgl.KMOD_SHIFT | pgl.KMOD_CAPS | pgl.KMOD_NUM):
        return k, modifiers

    # Test if it's a typable char.
    try:
        chars = TYPABLE[k]
    except KeyError:
        pass
    else:
        # It's typable. Check for case.
        shift = modifiers & pgl.KMOD_SHIFT
        caps = modifiers & pgl.KMOD_CAPS

        if shift or caps and not (shift and caps):
            return chars[1]
        else:
            return chars[0]

    return k, modifiers

A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z = \
                                    [object() for i in range(26)]
n0,n1,n2,n3,n4,n5,n6,n7,n8,n9 = [object() for i in range(10)]

Ampersand, Asterisk, At, Backquote, Backslash, Caret, Colon, Comma, Dollar, \
    Equals, Exclaim, Greater, Hash, kpDivide, kpEquals, kpMinus, kpAsterisk, \
    kpPlus, kpPoint, LeftBrace, LeftParenthesis, Less, Minus, Fullstop, Plus, \
    Quote, Quotes, RightBrace, RightParenthesis, Semicolon, Slash, Space, \
    Underscore = [object() for i in range(33)]

Backspace, Break, Capslock, Delete, Down, End, Escape, Euro, F1, F2, F3, F4, \
    F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15, First, Help, Home, \
    Insert, kp0, kp1, kp2, kp3, kp4, kp5, kp6, kp7, kp8, kp9, kpEnter, \
    LeftAlt, Last, LeftControl, Left, LeftMeta, LeftShift, LeftSuper, \
    Menu, Mode, Numlock, Pagedown, Pageup, Pause, Power, Print, RightAlt, \
    RightControl, Return, Right, RightMeta, RightShift, RightSuper, \
    Scrolllock, SysReq, Tab, Up, Clear = [object() for i in range(65)]

TYPABLE = {A: 'aA', B: 'bB', C: 'cC', D: 'dD', E: 'eE', F: 'fF',
           G: 'gG', H: 'hH', I: 'iI', J: 'jJ', K: 'kK', L: 'lL',
           M: 'mM', N: 'nN', O: 'oO', P: 'pP', Q: 'qQ', R: 'rR',
           S: 'sS', T: 'tT', U: 'uU', V: 'vV', W: 'wW', X: 'xX',
           Y: 'yY', Z: 'zZ', n0: '0)', n1: '1!', n2: '2@', n3: '3#',
           n4: '4$', n5: '5%', n6: '6^', n7: '7&', n8: '8*', n9: '9(',
           Ampersand: '&&', Asterisk: '**', At: '@@', Backquote: '`~',
           Backslash: '\\|', Caret: '^^', Colon: ':;', Comma: ',<',
           Dollar: '$$', Equals: '=+', Exclaim: '!!', Greater: '>>',
           Hash: '##', kpDivide: '/?', kpEquals: '==',
           kpMinus: '--', kpAsterisk: '**', kpPlus: '++', kpPoint: '..',
           LeftBrace: '[{', LeftParenthesis: '((', Less: '<<', Minus: '-_',
           Fullstop: '.>', Plus: '++', Quote: '\'"', Quotes: '""',
           RightBrace: ']}', RightParenthesis: '))', Semicolon: ';:',
           Slash: '/?', Space: '  ', Underscore: '__'
           }

NUMLOCKED = {kp0: n0, kp1: n1, kp2: n2, kp3: n3, kp4: n4, kp5: n5,
             kp6: n6, kp7: n7, kp8: n8, kp9: n9}
NUMUNLOCKED = {kp0: Insert, kp1: End, kp2: Down, kp3: Pagedown, kp4: Left,
               kp6: Right, kp7: Home, kp8: Up, kp9: Pageup, kpPoint: Delete,
               kpEnter: Return}

NAMED = {Backspace: 'Backspace', Break: 'Break', Capslock: 'Capslock',
         Clear: 'Clear', Delete: 'Del', Down: 'Down', End: 'End',
         Escape: 'Escape', Euro: 'Euro', F1: 'F1', F2: 'F2', F3: 'F3', F4: 'F4',
         F5: 'F5', F6: 'F6', F7: 'F7', F8: 'F8', F9: 'F9', F10: 'F10',
         F11: 'F11', F12: 'F12', F13: 'F13', F14: 'F14', F15: 'F15',
         First: 'First', Help: 'Help', Home: 'Home', Insert: 'Ins',
         LeftAlt: 'L.Alt', Last: 'Last', LeftControl: 'L.Ctrl', Left: 'Left',
         LeftMeta: 'L.Meta', LeftShift: 'L.Shift', LeftSuper: 'L.Super',
         Menu: 'Menu', Mode: 'Mode', Numlock: 'Numlock', Pagedown: 'PgDn',
         Pageup: 'PgUp', Pause: 'Pause', Power: 'Power', Print: 'Print',
         RightAlt: 'R.Alt', RightControl: 'R.Ctrl', Return: 'Return',
         Right: 'Right', RightMeta: 'R.Meta', RightShift: 'R.Shift',
         RightSuper: 'R.Super', Scrolllock: 'Scrolllock', SysReq: 'SysRq',
         Tab: 'Tab', Up: 'Up', Space: 'Space'}


STANDARD_MAP = {pgl.K_BACKSPACE: Backspace, pgl.K_BREAK: Break,
                pgl.K_CAPSLOCK: Capslock, pgl.K_CLEAR: Clear,
                pgl.K_DELETE: Delete, pgl.K_DOWN: Down, pgl.K_END: End,
                pgl.K_ESCAPE: Escape, pgl.K_EURO: Euro, pgl.K_F1: F1,
                pgl.K_F2: F2, pgl.K_F3: F3, pgl.K_F4: F4, pgl.K_F5: F5,
                pgl.K_F6: F6, pgl.K_F7: F7, pgl.K_F8: F8, pgl.K_F9: F9,
                pgl.K_F10: F10, pgl.K_F11: F11, pgl.K_F12: F12, pgl.K_F13: F13,
                pgl.K_F14: F14, pgl.K_F15: F15, pgl.K_FIRST: First,
                pgl.K_HELP: Help, pgl.K_HOME: Home, pgl.K_INSERT: Insert,
                pgl.K_KP0: kp0, pgl.K_KP1: kp1, pgl.K_KP2: kp2, pgl.K_KP3: kp3,
                pgl.K_KP4: kp4, pgl.K_KP5: kp5, pgl.K_KP6: kp6, pgl.K_KP7: kp7,
                pgl.K_KP8: kp8, pgl.K_KP9: kp9, pgl.K_KP_DIVIDE: kpDivide,
                pgl.K_KP_ENTER: kpEnter, pgl.K_KP_EQUALS: kpEquals,
                pgl.K_KP_MINUS: kpMinus, pgl.K_KP_MULTIPLY: kpAsterisk,
                pgl.K_KP_PERIOD: kpPoint, pgl.K_KP_PLUS: kpPlus,
                pgl.K_LALT: LeftAlt, pgl.K_LAST: Last, pgl.K_LCTRL: LeftControl,
                pgl.K_LEFT: Left, pgl.K_LMETA: LeftMeta,
                pgl.K_LSHIFT: LeftShift, pgl.K_LSUPER: LeftSuper,
                pgl.K_MENU: Menu, pgl.K_MODE: Mode, pgl.K_NUMLOCK: Numlock,
                pgl.K_PAGEDOWN: Pagedown, pgl.K_PAGEUP: Pageup,
                pgl.K_PAUSE: Pause, pgl.K_POWER: Power, pgl.K_PRINT: Print,
                pgl.K_RALT: RightAlt, pgl.K_RCTRL: RightControl,
                pgl.K_RETURN: Return, pgl.K_RIGHT: Right,
                pgl.K_RMETA: RightMeta,
                pgl.K_RSHIFT: RightShift, pgl.K_RSUPER: RightSuper,
                pgl.K_SCROLLOCK: Scrolllock, pgl.K_SYSREQ: SysReq,
                pgl.K_TAB: Tab, pgl.K_UP: Up, pgl.K_SPACE: Space,

                pgl.K_1: n1, pgl.K_2: n2, pgl.K_3: n3, pgl.K_4: n4, pgl.K_5: n5,
                pgl.K_6: n6, pgl.K_7: n7, pgl.K_8: n8, pgl.K_9: n9, pgl.K_0: n0
                }

DVORAK_MAP = \
    {
        pgl.K_BACKQUOTE: Backquote, pgl.K_MINUS: LeftBrace, \
            pgl.K_EQUALS: RightBrace, pgl.K_BACKSLASH: Backslash, \
        pgl.K_q: Quote, pgl.K_w: Comma, pgl.K_e: Fullstop, pgl.K_r: P, \
            pgl.K_t: Y, pgl.K_y: F, pgl.K_u: G, pgl.K_i: C, pgl.K_o: R, \
            pgl.K_p: L, pgl.K_LEFTBRACKET: Slash, pgl.K_RIGHTBRACKET: Equals, \
        pgl.K_a: A, pgl.K_s: O, pgl.K_d: E, pgl.K_f: U, pgl.K_g: I, \
            pgl.K_h: D, pgl.K_j: H, pgl.K_k: T, pgl.K_l: N, \
            pgl.K_SEMICOLON: S, pgl.K_QUOTE: Minus, \
        pgl.K_z: Semicolon, pgl.K_x: Q, pgl.K_c: J, pgl.K_v: K, pgl.K_b: X, \
            pgl.K_n: B, pgl.K_m: M, pgl.K_COMMA: W, pgl.K_PERIOD: V, \
            pgl.K_SLASH: Z
    }
DVORAK_MAP.update(STANDARD_MAP)

QWERTY_MAP = \
    {
        pgl.K_BACKQUOTE: Backquote, pgl.K_MINUS: Minus, \
            pgl.K_EQUALS: Equals, pgl.K_BACKSLASH: Backslash, \
        pgl.K_q: Q, pgl.K_w: W, pgl.K_e: E, pgl.K_r: R, \
            pgl.K_t: T, pgl.K_y: Y, pgl.K_u: U, pgl.K_i: I, pgl.K_o: O, \
            pgl.K_p: P, pgl.K_LEFTBRACKET: LeftBrace, \
            pgl.K_RIGHTBRACKET: RightBrace, \
        pgl.K_a: A, pgl.K_s: S, pgl.K_d: D, pgl.K_f: F, pgl.K_g: G, \
            pgl.K_h: H, pgl.K_j: J, pgl.K_k: K, pgl.K_l: L, \
            pgl.K_SEMICOLON: Semicolon, pgl.K_QUOTE: Quote, \
        pgl.K_z: Z, pgl.K_x: X, pgl.K_c: C, pgl.K_v: V, pgl.K_b: B, \
            pgl.K_n: N, pgl.K_m: M, pgl.K_COMMA: Comma, pgl.K_PERIOD: Fullstop, \
            pgl.K_SLASH: Slash
    }
QWERTY_MAP.update(STANDARD_MAP)

TYPABLE = {A: 'aA', B: 'bB', C: 'cC', D: 'dD', E: 'eE', F: 'fF',
           G: 'gG', H: 'hH', I: 'iI', J: 'jJ', K: 'kK', L: 'lL',
           M: 'mM', N: 'nN', O: 'oO', P: 'pP', Q: 'qQ', R: 'rR',
           S: 'sS', T: 'tT', U: 'uU', V: 'vV', W: 'wW', X: 'xX',
           Y: 'yY', Z: 'zZ', n0: '0)', n1: '1!', n2: '2@', n3: '3#',
           n4: '4$', n5: '5%', n6: '6^', n7: '7&', n8: '8*', n9: '9(',
           Ampersand: '&&', Asterisk: '**', At: '@@', Backquote: '`~',
           Backslash: '\\|', Caret: '^^', Colon: ':;', Comma: ',<',
           Dollar: '$$', Equals: '=+', Exclaim: '!!', Greater: '>>',
           Hash: '##', kpDivide: '/?', kpEquals: '==',
           kpMinus: '--', kpAsterisk: '**', kpPlus: '++', kpPoint: '..',
           LeftBrace: '[{', LeftParenthesis: '((', Less: '<<', Minus: '-_',
           Fullstop: '.>', Plus: '++', Quote: '\'"', Quotes: '""',
           RightBrace: ']}', RightParenthesis: '))', Semicolon: ';:',
           Slash: '/?', Space: '  ', Underscore: '__'
           }

KMOD_NAMES = ((pgl.KMOD_CTRL, 'Ctrl'), (pgl.KMOD_ALT, 'Alt'), \
              (pgl.KMOD_META, 'Meta'), (pgl.KMOD_SHIFT, 'Shift'))

KEY_MAPPING = DVORAK_MAP
