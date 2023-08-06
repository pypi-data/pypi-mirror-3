import ftplib
import tempfile
import getpass
import shutil
import os

from gitutils import command, colors

class Connection():
  @staticmethod
  def FromConfig(config):
    if 'port' in config:
      return FTPConnection(config)
    else:
      return RsyncConnection(config)

class RsyncConnection(Connection):

  def __init__(self, config):
    self.config = config

  @staticmethod
  def GetConfig():
    return {
      'host': raw_input('Host: '),
      'root': raw_input('Root: '),
      'login': raw_input('User: ')
    }

  def connect(self):
    pass

  def disconnect(self):
    pass

  def upload(self, upload_list):

    # print colors.HEADER + 'Creating upload directory ...' + colors.ENDC

    common = os.path.commonprefix([i[1] for i in upload_list])
    temp_dir = tempfile.mkdtemp()

    for i in upload_list:
      base = os.path.relpath(i[1], common)
      base = os.path.join(temp_dir, base)
      command('mkdir -p %s'%base)
      command('cp -a %s %s'%(i[0], base))
      
      loc = os.path.join(base, os.path.split(i[0])[1])

      command('chmod 644 %s'%loc) # this became necessary all of a sudden?

      if len(i) == 3:
        new = os.path.join(os.path.abspath(base), i[2])
        command('mv %s %s'%(loc, new))

    command('rsync -lrz %s/ %s@%s:~/%s'%(temp_dir, self.config['login'], self.config['host'], self.config['root']), verbose=False)

    shutil.rmtree(temp_dir)


  def download(self, filename):

    temp_dir = tempfile.mkdtemp()

    # print 'Downloading %s ...'%filenameh

    if not command('rsync -lrz %s@%s:~/%s %s'%(self.config['login'], self.config['host'], filename, temp_dir), verbose=False, return_success=True):
      return None
    with open(os.path.join(temp_dir, os.path.split(filename)[1]), 'rb') as f:
      contents = f.read()
    shutil.rmtree(temp_dir)
    return contents

  def supports_symlinks(self):
    return True


class FTPConnection(Connection):

  def __init__(self, config):
    self.config = config

  @staticmethod
  def GetConfig():
    return {
      'host': raw_input('Host: '),
      'root': raw_input('Root: '),
      'login': raw_input('User: '),
      'port': int(raw_input('Port: '))
    }

  def connect(self):
    print 'Logging in to %s as %s...'%(self.config['host'], self.config['login'])
    self.ftp = ftplib.FTP()
    self.ftp.connect(self.config['host'], self.config['port'])
    print self.ftp.getwelcome()
    self.ftp.login(self.config['login'], getpass.getpass('Password: '))

  def disconnect(self):
    print 'Logging out...'
    self.ftp.quit()

  def upload(self, upload_list):
    print 'Beginning FTP upload ...'
    for u in upload_list:
      self.__cwd(*u[1].split(os.sep))
      
      if len(u) == 3:
        self.__upload(u[0], u[2])
      else:
        self.__upload(u[0])

      self.__cwd('/') # move back up to root

  def download(self, filename):
    self.__cwd('/') # move back up to root
    lines = []
    try:
      self.ftp.retrlines('RETR ' + filename, lines.append)
      return '\n'.join(lines)
    except:
      print 'No file "%s" at remote path.'%filename
      return None

  def supports_symlinks(self):
    return False

  def __cwd(self, *args):
    for d in args:
      try:
        # print 'Moving to', d
        self.ftp.cwd(d)
      except Exception as e:
        # print e
        self.ftp.mkd(d)
        self.ftp.cwd(d)

  def __upload(self, fullname, name=None):
    if not name:
      name = os.path.split(fullname)[1]
    with open(fullname, 'rb') as f:
      self.ftp.storbinary('STOR ' + name, f)
      f.close()
    print 'Uploaded ', fullname
