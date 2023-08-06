'''
Copyright 2012 Alexey Kravets  <mr.kayrick@gmail.com>

This file is part of PyMind.

PyMind is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyMind is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyMind.  If not, see <http://www.gnu.org/licenses/>.
'''

import curses

def get_str(idea, offset, num):
  return "  " * offset + str(num) + "." + idea.title

def print_idea(idea, offset, num):
  print get_str(idea, offset, num)
  for index,item in enumerate(idea.ideas):
    print_idea (item, offset + 1, index + 1)

def print_map(data):
  print_idea (data.ideas[0], 0, 1)


def print_idea_curses(idea, offset, num, stdsrc, current):
  line = get_str (idea, offset, num) + "\n"
  if idea == current:
    stdsrc.addstr (line, curses.A_BOLD)
  else:
    stdsrc.addstr (line)
  for index,item in enumerate(idea.ideas):
    print_idea_curses (item, offset + 1, index + 1, stdsrc, current)

def print_curses(data, stdsrc, current):
  print_idea_curses (data.ideas[0], 0, 1, stdsrc, current)
