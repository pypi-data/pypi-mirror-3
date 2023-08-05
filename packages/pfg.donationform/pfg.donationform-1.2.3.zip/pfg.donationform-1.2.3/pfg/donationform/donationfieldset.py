from Products.Five import BrowserView
from Products.PloneFormGen.content.fieldsBase import BaseFormField
from Products.PloneFormGen.content.fieldsBase import finalizeFieldSchema
from Products.PloneFormGen.content.fieldsBase import BaseFieldSchemaStringDefault

from Products.ATContentTypes.content.base import registerATCT
from Products.Archetypes import atapi
from Products.CMFCore.permissions import View, ModifyPortalContent

from zope.interface import implements

from AccessControl import ClassSecurityInfo

from pfg.donationform.config import PROJECTNAME
from pfg.donationform.interfaces import IDonationFieldSet
from pfg.donationform import donationformMessageFactory as _

donationfieldset_schema = BaseFieldSchemaStringDefault.copy() + atapi.Schema((
        atapi.IntegerField('fgCost',
            searchable=0,
            required=0,
            default=u"",
            widget=atapi.IntegerWidget(
                label=_(u'Suggested Donation Amount'),
                ),
            ),
        atapi.IntegerField('fgMinimumDonation',
            searchable=0,
            required=0,
            default=1,
            widget = atapi.IntegerWidget(
                label = _(u'Minimum Donation Amount'),
                ),
            ),
        atapi.LinesField('fgDonationLevels',
            searchable=0,
            required=0,
            widget=atapi.LinesWidget(label=_(u'Predefined Donation Levels'),
                description=_(u'Use one line per option, with an "amount|label" format.'),
                ),
            ),
        atapi.BooleanField('fgAllowRecurringPayments',
            searchable=0,
            required=0,
            default=False,
            widget=atapi.BooleanWidget(label=_(u'Allow recurring payments'),
                description=_(u'(Payment processor support is required.)'),
                ),
            ),
        atapi.BooleanField('fgRecurForever',
            searchable=0,
            required=0,
            default=False,
            widget = atapi.BooleanWidget(label=_(u'Recur forever'),
                description = _(u'If checked, user will not be prompted for how many payments to make.'),
                ),
            ),
    ))

del donationfieldset_schema['required']
del donationfieldset_schema['hidden']
noview = {'view': 'invisible', 'edit': 'invisible'}
donationfieldset_schema['fgDefault'].widget.visible = noview
finalizeFieldSchema(donationfieldset_schema, folderish=True, moveDiscussion=False)

class DonationFieldSet(BaseFormField):
    """ Donation Entry Fieldset """
    
    implements(IDonationFieldSet)
    security  = ClassSecurityInfo()
    
    schema = donationfieldset_schema

    # Standard content type setup
    portal_type ='DonationFieldSet'
    content_icon = 'StringField.gif'
    typeDescription= 'Donation Fieldset'

    def __init__(self, oid, **kwargs):
        """ initialize class """
        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = atapi.StringField('fg_donation_fieldset',
            searchable=0,
            required=0,
            write_permission = View,
            widget=atapi.StringWidget(
                macro="donationfield_widget",
                ),
            )

    security.declareProtected(ModifyPortalContent, 'setFgCost')
    def setFgCost(self, value, **kw):
        if value:
            self.fgField.fgCost = int(value)
            self.fgCost = value
        else:
            self.fgField.fgCost = None
            self.fgCost = value
    
    security.declareProtected(ModifyPortalContent, 'setFgDonationLevels')
    def setFgDonationLevels(self, value, **kw):
        self.fgField.fgDonationLevels = value
        self.fgDonationLevels = value
    
    security.declareProtected(ModifyPortalContent, 'setFgAllowRecurringPayments')
    def setFgAllowRecurringPayments(self, value, **kw):
        self.fgField.fgAllowRecurringPayments = value
        self.fgAllowRecurringPayments = value
    
    security.declareProtected(ModifyPortalContent, 'setFgRecurForever')
    def setFgRecurForever(self, value, **kw):
        self.fgField.fgRecurForever = value
        self.fgRecurForever = value

    def htmlValue(self, REQUEST):
        """ return from REQUEST, this field's value, rendered as XHTML.
        """
        amount = REQUEST.form.get(self.getId() + '_level')
        if not amount:
            amount = REQUEST.form.get(self.getId() + '_amount', '0')
        amount = amount.lstrip('$')
        
        s = '%.2f' % float(amount)
        
        recurring = self.getId() + '_recurring' in REQUEST.form
        if recurring:
            if getattr(self, 'fgRecurForever', False):
                s += 'once a month.'
            else:
                occurrences = REQUEST.form.get(self.getId() + '_occurrences')
                s += ' once a month for a total of %s payments.' % occurrences
        
        return s
    
    def specialValidator(self, value, field, REQUEST, errors):
        fname = field.getName()
        amount = REQUEST.form.get(fname + '_level')
        if not amount:
            amount = REQUEST.form.get(fname + '_amount', '')
        amount = amount.lstrip('$')

        try:
            float(amount)
        except:
            return "Please enter digits only for the donation amount."
        
        if float(amount) < self.getFgMinimumDonation():
            return "Sorry, we cannot accept online donations of less than $%s" % self.getFgMinimumDonation()
        
        recurring = fname + '_recurring' in REQUEST.form
        if recurring:
            occurrences = REQUEST.form.get(fname + '_occurrences', 9999)
            try:
                int(occurrences)
            except:
                return "Please enter digits only for the number of payments."
        
        return 0 # OK

registerATCT(DonationFieldSet, PROJECTNAME)

class DonationFieldHelperView(BrowserView):
    
    def listFgDonationLevels(self, levels):
        res = []
        for level in levels:
            parts = level.split('|')
            try:
                value = float(parts[0])
            except ValueError:
                continue
            if len(parts) > 1:
                label = parts[1]
            else:
                label = ''
            res.append((value, label))
        return res

    def requestValue(self, defaultValue, fieldName):
        level_field = '%s_level' % fieldName
        amount_field = '%s_amount' % fieldName
        try:
            current_value = float(self.request.form[level_field])
        except (ValueError, KeyError):
            try:
                current_value = float(self.request.form[amount_field])
            except (ValueError, KeyError):
                current_value = defaultValue or ''
        return current_value

    def formatAmount(self, amount):
        try:
            return self.request.locale.numbers.getFormatter('decimal').format(amount, '#,##0')
        except:
            return '%.2f' % amount
