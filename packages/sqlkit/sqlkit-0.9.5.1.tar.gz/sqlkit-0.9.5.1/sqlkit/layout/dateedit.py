# Python GTK+ date and time entry widget. Version 0.2
# Copyright (C) 2005  Fabian Sturm, Sandro Dentella 2009
#
# ported from the libgnomeui/gnome-dateedit.c
# with changes where it makes sense for python (e.g. constructor, 
# return types etc.)
#
# This widget is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this widget; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

"""
.. _date_edit:

DateEdit
========

.. autoclass:: DateEdit
   :members: __init__, get_date, set_date

.. autoclass:: DateTimeEdit
   :members: __init__, get_datetime, set_datetime
   
"""



import sys
import os
import re
import time
import locale
import datetime

import pygtk
pygtk.require('2.0')
import gobject
import gtk
from gtk import gdk
from babel import dates

from sqlkit import _

class WrongDateFormat(Exception): pass
 # gnome_date_edit_new:
 # @the_date: date and time to be displayed on the widget
 # @show_time: whether time should be displayed
 # @use_24_format: whether 24-hour format is desired for the time display.
 #
 # Description: Creates a new #GnomeDateEdit widget which can be used
 # to provide an easy to use way for entering dates and times.
 # If @the_date is 0 then current time is used.
 #
 # Returns: a new #GnomeDateEdit widget. 
class DateEdit(gtk.HBox):
    """
    basic gtk widget to edit data
    """
    __gtype_name__ = 'DateEdit'
    
    __gproperties__ = {
        'date' : (gobject.TYPE_PYOBJECT,                       # type
                    'Date',                                    # nick name
                    'The date currently selected',             # description
                    gobject.PARAM_READWRITE),                  # flags

        'initial-date' : (gobject.TYPE_PYOBJECT,
                    'Initial Date',
                    'The initial date',
                    gobject.PARAM_READABLE),

        'width-chars' : (gobject.TYPE_PYOBJECT,
                    'Width of the entry in chars',
                    'The width of the entry',
                    gobject.PARAM_READWRITE),
                  
    }

    __gsignals__ = {
        'date-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          ()),                          
    }

    def __init__(self):
        gtk.HBox.__init__(self)
        
        # preset values
        self._initial_date = self._current_date = None
        self.invalid_date = False
        #datetime.datetime.today()

        try:
            self.locale_setup()
        except locale.Error:
            pass
        self.build_layout()

        hid = self._date_entry.connect('changed', self.date_entry_changed_cb)
        self._ids = {'date_entry_changed' : (self._date_entry, hid)}
        self._date_button.connect('clicked', self.date_button_clicked_cb)

        self._calendar.connect('day-selected', self.day_selected_cb)
        self._calendar.connect('day-selected-double-click', self.day_selected_double_click_cb)

        self._cal_popup.connect('delete_event', self.delete_popup_cb)
        self._cal_popup.connect('key_press_event', self.key_press_popup_cb)
           
        self.date_format = 'short'
        self.date_parse = None
        self._id_timeout_add = None
        
    def locale_setup(self):
        if os.name == 'nt' or sys.platform == 'darwin':
            # Todo: fix this for windows
            self._use_24h_format = False
        else:
            # locale stuff, ugly hack, due to ugly locale functions
            saved_locale = locale.getlocale()
            if saved_locale[0] == None:
                # no locale set, so set it myself
                locale.setlocale(locale.LC_ALL, '')
            # the time format
            if locale.nl_langinfo(locale.T_FMT_AMPM) == '' :
                self._use_24h_format = True
            else:
                self._use_24h_format = False
            # restore original locale
            locale.setlocale(locale.LC_ALL, saved_locale)
        
