============
Introduction
============
        
Collective.inventions, formely known as `xdvtheme.inventions <http://pypi.python.org/pypi/xdvtheme.inventions/>`_, is a two-column layout theme based on Invention, a design by sdworkz, published at oswd. A very simple skin to be used as is out of the box or as a Diazo sample theme.

.. contents:: Contents

Install
=======

If you are using zc.buildout just edit buildout.cfg following these instructions.

* Add ``collective.inventions`` to the list of eggs to install, e.g.::

    [buildout]
    ... 
    eggs =
        ... 
        collective.inventions
    
* Tell the plone.recipe.zope2instance recipe to install a ZCML slug::

    [instance]
    ... 
    zcml =
        collective.inventions
    
* Re-run buildout, e.g. with:

    $ ./bin/buildout
    
* In a web browser, open your Plone site, then go to Site Setup, Complements, select Collective Inventions and click on activate.

Credits
=======

- Inventions is a design made by sdworkz, http://www.oswd.org/user/profile/id/11103

- collective.inventions is rewritten for Diazo by Roberto Allende - rover@menttes.com

- collective.xdv is developed by Martin Aspeli.

- plone.app.theming is developed by Martin Aspeli and Laurence Rowe.

- diazo is developed by Paul Everitt, Laurence Rowe and Martin Aspeli. 


Copyright
=========

Collective.inventions is copyright by Menttes and it's published with GPLv2 Licence.

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

        
