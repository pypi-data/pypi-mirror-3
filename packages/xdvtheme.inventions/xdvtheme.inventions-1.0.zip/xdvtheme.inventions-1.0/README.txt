xdv.inventions ver 1.0
----------------------

xdv.inventions is a plone look and feel customization using collective.xdv.

Dependencies
------------
Plone 3.3rc5 or bigger. Tested with Plone 4.0b5.
xdv.inventions depends on collective.xdv To setup collective.xdv you can follow its instructions at `package's page <http://pypi.python.org/pypi/collective.xdv/>`_.

Setup
-----
1. Add collective.xdv and install it on your plone site using quickinstaller.

2. Add xdvtheme.inventions to your buildout::

    [buildout]
    ... 
    eggs =
        ... 
        collective.inventions

    [instance]
    ... 
    zcml =
        collective.inventions



3. Rerun buildout and restart your Plone instance.

4. Go to site setup, Theme transform, and fill the xdv form enabling it and to use the static resources. For example:

    Enabled: yes
    Domains: www.mysite.com:port
    Theme template: http://xxx.xx.xx.xxx:port/demo/static/index
    Rules file: /absolute_path_to_instance/themes/rules.xml

where www.mysite.com are the domains which you're going to use to access the site, http://xxx.xx.xx.xxx is the ip number of the site, or a file system path in your server to reach the file index.html. Click on save and if you access using www.mysite.com you should get the inventions look and feel customization.

If you're trying it locally, it could be something like:

    Domains: localhost:8080
    Theme template: http://127.0.0.1:8080/MY-PLONE-SITE/index
    Rules file: /PATH-TO-BOULDOUT-EGGS/xdvtheme.inventions/rules.xml



Documentation
-------------
- http://plone.org/documentation/manual/theming
- http://pypi.python.org/pypi/collective.xdv

Credits
-------
inventions is a design made by sdworkz, http://www.oswd.org/user/profile/id/11103
xdv.inventions is rewritten for xdv by Roberto Allende - rover@menttes.com
collective.xdv is developed by Martin Aspeli

Copyright
---------
xdvtheme.inventions is copyright by Menttes and it's published with GPLv2 Licence.

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston,
  MA 02111-1307 USA.



