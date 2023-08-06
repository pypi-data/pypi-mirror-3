#!/usr/bin/env python3

# gravnoise: a block-based, gravity-infused puzzle game
# Copyright (C) 2012  Niels G. W. Serup

# This file is part of gravnoise.
#
# gravnoise is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gravnoise is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gravnoise.  If not, see <http://www.gnu.org/licenses/>.

## Maintainer: Niels G. W. Serup <ns@metanohi.name>
## Homepage:   http://metanohi.name/projects/gravnoise/
## Version:    0.1


# IMPORTS #####
import sys
import argparse
import textwrap
import operator
import functools
from fractions import Fraction
import random
import time
import threading
import queue
import subprocess as subp
import re
import atexit
import pygame as pg

try:
    from termcolor import colored as color_text
except ImportError:
    color_text = lambda text, *x, **y: text

try:
    from setproctitle import setproctitle
except ImportError:
    setproctitle = lambda x: None
###############

    
# CONVENIENCE OBJECTS #####
_selfmodule = sys.modules[__name__]
_selfdict = _selfmodule.__dict__

def product(*objs):
    return functools.reduce(operator.mul, objs)

def _too_old_for(subj, obj):
    return 'this version of {} is too old for {}'.format(subj, obj)

def _fmt(text):
    return text.format(**globals())

def _default_values(values, defaults):
    if values is None:
        return defaults
    return tuple(values[i] if values[i] is not None
                 else defaults[i] for i in
                 range(min(map(len, (values, defaults)))))

_sgn = lambda t: 1 if t > 0 else -1 if t < 0 else 0

class _StringTuple(str):
    def __new__(self, *elems):
        self.tuple = elems
        return str.__new__(self, '.'.join(map(str, elems)))

def _resize_monitor(size, name):
    subp.call(['xrandr', '--output', name, '--mode',
               'x'.join(map(str, size))])

def _consts(*names):
    i = 1
    for name in names:
        _selfdict[name] = i
        i += 1

def _copy_attrs(src, dest, *names):
    for name in names:
        setattr(dest, name, getattr(src, name))

def _untupled_dict(*tupled):
    d = {}
    for key, val in tupled:
        try:
            for key in key:
                d[key] = val
        except TypeError:
            d[key] = val
    return d

_rotates = (
    lambda x, y: (x, y),
    lambda x, y: (y, -x),
    lambda x, y: (-x, -y),
    lambda x, y: (-y, x),
    )

_flips = (
    lambda x, y: (-x, y),
    lambda x, y: (x, -y)
    )

def backup(self, *names):
    '''
    For methods that might set class variables to new values only to realize
    that they have to be reverted.
    '''
    old = {}
    for name in names:
        old[name] = getattr(self, name)

    def revert():
        for name in names:
            setattr(self, name, old[name])
    return revert
###########################


# CONSTANTS #####
DEFAULT_WINDOW_SIZE = (640, 480)
DEFAULT_BOX_SIZE = (20, 20)
_consts('WINDOWED', 'REAL_FULLSCREEN', 'SIMPLE_FULLSCREEN',
        'NEW_GAME', 'GAME_OVER', 'EXIT', 'MOVE', 'ROTATE', 'FLIP',
        'SWAP_GRAVITY', 'DROP', 'HURRY', 'UNHURRY',
        'UP', 'DOWN', 'LEFT', 'RIGHT', 'CW', 'CCW', 'X_AXIS', 'Y_AXIS',
        'CURRENT_BLOCK_CHANGED',
        'CURRENT_BLOCK_POSITION_CHANGED',
        'CURRENT_BLOCK_ADDED_TO_BOARD',
        'BOARD_CHANGED',
        )
DEFAULT_WINDOW_CONFIGURATION = WINDOWED
DEFAULT_FPS = 30
KEYDOWN_DELAY = 0.1
K_CTRL = (pg.K_RCTRL,  pg.K_LCTRL)
K_SHIFT = (pg.K_RSHIFT, pg.K_LSHIFT)
ERROR_COLOR = 'red'
#################


# EXCEPTIONS #####
class GravnoiseError(Exception):
    '''For general gravnoise errors'''
    pass

class VersionError(GravnoiseError):
    pass

class SDLVersionError(VersionError):
    pass

class PygameVersionError(VersionError):
    pass
##################


# PROGRAM INFORMATION #####
__version__ = _StringTuple(0, 1, 0)
__program_name__ = 'gravnoise'
__program_description__ = \
    'a block-based, gravity-infused puzzle game'
__author_name__ = 'Niels G. W. Serup'
__author_email__ = 'ns@metanohi.name'
__author__ = _fmt('{__author_name__} <{__author_email__}>')
__home_page__ = 'http://metanohi.name/projects/gravnoise/'
__copyright_years__ = '2012'
__copyright_line__ = _fmt('''\
Copyright (C) {__copyright_years__}  {__author_name__}\
''')
__copyright__ = _fmt('''\
{__copyright_line__}

{__program_name__} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

{__program_name__} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with {__program_name__}.  If not, see <http://www.gnu.org/licenses/>.\
''')
__version_long__ = _fmt('''\
{__program_name__} {__version__}
{__copyright_line__}
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.\
''')
__license_short__ = 'GPLv3+'
__block_description__ = '''
A block of size n is a collection of boxes, where there is a path from any box
to any other box and where there is no empty space "locked in" between boxes.
'''
__doc__ = _fmt('''
{__program_description__}.

This is mainly a game, but it can be also used as a Python module to generate
all possible blocks of different sizes; see get_number_of_blocks and
generate_blocks.
{__block_description__}
''')
###########################


