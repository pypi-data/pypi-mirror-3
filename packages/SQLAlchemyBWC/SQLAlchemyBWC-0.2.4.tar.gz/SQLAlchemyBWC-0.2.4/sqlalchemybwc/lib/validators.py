from blazeutils.datastructures import BlankObject
import formencode
from savalidation._internal import ValidationHandler, ClassMutator
from sqlalchemy import sql as sasql

from compstack.sqlalchemy import db

class _UniqueValidator(formencode.validators.FancyValidator):
    """
    Calls the given callable with the value of the field.  If the return value
    does not evaluate to false, Invalid is raised
    """

    __unpackargs__ = ('fieldname', 'cls', 'instance')
    messages = {
        'notunique': u'the value for this field is not unique',
        }

    def validate_python(self, value, state):
        existing_record = self.cls.get_by(**{self.fieldname:value})
        if existing_record and existing_record is not state.instance:
            raise formencode.Invalid(self.message('notunique', state), value, state)
        return

class _UniqueValidationHandler(ValidationHandler):
    type = 'field'
    def add_validation_to_extension(self, field_names, fe_args, **kwargs):
        if not field_names:
            raise ValueError('validates_unique() must be passed at least one field name')
        for field_to_validate in field_names:
            valinst = _UniqueValidator(
                cls = self.entitycls,
                fieldname = field_to_validate
            )
            self.validator_ext.add_validation(valinst, field_to_validate)

validates_unique = ClassMutator(_UniqueValidationHandler)
