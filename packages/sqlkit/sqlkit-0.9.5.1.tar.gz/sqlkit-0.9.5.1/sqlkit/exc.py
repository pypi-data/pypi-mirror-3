from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import DBAPIError
from sqlkit import _

class FieldNotInLayout(Exception): pass
class FieldValueNotSet(Exception): pass
class NotHandledField(Exception): pass
class NotHandledDefault(Exception): pass

class MissingPrimaryKey(Exception): pass
class MissingWidget(Exception): pass

class NoSyncError(Exception): pass
class SyncNotAvailable(Exception): pass
class MissingEngine(Exception): pass

### Validation
class ValidationError(Exception):
    """
    Each hook or field.validate_value() can raise a ValidationError that will
    cause the saving/deleting procedure to abort and present a Dialog to inform
    the user of the error present, the old and the new value.
    """
    pass

class DialogValidationError(ValidationError):
    """
    A validation error that makes the outer procedures to abort. It's
    trapped by delete_event_cb and record_save_cb.
    """
    pass

class ValidationWarning(ValidationError):
    """
    This is not a real Error. It will make a different popup window to be
    presented with a message and a possibility to abort or continue.
    """
    pass

class NotNullableFieldError(ValidationError):
    """
    An error that specifies which field cannot be empty
    """
    def __init__(self, field_name, message=None, master=None):
        self.field_name = field_name
        if master:
            self.field_name = master.get_label(field_name)
        self.message = message or _("Field '%s' cannot be NULL") % self.field_name

    def __str__(self):
        return self.message
    
class InvalidValue(ValidationError):

    def __init__(self, field_name, value, message=None, master=None):
        self.field_name = field_name
        if master:
            self.field_name = master.get_label(field_name)
        self.value = value
        self.message = message or _("Field '%s' cannot have value %s") % (
            self.field_name, value)

class CommitError(ValidationError): pass
class HandledRollback(CommitError): pass

class NoCurrentObjError(Exception): pass

class CancelledAction(Exception): pass

class LookupValueError(Exception): pass
class LookupValueMissingValue(LookupValueError): pass
class LookupValueMultipleValues(LookupValueError): pass

class MissingDescriptorField(Exception): pass
class UnhandledMultipleForeignKeys(Exception): pass

class ParseFilterError(Exception): pass
class ColumnWithoutTable(Exception): pass

class ConnectionError(Exception): pass

