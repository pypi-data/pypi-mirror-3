# -*- coding: utf-8 -*-
# vim:sw=4:et:ai

# Copyright © 2010 etk.docking Contributors
#
# This file is part of etk.docking.
#
# etk.docking is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# etk.docking is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with etk.docking. If not, see <http://www.gnu.org/licenses/>.


from __future__ import absolute_import
import sys

from simplegeneric import generic
from xml.etree.ElementTree import Element, SubElement, tostring, fromstring

import gtk

from .docklayout import DockLayout
from .dockframe import DockFrame
from .dockpaned import DockPaned
from .dockgroup import DockGroup
from .dockitem import DockItem


SERIALIZABLE = ( DockFrame, DockPaned, DockGroup, DockItem )


def serialize(layout):
    def _ser(widget, element):
        if isinstance(widget, SERIALIZABLE):
            sub = SubElement(element, type(widget).__name__.lower() , attributes(widget))
            widget.foreach(_ser, sub)
        else:
            sub = SubElement(element, 'widget', attributes(widget))

    tree = Element('layout')
    map(_ser, layout.frames, [tree] * len(layout.frames))

    return tostring(tree, encoding=sys.getdefaultencoding())

widget_factory = {}

def deserialize(layoutstr, itemfactory):
    '''
    Return a new layout with it's attached frames. Frames that should be floating
    already have their gtk.Window attached (check frame.get_parent()). Transient settings
    and such should be done by the invoking application.
    '''
    def _des(element, parent_widget=None):
        if element.tag == 'widget':
            name = element.attrib['name']
            widget = itemfactory(name)
            widget.set_name(name)
            parent_widget.add(widget)
        else:
            factory = widget_factory[element.tag]
            widget = factory(parent=parent_widget, **element.attrib)
            assert widget, 'No widget (%s)' % widget
            if len(element):
                map(_des, element, [widget] * len(element))
        return widget

    tree = fromstring(layoutstr)
    layout = DockLayout()
    map(_des, tree, [ layout ] * len(tree))

    return layout

def get_main_frames(layout):
    return (f for f in layout.frames \
            if not isinstance(f.get_parent(), gtk.Window))

def finish(layout, main_frame):
    '''
    Finish the loading process by setting all floating windows "transient_for" the main
    window (which should be a ancestor of the main_frame).
    '''
    main_window = main_frame.get_toplevel()

    for frame in layout.frames:
        if frame is main_frame:
            continue

        parent = frame.get_parent()

        if parent:
            assert isinstance(parent, gtk.Window), parent
            parent.set_transient_for(main_window)

def parent_attributes(widget):
    """
    Add properties defined in the parent widget specific for this instance (like weight).
    """
    container = widget.get_parent()
    d = {}

    if isinstance(container, DockPaned):
        paned_item = [i for i in container._items if i.child is widget][0]
        if paned_item.weight:
            d['weight'] = str(int(paned_item.weight * 100))

    return d

@generic
def attributes(widget):
    raise NotImplementedError

@attributes.when_type(gtk.Widget)
def widget_attributes(widget):
    return { 'name': widget.get_name() or 'empty' }

@attributes.when_type(DockItem)
def dock_item_attributes(widget):
    d = { 'title': widget.props.title,
             'tooltip': widget.props.title_tooltip_text }
    if widget.props.icon_name:
        d['icon_name'] = widget.props.icon_name
    if widget.props.stock:
        d['stock_id'] = widget.props.stock
    return d

@attributes.when_type(DockGroup)
def dock_group_attributes(widget):
    d = parent_attributes(widget)
    name = widget.get_name()
    if name != widget.__gtype__.name:
        d['name'] = name
    return d

@attributes.when_type(DockPaned)
def dock_paned_attributes(widget):
    return dict(orientation=(widget.get_orientation() == gtk.ORIENTATION_HORIZONTAL and 'horizontal' or 'vertical'),
                **parent_attributes(widget))

@attributes.when_type(DockFrame)
def dock_frame_attributes(widget):
    a = widget.allocation
    d = dict(width=str(a.width), height=str(a.height))
    parent = widget.get_parent()

    if isinstance(parent, gtk.Window) and parent.get_transient_for():
        d['floating'] = 'true'
        d['x'], d['y'] = map(str, parent.get_position())

    return d

def factory(typename):
    '''
    Simple decorator for populating the widget_factory dictionary.
    '''
    def _factory(func):
        widget_factory[typename] = func
        return func

    return _factory

@factory('dockitem')
def dock_item_factory(parent, title, tooltip, icon_name=None, stock_id=None, pos=None, vispos=None, current=None, name=None):
    item = DockItem(title, tooltip, icon_name, stock_id)
    if name:
        item.set_name(name)
    if pos:
        pos = int(pos)
    if vispos:
        vispos = int(vispos)
    parent.insert_item(item, pos, vispos)
    return item

@factory('dockgroup')
def dock_group_factory(parent, weight=None, name=None):
    group = DockGroup()

    if name:
        group.set_name(name)

    if weight is not None:
        parent.insert_item(group, weight=float(weight) / 100.)
    else:
        parent.add(group)

    return group

@factory('dockpaned')
def dock_paned_factory(parent, orientation, weight=None, name=None):
    paned = DockPaned()

    if name:
        paned.set_name(name)

    if orientation == 'horizontal':
        paned.set_orientation(gtk.ORIENTATION_HORIZONTAL)
    else:
        paned.set_orientation(gtk.ORIENTATION_VERTICAL)

    if weight is not None:
        item = parent.insert_item(paned, weight=float(weight) / 100.)
    else:
        parent.add(paned)

    return paned

@factory('dockframe')
def dock_frame_factory(parent, width, height, floating=None, x=None, y=None):
    assert isinstance(parent, DockLayout), parent

    frame = DockFrame()
    frame.set_size_request(int(width), int(height))
    parent.add(frame)

    if floating == 'true':
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        #self.window.set_type_hint(gdk.WINDOW_TYPE_HINT_UTILITY)
        window.set_property('skip-taskbar-hint', True)
        window.move(int(x), int(y))
        window.add(frame)

    return frame
