--------------------------------------------------
z3wingdbg: Wing IDE debugger integration for Zope3
--------------------------------------------------

Overview
--------

Zope3 package providing debug integration with the Wing IDE, allowing you to
run Zope3 applications under the control of the Wing debugger.

Requirements
------------

- Zope 3 (>= 3.3)
- Wing IDE (>= 2.0.2)

Installation
------------

Simply install this package using the standard distutils mantra::

  $ python setup.py install
  
Alternatively, you can install z3wingdbg straight into a Zope3 instance by 
using the --home switch::

  $ python setup.py install --home=/path/to/instance
  
Then copy the included ``z3wingdbg-include.zcml`` file to your Zope3 instance's
``etc/package-includes`` directory (or link it) to have Zope3 load z3wingdbg.

Usage
-----

z3wingdbg adds a few configuration objects to the root site manager at
/++etc++site/default/WingConfiguration. Server configuration objects can be
found on the Contents tab, while the Edit tab lets you set general options. In
a future release the included debugger management views will include a more
userfriendly way of altering the configation, as well as documentation.

In the root ZMI view of your Zope3 instance, a link titled 
'Manage Wing Debugger' leads to /++wing++debugger/, where you can control the 
debug server. Once started, all calls to the debug server (by default, an HTTP
server listening on http://localhost:50080/) can be controlled by the Wing IDE.

Links
-----

Project homepage (including downloads)
    http://www.zopatista.com/projects/z3wingdbg
    
Development
    http://trac.zopatista.com/zopatista/z3wingdbg
    
Subversion Repository
    https://svn.zopatista.com/zopatista/z3wingdbg
    http://trac.zopatista.com/zopatista/browser/z3wingdbg
    
Reporting bugs, feature requests
    http://trac.zopatista.com/zopatista/
