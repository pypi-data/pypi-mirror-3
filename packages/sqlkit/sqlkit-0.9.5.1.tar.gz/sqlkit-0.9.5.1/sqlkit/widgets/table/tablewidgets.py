from sqlkit.widgets.common import completion 
from sqlkit import _, exc

class CellWidget(object):

    def __init__(self, field):
        self.field = field
        self.master = master = field.master
        self.field_name = field_name = field.field_name
        

        self.add_completion()
        self._dont_change_real_value = False

        self.master.field_widgets[field_name] = self
        
    def set_not_null_style(self):
        # FIXME: should set label in bold italics...
        pass

    def pop_completion(self):
        ## self.emit('changed') is needed as the only way to pop the completion
        ## when you click on the icon to pop the completion you should not invalidate
        ## self.real_value as it's not an editing action
        self._dont_change_real_value = True
        self.entry.emit('changed')
        self._dont_change_real_value = False
        
    def get_entry(self):
        # CellWidget has an editable only if we're editing...
        if self.field_name == self.master.currently_edited_field_name:
            return self.master.cell_entry.entry
        else:
            msg = _("No current obj for field '%s' in %s")
            raise NotImplementedError(msg  % (self.field_name, self.master))
    
    entry = property(get_entry)

    def add_completion(self, editable=False, force=False):
        """completion is set just for fkey and string fields

        :param editable: the editable widget to which completion should be added
        :param force: (boolen) if True a SimpleCompletion is added even if
                      field is not a Varchar. Used to add completion to other fields,
                      possibly in conjunction with enum.
        """

        
        if self.master.relationship_mode == 'm2m' and editable == False:
            Completion = completion.M2mCompletion
            
        elif self.master.is_fkey(self.field_name):
            Completion = completion.FkeyCompletion

        elif self.master.is_enum(self.field_name):
            Completion = completion.EnumCompletion

        elif force or self.master.get_field_type(self.field_name) in (str, unicode):
            Completion = completion.SimpleCompletion
        else:
            self.completion = None
            return
        
        try:
            self.completion = Completion(self.master, self, self.field_name)
            self.master.completions[self.field_name] = self.completion
        except exc.ColumnWithoutTable, e:
            ## function columns do not have .table so that won't complete
            pass
        
    def set_value_cb(self, field, value, shown=False, initial=False):
        self.set_value(value, initial=initial)   

    def set_value(self, value, shown=False, initial=False):
        self.master.set_value(self.field_name, value, shown=shown, initial=initial)

    def get_value(self, shown=False):
        return self.master.get_value(self.field_name)

    def set_max_length(self, length=None):
        if length is None:
            length = self.field.length
            
        try:
            self.entry.set_max_length(length)
        except:
            pass
            
    def __str__(self):
        return "<CellWidget: %s>" % self.field_name 
