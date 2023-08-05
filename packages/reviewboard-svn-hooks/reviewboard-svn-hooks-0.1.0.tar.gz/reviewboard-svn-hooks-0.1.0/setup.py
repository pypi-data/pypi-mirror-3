from setuptools import setup, find_packages
import distutils.dir_util
import sys, os

name='reviewboard-svn-hooks'
version = '0.1.0'

conf_file_template = '''
[common]
debug = 0

[reviewboard]
url=
username=
password=

[rule]
min_ship_it_count =
min_expert_ship_it_count =
experts =

'''

def get_os_log_dir():
  platform = sys.platform
  if platform.startswith('win'):
    try:
      return os.environ['APPDATA']
    except KeyError:
      print >>sys.stderr, 'Unspported operation system:%s'%platform
      sys.exit(1)
  return '/var/log'

def get_os_conf_dir():
  platform = sys.platform
  if platform.startswith('win'):
    try:
      return os.environ['ALLUSERSPROFILE']
    except KeyError:
      print 'Unspported operation system:%s'%platform
      sys.exit(1)
  return '/etc'

def mk_conf_path():
  directory = get_os_conf_dir()
  path = os.path.join(directory, name)
  distutils.dir_util.mkpath(path)
  return path

def mk_log_path():
  directory = get_os_log_dir()
  path = os.path.join(directory, name)
  distutils.dir_util.mkpath(path)
  return path

def after_install():
  if len(sys.argv) >= 2 and (sys.argv[1].lower() == 'install' or sys.argv[1].lower() == 'develop'):
    mk_log_path()
    conf_path = mk_conf_path()
    conf_file = os.path.join(conf_path, 'conf.ini')
    if os.path.exists(conf_file):
      return
    with open(conf_file, 'w') as f:
      print >>f, conf_file_template
    
setup(name=name,
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='reviewboard svn subversion hook',
      author='LaiYonghao',
      author_email='mail@laiyonghao.com',
      url='http://code.google.com/p/reviewboard-svn-hooks/',
      license='mit',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      init_used_rid_db = reviewboardsvnhooks.init_used_rid_db:main
      strict_review = reviewboardsvnhooks.strict_review:main
      """,
      )

after_install()

