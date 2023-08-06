import curses
import locale
import map_print
from mindmeister.ideas import insert, delete, change, move
from mindmeister.maps import undo as map_undo
from mindmeister.maps import redo as map_redo
from mindmeister.maps import getMap
from mindmeister.diagnostic import MindException

__idea_to_reparent = None

def get_position(win):
  curr_pos = win.getyx()
  while 1:
    win.addstr (curr_pos[0], curr_pos[1], "Position (optional) [x_pos y_pos] >> ")
    win.clrtobot()
    curses.echo()
    result = win.getstr().rstrip()
    curses.noecho()
    if len(result) == 0:
      return None
    pos = result.split()
    if len (pos) != 2:
      win.addstr ("Invalid pos format")
      win.getch()
      continue
    try:
      return map (lambda item: int(item), pos)
    except Exception:
      win.addstr ("Can not parse number")
      win.getch()
      continue

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
    win.addstr (chr(key) + " - " + action.__doc__  + '\n')

  win.addstr ('q' + " - " + 'quit'  + '\n')
  win.addstr ('CTLR+C' + " - " + 'break current operation'  + '\n')
  win.addstr ('Up' + " - " + 'go to the previous idea'  + '\n')
  win.addstr ('Down' + " - " + 'go to the next idea'  + '\n')
  win.addstr ('Right' + " - " + 'go to the first child idea'  + '\n')
  win.addstr ('Right' + " - " + 'go to the parent idea'  + '\n')
  win.refresh ()
  win.getch ()
  return False

def add_node (win, map, idea, token):
  '''Add new node to map'''
  name = get_name (win, "Idea title:")
  if name == None:
    return False
  pos = get_position (win)
  if pos != None:
    args = {'x_pos' : pos[0], 'y_pos' : pos [1]}
  else:
    args = {}
  insert (token, map.map.id, idea.id, name, **args)
  return True

def delete_node (win, map, idea, token):
  '''Delete node from map'''
  delete (token, idea.id, map.map.id)
  return True

def edit_node (win, map, idea, token):
  '''Edit existing node'''
  name = get_name (win, "New title:")
  if name == None:
    return False
  change (token, idea.id, map.map.id, title = name)
  return True

def reparent_node (win, map, idea, token):
  '''Change the parent of the existing node'''
  global __idea_to_reparent
  if __idea_to_reparent == None:
    __idea_to_reparent = idea
    return False
  move (token, __idea_to_reparent.id, map.map.id, idea.id, 0)
  __idea_to_reparent = None
  return True

def undo (win, map, idea, token):
  '''Undo last operation'''
  map_undo (token, map.map.id)
  return True

def redo (win, map, idea, token):
  '''Redo operation'''
  map_redo (token, map.map.id)
  return True

__mapping = {
    ord('h') : print_help,\
    ord('a') : add_node,\
    ord('d') : delete_node,\
    ord('e') : edit_node,\
    ord('r'): reparent_node,\
    ord('u') : undo,\
    ord('y') : redo}

def update_map (map, token):
  new = getMap (token, map.map.id)
  map.map = new.map
  map.ideas = new.ideas

def edit_map (map, token):
  global __idea_to_reparent
  locale.setlocale(locale.LC_ALL,"")
  stdscr = curses.initscr()
  curses.noecho()
  stdscr.keypad(1)

  index = [0]
  curr = map.ideas[index[-1]]

  try:
    while 1:
      try:
        stdscr.clear()
        map_print.print_curses (map, stdscr, curr)
        if __idea_to_reparent != None:
          stdscr.addstr("\nPlease select new parent and press 'r'")

        cmd = stdscr.getch()
        if cmd == ord('q'):
          break

        if cmd == curses.KEY_LEFT:
          if curr.parent:
            curr = curr.int_parent
            index.pop()
          continue

        if cmd == curses.KEY_RIGHT:
          if len(curr.ideas) > 0:
            curr = curr.ideas[0]
            index.append (0)
          continue

        if cmd == curses.KEY_UP:
          if curr.int_parent and index[-1] > 0:
            index[-1] -= 1
            curr = curr.int_parent.ideas [index[-1]]
          continue

        if cmd == curses.KEY_DOWN:
          if curr.int_parent and index[-1] + 1 < len(curr.int_parent.ideas):
            index[-1] += 1
            curr = curr.int_parent.ideas [index[-1]]
          continue

        if __idea_to_reparent != None:
          if cmd != ord('r'):
            continue

        if not __mapping.has_key (cmd):
          stdscr.addstr("\nInvalid command, use 'h' to obtain the list of the available commands")
          continue
        if __mapping[cmd](stdscr, map, curr, token):
          update_map (map, token)
          last = index.pop()
          curr = reduce (lambda idea, offset: idea.ideas[offset], index, map)
          if last < len (curr.ideas):
            index.append (last)
            curr = curr.ideas[last]

      except MindException as err:
        stdscr.addstr (str(err))
        stdscr.getch ()
      except KeyboardInterrupt:
        pass
      stdscr.clear ()
  except EOFError:
    pass
  finally:
    curses.echo()
    curses.endwin()
