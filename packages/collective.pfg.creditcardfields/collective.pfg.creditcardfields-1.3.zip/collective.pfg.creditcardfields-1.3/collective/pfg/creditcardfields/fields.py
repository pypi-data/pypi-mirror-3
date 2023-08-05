from Products.PloneFormGen.content.fieldsBase import BaseFormField
from Products.PloneFormGen.content.fieldsBase import finalizeFieldSchema
from Products.PloneFormGen.content.fieldsBase import BaseFieldSchemaStringDefault

from Products.ATContentTypes.content.base import registerATCT

from Products.Archetypes.public import Schema
from Products.Archetypes.public import IntegerField
from Products.Archetypes.public import IntegerWidget
from Products.Archetypes.public import DateTimeField
from Products.Archetypes.public import CalendarWidget

from Products.CMFCore.permissions import View, ModifyPortalContent

from zope.interface import implements

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
import cgi

from collective.pfg.creditcardfields.config import PROJECTNAME
from collective.pfg.creditcardfields.interfaces import IFGCCExpirationDateField

ccexpdate_schema = BaseFieldSchemaStringDefault.copy() + Schema((
        IntegerField('fgStartingYear',
            searchable=0,
            required=0,
            default=DateTime().year(),
            widget=IntegerWidget(
                label='Starting Year',
                i18n_domain = "ploneformgen",
                label_msgid = "label_fgstartingyear_text",
                description = "The first year to offer in the year drop-down.",
                description_msgid = "help_fgstartingyear_text",
                ),
        ),
        IntegerField('fgEndingYear',
            searchable=0,
            required=0,
            default=DateTime().year() + 20,
            widget=IntegerWidget(
                label='Ending Year',
                i18n_domain = "ploneformgen",
                label_msgid = "label_fgendingyear_text",
                description = """The last year to offer in the year drop-down.
                 Leave this empty if you wish to instead use a number of future years.""",
                description_msgid = "help_fgendingyear_text",
                ),
        ),
        IntegerField('fgFutureYears',
            searchable=0,
            required=0,
            default='20',
            widget=IntegerWidget(
                label='Future Years To Display',
                i18n_domain = "ploneformgen",
                label_msgid = "label_fgfutureyears_text",
                description = """The number of future years to offer in the year drop-down.
                 (This is only applicable if you have not specified an ending year.)""",
                description_msgid = "help_fgfutureyears_text",
                ),
        ),
    ))

finalizeFieldSchema(ccexpdate_schema, folderish=True, moveDiscussion=False)


class FGCCExpirationDateField(BaseFormField):
    """ CC Expiration Date Entry Field """
    
    implements(IFGCCExpirationDateField)
    security  = ClassSecurityInfo()
    
    schema = ccexpdate_schema

    # Standard content type setup
    portal_type ='FormExpirationDateField'
    content_icon = 'DateTimeField.gif'
    typeDescription= 'CC Expiration Date Entry Field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = DateTimeField('fg_ccexpirationdate_field',
            searchable=0,
            required=0,
            write_permission = View,
            widget=CalendarWidget(
                        macro="expirationdatecalendar",
                        show_hm=False,
                        format="%m-%Y",
                    ),
            )


    security.declareProtected(ModifyPortalContent, 'setFgStartingYear')
    def setFgStartingYear(self, value, **kw):
        """ set starting_year """

        if value:
            try:
                self.fgField.widget.starting_year = int(value)
                self.fgStartingYear = value
            except ValueError:
                pass
        else:
            self.fgField.widget.starting_year = None
            self.fgStartingYear = value            
            

    security.declareProtected(ModifyPortalContent, 'setFgEndingYear')
    def setFgEndingYear(self, value, **kw):
        """ set ending_year """

        if value:
            try:
                self.fgField.widget.ending_year = int(value)
                self.fgEndingYear = value
            except ValueError:
                pass
        else:
                self.fgField.widget.ending_year = None
                self.fgEndingYear = value


    security.declareProtected(ModifyPortalContent, 'setFgFutureYears')
    def setFgFutureYears(self, value, **kw):
        """ set future_years """

        if value:
            try:
                self.fgField.widget.future_years = int(value)
                self.fgFutureYears = value
            except ValueError:
                pass
        else:
            self.fgField.widget.future_years = None
            self.fgFutureYears = value            
    
    def htmlValue(self, REQUEST):
        """ return from REQUEST, this field's value, rendered as XHTML.
        """
        
        value = REQUEST.form.get(self.__name__, 'No Input')
        
        # The replace('-','/') keeps the DateTime routine from
        # interpreting this as UTC. Odd, but true.
        try:
            dt = DateTime(value.replace('-','/'))
        except (DateTime.SyntaxError, DateTime.DateError):
            # probably better to simply return the input
            return cgi.escape(value)
        
        value = dt.strftime("%m-%Y")
        
        return cgi.escape(value)
        
    
    def specialValidator(self, value, field, REQUEST, errors):
        """ Archetypes isn't validating non-required dates --
            so we need to.
        """
        fname = field.getName()
        month = REQUEST.form.get('%s_month'%fname, '01')
        day = REQUEST.form.get('%s_month'%fname, '01')
        
        if (month == '00') and (day == '00'):
            value = ''
            REQUEST.form[fname] = ''
        
        if value and not field.required:
            try:
                dt = DateTime(value)
            except (DateTime.SyntaxError, DateTime.DateError):
                return "Validation failed(isValidDate): this is not a valid date."
        return 0        


registerATCT(FGCCExpirationDateField, PROJECTNAME)
