from openerp import fields, models, api,exceptions, _
import openerp.addons.decimal_precision as dp
import re

class sale_order_line_disc(models.Model):
    _inherit = "sale.order.line"

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
        try:
            if disc :
                discounts = disc.split("+")
                for discount in discounts:
                    discount_factor = discount_factor * ((100.0 - float(discount)) / 100.0)
                    self.discount = 100.0 - (discount_factor * 100.0)
        except:
            raise exceptions.Warning(
                _('You2 have entered an invalid character or did not use a number as the last character. '
                  'The allowed characters are : 0 1 2 3 4 5 6 7 8 9 + .'))
            #return False



    @api.multi
    @api.onchange('multi_discount')
    def discount_onchange(self):
        if self.multi_discount:
            #p = re.compile('[0-9+.]')
            #m = p.finditer(self.multi_discount)
            # m = re.search('^[0-9+.]*',self.multi_discount)
            # print m
            # if m or self.multi_discount[-1:]=='+' or self.multi_discount[-1:]=='.' or self.multi_discount == '':
            #     raise exceptions.Warning(
            #         _('You have entered an invalid character or did not use a number as the last character. '
            #             'The allowed characters are : 0 1 2 3 4 5 6 7 8 9 + .'))
            #     return False
            record = self.multi_discount
            print record
            pattern ="^[0-9+.]$"
            for char in record:
                print char
                if re.match(pattern, char):
                    return True
                else:
                    raise exceptions.Warning(
                        _('You have entered an invalid character or did not use a number as the last character. '
                          'The allowed characters are : 0 1 2 3 4 5 6 7 8 9 + .'))
                    return False
        else:
             self.multi_discount = ''

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):

        res = super(sale_order_line_disc, self)._prepare_order_line_invoice_line(
            cr, uid, line, account_id=False, context=context
        )
        res.update({
            'multi_discount': line.multi_discount,
            })
        return res


class sale_order_disc(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_button_confirm(self):

        picking_vals = super(sale_order_disc, self).action_button_confirm()

        proc_obj = self.env['procurement.order']

        for lines in self.env['sale.order.line'].search([('order_id','=',self.id)]):
            proc_id = proc_obj.search([('sale_line_id','=',lines.id)])
            moves = self.env['stock.move'].search([('procurement_id','=',proc_id.id)])
            moves.write({'multi_discount': lines.multi_discount})

