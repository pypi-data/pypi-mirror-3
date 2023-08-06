==============
Scrapy recipes
==============


s01.scrapy:scrapy
-----------------------

The crawl recipe allows us to set the project settings for a given spider
package. All given settings will get set as environment variables and override
existing global or local package settings.


Options
~~~~~~~

The 'scrapy' recipe accepts the following options:

eggs
  The names of one or more eggs, with their dependencies that should
  be included in the Python path of the generated scripts.

module
  The ``module`` which contains the ``method`` to be executed. This isby default
  set to scrapy.cmdline. You only need to change this if you like to call
  another method from another module then scrapy.cmdline.

method
  The ``method`` which get called from the ``module``. This is by default
  set to execute. You only need to change this if you like to call another
  method then execute which is only the case if you doen't use the
  scrapy.cmdline.execute implementation.

arguments
  Optional cmdline execute method ``arguments`` e.g. 
  ``['scrapy', 'crawl', 'google.org']``. If not set the scrapy command 
  ``['scrapy']`` get used as default argument

settings
  A scrapy configuration file which get used as settings. This variables
  will override the existing global and local settings.


scrapy script
~~~~~~~~~~~~~

Lets define a egg that we can use in our application:

  >>> mkdir('hello')
  >>> write('hello', 'setup.py',
  ... '''
  ... from setuptools import setup
  ... setup(name='hello')
  ... ''')

And let's define a python module which we use for our test. Note, this is just
a dummy package this is normaly your spider package:

  >>> write('hello', 'default.py',
  ... """
  ... BOT_NAME = 'mybot'
  ... BOT_VERSION = '1.0'
  ... """)

Alos add a `__init__` to the `hello` package:

  >>> write('hello', '__init__.py', '#make package')

We'll create a `buildout.cfg` file that defines our script:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... develop = hello
  ... parts = scrapy crawl list
  ... newest = false
  ...
  ... [scrapy]
  ... recipe = s01.scrapy:scrapy
  ... eggs = hello
  ... settings = hello/default.py
  ...
  ... [crawl]
  ... recipe = s01.scrapy:crawl
  ... eggs = hello
  ... settings = hello/default.py
  ...
  ... [list]
  ... recipe = s01.scrapy:list
  ... eggs = hello
  ... settings = hello/default.py
  ...
  ... ''' % globals())

Let's run buildout again:

  >>> print system(join('bin', 'buildout')),
  Develop: '/sample-buildout/hello'
  Installing scrapy.
  s01.worker: Load settings from path /sample-buildout/hello/default.py
  Generated script '/sample-buildout/bin/scrapy'.
  Installing crawl.
  s01.worker: Load settings from path /sample-buildout/hello/default.py
  Generated script '/sample-buildout/bin/crawl'.
  Installing list.
  s01.worker: Load settings from path /sample-buildout/hello/default.py
  Generated script '/sample-buildout/bin/list'.

scrapy
------

If you check the bin/scrapy script, you can see that we inject our settings
given from the default.py file as scrapy.settings.overrides variables:

  >>> cat('bin', 'scrapy')
  <BLANKLINE>
  import sys
  sys.path[0:0] = [
      '/sample-buildout/hello',
      ]
  <BLANKLINE>
  <BLANKLINE>
  import os
  sys.argv[0] = os.path.abspath(sys.argv[0])
  <BLANKLINE>
  import scrapy.conf
  # fake inproject marker
  scrapy.conf.settings.settings_module = True
  # settings overrides
  scrapy.conf.settings.overrides['BOT_VERSION'] = '1.0'
  scrapy.conf.settings.overrides['BOT_NAME'] = 'mybot'
  <BLANKLINE>
  <BLANKLINE>
  import s01.scrapy.cmdline
  <BLANKLINE>
  if __name__ == '__main__':
      s01.scrapy.cmdline.execute(['scrapy'])

crawl
-----

If you check the bin/crawl script, you can see that we inject our settings
given from the default.py file as scrapy.settings.overrides variables:

  >>> cat('bin', 'crawl')
  <BLANKLINE>
  import sys
  sys.path[0:0] = [
      '/sample-buildout/hello',
      ]
  <BLANKLINE>
  <BLANKLINE>
  import os
  sys.argv[0] = os.path.abspath(sys.argv[0])
  <BLANKLINE>
  import scrapy.conf
  # fake inproject marker
  scrapy.conf.settings.settings_module = True
  # settings overrides
  scrapy.conf.settings.overrides['BOT_VERSION'] = '1.0'
  scrapy.conf.settings.overrides['BOT_NAME'] = 'mybot'
  <BLANKLINE>
  <BLANKLINE>
  import s01.scrapy.cmdline
  <BLANKLINE>
  if __name__ == '__main__':
      s01.scrapy.cmdline.execute(['scrapy', 'crawl'])


list
----

If you check the bin/list script, you can see that we inject our settings
given from the default.py file as scrapy.settings.overrides variables:

  >>> cat('bin', 'list')
  <BLANKLINE>
  import sys
  sys.path[0:0] = [
      '/sample-buildout/hello',
      ]
  <BLANKLINE>
  <BLANKLINE>
  import os
  sys.argv[0] = os.path.abspath(sys.argv[0])
  <BLANKLINE>
  import scrapy.conf
  # fake inproject marker
  scrapy.conf.settings.settings_module = True
  # settings overrides
  scrapy.conf.settings.overrides['BOT_VERSION'] = '1.0'
  scrapy.conf.settings.overrides['BOT_NAME'] = 'mybot'
  <BLANKLINE>
  <BLANKLINE>
  import s01.scrapy.cmdline
  <BLANKLINE>
  if __name__ == '__main__':
      s01.scrapy.cmdline.execute(['scrapy', 'list'])


test script
~~~~~~~~~~~

The scrapy test script allows to setup a test environment based on the
zope.testrunner. The recipe allows to define a settings section which get used
additional to the zope.testing setup.
