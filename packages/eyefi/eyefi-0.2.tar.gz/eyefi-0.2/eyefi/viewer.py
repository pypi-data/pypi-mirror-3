#!/usr/bin/python

# EyeFi Python Server
#
# Copyright (C) 2010 Robert Jordens
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from enthought.traits.api import HasTraits, Int, File, Str
from enthought.traits.ui.api import (ImageEditor, Item, View, HGroup,
        VGroup, Image)
from twisted.internet import gtk2reactor
import wx


class Viewer(HasTraits):
    view = View(
            Item("image", editor=ImageEditor(), show_label=False,
                resizable=True),
            resizable=True)
    image = Image("/home/rj/test.jpg")


def main():
    reactor = gtk2reactor.install()
    v = Viewer()
    view = v.edit_traits()
    view.control.ShowFullScreen(True)
    reactor.callLater(1, reactor.stop)
    reactor.run()
    return v


if __name__ == "__main__":
    v = main()
