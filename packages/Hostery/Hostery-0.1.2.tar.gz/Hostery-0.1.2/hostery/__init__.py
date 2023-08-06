#!/usr/bin/env python
import os
import sys
import json
import tempfile
import shutil
import time

from datetime import datetime
from jinja2 import Template

from Connection import *
from gitutils import *

HOSTERY_CONFIG = '.hostery-config'
HOSTERY_FILE = '.hostery'
HOSTERY_DIR = os.path.dirname(os.path.realpath(__file__))

INDEX_TEMPLATE = os.path.join(HOSTERY_DIR, 'iframe.tmpl')

EXCLUDE_DIRS = ['.git']
EXCLUDE_FILES = ['.gitignore', HOSTERY_FILE, HOSTERY_CONFIG]
DIR = os.getcwd()

def update_index_file(repo_name, commit_data):

  print 'Updating index.html...'

  commit_data = sorted(commit_data.values(),
    key=lambda commit: commit['date'],
    reverse=True)

  def convert_date(commit):
    commit['date'] = datetime.fromtimestamp(commit['date'])

  map(convert_date, commit_data)

  template_file = open(INDEX_TEMPLATE, 'r')
  template = Template(template_file.read())
  html = template.render(commit_data=commit_data, repo_name=repo_name)
  template_file.close()

  temp = tempfile.NamedTemporaryFile(mode='w+t')
  temp.write(html)
  temp.seek(0)
  return temp

def update_history_file(data, branch, commit):

  print 'Updating %s file...'%HOSTERY_FILE

  data[commit] = {
    'date': int(time.time()),
    'branch': branch,
    'commit': commit
  }

  temp = tempfile.NamedTemporaryFile(mode='w+t')
  temp.write(json.dumps(data, indent=2))
  temp.seek(0)

  return temp, data

def get_upload_list(path, prefix):
  r = []
  for root, folders, files in os.walk(path):
    try:
      for i in EXCLUDE_DIRS:
        folders.remove(i)
    except ValueError:
      pass
    for f in files:
      if f in EXCLUDE_FILES:
        continue
      path = os.path.join(root, f)
      relpath = os.path.relpath(path, DIR)
      remotepath = os.path.join(prefix, os.path.split(relpath)[0])
      r.append( (relpath, remotepath) )
  return r

def make_symlink(f, to, temp_dir):
  relpath = os.path.relpath(to, os.path.split(f)[0])
  temp_link = os.path.join(temp_dir, f)
  command('mkdir -p %s'%os.path.split(temp_link)[0])
  command('ln -s %s %s'%(relpath, temp_link))
  return temp_link

def init(ftp=False):

  if not os.path.isdir('.git'):
    print colors.FAIL + 'fatal: Not a git repository' + colors.ENDC
    quit()

  if os.path.isfile(HOSTERY_CONFIG):
    print colors.FAIL + 'fatal: Hostery already configured. Edit or delete %s'%HOSTERY_CONFIG + colors.ENDC
    quit()

  hostery_config = open(HOSTERY_CONFIG, 'wb')

  if ftp:
    data = FTPConnection.GetConfig()
  else:
    data = RsyncConnection.GetConfig()

  hostery_config.write(json.dumps(data, indent=2))
  hostery_config.close()

  git_ignore('.hostery-config')

  print 'Hostery configured! Use "hostery mark" to upload a commit.'

def mark(git=True):

  if not os.path.isfile(HOSTERY_CONFIG):
    print colors.FAIL + 'fatal: Not a configured for hostery. Use "hostery init".' + colors.ENDC
    quit()

  #read hostery file
  hostery_config = open(HOSTERY_CONFIG, 'rb')
  config = json.loads(hostery_config.read())
  hostery_config.close()

  # check if has single revision
  commit_number = get_commit_number()
  if not commit_number:
    quit()

  repo_name = os.path.basename(DIR)
  branch_name = get_branch_name()

  if git:

    if is_git_dirty():
      print colors.FAIL + 'fatal: Can\'t publish a dirty directory.' + colors.ENDC
      quit()

    if is_git_untracked():
      print colors.FAIL + 'fatal: There are untracked files.' + colors.ENDC
      quit()
    
    command('git pull origin %s'%branch_name, verbose=True, return_success=True)

    if is_git_dirty():
      print colors.FAIL + 'Fix merge conflicts.' + colors.ENDC
      quit()

    if not command('git push origin %s'%branch_name, verbose=True, return_success=True):
      quit()

  else: 

      print colors.WARNING + 'Skipping git sync.' + colors.ENDC


  #read hostery config, instantiate connection
  hostery_config = open(HOSTERY_CONFIG, 'rb')
  config = json.loads(hostery_config.read())
  hostery_config.close()

  # make connection
  connection = Connection.FromConfig(config)
  connection.connect()

  # download prev data
  prev_data = json.loads(connection.download(os.path.join(config['root'], '.hostery')) or '{}')

  prev_commit = None
  if prev_data:
    d = sorted(prev_data.values(),
      key=lambda commit: commit['date'],
      reverse=True)
    prev_commit = d[0]['commit']


  # update history file
  temp_history_file, commit_data = update_history_file(prev_data, branch_name, commit_number)

  # update index.html
  temp_index_file = update_index_file(repo_name, commit_data)

  # get files to upload
  upload_prefix = os.path.join(config['root'], branch_name, commit_number)
  upload_list = get_upload_list(DIR, upload_prefix)

  use_symlinks = connection.supports_symlinks() and prev_commit and prev_commit != commit_number

  def do_symlinks(upload_list):

    print '%sPrevious marked commit is %s%s%s%s'%(colors.HEADER, colors.ENDC, colors.OKGREEN, prev_commit, colors.ENDC)
    
    # replace unchanged files with symlinks to corresponding files in older commit
    changed_files = get_changed_files(commit_number, prev_commit)

    if changed_files == False:
      print colors.FAIL + 'Skipping symlink step.' + colors.ENDC
      return

    symlink_dir = tempfile.mkdtemp() # holds symlinks
    def make_symlinks(i):
      if i[0] not in changed_files:
        # print config['root'], branch_name, prev_commit, i[0]
        temp_link = make_symlink(
          os.path.join(config['root'], branch_name, commit_number, i[0]), 
          os.path.join(config['root'], branch_name, prev_commit, i[0]),
          symlink_dir)
        return (temp_link, i[1])
      return i

    return map(make_symlinks, upload_list), symlink_dir

  if use_symlinks:
    upload_list, symlink_dir = do_symlinks(upload_list)

  upload_list.append( (temp_history_file.name, config['root'], HOSTERY_FILE)  )
  upload_list.append( (temp_index_file.name, config['root'], 'index.html') )

  connection.upload(upload_list)

  connection.disconnect()

  # because this is yelling at me in rsync
  try:
    temp_history_file.close()
    temp_index_file.close()
  except:
    pass

  if use_symlinks:
    shutil.rmtree(symlink_dir)

  print 'Done.'

