"""
Very very minimal widget to edit intervals in 4 entries.  Mainly used to
make test pass. I gues anybody that needs to work with intervals should work
out a bettere widget and possibly contribute it...


"""
import re
from datetime import timedelta

import gobject
import gtk

from sqlkit import debug as dbg


class IntervalEdit(gtk.Alignment):
    __gtype_name__ = 'IntervalEdit'

    __gproperties__ = {
        'interval' : (gobject.TYPE_PYOBJECT,             # type
                    'Interval',                          # nick name
                    'The interval currently selected',   # description
                    gobject.PARAM_READWRITE),            # flags

        }
    def __init__(self):
        gtk.Alignment.__init__(self)
        self.hbox = gtk.HBox()
        self.days = gtk.Entry()
        self.hours = gtk.Entry()
        self.minutes = gtk.Entry()
        self.seconds = gtk.Entry()
        try:
            ## only from gtk 2.12
            self.days.set_tooltip_text('Days')
            self.hours.set_tooltip_text('Hours')
            self.minutes.set_tooltip_text('Minutes')
            self.seconds.set_tooltip_text('Seconds')
        except:
            pass
        
        self._align = gtk.Alignment(0,0,0,0)

        self.add(self.hbox)
        for name in ('days', 'hours',): # 'minutes', 'seconds'):
            widget = getattr(self, name)
            widget.set_property('width_chars', 8)
            widget.set_alignment(1)
            self.hbox.add(widget)

        self.show_all()
        
        self.connect('realize', self.set_packing)

    def set_packing(self, other):
        parent = self.get_parent()
        props = [prop.name for prop in parent.list_child_properties()]
        if 'y-options' in props:
            parent.child_set_property(self, 'y-options', 0)

    def split_interval(self, interval):
        if interval is None:
            return [0] * 4
        days = interval.days
        hours, spare = divmod(interval.seconds, 3600)
        minutes, seconds = divmod(spare, 60)
        return days, hours, minutes, seconds
        
    def do_set_property(self, property, value):
        if property.name == 'interval':
            days, hours, minutes, seconds = self.split_interval(value)
            self.days.set_text(str(days) or '')
            self.hours.set_text("%.2d:%.2d:%.2d" % (hours, minutes, seconds))
            #self.minutes.set_text(str(minutes))
            #self.seconds.set_text(str(seconds))
            
    def do_get_property(self, property):
        if property.name == 'interval':
            
            days = self.days.get_text() or 0
            hours = self.hours.get_text() or '0:0:0'
        

            sep = "[:.]"
            H = "(?P<hours>\d+)"
            M = "(?:[:.](?P<minutes>\d+))?"
            S = "(?:[:.](?P<seconds>\d+))?"

            try:
                m = re.match(H+M+S, hours)
                hours, minutes, seconds = m.groups()
            except:
                ## FIXME: I should propagate an error
                hours, minutes, seconds = [0,0,0]
                
            value = timedelta(days=int(days),
                              hours=int(hours or 0),
                              minutes=int(minutes or 0),
                              seconds=int(seconds or 0))
            return value
            

