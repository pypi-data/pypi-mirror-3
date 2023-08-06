from subprocess import call
from subprocess import check_output
import curses
import locale
import os
from mindmeister.ideas import insert, delete, change, move
from mindmeister.maps import undo as map_undo
from mindmeister.maps import redo as map_redo
from mindmeister.diagnostic import MindException

def get_position(win):
  win.addstr ("Position (optional) [x_pos y_pos] >> ")
  curses.echo()
  result = win.getstr().rstrip()
  curses.noecho()
  while 1:
    if len(result) == 0:
      return None
    pos = result.split()
    if len (pos) != 2:
      win.addstr ("Invalid pos format")
      continue
    try:
      return map (lambda item: int(item), pos)
    except ValueError:
      win.addstr ("Can not parse number")
      continue

def select_idea (win, message, idea):
  win.addstr (message)
  curses.echo()
  result = win.getstr().rstrip()
  curses.noecho()
  if result == 'q':
    return None
  indices = result.split('.')
  if len (indices) == 0:
    return None
  try:
    for index in indices:
      index = int(index) - 1
      idea = idea.ideas [index]
    return idea.id
  except ValueError:
    win.addstr ("Can not parse number")
    return None
  except IndexError:
    win.addstr ("Invalid selection")
    return None

def get_name (win, message):
  win.addstr (message)
  curses.echo()
  result = win.getstr().rstrip()
  curses.noecho()
  if len (result) == 0:
    return None
  return result

def print_help (win, map, token):
  '''Print help'''
  win.clear ()
  win.addstr (0, 0, "Commands list\n")
  for key,action in __mapping.items():
    win.addstr (key + " - " + action.__doc__  + '\n')

  win.addstr ('q' + " - " + 'quit'  + '\n')
  win.refresh ()
  win.getch ()
  return False

def add_node (win, map, token):
  '''Add new node to map'''
  idea = select_idea (win, "Parent idea:", map)
  if idea == None:
    win.getch()
    return False
  name = get_name (win, "Idea title:")
  if name == None:
    return False
  pos = get_position (win)
  if pos != None:
    args = {'x_pos' : pos[0], 'y_pos' : pos [1]}
  else:
    args = {}
  insert (token, map.map.id, idea, name, **args)
  return True

def delete_node (win, map, token):
  '''Delete node from map'''
  idea = select_idea (win, "Idea to delete:", map)
  if idea == None:
    win.getch()
    return False
  delete (token, idea, map.map.id)
  return True

def edit_node (win, map, token):
  '''Edit existing node'''
  idea = select_idea (win, "Idea to edit:", map)
  if idea == None:
    win.getch()
    return False
  name = get_name (win, "New title:")
  if name == None:
    return False
  change (token, idea, map.map.id, title = name)
  return True

def reparent_node (win, map, token):
  '''Change the parent of the existing node'''
  idea = select_idea (win, "Idea to reparent:", map)
  if idea == None:
    win.getch()
    return False
  new_parent = select_idea (win, "New parent:", map)
  if new_parent == None:
    win.getch()
    return False
  move (token, idea, map.map.id, new_parent, 0)
  return True

def undo (win, map, token):
  '''Undo last operation'''
  map_undo (token, map.map.id)
  return True

def redo (win, map, token):
  '''Redo operation'''
  map_redo (token, map.map.id)
  return True

__mapping = {'h' : print_help, 'a' : add_node,\
    'd' : delete_node, 'e' : edit_node, 'r': reparent_node,\
    'u' : undo, 'y' : redo}

def edit_map (map, token):
  locale.setlocale(locale.LC_ALL,"")
  stdscr = curses.initscr()
  curses.noecho()
  file = map.put_to_file ()
  while 1:
    try:
      data = check_output (['todo', '--database', file, '--sort', '-created'])
      stdscr.addstr (0, 0, data)
      stdscr.refresh()
      cmd = chr(stdscr.getch())
      if cmd == 'q':
        break
      if not __mapping.has_key (cmd):
        stdscr.addstr("\n\nInvalid command, use 'h' to obtain the list of the available commands")
        continue
      if __mapping[cmd](stdscr, map, token):
        map.update (token)
        file = map.put_to_file (file)
    except KeyboardInterrupt:
      break
    except MindException as err:
      stdscr.addstr (str(err))
      stdscr.getch ()
    except EOFError:
      break
    stdscr.clear ()
  curses.echo()
  curses.endwin()
  os.remove (file)
