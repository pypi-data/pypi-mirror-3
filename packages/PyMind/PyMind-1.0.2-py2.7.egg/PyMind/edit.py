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

def select_example (idea):
  max_depth = 3
  depth = 1
  result = "1"
  while len (idea.ideas) > 0 and depth <= max_depth:
    idea = idea.ideas[0];
    result += ".1"
  return result + " for " + idea.title + " for example"

def show_select_map(win, body, curr, message, indices, index):
  offset = curr.offset
  before = '\n'.join(body[0:offset])
  if before != '':
    before += '\n'
  exact = body[offset] + '\n'
  after = '\n'.join(body[offset+1:])
  win.clear ()
  win.addstr (0, 0, before)
  win.addstr (exact, curses.A_BOLD)
  win.addstr (after)
  user_indices = map (lambda item: str(item), indices)
  if index > 0:
    user_indices.append (str(index))
  else:
    user_indices.append ("")
  win.addstr (message + '.'.join(user_indices))


def get_input_idea(win, idea, body, message):
  curr = idea.ideas[0]
  indices = [1]
  index = 0
  body = body.split('\n')
  while True:
    if index != 0:
      result = curr.ideas[index - 1]
    else:
      result = curr
    show_select_map(win, body, result, message, indices, index)
    cmd = win.getch()
    if cmd == 127:
      if index == 0: #Last element was dot
        if len (indices) == 1: #Always keep first idea
          continue
        curr = curr.int_parent
        index = indices.pop()
      else:
        index /= 10
      continue
    cmd = chr(cmd)
    if cmd == '\n':
      break
    if cmd == '.' and index > 0:
      curr = curr.ideas[index - 1]
      indices.append (index)
      index = 0
      continue
    if not cmd.isdigit():
      continue
    tmp_index = index * 10 + int(cmd)
    if tmp_index > len(curr.ideas):
      continue
    index = tmp_index
  win.addstr ('\n')
  return result

def select_idea (win, message, idea, body):
  try:
    result = get_input_idea (win, idea, body, message + " (" + select_example (idea.ideas[0]) + "):")
  except KeyboardInterrupt:
    result = None
  if result == None:
    return None
  return result.id

def get_name (win, message):
  win.addstr (message)
  curses.echo()
  result = win.getstr().rstrip()
  curses.noecho()
  if len (result) == 0:
    return None
  return result

def print_help (win, map, token, data):
  '''Print help'''
  win.clear ()
  win.addstr (0, 0, "Commands list\n")
  for key,action in __mapping.items():
    win.addstr (key + " - " + action.__doc__  + '\n')

  win.addstr ('q' + " - " + 'quit'  + '\n')
  win.refresh ()
  win.getch ()
  return False

def add_node (win, map, token, data):
  '''Add new node to map'''
  idea = select_idea (win, "Parent idea", map, data)
  if idea == None:
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

def delete_node (win, map, token, data):
  '''Delete node from map'''
  idea = select_idea (win, "Idea to delete", map, data)
  if idea == None:
    return False
  delete (token, idea, map.map.id)
  return True

def edit_node (win, map, token, data):
  '''Edit existing node'''
  idea = select_idea (win, "Idea to edit", map, data)
  if idea == None:
    return False
  name = get_name (win, "New title:")
  if name == None:
    return False
  change (token, idea, map.map.id, title = name)
  return True

def reparent_node (win, map, token, data):
  '''Change the parent of the existing node'''
  idea = select_idea (win, "Idea to reparent", map, data)
  if idea == None:
    return False
  new_parent = select_idea (win, "New parent", map, data)
  if new_parent == None:
    return False
  move (token, idea, map.map.id, new_parent, 0)
  return True

def undo (win, map, token, data):
  '''Undo last operation'''
  map_undo (token, map.map.id)
  return True

def redo (win, map, token, data):
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
      if __mapping[cmd](stdscr, map, token, data):
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
