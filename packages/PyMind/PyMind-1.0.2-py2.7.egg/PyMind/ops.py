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


from mindmeister.auth import AuthToken, getTokenBegin, getTokenEnd, checkToken
from mindmeister.maps import getList, add
import mindmeister.maps

from tempfile import mkstemp
from subprocess import call
from edit import edit_map
import os.path

__token = None

ops = ['list', 'show', 'edit', 'download', 'create', 'delete', 'duplicate', 'rename']

def print_map (map, prefix = ""):
  print prefix + "Map: " + map.title + " created: " + map.created\
      + " last modified: " + map.modified + " id: " + map.id


def get_maps (map):
  maps = getList (__token)
  result = []
  for curr_map in maps:
    if curr_map.id == map:
      return [curr_map]
    if curr_map.title == map:
      result.append (curr_map)
  return result

def maps_select_dialog (maps):
  print "Please specify map (or q) to exit"
  index = 0
  for curr_map in maps:
    print_map (curr_map, "[" + str(index) + "] ")
    index += 1
  while True:
    try:
      cmd = raw_input ("map number>>")
      if cmd == "q":
        return None
      elif cmd.isdigit and int (cmd) < len (maps):
        return maps[int(cmd)].id
      else:
        print "Invalid selection. Try again."
    except KeyboardInterrupt:
      print
      continue
    except EOFError:
      print
      return None


def get_map_id_from_user (map):
  maps = get_maps (map)
  if len(maps) == 1:
    return maps[0].id
  if len(maps) == 0:
    print "None maps found for " + map
    return None
  return maps_select_dialog (maps)

def list():
  '''List all available maps.'''
  result = getList (__token)
  for curr_map in result:
    print_map (curr_map)

def show(map):
  '''Show map as devtodo list.'''
  map_id = get_map_id_from_user (map)
  if map_id == None:
    return
  result = mindmeister.maps.getMap (__token, map_id)
  print_map (result.map)
  file = result.put_to_file ()
  call (['todo', '--database', file, '--sort', '-created'])
  os.remove (file)


def edit(map):
  '''Edit map.'''
  map_id = get_map_id_from_user (map)
  if map_id == None:
    return
  result = mindmeister.maps.getMap (__token, map_id)
  edit_map (result,  __token)

def download(map, file):
  '''Download map as devtodo list to file.'''
  map_id = get_map_id_from_user (map)
  if map_id == None:
    return
  result = mindmeister.maps.getMap (__token, map_id)
  print_map (result.map)
  result.put_to_file (os.path.expanduser (file))
  print "Map " + map + " has been downloaded to " + file

def create():
  '''Create new map on server.'''
  result = add (__token)
  print_map (result)

def delete(map):
  '''Delete map on server.'''
  map_id = get_map_id_from_user (map)
  if map_id == None:
    return
  mindmeister.maps.delete (__token, map_id)
  print "Map successfully deleted"

def duplicate(map):
  '''Duplicate map on server.'''
  map_id = get_map_id_from_user (map)
  if map_id == None:
    return
  result = mindmeister.maps.duplicate (__token, map_id)
  print_map (result)

def rename(map, new_name):
  '''Change map name (root idea title) to new_name'''
  map_id = get_map_id_from_user (map)
  if map_id == None:
    return
  result = mindmeister.maps.getMap (__token, map_id)
  old_name = result.ideas[0].title
  mindmeister.ideas.change (__token, result.ideas[0].id, result.map.id, title = new_name)
  print "Map " + old_name  + " successfully renamed to " + new_name


def login(token, method="delete"):
  if not (token.load () and checkToken (token)):
    frob = getTokenBegin (token, method)
    raw_input("Please login to mindmeister account with your browser and press ENTER")
    getTokenEnd(token, frob)
    token.store ()

  print "Successfully login as " + token.username + " (" + token.fullname + ")"
  global __token
  __token = token


def get_name():
  return __token.fullname
