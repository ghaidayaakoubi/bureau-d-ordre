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
from datetime import datetime,timedelta
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp import api
from openerp.tools.translate import _
from openerp.tools import Number_To_Word

class account_invoice(osv.osv):

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_amount(self):
        self.amount_untaxed = sum(round(line.price_subtotal,3) for line in self.invoice_line)
        self.amount_tax = round(sum(round(line.amount,3) for line in self.tax_line),3)



        if self.partner_id.exoner == True:
		self.amount_tax=0.0
        self.amount_total = round((self.amount_untaxed + self.amount_tax),3)
        if self.partner_id.timbre == True:
		self.amount_total = round((self.amount_untaxed + self.amount_tax+self.timbre),3)



    @api.model
    def _default_currency(self):
        journal = self._default_journal()
        return journal.currency or journal.company_id.currency_id
      
  
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


                res[invoice.id]['discount_total'] += line.quantity*line.price_unit-line.price_subtotal
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
                res[invoice.id]['undiscount_total'] += line.quantity*line.price_unit
        for line in invoice.tax_line:
                    res[invoice.id]['amount_tax'] +=line.amount



	if invoice.partner_id.exoner:
		res[invoice.id]['amount_tax'] = 0
        res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']

        if invoice.partner_id.timbre == True and invoice.type == 'out_invoice' or invoice.type == 'in_refund':

                res[invoice.id]['amount_total'] +=timbre

                res[invoice.id]['timbre'] = timbre
        if (invoice.partner_id.timbre == True and invoice.type == 'in_invoice') :
               	res[invoice.id]['amount_total'] += timbre
                res[invoice.id]['timbre'] =timbre
        
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
 	    move=0            
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

    def _rappel_payement_facture(self, cr,ids, uid, context=None):

		print "dans rappel_payement_facture( *********** "
	
		date1= (datetime.now() + timedelta(days=7)).date()
		print "date now =====",date1 
		reg_ids =  self.pool.get('account.invoice').search(cr, uid, [('state','not in',['draft','paid']),('type','=','in_invoice')])
		date= date1.strftime('%Y-%m-%d')
		for facture in self.browse(cr, uid, reg_ids):
			print "facture date_due ====",facture.date_due
			if facture.type=='in_invoice':
				print "dans facture.type== 88888888888"
				if facture.date_due==date :
					cr.execute('SELECT id FROM res_users')
		 			record=cr.dictfetchall()
		 			print "record =======",record
		 			for user in record:
			
						user_id=user['id']
						mail_vals = {
								'body':'<html>Vous avez une facture doit etre payer </html>',
								'record_name':facture.number,
								'res_id':facture.id,
								'reply_to':self.pool.get('res.users').browse(cr, uid, uid, context=context).name,
								'author_id':self.pool.get('res.users').browse(cr, uid, uid, context=context).partner_id.id,
								'model':'account.invoice',
								'type':'comment',
								'email_from':self.pool.get('res.users').browse(cr, uid, uid, context=context).name,
								'starred':True,
						}
						message = self.pool.get('mail.message').create(cr, uid, mail_vals) 
						print "messages reeeeeeeeeeeeeeeeeeeeeee" 
					
						mail_notif_vals = {
								'partner_id':self.pool.get('res.users').browse(cr, uid,user_id, context=context).partner_id.id,
								'message_id':message,
								'is_read':False,
								'starred':True,
						
						}
						self.pool.get('mail.notification').create(cr, uid, mail_notif_vals)
						print "notiiiiiiiiifffffff reeeeeeeeeeeeeeeeeeeeeee" 


    _name = "account.invoice"
    _order = "id desc"
    _inherit = ['account.invoice', 'mail.thread']

    _columns = {
        'amount_word': fields.char('Lettre', size=254,readonly=True),

	'timbre': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Timbre', store=True, method=True,multi='all'),
        #'amount_word': fields.char('Lettre', size=254),
        'undiscount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total sans remise', store=True, method=True, multi='all'),
        'discount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total Remise', store=True, method=True, multi='all'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total taxe', store=True, method=True, multi='all'),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total NHT', store=True, method=True, multi='all'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total', store=True, method=True, multi='all'),
        'date_invoice': fields.date('Invoice Date', required=True,readonly=False,states={'draft': [('readonly', False)],'open': [('readonly', False)],'paid': [('readonly', False)],'proforma': [('readonly', False)],'proforma2': [('readonly', False)],'ppaid': [('readonly', False)]}),
	'currency_id': fields.many2one('res.currency', 'Devise', required=True, ),
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
	'mode_reg': fields.char('Mode reglément ', size=100),
	'state' :fields.selection([
	    ('draft', 'Draft'),
	    ('proforma', 'Pro-forma'),
	    ('proforma2', 'Pro-forma'),
	    ('open', 'Open'),
	    ('ppaid','Partiellement Payee'),
	    ('paid', 'Paid'),
	    ('cancel', 'Cancelled'),
	    ('annule','Annulée'),
	    ], string='Status', index=True, readonly=True, default='draft',
	    track_visibility='onchange', copy=False,
	    help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
		 " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
		 " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
		 " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
		 " * The 'Cancelled' status is used when user cancel invoice."),
	'date_due' :fields.date(string='Due Date',readonly=True, required=True,states={'draft': [('readonly', False)],'open': [('readonly', False)]},  copy=False),
    }
    _defaults = {
        'currency_id': _default_currency,
    }


account_invoice()

class account_invoice_line(osv.osv):
    
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)

        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)

        self.price_subtotal = taxes['total']

        if self.invoice_id:
            #self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)
            self.price_subtotal = self.price_subtotal


    _name = "account.invoice.line"
    _inherit = 'account.invoice.line'
    _columns = {
        'move_dest_id': fields.many2one('stock.move', 'Reservation Destination', ondelete='set null'),
	#'discount': fields.float('Remise',digits=(16,2)),
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
                print "taaaaaaaaaaaaaaaaaaaaaaaaaaaxx",tax['amount']
                val = {
                    'invoice_id': invoice.id,
                    #'name': tax['name'],
                    'name': tax['name'][-3:].replace('-',''),
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
            #t['amount'] = currency.round(t['amount'])
            t['amount'] = t['amount']
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

