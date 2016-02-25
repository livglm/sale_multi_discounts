from openerp import fields, models, api,exceptions, _
import openerp.addons.decimal_precision as dp
import re

class stock_move_disc(models.Model):
    _inherit = "stock.move"

    multi_discount = fields.Char(
        'Discount',
        readonly=True,
        default = '',
        states={'draft': [('readonly', False)]}
        )
    discount = fields.Float(
         compute='get_discount',
         store=True,
         readonly=True,
         # states={}
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


    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        fp_obj = self.pool.get('account.fiscal.position')
        # Get account_id
        fp = fp_obj.browse(cr, uid, context.get('fp_id')) if context.get('fp_id') else False
        name = False
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = move.product_id.property_account_income.id
            if not account_id:
                account_id = move.product_id.categ_id.property_account_income_categ.id
            if move.procurement_id and move.procurement_id.sale_line_id:
                name = move.procurement_id.sale_line_id.name
        else:
            account_id = move.product_id.property_account_expense.id
            if not account_id:
                account_id = move.product_id.categ_id.property_account_expense_categ.id
        fiscal_position = fp or partner.property_account_position
        account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)

        # set UoS if it's a sale and the picking doesn't have one
        uos_id = move.product_uom.id
        quantity = move.product_uom_qty
        if move.product_uos:
            uos_id = move.product_uos.id
            quantity = move.product_uos_qty

        taxes_ids = self._get_taxes(cr, uid, move, context=context)
        print move.multi_discount
        return {
            'name': name or move.name,
            'account_id': account_id,
            'product_id': move.product_id.id,
            'uos_id': uos_id,
            'quantity': quantity,
            'price_unit': self._get_price_unit_invoice(cr, uid, move, inv_type),
            'invoice_line_tax_id': [(6, 0, taxes_ids)],
            'discount':move.discount,
            'multi_discount': move.multi_discount,
            'account_analytic_id': False,
        }
