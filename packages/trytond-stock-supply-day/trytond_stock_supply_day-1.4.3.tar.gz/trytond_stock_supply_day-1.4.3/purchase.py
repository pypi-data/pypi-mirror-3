#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
import datetime


class ProductSupplier(ModelSQL, ModelView):
    _name = 'purchase.product_supplier'
    weekdays = fields.One2Many('purchase.product_supplier.day', 'product_supplier',
            'Week Days')

    def compute_supply_date(self, cursor, user, product_supplier, date=None,
            context=None):
        res = super(ProductSupplier, self).compute_supply_date(cursor, user,
                product_supplier, date=date, context=context)
        earlier_date = None
        date = res[0]
        next_date = res[1]
        for day in product_supplier.weekdays:
            weekday = int(day.weekday)
            diff = weekday - date.weekday()
            if diff < 0:
                diff += 7
            new_date = date + datetime.timedelta(diff)

            if earlier_date and earlier_date <= new_date:
                continue
            earlier_date = new_date

            diff = weekday - next_date.weekday()
            if diff < 0:
                diff += 7
            new_next_date = next_date + datetime.timedelta(diff)
            res = (new_date, new_next_date)
        return res

    def compute_purchase_date(self, cursor, user, product_supplier, date,
            context=None):
        later_date = None
        for day in product_supplier.weekdays:
            weekday = int(day.weekday)
            diff = (date.weekday() - weekday) % 7
            new_date = date - datetime.timedelta(diff)
            if later_date and later_date >= new_date:
                continue
            later_date = new_date
        if later_date:
            date = later_date
        return super(ProductSupplier, self).compute_purchase_date(cursor, user,
                product_supplier, date, context=context)

ProductSupplier()


class ProductSupplierDay(ModelSQL, ModelView):
    'Product Supplier Day'
    _name = 'purchase.product_supplier.day'
    _rec_name = 'weekday'
    _description = __doc__

    product_supplier = fields.Many2One('purchase.product_supplier', 'Supplier',
            required=True)
    weekday = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
        ], 'Week Day', required=True, sort=False)

    def __init__(self):
        super(ProductSupplierDay, self).__init__()
        self._order.insert(0, ('weekday', 'ASC'))

    def default_weekday(self, cursor, user, context=None):
        return '0'

ProductSupplierDay()