#####  layout
    def build_layout(self):

        self.set_spacing(6)
        date_box = gtk.HBox()
        self.add(date_box)
        date_box.show()
        
        # the date entry
        self._date_entry = gtk.Entry()
        self._entry = self._date_entry
        self._date_entry.set_max_length(15)
        self._date_entry.set_width_chars(10)
        self._align_entry = gtk.Alignment(0,0)
        #self.pack_start(self._date_entry, True, True, 0)
        date_box.add(self._align_entry)
        date_box.child_set_property(self._align_entry, 'expand', False)
        self._align_entry.add(self._date_entry)
        self._align_entry.show()
        self._date_entry.show()


        ## default style
        self._default_base = self._date_entry.get_style().base[gtk.STATE_NORMAL]

        # the date button
        self._date_button = gtk.Button()
        #pixmap = gtk.gdk.pixbuf_new_from_file('cal32.png')
        image = gtk.Image()
        image.set_from_stock('sk-calendar', gtk.ICON_SIZE_MENU)
        self._date_button.set_image(image)
        self._align_arrow = gtk.Alignment(0,0,0,0)
        self._align_arrow.show()
        self._align_arrow.add(self._date_button)

        #self.pack_start(self._date_button, False, False, 0)
        date_box.add(self._align_arrow)
#         # the down arrow
#         arrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_OUT)
#         self._date_button.add(arrow)
#         arrow.show()
        # finally show the button
        self._date_button.show()
        
        # the calendar popup
        self._cal_popup = gtk.Window(gtk.WINDOW_POPUP)
        self._cal_popup.set_title('popup for calendar')
        self._cal_popup.set_events(self._cal_popup.get_events() | gdk.KEY_PRESS_MASK)
        self._cal_popup.set_resizable(False) # Todo: Needed?
        self._cal_popup.set_tooltip_text(_(
            'Press Esc to close or double click a date to select it'))

        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_OUT)
        self._cal_popup.add(frame)
        frame.show()

        # the calendar
        self._calendar = gtk.Calendar()
        self._calendar.display_options(gtk.CALENDAR_SHOW_DAY_NAMES 
        # some space around the widgets, and two boxes
                                        | gtk.CALENDAR_SHOW_HEADING)
        frame.add(self._calendar)

        self._calendar.show()

    def flash_bg(self, entry, color, seconds):
        """
        flash background color for seconds to warn for wrong date format
        """
        colormap = entry.get_colormap()
        base_color = colormap.alloc_color(color)
        entry.modify_base(gtk.STATE_NORMAL, base_color)

        gobject.timeout_add(1000 * seconds, entry.modify_base,
                            gtk.STATE_NORMAL, self._default_base)
        
    def modify_base(self, state, color):
        self._date_entry.modify_base(state, color)
        self._default_base = color
        
    def popup_grab_on_window(self, window, activate_time):
        grab = gdk.pointer_grab(window, True, gdk.BUTTON_PRESS_MASK 
                                          | gdk.BUTTON_RELEASE_MASK
                                          | gdk.POINTER_MOTION_MASK, 
                            None, None, activate_time)
        if grab == 0:
            if gdk.keyboard_grab (window, True, activate_time) == 0:
                return True
            else:
                gdk.pointer_ungrab(activate_time)
                return False
        return False

    def position_popup(self):
        req = self._cal_popup.size_request()
        (x,y) = gdk.Window.get_origin(self._date_button.window)

        x += self._date_button.allocation.x
        y += self._date_button.allocation.y
        bwidth = self._date_button.allocation.width
        bheight = self._date_button.allocation.height

        x += bwidth - req[0]
        y += bheight

        if x < 0: x = 0
        if y < 0: y = 0
        
        self._cal_popup.move(x,y)


    def hide_popup(self):
        self._cal_popup.hide()
        self._cal_popup.grab_remove()
        
        
