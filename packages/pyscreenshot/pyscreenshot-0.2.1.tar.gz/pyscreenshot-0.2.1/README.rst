The ``pyscreenshot`` module can be used to copy
the contents of the screen to a PIL_ image memory or file.
Replacement for the ImageGrab_ Module, which works on Windows only.

Links:
 * home: https://github.com/ponty/pyscreenshot
 * documentation: http://ponty.github.com/pyscreenshot

Features:
 * Crossplatform wrapper
 * Capturing the whole desktop
 * Capturing an area
 * saving to file or PIL_ image memory
 * some backends are based on this discussion: http://stackoverflow.com/questions/69645/take-a-screenshot-via-a-python-script-linux
 * Plugin based, it has wrappers for various backends:
     * scrot_ 
     * ImageMagick_
     * PyGTK_ 
     * PIL_ (only on windows)
     * PyQt4_
     * wxPython_
 
Known problems:
 * not implemented: Capturing an active window
 * different backends generate slightly different images from the same desktop,
   this should be investigated 
 * ImageMagick_ creates blackbox_ on some systems
 * PyGTK_ backend does not check $DISPLAY -> not working with Xvfb
 * slow: 0.2s - 0.7s
 
Similar projects:
 - http://sourceforge.net/projects/gtkshots/
 

Usage
============

Example::

    import pyscreenshot as ImageGrab
    
    # fullscreen
    im=ImageGrab.grab()
    im.show()
    
    # part of the screen
    im=ImageGrab.grab(bbox=(10,10,500,500))
    im.show()
    
    # to file
    ImageGrab.grab_to_file('im.png')
 
Installation
============

General
--------

 * install setuptools_ or pip_
 * install PIL_
 * install at least one backend
 * install the program:

if you have setuptools_ installed::

    # as root
    easy_install pyscreenshot

if you have pip_ installed::

    # as root
    pip install pyscreenshot

Ubuntu
----------
::

    # one or more
    sudo apt-get install scrot
    sudo apt-get install imagemagick
    sudo apt-get install python-gtk2
    sudo apt-get install python-qt4
    sudo apt-get install python-wxversion

    # Python Imaging Library (required)
    sudo apt-get install python-imaging

    sudo apt-get install python-setuptools
    sudo easy_install pyscreenshot

Uninstall
----------
::

    # as root
    pip uninstall pyscreenshot



.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _pip: http://pip.openplans.org/
.. _ImageGrab: http://www.pythonware.com/library/pil/handbook/imagegrab.htm
.. _PIL: http://www.pythonware.com/library/pil/
.. _ImageMagick: http://www.imagemagick.org/
.. _PyGTK: http://www.pygtk.org/
.. _blackbox: http://www.imagemagick.org/discourse-server/viewtopic.php?f=3&t=13658
.. _scrot: http://linux.die.net/man/1/scrot
.. _PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt
.. _wxPython: http://www.wxpython.org/