class Block:
    def __init__(self, boxes=None):
        if boxes is None:
            return
        if isinstance(boxes, Block):
            _copy_attrs(boxes, self, 'boxes', '_temp_boxes',
                        'origo_boxes', '_temp_origo_boxes', 'size', 'origo')
        else:
            self.boxes = boxes
            self.origo_boxes = []
            mi = min(x for x, y in self.boxes), min(y for x, y in self.boxes)
            ma = max(x for x, y in self.boxes), max(y for x, y in self.boxes)
            self.size = tuple(ma[i] - mi[i] + 1 for i in range(2))
            self._create_origo()
            for pos in self.boxes:
                self.origo_boxes.append(self.upper_left_pos_to_origo_pos(pos))
            self.origo_boxes.sort()
            self.origo_boxes = tuple(self.origo_boxes)
            self._create_temp_boxes()

    def _create_temp_boxes(self):
        self._temp_boxes = [(0, 0) for b in self.boxes]
        self._temp_origo_boxes = [(0, 0) for b in self.boxes]

    def _create_origo(self):
        self.origo = tuple(Fraction(self.size[i], 2)
                           if self.size[i] % 2 == 1
                           else self.size[i] // 2
                           for i in range(2))

    @staticmethod
    def from_2d_list(tss):
        self = Block()
        self.boxes = []
        self.origo_boxes = []
        self.size = (max(map(len, tss)), len(tss))
        self._create_origo()

        y = 0
        for ts in tss:
            x = 0
            for t in ts:
                if t:
                    pos = (x, y)
                    self.boxes.append(pos)
                    self.origo_boxes.append(self.upper_left_pos_to_origo_pos(pos))
                x += 1
            y += 1
        self.origo_boxes = tuple(self.origo_boxes)
        self._create_temp_boxes()
        return self

    def upper_left_pos_to_origo_pos(self, pos):
        return tuple(pos[i] + Fraction(1, 2) - self.origo[i] for i in range(2))

    def origo_pos_to_upper_left_pos(self, origo_pos):
        return tuple(int(origo_pos[i] - Fraction(1, 2) + self.origo[i]) for i in range(2))
            
    def rotate(self, amount):
        amount %= 4
        f = _rotates[amount]
        if amount == 1 or amount == 3:
            self.origo = self.origo[::-1]
            self.size = self.size[::-1]
        self._temp_origo_boxes = [f(*pos) for pos in self.origo_boxes]
        self._temp_boxes = [self.origo_pos_to_upper_left_pos(pos)
                            for pos in self._temp_origo_boxes]
        self._temp_origo_boxes.sort()
        self.origo_boxes, self._temp_origo_boxes \
            = tuple(self._temp_origo_boxes), self.origo_boxes
        self.boxes, self._temp_boxes \
            = self._temp_boxes, self.boxes

    def flip(self, direction):
        f = _flips[{X_AXIS: 0, Y_AXIS: 1}[direction]]
        self._temp_origo_boxes = [f(*pos) for pos in self.origo_boxes]
        self._temp_boxes = [self.origo_pos_to_upper_left_pos(pos)
                            for pos in self._temp_origo_boxes]
        self._temp_origo_boxes.sort()
        self.origo_boxes, self._temp_origo_boxes \
            = tuple(self._temp_origo_boxes), self.origo_boxes
        self.boxes, self._temp_boxes \
            = self._temp_boxes, self.boxes

    def multi_line_repr(self, block_char='#'):
        arr = [[' ' for i in range(self.size[0])] for i in range(self.size[1])]
        for x, y in self.boxes:
            arr[y][x] = block_char
        return '\n'.join(''.join(line) for line in arr)


FALLBACK_BLOCKS = None
def _generate_fallback_blocks():
    global FALLBACK_BLOCKS
    FALLBACK_BLOCKS = tuple(map(Block.from_2d_list, (
        [[1, 1, 1, 1]],

        [[1, 1, 1],
         [0, 0, 1]],

        [[1, 1, 1],
         [1]],

        [[1, 1],
         [1, 1]],
        
        [[0, 1, 1],
         [1, 1]],

        [[1, 1, 1],
         [0, 1]],

        [[1, 1],
         [0, 1, 1]],
        )))

def sum_permutations(size):
    yield [size]
    for sub_size in range(1, size):
        size -= 1
        for perm in sum_permutations(sub_size):
            new = [size]
            new.extend(perm)
            yield new

class _BoolCallValue:
    __bool__ = lambda self: self.value
    __call__ = __bool__

def _bool_class(value):
    class _(_BoolCallValue):
        pass
    _.value = value
    return _

_False, _True = (_bool_class(x)() for x in (False, True))

class PersistentStack:
    @staticmethod
    def create_empty():
        return _EmptyPersistentStack()

    def push(self, value):
        return _NonEmptyPersistentStack(self, value)

    def pop(self):
        pass

    def peek(self):
        pass

    def __iter__(self):
        while not self.is_empty():
            yield self.peek()
            self = self.pop()

