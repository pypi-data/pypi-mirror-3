#!/usr/bin/env python
import ftplib
import os
import sys
import getpass
import json
import tempfile
import time

from datetime import datetime
from jinja2 import Template

HOSTERY_CONFIG = '.hostery-config'
HOSTERY_FILE = '.hostery'
HOSTERY_DIR = os.path.dirname(os.path.realpath(__file__))

INDEX_TEMPLATE = os.path.join(HOSTERY_DIR, 'iframe.tmpl')

EXCLUDE_DIRS = ['.git']
EXCLUDE_FILES = ['.gitignore', HOSTERY_FILE, HOSTERY_CONFIG]
DIR = os.getcwd()

def update_index_file(repo_name, commit_data):

  print "Updating index.html..."

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

  print "Updating %s file..."%HOSTERY_FILE

  data[commit] = {
    'date': int(time.time()),
    'branch': branch,
    'commit': commit
  }

  temp = tempfile.NamedTemporaryFile(mode='w+t')
  temp.write(json.dumps(data, indent=2))
  temp.seek(0)

  return temp, data

def command(cmd, verbose=False):
  if verbose:
    print cmd
  p = os.popen(cmd)
  s = p.readline().strip()
  if verbose:
    print s
  return s, p.close() == None

def is_git_dirty():
  return '*' == command('[[ $(git diff --shortstat 2> /dev/null | tail -n1) != "" ]] && echo "*"')[0]

def is_git_untracked():
  return 0 < len(command('git ls-files . --exclude-standard --others')[0])

def get_commit_number():
  line = command('git rev-parse --verify HEAD')[0][:7]
  if line == 'fatal: Needed a single revision':
    return False
  return line

def get_branch_name():
  return command('git branch | grep "*" | sed "s/* //"')[0]

def get_repo_name():
  return DIR.split('/')[-1]

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
      s = "%s/%s"%(root, f)
      s = s.replace(DIR+'/', '')
      dirs = s.split('/')[:-1]
      s = (prefix + dirs, s)
      r.append(s)
  return r

def ftp_cwd(ftp, *args):
  for d in args:
    try:
      ftp.cwd(d)
    except:
      ftp.mkd(d)
      ftp.cwd(d)

def ftp_upload(ftp, fullname):
  if not isinstance(fullname, basestring):
    name = fullname[1]
    fullname = fullname[0]
  else:
    name = os.path.split(fullname)[1]
  f = open(fullname, "rb")
  ftp.storbinary('STOR ' + name, f)
  f.close()
  print "Uploaded ", fullname

def ftp_upload_list(ftp, root='', upload_list=[]):

  print "Beginning FTP upload..."

  for u in upload_list:
    ftp_cwd(ftp, *u[0])
    ftp_upload(ftp, u[1])
    ftp_cwd(ftp, '/%s'%root) # move back up to root

def ftp_download(ftp, path=[], filename='', default_content=''):
  ftp_cwd(ftp, *path)
  lines = []
  try:
    ftp.retrlines('RETR ' + filename, lines.append)
    return "\n".join(lines)
  except:
    print 'No file "%s" at remote path.'%filename
    return default_content

def init():

  if not os.path.isdir('.git'):
    print "fatal: Not a git repository"
    quit()

  if os.path.isfile(HOSTERY_CONFIG):
    print "fatal: Hostery already configured. Edit or delete %s"%HOSTERY_CONFIG
    quit()

  hostery_config = open(HOSTERY_CONFIG, 'wb')
  data = {
    'host': raw_input('FTP Host: '),
    'root': raw_input('FTP Root: '),
    'login': raw_input('FTP Login: '),
    'port': int(raw_input('FTP Port: '))
  }
  hostery_config.write(json.dumps(data, indent=2))
  hostery_config.close()

  print "Hostery configured! Use \"hostery mark\" to upload a commit."

def mark(git=True):

  if not os.path.isfile(HOSTERY_CONFIG):
    print "fatal: Not a configured for hostery. Use \"hostery init\"."
    quit()

  #read hostery file
  hostery_config = open(HOSTERY_CONFIG, 'rb')
  config = json.loads(hostery_config.read())
  hostery_config.close()

  # check if has single revision
  commit_number = get_commit_number()
  if not commit_number:
    quit()

  repo_name = get_repo_name()
  branch_name = get_branch_name()

  if git:

    if is_git_dirty():
      print "fatal: Can't publish a dirty directory."
      quit()

    if is_git_untracked():
      print "fatal: There are untracked files."
      quit()

    # todo check for remote origin, warn if doesn't exist and skip git stuff.

    # pull and pause for git issues
    if not command('git pull origin %s'%branch_name, verbose=True)[1] or is_git_dirty():
      quit()

    if not command('git push origin %s'%branch_name, verbose=True)[1]:
      quit()


  #read hostery config
  hostery_config = open(HOSTERY_CONFIG, 'rb')
  config = json.loads(hostery_config.read())
  hostery_config.close()

  # get files to upload
  upload_prefix = [branch_name, commit_number]
  upload_list = get_upload_list(DIR, upload_prefix)

  # todo: init ftp connection
  print "Logging in to %s as %s..."%(config['host'], config['login'])
  ftp = ftplib.FTP()
  ftp.connect(config['host'], config['port'])
  print ftp.getwelcome()

  ftp.login(config['login'], getpass.getpass("Password: "))

  # download prev data from FTP
  prev_data = ftp_download(ftp,
    path=[config['root']],
    filename='.hostery',
    default_content='{}')
  prev_data = json.loads(prev_data)

  # update history file
  temp_history_file, commit_data = update_history_file(prev_data, branch_name, commit_number)

  # update index.html
  temp_index_file = update_index_file(repo_name, commit_data)

  upload_list.append( ( [ ], (temp_history_file.name, HOSTERY_FILE ) ) )
  upload_list.append( ( [ ], (temp_index_file.name, 'index.html') ) )

  # upload the files
  ftp_cwd(ftp, '/%s'%config['root']) # move ftp session back up to root
  ftp_upload_list(ftp, root=config['root'], upload_list=upload_list)

  print "Logging out..."

  ftp.quit()

  temp_history_file.close()
  temp_index_file.close()

  print "Done."

