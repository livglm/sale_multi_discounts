from openerp import fields, models, api,exceptions, _
import openerp.addons.decimal_precision as dp
import re

class account_invoice_line_disc(models.Model):
    _inherit = "account.invoice.line"

    multi_discount = fields.Char(
        'Discount',
        default = ''
        )
    discount = fields.Float(
        compute='get_discount',
        store=True,
        readonly=True
        )

    @api.one
    @api.depends('multi_discount')
    def get_discount(self):
        discount_factor = 1.0
        disc = ''
        disc = self.multi_discount
        if disc :
            discounts = disc.split("+")
            for discount in discounts:
                discount_factor = discount_factor * ((100.0 - float(discount)) / 100.0)
                self.discount = 100.0 - (discount_factor * 100.0)


    @api.onchange('multi_discount')
    def discount_onchange(self):
        if self.multi_discount:
            p = re.compile('^[0-9+.]')
            m = p.search(self.multi_discount)
            print m
            if not m or self.multi_discount[-1:]=='+' or self.multi_discount[-1:]=='.' or self.multi_discount == '':
                raise exceptions.Warning(
                    _('You have entered an invalid character or did not use a number as the last character. '
                        'The allowed characters are : 0 1 2 3 4 5 6 7 8 9 + .'))
        else:
            self.multi_discount = ''