class _EmptyPersistentStack(PersistentStack):
    def is_empty(self):
        return True

    def pop(self):
        raise Empty

    def peek(self):
        raise Empty

class _NonEmptyPersistentStack(PersistentStack):
    def __init__(self, prev_stack, value):
        self.prev_stack = prev_stack
        self.value = value

    def is_empty(self):
        return False

    def pop(self):
        return self.prev_stack

    def peek(self):
        return self.value

class _Node:
    def __init__(self, value, next_node):
        self.value = value
        self.next_node = next_node

class Queue:
    def __init__(self):
        self.first_node = None
        self.last_node = None

    def is_empty(self):
        return self.first_node is None

    def add(self, value):
        node = _Node(value, None)
        if self.last_node is None:
            self.last_node = self.first_node = node
        else:
            self.last_node.next_node = node
            self.last_node = node

    def peek(self):
        if self.is_empty():
            raise Empty
        else:
            return self.first_node.value

    def pop(self):
        ret = self.peek()
        self.first_node = self.first_node.next_node
        return ret

    def __iter__(self):
        node = self.first_node
        while node:
            yield node.value
            node = node.next_node
    
def sum_permutations(size):
    perms = [Queue() for i in range(size + 1)]
    perms[0].add(PersistentStack.create_empty())
    for cur_size in range(1, size + 1):
        cur_perms = perms[cur_size]
        for sub_perms in perms[:cur_size]:
            for perm in sub_perms:
                cur_perms.add(perm.push(cur_size))
            cur_size -= 1
    return perms[-1]

def _shift(ns):
    ns = iter(ns)
    m = next(ns)
    for n in ns:
        yield m + n - 1
        m = n

def get_number_of_blocks(size=4, remove_rotated=False, remove_flipped=False):
    '''
    Returns the number of blocks that can arise from different box combinations
    of a given size. The note from generate_blocks apply here too.
    '''
    if size < 1:
        return 0

    if not remove_rotated and not remove_flipped:
        return sum(functools.reduce(operator.mul, _shift(perm), 1)
                   for perm in sum_permutations(size))
    else:
        return len(size, remove_rotated, remove_flipped)

def generate_blocks(size=4, remove_rotated=False, remove_flipped=False):
    '''
    Returns the blocks that can arise from different box combinations of a
    given size. Does not necessarily generate all rotated and flipped versions
    of a block: sometimes the algorithm generates all versions of a block,
    sometimes only some of them, but always at least one.
    '''
    if size < 1:
        return []

    blocks = []
    for local_size in range(1, size + 1):
        first_block = ([(x, 0) for x in range(local_size)],
                       local_size, 0)
        local_blocks = [first_block]
        blocks.append(local_blocks)
        for rest in range(1, local_size):
            cur_start_width = local_size - rest
            for block, first_width, first_offset in blocks[rest - 1]:
                slide_width = cur_start_width - 1 + first_width
                leading_empty = first_width + first_offset - 1
                for local_slide_x in range(slide_width):
                    first_start_x = 0 if local_slide_x >= leading_empty \
                        else leading_empty - local_slide_x
                    x_offset = 0 if local_slide_x <= leading_empty \
                        else local_slide_x - leading_empty
                    new_block = [(x, 0) for x in
                                 range(first_start_x, first_start_x
                                       + cur_start_width)]
                    new_block.extend((x + x_offset, y + 1) for x, y in block)
                    local_blocks.append((new_block, cur_start_width,
                                         first_start_x))
    blocks = [Block(block[0]) for block in blocks[-1]]
    if remove_rotated:
        blocks = _remove_rotated_blocks(blocks)
    if remove_flipped:
        blocks = _remove_flipped_blocks(blocks)
    return blocks

def _remove_rotated_blocks(blocks):
    rotated = set()
    for block in blocks:
        if not block.origo_boxes in rotated:
            yield block
            for i in range(1, 4):
                rotated.add(tuple(sorted(_rotates[i](*pos)
                                         for pos in block.origo_boxes)))

def _remove_flipped_blocks(blocks):
    flipped = set()
    for block in blocks:
        if not block.origo_boxes in flipped:
            yield block
            for i in range(2):
                flipped.add(tuple(sorted(_flips[i](*pos)
                                         for pos in block.origo_boxes)))