#####  callback
    def date_entry_changed_cb(self, entry):
        # check entry for valid date 
        if self._id_timeout_add:
            gobject.source_remove(self._id_timeout_add)
        
        # let's delay the check so we can complete our input
        self._id_timeout_add = gobject.timeout_add(700, self.verify_date, entry)

    def verify_date(self, entry):
        """Verify the text anc heck if it parses as date, complain if not
        """
        date_string = self._date_entry.get_text()
        if not date_string:
            self.set_date(None)
            return False
        try:
            if callable(self.date_parse):
                the_date = self.date_parse(date_string)
            else:
                the_date = dates.parse_date(date_string)
        except Exception, e:
            self.wrong_date_format(e, date_string)
            return False

        try:
            self.set_date(the_date, from_focus_out=True)
        except Exception, e:
            print e
            return False
        entry.modify_base(gtk.STATE_NORMAL, self._default_base)
        return False

    def date_button_clicked_cb(self, widget):
        # Temporarily grab pointer and keyboard on a window we know exists        
        if not self.popup_grab_on_window(widget.window, gtk.get_current_event_time()):
            return
        
        # set calendar date
        if self.get_date():
            self._calendar.select_month(self._current_date.month - 1, self._current_date.year)
            self._calendar.select_day(self._current_date.day)        
        
        # position and show popup window
        self.position_popup()
        self._cal_popup.show()
        self._calendar.grab_focus()
        
        # Now transfer our grabs to the popup window, this should always succed
        self.popup_grab_on_window(self._cal_popup.window, gtk.get_current_event_time())

    def day_selected_cb(self, widget):
        year, month, day = self._calendar.get_date()
        month += 1        
        the_date = datetime.date(year, month, day)
        self.set_date(the_date)

    def day_selected_double_click_cb(self, widget, data=None):
        self.hide_popup()


    def key_press_popup_cb(self, widget, event):   
        """
        Implement Esc to get rid of calendar
        """
        if event.keyval == gtk.keysyms.Escape:
            self.hide_popup()
            return True

        return False


    def delete_popup_cb(self, widget, data=None):
        # Todo: is this ever called??
        self.hide_popup();
        lll
        return TRUE;

####### date & gobject
    def wrong_date_format(self, error, date_string):
        self.invalid_date = True
        colormap = self._date_entry.get_colormap()
        base_color = colormap.alloc_color('orangered')
        self._date_entry.modify_base(gtk.STATE_NORMAL, base_color)
        #self.flash_bg(self._date_entry, 'orangered', 2)
        
    def get_date(self):

        date_string = self._date_entry.get_text()
        
        if self.invalid_date:
            return date_string
            ## i'd like to raise the error but python wouldn't catch it...
            #raise WrongDateFormat(_('Wrong format for date %s' % date_string))

        if not date_string:
            self._current_date = None
            return None

        return self._current_date

    def set_date(self, new_date, from_focus_out=False):
        """
        new_date is a datetime.date object. Can be set by:
          - do_set_property
          - focus_out_event
          - popup click 
        """

        date_changed = not new_date == self._current_date
        self.invalid_date = False
        
        # set the time and date string
        entry, hid = self._ids['date_entry_changed']
        entry.handler_block(hid)

        if new_date:
            if callable(self.date_format):
                try:
                    self._date_entry.set_text(self.date_format(new_date))
                except:
                    self._date_entry.set_text(
                        dates.format_date(new_date, format='short'))
            else:
                self._date_entry.set_text(
                    dates.format_date(new_date, format=self.date_format))
        else:
            self._date_entry.set_text('')
        entry.handler_unblock(hid)

        if date_changed:
            self._current_date = new_date
            self.emit('date-changed')
            return True
        return False
    
    def do_get_property(self, property): 
        if property.name == 'date':
            return self.get_date()
        elif property.name == 'initial-date':
            return self._initial_date
        elif property.name == 'width-chars':
            return self._date_entry.props.width_chars
        else:
            raise AttributeError, 'unknown property %s' % property.name

    # set_properties
    def do_set_property(self, property, value):
        if property.name == 'date':
            self.set_date(value)
        elif property.name == 'width-chars':
            self._date_entry.props.width_chars = value
        else:
            raise AttributeError, 'unknown property %s' % property.name
            


