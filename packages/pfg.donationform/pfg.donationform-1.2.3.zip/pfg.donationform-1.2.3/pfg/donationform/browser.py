from Acquisition import aq_base
from zope.component.factory import Factory
from zope.formlib import form
from zope.app.form.browser import TextAreaWidget
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.PloneFormGen.content.form import FormFolder

try:
    from five.formlib import formbase
    formbase
except ImportError:
    from Products.Five.formlib import formbase

from pfg.donationform import donationformMessageFactory as _
from pfg.donationform.interfaces import IDonationFormSettings
from pfg.donationform.utils import addDonationForm


DonationFormFactory = Factory(
    FormFolder,
    title=_(u'Create a new donation form')
    )

def ShortTextAreaWidget(field, request):
    widget = TextAreaWidget(field, request)
    widget.height = 4
    return widget

class DonationFormAddForm(formbase.AddForm):
    label = _(u'Add Donation Form')
    description = _(u'This form helps you create a PloneFormGen form to collect '
                    u'donations.  When you click the "Add" button, it will create '
                    u'a PloneFormGen form with a donation field, a GetPaid checkout '
                    u'adapter, and optionally contact and billing fields.')
    
    form_fields = form.Fields(IDonationFormSettings)
    form_fields['levels'].custom_widget = ShortTextAreaWidget
    pfg = None

    def update(self):
        mailhost = getToolByName(self.context, 'MailHost', None)
        mailhost = getattr(aq_base(mailhost), 'smtp_host', None)
        if not mailhost:
            IStatusMessage(self.request).add(
                _(u'Please configure your mailhost before adding a donation form.'))
            portal_url = getToolByName(self.context, 'portal_url')()
            return self.request.response.redirect(portal_url + '/@@mail-controlpanel')
        super(DonationFormAddForm, self).update()

    def createAndAdd(self, data):
        folder = self.context.context
        form = addDonationForm(folder, **data)
        self.pfg = form
        self._finished_add = True

    def nextURL(self):
        if self.pfg is not None:
            return self.pfg.absolute_url()
        return formbase.AddForm.nextURL(self)