class Controller:
    '''
    The class controls the game and the screen. It is the medium through which
    Game and Screen communicates.
    '''
    def __init__(self, game, screen,
                 window_size=DEFAULT_WINDOW_SIZE,
                 box_size=DEFAULT_BOX_SIZE,
                 message_handler=None):
        self.game = game
        self.screen = screen
        self.message_handler = message_handler
        self.window_size = _default_values(window_size, DEFAULT_WINDOW_SIZE)
        self.box_size = _default_values(box_size, DEFAULT_BOX_SIZE)
        if not all(self.window_size[i] % self.box_size[i] == 0
                   for i in range(2)):
            raise GravnoiseError('window size not a multiple of block size')
        self.board_size = tuple(self.window_size[i] // self.box_size[i]
                                for i in range(2))
        if self.message_handler is not None:
            self.emit_message = self._emit_message

        self.actions = {
            NEW_GAME: lambda *_: self.new_game(),
            GAME_OVER: lambda *_: self.game_over_declare(),
            EXIT: lambda *_: self.exit(),
            }

    def start(self):
        '''Starts the game and initiates the graphics.'''
        self.emit_message("""
Welcome to gravnoise. Game configuration takes place on the command-line. Run
'gravnoise --help' for help.
""")
        self.emit_message("(Messages like this can be disabled with the argument '-q'.)")
        self.emit_message('''
You probably should not play this game for more than a few minutes as it screws
up your vision a little.
''')
        self.exiting = False
        self.game_over = False
        self.rlock = threading.RLock()
        self.next_events = queue.Queue()
        for obj in self.screen, self.game:
            obj.set_controller(self)
            obj.start()

        self.run()

    def run(self):
        self.screen_thread = threading.Thread(target=self.screen.run)
        self.game_thread = threading.Thread(target=self.game.run)
        self.screen_thread.start()
        self.game_thread.start()
        self.ready = threading.Event()
        threading.Thread(target=self._process_loop).start()
        self.ready.wait()
        self.process(NEW_GAME)

    def emit_message(self, message):
        '''Emits a message to the message handler.'''
        pass

    def _emit_message(self, message):
        # Emits a message if a message handler exists.
        self.message_handler(message.strip().replace('\n', ' '))

    def process(self, *args):
        self.next_events.put(args)
        
    def _process_loop(self):
        self.ready.set()
        while True:
            while True:
                try:
                    next_event = self.next_events.get()
                except Empty:
                    break
                if next_event[0] == EXIT:
                    break
                for o in self, self.game, self.screen:
                    action = o.actions.get(next_event[0])
                    if action:
                        action(*next_event[1:])
            if next_event[0] == EXIT:
                break
            self.next_events.task_done()
        self.exit()

    def exit(self):
        self.exiting = True
        self.emit_message('exiting')

    def game_over_declare(self):
        self.game_over = True
        self.emit_message('game over')

    def new_game(self):
        self.emit_message('starting new game')
        self.game_over = False

class Controlled:
    '''For anything that can be controlled by a controller.'''
    def __init__(self):
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def notify(self, event, *args):
        self.controller.process(event, *args)

class SimpleTimer:
    def __init__(self, func, may_run):
        self.func = func
        self.may_run = may_run
        
    def start(self, wait):
        self.in_temp_wait = False
        self.wait = wait
        while self.may_run():
            if self.wait > 0:
                self.target = time.time() + self.wait
                while time.time() < self.target:
                    time.sleep(0.01)
            if not self.func():
                break
            if self.wait is not None:
                if self.wait < 0.1 and not self.in_temp_wait:
                    self.wait = 0.1

    def set_temp_wait(self, temp_wait):
        self.wait_backup = self.wait
        self.wait = temp_wait
        self.in_temp_wait = True
        if self.target - time.time() > temp_wait:
            self.target -= self.target - time.time() - temp_wait

    def unset_temp_wait(self):
        if hasattr(self, 'wait_backup'):
            self.wait = self.wait_backup
            self.in_temp_wait = False

    def set_wait(self, wait):
        if not self.in_temp_wait:
            self.wait = wait

