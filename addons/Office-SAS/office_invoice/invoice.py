# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.              
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp import api
from openerp.tools.translate import _
from openerp.tools import Number_To_Word

class account_invoice(osv.osv):
        
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        '''
           Calculer les montants : untaxed,tax,total,discount,undiscount et mettre à jour le montant en toute lettre
           @return:timbre
           @return:amount_untaxed
           @return:amount_tax
           @return:amount_total
           @return:discount_total
           @return:undiscount_total
        '''
        res = {}
        var='Timbre'
        cr.execute('SELECT valeur FROM account_parametre WHERE designation=%s', (var,))
        timbre = cr.dictfetchone()['valeur']
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'timbre': 0.0,
                'discount_total': 0.0,
                'amount_untaxed': 0.0,
                'undiscount_total': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
        
        for line in invoice.invoice_line:
                res[invoice.id]['discount_total'] += (line.quantity*line.price_unit)-line.price_subtotal
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
                res[invoice.id]['undiscount_total'] += line.quantity*line.price_unit
        for line in invoice.tax_line:
                    res[invoice.id]['amount_tax'] += line.amount
        res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']
        if invoice.partner_id.timbre == True and invoice.type == 'out_invoice' or invoice.type == 'in_refund':
                res[invoice.id]['amount_total'] += timbre
                res[invoice.id]['timbre'] = timbre
        if (invoice.partner_id.supplier == True and invoice.type == 'in_invoice') :
               	res[invoice.id]['amount_total'] += timbre
                res[invoice.id]['timbre'] = timbre
        
        amount_word=""
        if res[invoice.id]['amount_total'] != 0.0 :
            amount_word=Number_To_Word.Number_To_Word(res[invoice.id]['amount_total'], 'fr', 'Dinars', 'Millimes', 3)
            cr.execute('UPDATE account_invoice SET amount_word=%s WHERE id=%s', (amount_word, invoice.id)) 
              
        return res

    def _get_supplier_id(self, cr, uid):
        supplier_id = self.pool.get('stock.location').search(cr, uid, [('name', '=', 'Suppliers')])[0]
        return supplier_id

    def button_reset_taxes(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ait_obj = self.pool.get('account.invoice.tax')
        for id in ids:
            cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (id,))
            partner = self.browse(cr, uid, id, context=ctx).partner_id
            if partner.lang:
                ctx.update({'lang': partner.lang})
            for taxe in ait_obj.compute(cr, uid, id, context=ctx).values():
                ait_obj.create(cr, uid, taxe)
        # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, ids, {'invoice_line':[]}, context=ctx)

        return True
 
    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        '''
           TODO: This fuction is not in use, check the amount_total and residual problem first
           Ajouter le timbre au montant total lors de l'inirialisation du montant residual
           @return:residual
        '''
        var='Timbre'
        cr.execute('SELECT valeur FROM account_parametre WHERE designation=%s', (var,))
        timbre = cr.dictfetchone()['valeur']
        result = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            result[invoice.id] = 0.0
            if invoice.move_id:
                for m in invoice.move_id.line_id:
                    if ((m.account_id.type in ('receivable','payable')) and (invoice.partner_id.timbre == True)):
                        result[invoice.id] += m.amount_residual_currency+timbre
                    elif m.account_id.type in ('receivable','payable'):
                        result[invoice.id] += m.amount_residual_currency +timbre
        return result
     
    def onchange_location_dest_id(self, cr, uid, ids, location_dest_id):
        return {'domain':{'cash_id':[('location_id','=',location_dest_id),('state','=','open')]}}    
   
    def action_date_assign(self, cr, uid, ids, *args):
        ''' 
           Creer les mouvements de stocks pour les lignes de facture au comptant
           
        '''
        for inv in self.browse(cr, uid, ids):
            res = self.onchange_payment_term_date_invoice(cr, uid, inv.id, inv.payment_term.id, inv.date_invoice)
            if res and res['value']:
                self.write(cr, uid, [inv.id], res['value'])
            todo_moves = []
            
 	    for invoice_line in inv.invoice_line:
                if not invoice_line.product_id:
                    continue
                if  inv.type =='in_invoice' or inv.type =='out_refund':#
                    location_id = 8 #Partner locations/Suppliers
                    location_dest_id = 12 #Stock
                else:
                    location_id = 12 #Stock
                    location_dest_id = 9 #Partner locations/Customers
                if invoice_line.product_id.product_tmpl_id.type in ('consu'):    
                    move = self.pool.get('stock.move').create(cr, uid, {
                        'name': (invoice_line.name ),
                        'product_id': invoice_line.product_id.id,
                        'location_id': location_id,
                        'location_dest_id': location_dest_id,
                        'partner_id': inv.partner_id.id,
                        'invoice_id': inv.id,
                        'product_uom_qty': invoice_line.quantity,
                        'product_uom': invoice_line.uos_id.id,
                        'product_uos': invoice_line.uos_id.id,
                        'state': 'done',
                        'price_unit': invoice_line.price_unit,
                        'picking_type_id':1,
                    })
                if invoice_line.move_dest_id:
                    self.pool.get('stock.move').write(cr, uid, [invoice_line.move_dest_id],)
                todo_moves.append(move)
        return True

    @api.multi
    def invoice_validate(self):
        self._cr.execute("SELECT amount_total FROM account_invoice WHERE id =%s ",(self.id,))
        reste_a_payer = self._cr.dictfetchone()['amount_total']
        self._cr.execute("UPDATE account_invoice SET reste_a_payer=%s WHERE id =%s ",(reste_a_payer,self.id,))
        return self.write({'state': 'open'})

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_from_line(self, cr, uid, ids, context=None):
        move = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids

    def _get_invoice_from_reconcile(self, cr, uid, ids, context=None):
        move = {}
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids, context=context):
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True

        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids

    _name = "account.invoice"
    _order = "id desc"
    _inherit = 'account.invoice'

    _columns = {
        'amount_word': fields.char('Lettre', size=254,readonly=True),
	'timbre': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Timbre', store=True, method=True,multi='all'),
        #'amount_word': fields.char('Lettre', size=254),
        'undiscount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total sans remise', store=True, method=True, multi='all'),
        'discount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total Remise', store=True, method=True, multi='all'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total taxe', store=True, method=True, multi='all'),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total NHT', store=True, method=True, multi='all'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total', store=True, method=True, multi='all'),
        'date_invoice': fields.date('Invoice Date', required=True,readonly=True,states={'draft': [('readonly', False)]}),
	'residual': fields.function(_amount_residual, method=True, digits_compute=dp.get_precision('Account'), string='Residual',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line','move_id','amount_total'], 50),
                'account.invoice.tax': (_get_invoice_tax, None, 50),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 50),
                'account.move.line': (_get_invoice_from_line, None, 50),
                'account.move.reconcile': (_get_invoice_from_reconcile, None, 50),
            },
            help="Remaining amount due."),
	'location_dest_id': fields.many2one('stock.location', 'Destination Location', states={'open': [('readonly', True)]}, help="Location where the system will stock the finished products."),
        'location_src_id': fields.many2one('stock.location', 'Source Location', states={'open': [('readonly', True)]}),
	'number_invoicing_picking': fields.char('Code Facture', size=32),
        'montant_retenue':fields.float('Montant Retenue', digits_compute=dp.get_precision('Account')),
        'reste_a_payer':fields.float('Reste à payer', digits_compute=dp.get_precision('Account'), readonly=True),
    }
     
account_invoice()

class account_invoice_line(osv.osv):
    
    _name = "account.invoice.line"
    _inherit = 'account.invoice.line'
    _columns = {
        'move_dest_id': fields.many2one('stock.move', 'Reservation Destination', ondelete='set null'),
    }

account_invoice_line()

class account_invoice_tax(osv.osv):

    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line:
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                }
                if invoice.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])

        return tax_grouped

    @api.v7
    def compute(self, cr, uid, invoice_id, context=None):
        recs = self.browse(cr, uid, [], context)
        invoice = recs.env['account.invoice'].browse(invoice_id)
        return recs.compute(invoice)
    _name = "account.invoice.tax"
    _inherit = 'account.invoice.tax'

    
    _columns = {
        'name': fields.char('Tax Description', size=64, required=True),
    }

account_invoice_tax()

class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = 'stock.move'
    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Reference Facture', select=True,states={'done': [('readonly', True)]}),
    }
stock_move()

