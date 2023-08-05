import base64
import datetime
import decimal
import logging
import re

from core import make_request

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

class Item(object):
    def __init__(self, **kwargs):
        required_properties = 'id title price'.split()
        for prop in required_properties:
            if prop not in kwargs:
                raise ValueError('{0} property must be provided'.format(prop))
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def as_dict(self):
        logging.debug('as_dict')
        properties = []
        d = {}
        for attr in dir(self.__class__):
            logging.debug('as_dict first loop {0}'.format(attr))
            ca = getattr(self.__class__, attr)
            if hasattr(ca, 'fget') and hasattr(ca, '__doc__'):
                properties.append(attr)
        for prop in properties:
            logging.debug('as_dict second loop {0}'.format(prop))
            ca = getattr(self.__class__, prop)
            key = ca.__doc__
            value = ca.fget(self)
            if key is not None and value is not None and value != '':
                d[key] = value

        return d

    @property
    def id(self):
        '''MerchantItemId'''
        return self._id
    @id.setter
    def id(self, value):
        value = unicode(value)
        if not re.match(r'[a-zA-Z0-9]+', value):
            raise ValueError('id must be alphanumeric only')
        self._id = value

    _sku = None
    @property
    def sku(self):
        '''SKU'''
        return self._sku
    @sku.setter
    def sku(self, value):
        self._sku = unicode(value)

    @property
    def title(self):
        '''Title'''
        return self._title
    @title.setter
    def title(self, value):
        self._title = unicode(value)

    _desc = None
    @property
    def description(self):
        '''Description'''
        return self._desc
    @description.setter
    def description(self, value):
        self._desc = unicode(value)

    @property
    def price(self):
        '''UnitPrice.Amount'''
        return self._price
    @price.setter
    def price(self, value):
        value = decimal.Decimal(unicode(value)).quantize(
            decimal.Decimal('0.01'), rounding=decimal.ROUND_DOWN
        )
        if value < 0:
            raise ValueError('price must be non-negative')
        self._price = value

    _currency = u'USD'
    @property 
    def currency(self):
        '''UnitPrice.CurrencyCode'''
        return self._currency
    @currency.setter
    def currency(self, value):
        value = unicode(value).upper()
        if len(value) != 3:
            raise ValueError('Invalid currency code')
        self._currency = value

    _quantity = 1
    @property
    def quantity(self):
        '''Quantity'''
        return self._quantity
    @quantity.setter
    def quantity(self, value):
        value = int(value)
        if value < 1:
            raise ValueError('quantity must be at least 1')

    _url = None
    @property
    def url(self):
        '''URL'''
        return self._url
    @url.setter
    def url(self, value):
        self._url = unicode(value)

    _category = None
    @property
    def category(self):
        '''Category'''
        return self._category
    @category.setter
    def category(self, value):
        self._category = unicode(value)

    _fulfillment = None
    @property
    def fulfillment(self):
        '''FulfillmentNetwork'''
        return self._fulfillment
    @fulfillment.setter
    def fulfillment(self, value):
        value = unicode(value)
        valid = u'MERCHANT AMAZON_NA'.split
        if value not in valid:
            raise ValueError('fulfillment must be one of {0}'.format(valid))
        self._fulfillment = value

    _custom_data = ''
    @property
    def custom_data(self):
        return base64.b64decode(self._custom_data)
    @property
    def custom_data_base64(self):
        '''ItemCustomData'''
        return self._custom_data
    @custom_data.setter
    def custom_data(self, value):
        value = base64.b64encode(unicode(value))
        if len(value) > 1024:
            raise ValueError('custom_data too long')
        self._custom_data = value

    _product_type = None
    @property
    def product_type(self):
        '''ProductType'''
        return self._product_type
    @product_type.setter
    def product_type(self, value):
        self._product_type = unicode(value).upper()

    _weight = None
    @property
    def weight(self):
        '''PhysicalProductAttributes.Weight.Value'''
        return self._weight
    @weight.setter
    def weight(self, value):
        value = decimal.Decimal(unicode(value)).quantize(
            decimal.Decimal('0.0001'), rounding=decimal.ROUND_UP
        )
        if value < 0:
            raise ValueError('weight must be non-negative')

        self._weight = weight

    _weight_unit = None
    @property
    def weight_unit(self):
        '''PhysicalProductAttributes.Weight.Unit'''
        if self.weight is not None and self._weight_unit is None:
            raise ValueError('weight and weight_unit are mutually inclusive')
        return self._weight_unit
    @weight_unit.setter
    def weight_unit(self, value):
        self._weight_unit = unicode(value)

    _condition = None
    @property
    def condition(self):
        '''PhysicalProductAttributes.Condition'''
        return self._condition
    @condition.setter
    def condition(self, value):
        valid = u'Any Club Collectible New Refurbished New'.split()
        value = unicode(value)
        if value not in valid:
            raise ValueError('condition must be one of {0}'.format(valid))
        self._condition = value

    _shipping_level = u'Standard'
    @property
    def shipping_level(self):
        '''PhysicalProductAttributes.DeliveryMethod.ServiceLevel'''
        return self._shipping_level
    @shipping_level.setter
    def shipping_level(self, value):
        valid = u'Standard OneDay TwoDay Expedited'.split()
        value = unicode(value)
        if value not in valid:
            raise ValueError('shipping_level must be one of {0}'.format(valid))
        self._shipping_level = value

    _shipping_level_label = None
    @property
    def shipping_level_label(self):
        '''PhysicalProductAttributes.DeliveryMethod.DisplayableShippingLabel'''
        return self._shipping_level_label
    @shipping_level_label.setter
    def shipping_level_label(self, value):
        self._shipping_level_label = unicode(value)

    _shipping_dest = u'#default'
    @property
    def shipping_dest(self):
        '''PhysicalProductAttributes.DeliveryMethod.DestinationName'''
        return self._shipping_dest
    @shipping_dest.setter
    def shipping_dest(self, value):
        self._shipping_dest = unicode(value)

    _shipping_custom_data = ''
    @property
    def shipping_custom_data(self):
        return base64.b64decode(self._shipping_custom_data)
    @property
    def shipping_custom_data_base64(self):
        '''PhysicalProductAttributes.DeliveryMethod.ShippingCustomData'''
        return self._shipping_custom_data
    @shipping_custom_data.setter
    def shipping_custom_data(self, value):
        value = base64.b64encode(unicode(value))
        if len(value) > 1024:
            raise ValueError('shipping_custom_data too long')
        self._shipping_custom_data = value

    _shipping_amount = decimal.Decimal('0')
    @property
    def shipping(self):
        '''PhysicalProductAttributes.ItemCharges.Shipping.Amount'''
        return self._shipping_amount
    @shipping.setter
    def shipping(self, value):
        value = decimal.Decimal(unicode(value)).quantize(
            decimal.Decimal('0.01'), rounding.ROUND_DOWN
        )
        if value < 0:
            raise ValueError('shipping amount must be non-negative')
        self._shipping_amount = value

    @property
    def shipping_currency(self):
        '''PhyiscalProductAttributes.ItemCharges.Shipping.CurrencyCode'''
        return self.currency