class DateTimeEdit(DateEdit):

    __gtype_name__ = 'DateTimeEdit'
    
    __gproperties__ = {
        'datetime' : (gobject.TYPE_PYOBJECT,                       # type
                    'Date',                                    # nick name
                    'The date currently selected',             # description
                    gobject.PARAM_READWRITE),                  # flags

        'initial_datetime' : (gobject.TYPE_PYOBJECT,
                    'Initial Date',
                    'The initial date',
                    gobject.PARAM_READABLE),
                  
        'lower-hour' : (gobject.TYPE_INT,
                    'Lower Hour',
                    'Lower hour in the time popup selector',
                    0,
                    24,
                    7,
                    gobject.PARAM_READWRITE),

        'upper-hour' : (gobject.TYPE_INT,
                    'Upper Hour',
                    'Upper hour in the time popup selector',
                    0,
                    24,
                    19,
                    gobject.PARAM_READWRITE),
                  
        'show-time' : (gobject.TYPE_BOOLEAN,
                    'Show Time',
                    'Show the time widget',
                    True,
                    gobject.PARAM_READWRITE),
                    
        # TODO: use-24 is not working, only 24 hours is working
        'use-24h-format' : (gobject.TYPE_BOOLEAN,
                    'Use 24h Format',
                    'Display time in 24h format',
                    True,
                    gobject.PARAM_READWRITE)
        }

    __gsignals__ = {
        'datetime-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          ()),
        'time-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          ()),
        }
    def __init__(self):

        # preset values
        self._initial_datetime = self._current_datetime = None
        self._lower_hour = 7;
        self._upper_hour = 19;        
        self._show_time = True
        self._use_24h_format = True
        
        DateEdit.__init__(self)
        self._time_combobox.connect('changed', self.time_combobox_changed_cb)
        self._time_combobox.child.connect('focus-out-event', self.time_entry_focus_out_event_cb)
        self.connect('realize', self.fill_time_combobox)

    def build_layout(self):

        DateEdit.build_layout(self)

        time_box = gtk.HBox()
        self.add(time_box)
        time_box.show()

        # the time entry combobox
        self._time_combobox = gtk.ComboBoxEntry()
        self._time_combobox.child.set_max_length(12)
        self._time_combobox.child.set_width_chars(8)
        time_box.add(self._time_combobox)
        self._time_combobox.set_no_show_all(True)
        self._time_combobox.show()
           
        # set the initial widget properties
        self.set_show_time(self._show_time)
        self.set_use_24h_format(self._use_24h_format)

    def fill_time_combobox(self, widget, data=None):
        if self._lower_hour > self._upper_hour:
            return
            
        # create the new model    
        store = gtk.TreeStore(str)
        for i in range(self._lower_hour, self._upper_hour + 1):
            the_time = datetime.time(i, 0)
            if self._use_24h_format:
                label = the_time.strftime('%H:%M')
            else:
                label = the_time.strftime('%I:%M %p')
            iter = store.append(None, [label])
            
            # create sub menu
            for j in range(15,60,15):
                the_time = datetime.time(i,j)
                if self._use_24h_format:
                    label = the_time.strftime('%H:%M')
                else:
                    label = the_time.strftime('%I:%M %p')
                store.append(iter, [label])
                
        # finally replace current model with this new one                
        self._time_combobox.set_model(store)
        if self._time_combobox.get_text_column() == -1:
            self._time_combobox.set_text_column(0)

    def time_combobox_changed_cb(self, widget, data=None):
        # if the changed was due to a time selection in the menu, 
        # handle as if focus-out-event
        if self._time_combobox.get_active_iter() != None:
            self.time_entry_focus_out_event_cb(widget, data)

    def time_entry_focus_out_event_cb(self, widget, data=None):

        # check entry for valid time, reset if not
        time_text = self._time_combobox.child.get_text()
        try:
            if self._use_24h_format:
                new_time = time.strptime(time_text, '%H:%M')
            else:
                new_time = time.strptime(time_text, '%I:%M %p')

            the_time = datetime.time(new_time.tm_hour,new_time.tm_min)
            the_date = self.get_date()
            
            the_datetime = datetime.datetime.combine(self.get_date(), the_time)

        except Exception, e:
            self.wrong_time_format(e, time_text)
        self.set_time(the_time)
        
    ############################################
    # properties and their convenience functions

    def wrong_time_format(self, error, date_string):
        self.invalid_time = True
        self.flash_bg(self._time_combobox.child, 'orangered', 2)
        
    def set_use_24h_format(self, use_24h_format):
        dt = self.get_time()
        self._use_24h_format = use_24h_format
        self.fill_time_combobox(self)
        self._current_time = dt

    # get_properties
    def set_lower_hour(self, value):
        if value < 0 or value > 24 or value > self._upper_hour:
            return
        self._lower_hour = value
        self.fill_time_combobox(None)


    def set_upper_hour(self, value):
        if value < 0 or value > 24 or value < self._lower_hour:
            return
        self._upper_hour = value
        self.fill_time_combobox(None)
        
        
    def set_show_time(self, show_time):
        if show_time == True:
            self._show_time = True
            self._time_combobox.show()
        else:
            self._show_time = False
            self._time_combobox.hide()
    
    
    def get_time(self):
        """
        return only the time
        """

        time_string = self._time_combobox.child.get_text()
        
        if not time_string:
            self._current_time = None
            return None

        else:
            try:
                value = datetime.time(*[int(i) for i in re.split('[.:]', time_string)]) 
                return value
            except Exception, e:
                self.wrong_time_format(e, time_string)
                return time_string
            
    def get_datetime(self):
        ### I should propagate errors via an Exception but I'm not able write now. See:
        # http://www.mail-archive.com/pygtk@daa.com.au/msg17444.html

        new_date = self.get_date()
        if isinstance(new_date, basestring):
            return new_date

        new_time = self.get_time()
        if isinstance(new_date, basestring):
            return new_time

        if not new_date:
            return None
        
        return datetime.datetime.combine(self.get_date(), self.get_time() or datetime.time())
        
    def set_datetime(self, new_datetime):

        if new_datetime:
            date_changed = self.set_date(new_datetime.date())
            time_changed = self.set_time(new_datetime.time())
        else:
            date_changed = self.set_date(None)
            time_changed = self.set_time(None)

        if date_changed or time_changed:
            self.invalid_time = False
            self.invalid_date = False
            self.emit('datetime-changed')


    def set_time(self, new_time, focus=False):

        time_changed =  not new_time == self._current_time
        if new_time == None:
            self._time_combobox.child.set_text('')
        else:
            # set the time and date string
            if self._use_24h_format == True:
                self._time_combobox.child.set_text(new_time.strftime('%H:%M'))
            else:
                self._time_combobox.child.set_text(new_time.strftime('%I:%M %p'))

        # emit signal on time change
        if time_changed == True:
            self._current_time = new_time
            self.invalid_time = False
            self.emit('time-changed')    
            return True

        return False

    # get_properties
    def do_get_property(self, property): 
        if property.name == 'datetime':
            return self.get_datetime()
        elif property.name == 'initial-datetime':
            return self._initial_datetime
        elif property.name == 'lower-hour': 
            return self._lower_hour
        elif property.name == 'upper-hour':
            return self._upper_hour
        elif property.name == 'show-time':
            return self._show_time
        elif property.name == 'use-24h-format':
            return self._use_24h_format
        else:
            raise AttributeError, 'unknown property %s' % property.name


    # set_properties
    def do_set_property(self, property, value):
        if property.name == 'datetime':
            self.set_datetime(value)
        elif property.name == 'lower-hour': 
            self.set_lower_hour(value)
        elif property.name == 'upper-hour':
            self.set_upper_hour(value)
        elif property.name == 'show-time':
            self.set_show_time(value)
        elif property.name == 'use-24h-format':
            self.set_use_24h_format(value)
        else:
            raise AttributeError, 'unknown property %s' % property.name
            

