from zope.event import notify
from zope.component import adapts, queryUtility
from zope.interface import implements, alsoProvides
from getpaid.core.interfaces import ILineItemFactory, IShoppingCart
from getpaid.core.item import PayableLineItem, RecurringLineItem
from pfg.donationform.interfaces import IDonationFieldSet, DonationCreatedEvent, IDonationCart
from Products.CMFPlone.utils import safe_unicode

try:
    from zope.intid.interfaces import IIntIds
    IIntIds
except ImportError:
    IIntIds = None

try:
    from Products.PloneGetPaid import sessions
    sessions
except ImportError:
    sessions = None


class DonationFieldLineItemFactory(object):
    implements(ILineItemFactory)
    adapts(IShoppingCart, IDonationFieldSet)
    
    def __init__(self, cart, field):
        self.cart = cart
        self.field = field
        
        form = field.REQUEST.form
        fname = self.field.getId()
        self.amount = form.get(fname + '_level')
        if not self.amount:
            self.amount = form.get(fname + '_amount', '0')
        self.amount = self.amount.lstrip('$')
        self.is_recurring = form.get(fname + '_recurring', False)
        self.occurrences = form.get(fname + '_occurrences', 9999)

    def create(self):

        pfg = self.field.aq_parent
        
        if self.is_recurring:
            item = RecurringLineItem()
            item.interval = 1
            item.unit = 'months'
            item.total_occurrences = self.occurrences
        else:
            item = PayableLineItem()
        item.item_id = self.field.UID()
        if IIntIds:
            intid_utility = queryUtility(IIntIds)
            if intid_utility:
                item.uid = intid_utility.register(self.field)
        item.name = safe_unicode(pfg.Title())
        item.cost = float(self.amount)
        item.quantity = 1
        
        # Clear the cart before adding the donation.
        # We don't want to surprise users by charging them for something
        # they didn't realize they were buying!
        for key in self.cart.keys():
            del self.cart[key]
        
        self.cart[item.item_id] = item
        
        alsoProvides(self.cart, IDonationCart)
        notify(DonationCreatedEvent(self.cart))
        
        try:
            sessions.set_came_from_url(pfg)
        except:
            pass
        return item
