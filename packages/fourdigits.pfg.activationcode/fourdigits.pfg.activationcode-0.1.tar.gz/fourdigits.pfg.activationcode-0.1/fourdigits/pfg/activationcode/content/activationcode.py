from Products.ATContentTypes.content.base import registerATCT
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringWidget, LinesWidget
from Products.Archetypes.public import StringField, LinesField
from fourdigits.pfg.activationcode.config import PROJECTNAME
from AccessControl import ClassSecurityInfo

from Products.PloneFormGen.content.fieldsBase import BaseFormField
from Products.PloneFormGen.content.fieldsBase import finalizeFieldSchema
from Products.PloneFormGen.content.fieldsBase import \
    BaseFieldSchemaStringDefault
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.PloneFormGen.content.actionAdapter import \
    FormActionAdapter, FormAdapterSchema

activation_schema = FormAdapterSchema.copy() + \
                    BaseFieldSchemaStringDefault.copy() + Schema((
    LinesField('activationcode',
        searchable=0,
        required=1,
        widget=LinesWidget(
            label='Activation Codes',
            i18n_domain="ploneformgen",
            description="Place a code on a new line",
            ),
    ),
    StringField('validation_error_message',
        required=1,
        default="Validation failed: Activation code is invalid",
        widget=StringWidget(
            label='Validation error message',
            i18n_domain="ploneformgen",
            description="Message to show on invalid code",
            ),
       ),
))

finalizeFieldSchema(activation_schema, folderish=True, moveDiscussion=False)


class FormActivationCodeField(BaseFormField, FormActionAdapter):
    """
    """
    portal_type = 'FormActivationCodeField'
    security = ClassSecurityInfo()
    schema = activation_schema

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = LinesField('fg_activationcode_field',
            searchable=0,
            required=1,
            write_permission=View,
            widget=StringWidget(),
            )

    security.declareProtected(ModifyPortalContent, 'setActivationcode')

    def setValidation_error_message(self, value, **kw):
        if value:
            try:
                self.fgField.widget.validation_error_message = value
                self.validation_error_message = value
            except ValueError:
                pass
        else:
            self.fgField.widget.validation_error_message = None
            self.validation_error_message = value

    def setActivationcode(self, value, **kw):
        """ set setActivationcode """

        if value:
            try:
                self.fgField.widget.activationcode = value
                self.activationcode = value
            except ValueError:
                pass
        else:
            self.fgField.widget.activationcode = None
            self.activationcode = value

    def specialValidator(self, value, field, REQUEST, errors):
        """ validate our code
        """
        if value:
            if value not in self.activationcode:
                return str(self.validation_error_message)
        return 0

    security.declarePrivate('onSuccess')

    def onSuccess(self, fields, REQUEST=None):
        """
        e-mails data.
        """
        for field in fields:
            if field.portal_type == 'FormActivationCodeField':
                self.activationcode.remove(REQUEST.form[field.id])

registerATCT(FormActivationCodeField, PROJECTNAME)