class GameBlock(Block):
    def __init__(self, game, boxes):
        super().__init__(boxes)
        self.game = game
        self.position = [self.game.center_position[i] - int(self.origo[i])
                         for i in range(2)]

    def move(self, direction):
        revert = backup(self, 'position')
        self.position = [self.position[i] + direction[i] for i in range(2)]
        return self._hit_status(revert)

    def rotate(self, amount):
        revert = backup(self, 'origo', 'origo_boxes', '_temp_origo_boxes',
                        'boxes', '_temp_boxes',
                        'size', 'position')
        old_size = self.size[:]
        super().rotate(amount)
        diff = tuple(old_size[i] - self.size[i] for i in range(2))
        self.position = [self.position[i] + _sgn(diff[i]) * (abs(diff[i]) // 2)
                         for i in range(2)]
        return self._hit_status(revert)
    
    def flip(self, direction):
        revert = backup(self, 'origo_boxes', '_temp_origo_boxes',
                        'boxes', '_temp_boxes')
        super().flip(direction)
        return self._hit_status(revert)
    
    def _hit_status(self, revert):
        if self.hits_boundary():
            revert()
            return None
        elif self.hits_blocks():
            revert()
            return False
        return True

    def offset_boxes(self):
        return (tuple(self.position[i] + pos[i] for i in range(2))
                for pos in self.boxes)
    
    def hits_boundary(self):
        return self.position[1] < 0 or \
            self.position[1] + self.size[1] \
            > self.game.controller.board_size[1]

    def hits_blocks(self):
        if self.position[0] < 0 or \
                self.position[0] + self.size[0] \
                > self.game.controller.board_size[0]:
            return True
        for pos in self.offset_boxes():
            if pos in self.game.board:
                return True
        return False
        

class Game(Controlled):
    direction_distance = {
        UP:    (0, -1),
        DOWN:  (0, 1),
        LEFT:  (-1, 0),
        RIGHT: (1, 0),
        CW:    -1,
        CCW:   1
        }
    
    def __init__(self, block_size=None):
        super().__init__()
        if not block_size or block_size < 1:
            _generate_fallback_blocks()
            self.blocks = FALLBACK_BLOCKS
        else:
            self.blocks = tuple(generate_blocks(block_size, True, True))
        self.current_block = None
        self.actions = {
            MOVE: lambda direc, *_: self.move_current(direc),
            ROTATE: lambda direc, *_: self.rotate_current(direc),
            FLIP: lambda direc, *_: self.flip_current(direc),
            SWAP_GRAVITY: lambda *_: self.swap_gravity(),
            DROP: lambda *_: self.drop_current(),
            HURRY: lambda *_: self.hurry_current(),
            UNHURRY: lambda *_: self.unhurry_current(),
            NEW_GAME: lambda *_: self.new_game()
            }

    def start(self):
        self.center_position = tuple(self.controller.board_size[i] // 2
                                     for i in range(2))
        self.start_wait = 800
        self.start_wait_subtract = 1
        self.wait_multiply = 0.99
        self.hurry_wait = 0.1

    def new_game(self):
        self.board = set()
        self.gravity_direction = random.choice((LEFT, RIGHT))
        self.cur_start_wait = self.start_wait
        threading.Thread(target=self._game_loop).start()

    def _game_loop(self):
        while not self.controller.exiting and self.new_block():
            pass
        self.notify(GAME_OVER)

    def run(self):
        pass

    def new_block(self):
        self.current_block = GameBlock(self, random.choice(self.blocks))
        if self.current_block.hits_boundary() \
                or self.current_block.hits_blocks():
            return False
        self.notify(CURRENT_BLOCK_CHANGED, self.current_block)
        self.notify(CURRENT_BLOCK_POSITION_CHANGED, self.current_block)
        t = threading.Thread(target=self._new_timer)
        t.start()
        t.join()
        return True

    def _new_timer(self):
        self.timer = SimpleTimer(self._move_block_autonomously, self._may_run)
        self.timer.start(self.cur_start_wait / 1000.0)

    def _add_current_block_to_board(self):
        for x, y in self.current_block.offset_boxes():
            self.board.add((x, y))
        self.notify(CURRENT_BLOCK_ADDED_TO_BOARD, self.current_block)

    def _check_for_lines(self):
        lines_to_remove = []
        for x in range(self.controller.board_size[0]):
            if all((x, y) in self.board for y in
                   range(self.controller.board_size[1])):
                lines_to_remove.append(x)
        if lines_to_remove:
            self._remove_lines(lines_to_remove)
            self.notify(BOARD_CHANGED, self.board)

    def _remove_lines(self, xs):
        half = self.controller.board_size[0] // 2
        for x in xs:
            if x < half:
                for x_ in range(x, half - 1):
                    for y in range(self.controller.board_size[1]):
                        if (x_ + 1, y) in self.board:
                            self.board.remove((x_ + 1, y))
                            self.board.add((x_, y))
                        else:
                            self.board.discard((x_, y))
                for y in range(self.controller.board_size[1]):
                    self.board.discard((half - 1, y))
            else:
                for x_ in range(x, half + 1, -1):
                    for y in range(self.controller.board_size[1]):
                        if (x_ - 1, y) in self.board:
                            self.board.remove((x_ - 1, y))
                            self.board.add((x_, y))
                        else:
                            self.board.discard((x_, y))
                for y in range(self.controller.board_size[1]):
                    self.board.discard((half + 1, y))

    def _may_run(self):
        return not self.controller.exiting
    
    def _move_block_autonomously(self):
        # Called from timer
        status = self.move_current(self.gravity_direction)
        if status is False:
            self._add_current_block_to_board()
            self._check_for_lines()
            self.cur_start_wait -= self.start_wait_subtract
            if self.cur_start_wait < 100:
                self.cur_start_wait = 100
            return False
        else:
            new_wait = self.timer.wait * self.wait_multiply
            self.timer.set_wait(new_wait)
            return True

    def move_current(self, direction):
        status = self.current_block.move(self.direction_distance[direction])
        if status:
            self.notify(CURRENT_BLOCK_POSITION_CHANGED, self.current_block)
        return status

    def rotate_current(self, direction):
        status = self.current_block.rotate(self.direction_distance[direction])
        if status:
            self.notify(CURRENT_BLOCK_CHANGED, self.current_block)
            self.notify(CURRENT_BLOCK_POSITION_CHANGED, self.current_block)
        return status

    def flip_current(self, direction):
        status = self.current_block.flip(direction)
        if status:
            self.notify(CURRENT_BLOCK_CHANGED, self.current_block)
            self.notify(CURRENT_BLOCK_POSITION_CHANGED, self.current_block)
        return status

    def drop_current(self):
        self.timer.set_temp_wait(0)

    def hurry_current(self):
        self.timer.set_temp_wait(self.hurry_wait)

    def unhurry_current(self):
        self.timer.unset_temp_wait()

    def swap_gravity(self):
        self.gravity_direction = (RIGHT if self.gravity_direction == LEFT
                                  else LEFT)


class LineSlideSurf(pg.Surface):
    def __init__(self, screen, direction=LEFT):
        self.screen = screen
        self.direction = direction or LEFT
        if self.direction == RIGHT:
            self.line_pos = self.game.controller.window_size[0] - 1
            self._update = self._update_right
        elif self.direction == LEFT:
            self._update = self._update_left
        elif self.direction == UP:
            self._update = self._update_up
        elif self.direction == DOWN:
            self.line_pos = self.screen.controller.window_size[1] - 1
            self._update = self._update_down
        else:
            raise GravnoiseError('direction not usable; \
must be either LEFT, RIGHT, UP or DOWN')
        if self.direction in (LEFT, RIGHT):
            self.lines = self.screen.hori_lines
        else:
            self.lines = self.screen.verti_lines
        self._create()

    def _create(self):
        self.surface = pg.Surface(self.screen.controller.window_size).convert()
        self.current_line = self.lines[random.randint(0, 1)]
        self.line_countdown = random.randint(2, 10)

        if self.direction in (LEFT, RIGHT):
            rng = range(self.screen.controller.window_size[0])
            if self.direction == LEFT:
                rng = reversed(rng)
            for i in rng:
                self.surface.blit(self.current_line, (i, 0))
                self._update_vars()
        if self.direction in (UP, DOWN):
            rng = range(self.screen.controller.window_size[1])
            if self.direction == UP:
                rng = reversed(rng)
            for i in rng:
                self.surface.blit(self.current_line, (0, i))
                self._update_vars()

    def update(self):
        self._update()
        self._update_vars()

    def _update_left(self):
        self.surface.blit(self.surface, (1, 0))
        self.surface.blit(self.current_line, (1, 0))

    def _update_right(self):
        self.surface.blit(self.surface, (-1, 0))
        self.surface.blit(self.current_line, (self.line_pos, 0))

    def _update_up(self):
        self.surface.blit(self.surface, (0, 1))
        self.surface.blit(self.current_line, (0, 1))

    def _update_down(self):
        self.surface.blit(self.surface, (0, -1))
        self.surface.blit(self.current_line, (0, self.line_pos))

    def _update_vars(self):
        self.line_countdown -= 1
        if self.line_countdown == 0:
            self.line_countdown = random.randint(2, 10)
            self.current_line = self.lines[0] \
                if self.current_line == self.lines[1] \
                else self.lines[1]

class Screen(Controlled):
    event_actions = {
        pg.KEYDOWN: _untupled_dict(
            (pg.K_UP,    (MOVE, UP)),
            (pg.K_DOWN,  (MOVE, DOWN)),
            (pg.K_LEFT,  (ROTATE, CCW)),
            (pg.K_RIGHT, (ROTATE, CW)),
            (pg.K_x,     (FLIP, X_AXIS)),
            (pg.K_y,     (FLIP, Y_AXIS)),
            (pg.K_SPACE, (SWAP_GRAVITY,)),
            (K_CTRL,     (DROP,)),
            (K_SHIFT,    (HURRY,))
            ),
        pg.KEYUP: _untupled_dict(
            (K_SHIFT,    (UNHURRY,))
            )
        }

    def __init__(self, window_conf=DEFAULT_WINDOW_CONFIGURATION,
                 force_monitor_resize=False, fps=DEFAULT_FPS):
        super().__init__()
        self.window_conf = window_conf or DEFAULT_WINDOW_CONFIGURATION
        self.force_monitor_resize = force_monitor_resize
        self.fps = fps or DEFAULT_FPS

        self.actions = {
            NEW_GAME: lambda *_: self.clear(),
            CURRENT_BLOCK_CHANGED: lambda block, *_:
                self.update_current_block(block),
            CURRENT_BLOCK_POSITION_CHANGED: lambda block, *_:
                self.update_current_block_position(block),
            CURRENT_BLOCK_ADDED_TO_BOARD: lambda block, *_:
                self.add_block_to_board(block),
            BOARD_CHANGED: lambda board, *_:
                self.update_constant_surf(board),
            }

    def start(self):
        pg.display.init()
        flags = pg.DOUBLEBUF
        if self.window_conf == REAL_FULLSCREEN:
            flags |= pg.FULLSCREEN | pg.HWSURFACE
            screen_size = self.get_best_fullscreen_resolution(flags)
        elif self.window_conf == SIMPLE_FULLSCREEN:
            flags |= pg.NOFRAME
            if self.force_monitor_resize:
                screen_size = self.fit_monitor()
            else:
                screen_size = self.get_current_screen_resolution()
        elif self.window_conf == WINDOWED:
            screen_size = self.controller.window_size
        else:
            raise GravnoiseError('window configuration not recognized')
        if not self._covers_window(screen_size):
            raise GravnoiseError('current resolution not large enough')

        if self.window_conf != WINDOWED:
            self.window_offset = tuple((screen_size[i] - self.controller.window_size[i]) // 2
                                       for i in range(2))
        else:
            self.window_offset = (0, 0), (0, 0)
        pg.display.set_caption(__program_name__)
        self.screen = pg.display.set_mode(screen_size, flags)
        self.screen.fill(0)

        self.constant_surface = self._create_full_size_surface()
        self.constant_surface.set_colorkey(0)
        self.temp_surface = self._create_full_size_surface()
        self.temp_surface.set_colorkey(1)
        self.box = pg.Surface(self.controller.box_size).convert()
        self.box.fill(1)

        self.current_event = None
        self.clear()

        self.hori_lines = tuple(
            pg.Surface((1, self.screen.get_size()[1])).convert()
            for i in range(2))
        self.verti_lines = tuple(
            pg.Surface((self.screen.get_size()[0], 1)).convert()
            for i in range(2))
        i = 0
        for color in (0xffffff, 0x999999):
            self.hori_lines[i].fill(color)
            self.verti_lines[i].fill(color)
            i += 1

        d = (UP, DOWN)
        self.slide_surfs = tuple(LineSlideSurf(self, d[i]) for i in range(2))

        self.current_block = None

    def clear(self):
        self.constant_surface.fill(0)

    def run(self):
        clock = pg.time.Clock()
        while not self.controller.exiting:
            for surf in self.slide_surfs:
                surf.update()
            self._get_inputs()
            self._draw()
            clock.tick(self.fps)

    def _get_inputs(self):
        for event in pg.event.get((pg.QUIT, pg.KEYDOWN, pg.KEYUP)):
            if event.type == pg.QUIT:
                self.notify(EXIT)
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.notify(EXIT)
                elif self.controller.game_over:
                    self.notify(NEW_GAME)
                else:
                    act_event = self.event_actions[event.type].get(event.key)
                    if act_event:
                        self.notify(*act_event)
                        if act_event[0] == MOVE:
                            self.current_event = act_event
                            self.current_event_time_target = time.time() \
                                + KEYDOWN_DELAY
            elif event.type == pg.KEYUP:
                act_event = self.event_actions[event.type].get(event.key)
                if act_event:
                    self.notify(*act_event)
                else:
                    act_event = self.event_actions[pg.KEYDOWN].get(event.key)
                    if act_event and act_event == self.current_event:
                        self.current_event = None
        if self.current_event and time.time() >= self.current_event_time_target:
                self.notify(*self.current_event)
                self.current_event_time_target = time.time() + KEYDOWN_DELAY


    def update_current_block(self, cur_block):
        self.current_block = self._create_surface_from_block(cur_block)
        self.current_block.set_colorkey(0)

    def update_current_block_position(self, block):
        self.current_block_pos = tuple(
            block.position[i] * self.controller.box_size[i]
            for i in range(2))
                    
    def add_block_to_board(self, block):
        for pos in block.offset_boxes():
            self.constant_surface.blit(self.box, tuple(pos[i] * self.controller.box_size[i]
                                                       for i in range(2)))

    def update_constant_surf(self, board_boxes):
        self.constant_surface.fill(0)
        for pos in board_boxes:
            self.constant_surface.blit(self.box, tuple(pos[i] * self.controller.box_size[i]
                                                       for i in range(2)))

    def _draw(self):
        self.temp_surface.blit(self.slide_surfs[0].surface, (0, 0))
        self.temp_surface.blit(self.constant_surface, (0, 0))
        if self.current_block:
            self.temp_surface.blit(self.current_block, self.current_block_pos)
        self.screen.blit(self.slide_surfs[1].surface, self.window_offset)
        self.screen.blit(self.temp_surface, self.window_offset)
        pg.display.flip()

    def _create_full_size_surface(self):
        return pg.Surface(self.controller.window_size).convert()

    def _create_surface_from_block(self, block):
            surf = pg.Surface(tuple(
                    block.size[i] * self.controller.box_size[i]
                    for i in range(2)))
            surf.fill(0)
            for pos in block.boxes:
                surf.blit(self.box, tuple(
                        pos[i] * self.controller.box_size[i]
                        for i in range(2)))
            return surf
    
    def _covers_window(self, size):
        return all(size[i] >= self.controller.window_size[i] for i in range(2))
    
    def _blit_white_at(self, p):
        self.screen.blit(self.white_pixel, p)

    def get_current_screen_resolution(self):
        try:
            info = pg.display.Info()
            size = info.current_w, info.current_h
            if size[0] == -1: # in this case, size[1] will also be -1
                raise SDLVersionError(_too_old_for('SDL',
                                                   'resolution detection'))
        except pg.error:
            raise PyGameVersionError(_too_old_for('PyGame',
                                                  'resolution detection'))
        return size

    def get_best_fullscreen_resolution(self, flags):
        for size in reversed(pg.display.list_modes(0, flags)):
            if self._covers_window(size):
                return size
        raise GravnoiseError('no fullscreen resolution large enough')

    def fit_monitor(self):
        '''
        If possible, resize the monitor to the available resolution closest to,
        but not lower than, the window size.
        '''
        self._get_xrandr_info()
        size = self._get_new_monitor_resolution()
        current = self.get_current_screen_resolution()
        monitor_name = self._get_monitor_name()
        if size is None or size == current or monitor_name is None:
            return

        _resize_monitor(size, monitor_name)
        atexit.register(lambda: _resize_monitor(current, monitor_name))
        return size

    def _get_xrandr_info(self):
        try:
            self.xrandr_info = subp.Popen(
                ['xrandr'], stdin=subp.PIPE, stdout=subp.PIPE,
                stderr=subp.PIPE).communicate()[0].decode()
        except OSError:
            self.xrandr_info = None
            self.controller.emit_message(
                'xrandr cannot be found; not changing monitor resolution')
            
    def _get_new_monitor_resolution(self):
        if not self.xrandr_info:
            return
        for size in (tuple(map(int, res)) for res in
                     reversed(re.findall('(\d+)x(\d+)', self.xrandr_info))):
            if self._covers_window(size):
                return size

    def _get_monitor_name(self):
        if not self.xrandr_info:
            return
        m = re.search(r'([\w\d\-]+)\s+connected', self.xrandr_info)
        if not m:
            self.controller.emit_message('cannot find name of current monitor')
            return
        return m.group(1)

class _ExtendedArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        argparse.ArgumentParser.error(self, color_text(message, ERROR_COLOR))
    
def parse_args(args=sys.argv, set_process_title=True):
    parser = _ExtendedArgumentParser(
        description=__program_description__,
        epilog=_fmt('''\
This is the PyGame frontend. No other frontends currently exist.

No scoring system is implemented because such a system is not needed (you will
not want to play this game for long).

Gameplay:
  [Tetris clone.]

Controls:
  Left arrow key:  try to rotate current block counter-clockwise
  Right arrow key: try to rotate current block clockwise
  Down arrow key:  try to move current block downwards
  Up arrow key:    try to move current block upwards
  x key:           try to flip the current block on the x axis
  y key:           try to flip the current block on the y axis
  Space key:       swap gravity
  Ctrl key:        drop current block
  Shift key:       make current block go faster
  Any key:         start a new game (only if the current game is over)

Report bugs to: {__author__}
{__program_name__} home page: <{__home_page__}>\
'''),
        prog=__program_name__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument('--version', action='version',
                        version=__version_long__,
                        help="show program's version information and exit")
    parser.add_argument('-f', '--real-fullscreen', dest='window_conf',
                        action='store_const', const=REAL_FULLSCREEN,
                        help='''
use real, hardware-accelerateable fullscreen. The resolution closest in size
and always equal to or larger the window size will be chosen. This might result
in black borders and a centered game window.
''')
    parser.add_argument('-F', '--simple-fullscreen', dest='window_conf',
                        action='store_const', const=SIMPLE_FULLSCREEN,
                        help='''
use simple, no frame, non-hardware-accelerateable fullscreen (might work in
more cases than --real-fullscreen). This might result in black borders. Does
not change your monitor resolution unless --force-monitor-resize is also
entered.
''')
    parser.add_argument('-M', '--force-monitor-resize', action='store_true',
                        default=False, help='''
If --simple-fullscreen, resize the current monitor to the available resolution
that best fits the window size. Currently, this is not very cross-platform; it
only works on systems where the 'xrandr' program is installed, usable and is in
your $PATH (it probably is if you installed it). It also does not take into
account setups with multiple monitors. This argument is disabled by default.
''')
    parser.add_argument('-w', '--windowed', dest='window_conf',
                        action='store_const', const=WINDOWED,
                        help='run the game in a window (default)')

    parser.add_argument('-X', '--box-width', type=int, action='store',
                        help=_fmt('''
set the width of a block (defaults to {DEFAULT_BOX_SIZE[0]})
'''))
    parser.add_argument('-Y', '--box-height', type=int, action='store',
                        help=_fmt('''
set the height of a block (defaults to {DEFAULT_BOX_SIZE[1]})
'''))
    parser.add_argument('-x', '--window-width', type=int, action='store',
                        help=_fmt('''
set the width of the game window (defaults to {DEFAULT_WINDOW_SIZE[0]}).
Must be a multiple of BOX_WIDTH
'''))
    parser.add_argument('-y', '--window-height', type=int, action='store',
                        help=_fmt('''
set the height of the game window (defaults to {DEFAULT_WINDOW_SIZE[1]}).
Must be a multiple of BOX_HEIGHT
'''))
    parser.add_argument('-p', '--fps', type=int, action='store', help=_fmt('''
set the number of frames per second the game graphics should optimally run at
(defaults to {DEFAULT_FPS}). Does not affect the speed of the game, only the
speed of the graphics and input event fetching.
'''))
    parser.add_argument('-n', '--block-size', type=int,
                        action='store', help=_fmt('''
set the number of boxes a block is to consist of. {__block_description__} If
this argument is not set, __program_name__ falls back on the default 7 Tetris
blocks. Note that if this argument is set, the blocks will be generated
dynamically, which can be slow if n > 7, as the algorithm in use generates all
possible blocks, except for those that are rotated or flipped versions of other
blocks. There are quite a lot of blocks when n gets high.
'''))
    parser.add_argument('-q', '--quiet', dest='verbose', default=True,
                        action='store_false', help='''
do not print anything to standard out
''')

    args = parser.parse_args()
    if args.window_conf is None:
        args.window_conf = WINDOWED
        
    game = Game(block_size=args.block_size)
    screen = Screen(window_conf=args.window_conf,
                    force_monitor_resize=args.force_monitor_resize,
                    fps=args.fps)
    if args.verbose:
        prefix = __program_name__ + ': '
        tw = textwrap.TextWrapper(subsequent_indent=' ' * len(prefix))
        msg_printer = lambda message: print(tw.fill(prefix + message))
    else:
        msg_printer = None
    controller = Controller(
        game=game, screen=screen, message_handler=msg_printer,
        window_size=(args.window_width, args.window_height),
        box_size=(args.box_width, args.box_height))

    if set_process_title:
        setproctitle(__program_name__)
    try:
        controller.start()
    except GravnoiseError as error:
        parser.error(error)
        __import__('traceback').print_exc()

if __name__ == '__main__':
    parse_args()