class EntryCal(gtk.Entry):
    """
    basic gtk widget to edit data that uses primary/secondary icon stock
    """
    __gtype_name__ = 'DateEdit2'
    
    __gproperties__ = {
        'date' : (gobject.TYPE_PYOBJECT,                       # type
                    'Date',                                    # nick name
                    'The date currently selected',             # description
                    gobject.PARAM_READWRITE),                  # flags

        'initial-date' : (gobject.TYPE_PYOBJECT,
                    'Initial Date',
                    'The initial date',
                    gobject.PARAM_READABLE),

        'width-chars' : (gobject.TYPE_PYOBJECT,
                    'Width of the entry in chars',
                    'The width of the entry',
                    gobject.PARAM_READWRITE),
                  
    }

    __gsignals__ = {
        'date-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          ()),                          
    }

    def __init__(self):
        
        gtk.Entry.__init__(self)
        self.props.primary_icon_stock = 'gtk-quit'
        self.props.secondary_icon_stock = 'sk-calendar'
        self.props.secondary_icon_tooltip_text = "Calendar"

if __name__ == '__main__':

    import misc  # adds the sk-calendar stock-icon
    w = gtk.Window()
    d = EntryCal()
#    d = DateTimeEdit()
    w.add(d)
    w.show_all()

    gtk.set_interactive(True)
    
