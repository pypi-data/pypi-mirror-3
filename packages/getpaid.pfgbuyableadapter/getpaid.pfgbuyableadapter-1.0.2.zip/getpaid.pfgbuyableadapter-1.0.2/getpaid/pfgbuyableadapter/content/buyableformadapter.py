"""Definition of the Buyable Form Adapter content type
"""

from zope.interface import implements
from zope.component import getUtility

from zope.app.component.hooks import getSite

from getpaid.core.interfaces import IShoppingCartUtility
from getpaid.core.item import PayableLineItem

from Products.PloneFormGen.content.actionAdapter import \
    FormActionAdapter, FormAdapterSchema

from zope.app.intid.interfaces import IIntIds

from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-
from getpaid.pfgbuyableadapter import pfgbuyableadapterMessageFactory as _

from getpaid.pfgbuyableadapter.interfaces import IBuyableFormAdapter
from getpaid.pfgbuyableadapter.config import PROJECTNAME

BuyableFormAdapterSchema = FormAdapterSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.FixedPointField(
        'price',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Price"),
            description=_(u"How much does this form cost"),
            dollars_and_cents=True,
        ),
        required=True,
        precision = 2,
        validators=('isDecimal'),
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

BuyableFormAdapterSchema['title'].storage = atapi.AnnotationStorage()
BuyableFormAdapterSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(BuyableFormAdapterSchema, moveDiscussion=False)


class BuyableFormAdapter(FormActionAdapter):
    """An adapter for PloneFormGen to allow forms to be purchased."""
    implements(IBuyableFormAdapter)

    meta_type = "BuyableFormAdapter"
    schema = BuyableFormAdapterSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    price = atapi.ATFieldProperty('price')

    def onSuccess(self, fields, REQUEST=None):
        """
        saves data.
        """

        disallowed_types = ('FormLabelField','FormFolder','FieldsetFolder','FormCaptchaField','FormRichLabelField','FormMailerAdapter','FomrSaveDataAdapter','FormThanksPage','FormCustomScriptAdapter')

        data = {}
        #import pdb; pdb.set_trace()
        for f in fields:
            if f.portal_type not in disallowed_types:
                field_name = f.fgField.getName()
                data[field_name] = REQUEST.form.get(field_name,'')

        self.createLineItem(data)
        return REQUEST.response.redirect('%s/@@getpaid-checkout-wizard' % getSite().absolute_url())

    def createLineItem(self, data):
        parent = self.aq_parent
        utility = getUtility( IShoppingCartUtility )
        cart = utility.get(parent, create=True)

        intids = getUtility(IIntIds)
        iid = intids.queryId(parent)
        if iid is None:
            iid = intids.register(parent)

        nitem = PayableLineItem()
        nitem.item_id = parent.UID() # archetypes uid
        nitem.uid = iid

        # copy over information regarding the item
        nitem.name = "Supplemental Pharmacy Application"
        nitem.description = "Supplemental Pharmacy Application 2011"
        nitem.cost = float(self.price)
        nitem.quantity = 1
        nitem.product_code = nitem.item_id
        
        nitem.data = data
 
        # add to cart
        if nitem.item_id not in cart.keys():
            cart[nitem.item_id] = nitem
            cart.last_item = nitem.item_id        
            


atapi.registerType(BuyableFormAdapter, PROJECTNAME)