class Order(object):
    def __init__(self, items=[]):
        self.items = list(items)

    def add_item(self, item):
        self.items.append(item)

    @property
    def price(self):
        total = 0
        for item in items:
            total += item.price * item.quantity
        return total

    @property
    def shipping(self):
        total = 0
        for item in items:
            total += item.shipping * item.quantity
        return total

class PurchaseContract(object):
    def __init__(self, id=None, settings={}):
        self.settings = dict(settings)
        if id is None:
            id_list, request_id = make_request(
                'POST',
                'CreatePurchaseContract',
                {
                    'DirectedId': '',
                    'AuthorizationToken': '',
                },
                settings,
            )
            self.id = id_list[0]
        else:
            self.id = id

        self.destinations = {}
        self.order = Order()
        self.completed = False
        self.update()

    def update(self):
        params = {
            'PurchaseContractId': self.id,
        }
        contract_list, request_id = make_request('GET', 'GetPurchaseContract', params, self.settings)
        contract = contract_list[0]
        assert contract.Id.text == self.id
        self.state = contract.State.text
        self.merchant_id = contract.MerchantId.text
        self.marketplace_id = contract.MarketplaceId.text
        self.expires = datetime.datetime.strptime(
            contract.ExpirationTimeStamp.text,
            '%Y-%m-%dT%H:%M:%S.%fZ',
        )
        try:
            for dest in contract.Destinations.Destination[:]:
                address = dest.PhysicalDestinationAttributes.ShippingAddress
                self.add_destination(
                    dest_name = dest.DestinationName.text,
                    name = address.Name.text,
                    address = [], # ??? Didn't get an address from Amazon while testing this.
                    city = address.City.text,
                    state = address.StateOrProvinceCode.text,
                    country_code = address.CountryCode.text,
                    phone = address.PhoneNumber.text,
                )

        except AttributeError:
            pass # No destinations chosen yet

    def add_destination(self, dest_name, name, address, city, state, country_code='US', phone=''):
        if self.completed:
            logging.warn('This contract has already been completed.')
        self.destinations[dest_name] = {
            'dest-name': dest_name,
            'dest-type': 'PHYSICAL',
            'address': {
                'name': name,
                'address': address,
                'city': city,
                'state': state,
                'country-code': country_code,
                'phone-number': phone,
            },
        }
        return len(self.destinations)

    def complete(self):
        self.completed = True
        try:
            params = {'PurchaseContractId': self.id}
            order_ids, request_id = make_request('POST', 'CompletePurchaseContract', params, self.settings)
        except:
            self.completed = False
            raise

class Settings(object):
    secret_access_key = ''
    public_access_key = ''

    merchant_id = ''
    marketplace_id = ''

    sandbox = True

    def __init__(self, **kwargs):
        for k,v in kwargs.iteritems():
            setattr(self, k, v)

    def __iter__(self):
        return self.as_dict().iteritems()

    def as_dict(self):
        keys = 'secret_access_key public_access_key merchant_id marketplace_id sandbox'.split()
        transform_key = lambda key: key.replace('_', '-')
        return dict((transform_key(key), getattr(self, key)) for key in keys)
