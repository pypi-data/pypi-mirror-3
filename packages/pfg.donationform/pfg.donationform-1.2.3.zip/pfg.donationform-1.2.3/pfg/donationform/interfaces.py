from zope.interface import Interface
from zope import schema
from zope.component.interfaces import ObjectEvent
from getpaid.core.interfaces import IShoppingCart
from pfg.donationform import donationformMessageFactory as _

class IDonationFormSettings(Interface):
    
    title = schema.TextLine(
        title = _(u'Title'),
        default = _(u'Support Us'),
        )
    
    levels = schema.Text(
        title = _(u'Donation Levels'),
        description = _(u'List predefined donation levels that may be selected by '
                        u'donors.  Enter one level per line, in the format amount|description, '
                        u'where amount is a number (no currency symbol), and description is '
                        u'the text that will be shown.'),
        required = False,
        default=u"""10|Supporter
25|Friend
50|Patron
""",
        )
    
    create_fields = schema.Bool(
        title = _(u'Create contact and billing fields'),
        description = _(u'If selected, fields for contact and billing info will be '
                        u'automatically added to the form. Select this if you want to bypass '
                        u'the normal GetPaid checkout wizard so that checkout can happen in a '
                        u'single step.  Do not select it if you are using an off-site '
                        u'processor (e.g. PayPal) that collects this information itself.'),
        default=True,
        )
    
    use_ssl = schema.Bool(
        title = _(u'Use HTTPS'),
        description = _(u"Select this to submit the form using HTTPS.  Highly recommended, "
                        u"but won't work on a development machine without HTTPS configured."),
        default=True,
        )
    
class IDonationFieldSet(Interface):
    """A custom PloneFormGen field for configuring a donation amount."""

class DonationCreatedEvent(ObjectEvent):
    """Event fired for a cart after a donation is added via pfg.donationform"""

class IDonationCart(IShoppingCart):
    """A GetPaid cart containing a donation."""
