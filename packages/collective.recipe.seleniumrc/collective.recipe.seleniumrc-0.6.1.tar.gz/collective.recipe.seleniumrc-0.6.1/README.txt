*******************************
Download recipe for Selenium RC
*******************************

This package downloads and installs Selenium RC using zc.buildout. It is based
on hexagonit.recipe.download.

buildout.cfg example::

  [buildout]
  parts = seleniumrc

  [seleniumrc]
  recipe = collective.recipe.seleniumrc

If no options are specified, the recipe downloads from
http://selenium.googlecode.com/files/selenium-server-standalone-2.0rc2.jar .

A control script is created based on the part name. In the case above, the
control script created is ``bin/seleniumrc``.

FYI, there is the Python ``selenium`` module which allows to control Selenium RC.

  http://pypi.python.org/pypi/selenium

The recipe let you also choose the exact version of Selenium RC to be used::

  [buildout]
  parts = seleniumrc

  [seleniumrc]
  recipe = collective.recipe.seleniumrc
  url = http://selenium.googlecode.com/files/selenium-server-standalone-2.0rc1.jar
  md5sum = 19ac13b18cdc6840dd32678215d38e1b

In case you still need to use Selenium RC 1.x, you need to ask
explicitely to unzip the download::

  [buildout]
  parts = seleniumrc

  [seleniumrc]
  recipe = collective.recipe.seleniumrc
  url = http://selenium.googlecode.com/files/selenium-remote-control-1.0.3.zip
  md5sum = 8935cc7fe4dde2fd2a95ddd818e7493b
  download-only = false

Sometimes, you may want to use another Java executable::

  [buildout]
  parts = seleniumrc

  [seleniumrc]
  recipe = collective.recipe.seleniumrc
  java-cmd = /home/www/java/bin/java

To suppress all default values (e.g., to install without verifying the MD5
checksum), use the 'no-defaults' option::

  [buildout]
  parts = seleniumrc

  [seleniumrc]
  recipe = collective.recipe.seleniumrc
  url = http://selenium.googlecode.com/files/selenium-remote-control-1.0.3.zip
  java-cmd = /home/www/java/bin/java
  no-defaults = True

License
-------

Open Source License - Zope Public License v2.1


