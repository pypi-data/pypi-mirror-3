import os
import subprocess 

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def command(cmd, verbose=False, return_success=False, multiline=False):
  
  if verbose:
    print colors.OKBLUE + cmd + colors.ENDC

  if multiline:
    cmd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    s = []
    for line in cmd.stdout:
      line = line.strip()
      if line != '':
        s.append(line) 
  else:
    p = os.popen(cmd)
    s = p.readline().strip()

  if verbose:
    print s

  if return_success:
    return p.close() == None
  return s
  
def is_git_dirty():
  return '*' == command('[[ $(git diff --shortstat 2> /dev/null | tail -n1) != "" ]] && echo "*"')

def is_git_untracked():
  return 0 < len(command('git ls-files . --exclude-standard --others'))

def get_controlled_files():
  return command('git ls-tree -r master | cut -f2', multiline=True)

def git_ignore(pattern):
  command('touch .gitignore')
  with open('.gitignore', 'r') as f:
    ignored = f.read().split('\n')
  if not pattern in ignored:
    with open('.gitignore', 'a') as f:
      f.write('\n'+pattern)

def get_commit_number():
  line = command('git rev-parse --verify HEAD')[:7]
  if line == 'fatal: Needed a single revision':
    return False
  return line

def get_branch_name():
  return command('git branch | grep "*" | sed "s/* //"')

def get_changed_files(commit, prev):
  cmd = 'git diff --name-only %s %s'%(commit, prev)
  if command(cmd, return_success=True):
    return command(cmd, multiline=True)
  else:
    return False