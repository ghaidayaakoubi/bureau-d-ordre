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
from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _


class stock_picking(osv.osv):
    _name = 'stock.picking'
    _inherit = 'stock.picking'
    _order = "name desc, id desc"

    # added by salwa ksila
    def set_copy_data(self, cr, uid, ids, vals, context=None):

        invoice_state = self.browse(cr, uid, ids, context=context).invoice_state
        # ------------------------------------------------------------------------------------------------
        # BL a une controle de facturation égale à Facturé
        # ------------------------------------------------------------------------------------------------

        if invoice_state == 'invoiced':
            ##---------------------------search FBL ---------------------------------------------##

            ref = self.browse(cr, uid, ids, context=context).name

            id_bl = ids[0]

            # cr.execute('UPDATE stock_picking SET state=%s WHERE  id =%s',
            #            ('cancel', id_bl))

            self.write(cr, uid, ids, {'name': False}, context=None)
            self.write(cr, uid, ids, {'origin': ref}, context=None)

            picking_obj = self.pool.get('stock.picking')

            pick_enr = picking_obj.browse(cr, uid, ids)

            active_id = picking_obj.browse(cr, uid, ids).id

            partner_id = self.browse(cr, uid, ids, context=context).partner_id.id

            ref_description = self.browse(cr, uid, ids, context=context).ref_description

            currency_id = self.browse(cr, uid, ids, context=context).currency_id.id

            date = self.browse(cr, uid, ids, context=context).date

            min_date = self.browse(cr, uid, ids, context=context).min_date

            sale_order_id = self.browse(cr, uid, ids, context=context).sale_order_id.id

            val = {
                'name': ref,
                'partner_id': partner_id,
                'ref_description': ref_description,
                'currency_id': currency_id,
                'date': date,
                'min_date': min_date,
                'sale_order_id': sale_order_id,
                'move_lines': '',
                'tax_line': '',
            }

            inv_id = self.pool.get('stock.picking').copy(cr, uid, active_id, val)

            default = {'name': ref, 'partner_id': partner_id}

            picking_obj = self.browse(cr, uid, ids)

            inv_pick_obj = self.pool.get('invoice.picking').browse(cr, uid, ids)

            inv_pick_line_obj = self.pool.get('invoice.picking.line').browse(cr, uid, ids)

            cr.execute('SELECT * FROM invoice_picking_line WHERE picking_id =%s', (picking_obj.id,))
            lines = cr.dictfetchall()
            for line in lines:
                p_id = line['invoice_picking_id']

                cr.execute('SELECT * FROM invoice_picking WHERE id =%s', (p_id,))
                lines_inv_pick = cr.dictfetchall()

                for line in lines_inv_pick:
                    internal_number = line['internal_number']

                    date_invoice_picking = line['date_invoice_picking']

                    partner_id = line['partner_id']

                    currency_id = line['currency_id']

                    discount_total = line['discount_total']

                    mode_reglement = line['mode_reglement']

                    amount_untaxed = line['amount_untaxed']

                    amount_tax = line['amount_tax']

                    amount_word = line['amount_word']

                    type = line['type']

                    date_invoice_picking = line['date_invoice_picking']

                    discount_total = line['discount_total']

                    amount_total = line['amount_total']

                    timbre = line['timbre']

                    user_id = line['user_id']

                    create_uid = line['create_uid']
                    ##----------------------supprimer reference du facture BL---------------------------------##

                    internal_number = self.pool.get('invoice.picking').browse(cr, uid, p_id).internal_number

                    inv = self.pool.get('invoice.picking').write(cr, uid, p_id, {'internal_number': False},
                                                                 context=None)
                    # ajouter par salwa le 16/05/2017 pour le statu annulee
                    inv = self.pool.get('invoice.picking').write(cr, uid, p_id, {'state': 'cancel'},
                                                                 context=None)

                    ##-----------------------create FBL avec la meme reference------------------------------##

                    cr.execute(
                        "INSERT INTO invoice_picking (internal_number, date_invoice_picking, currency_id,company_id,type,partner_id,state,user_id,create_uid) VALUES ('%s', '%s', '%s', '%s','%s','%s','%s','%s','%s')"
                        % (internal_number, date_invoice_picking, 1, 1, type, partner_id, 'draft', user_id, create_uid))

                    ##---------------------annuler la reference de facture client -----------------------##
                    id_stock_pick = picking_obj.internal_number_invoice

                    cr.execute('SELECT * FROM invoice_picking WHERE internal_number =%s', (id_stock_pick,))
                    lines = cr.dictfetchall()
                    for line in lines:
                        id_invoice = line['id']

                        id_invoice_pick = line['internal_number']

                        cr.execute('SELECT * FROM account_invoice WHERE internal_number =%s', (id_invoice_pick,))
                        lines = cr.dictfetchall()
                        for line in lines:
                            number = line['number']

                            id_acc_inv = line['id']

                            inv_acc = self.pool.get('account.invoice').write(cr, uid, id_acc_inv, {'number': False},
                                                                             context=None)
                            inv_acc = self.pool.get('account.invoice').write(cr, uid, id_acc_inv,
                                                                             {'state': 'cancel'},
                                                                             context=None)

            # ------------------------------------------------------------------------------------------------
            # BL a une controle de facturation égale à non applicable
            # ------------------------------------------------------------------------------------------------
        if invoice_state == 'none':
            ref = self.browse(cr, uid, ids, context=context).name

            self.write(cr, uid, ids, {'name': False}, context=None)
            self.write(cr, uid, ids, {'origin': ref}, context=None)
            # ajouter par salwa le 16/05/2017 pour le statu annulee
            # self.pool.get('stock.picking').write(cr, uid, ids, {'state': 'cancel'}, context=None)
            # ,
            #                                                                          {'state': 'cancel'},
            #                                                                          context=None)
            # --------------------duplication  de BL avec la meme reference-------------------##

            picking_obj = self.pool.get('stock.picking')

            partner_id = self.browse(cr, uid, ids, context=context).partner_id.id

            ref_description = self.browse(cr, uid, ids, context=context).ref_description

            currency_id = self.browse(cr, uid, ids, context=context).currency_id.id

            date = self.browse(cr, uid, ids, context=context).date

            min_date = self.browse(cr, uid, ids, context=context).min_date

            sale_order_id = self.browse(cr, uid, ids, context=context).sale_order_id.id

            move_lines = self.browse(cr, uid, ids, context=context).move_lines

            default = {'name': ref, 'partner_id': partner_id}

            active_id = picking_obj.browse(cr, uid, ids).id

            val = {
                'name': ref,
                'partner_id': partner_id,
                'ref_description': ref_description,
                'currency_id': currency_id,
                'date': date,
                'min_date': min_date,
                'sale_order_id': sale_order_id,
                'move_lines': '',
                'tax_line': '',

            }

            inv_id = self.pool.get('stock.picking').copy(cr, uid, active_id, val)

        return {
            'name': _('My Form'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.return.picking',
            # 'view_id ref="stock.view_stock_return_picking_form"': True,
            'type': 'ir.actions.act_window',
        }

    # def get_cancel_state(self, cr, uid, ids, context=None):
    #     self.set_copy_data(self, cr, uid, ids,context=None)
    #     id_bl = ids[0]
    #     
    #     cr.execute('UPDATE stock_picking SET state=%s WHERE  id =%s',
    #                ('cancel', id_bl))
    #     return True



    def _get_picking_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('stock.picking.tax').browse(cr, uid, ids, context=context):
            result[tax.picking_id.id] = True

        return result.keys()

    def _get_move(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            result[line.picking_id.id] = True
        return result.keys()

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        '''
           Methode qui calcule et retourne les montants suivants
           @return:amount_untaxed
           @return:amount_tax
           @return:amount_total
           @return:undiscount_total
           @return:discount_total
           
        '''
        res = {}
        for pick in self.browse(cr, uid, ids, context=context):
            res[pick.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'undiscount_total': 0.0,
                'discount_total': 0.0,
            }

            for line in pick.move_lines:
                res[pick.id]['amount_untaxed'] += line.price_subtotal
                res[pick.id]['discount_total'] += line.product_qty * line.price_unit * ((line.discount or 0.0) / 100.0)
                res[pick.id]['undiscount_total'] += line.product_qty * line.price_unit

            for line in pick.tax_line:
                res[pick.id]['amount_tax'] += line.amount
            if pick.partner_id.exoner:
                res[pick.id]['amount_tax'] = 0
            res[pick.id]['amount_total'] = res[pick.id]['amount_tax'] + res[pick.id]['amount_untaxed']
            return res

    def get_min_max_date(self, cr, uid, ids, field_name, arg, context=None):
        """ Finds minimum and maximum dates for picking.
        @return: Dictionary of values
        """
        res = {}
        for id in ids:
            res[id] = {'min_date': False, 'max_date': False, 'priority': '1'}
        if not ids:
            return res
        cr.execute("""select
                picking_id,
                min(date_expected),
                max(date_expected),
                max(priority)
            from
                stock_move
            where
                picking_id IN %s
            group by
                picking_id""", (tuple(ids),))
        for pick, dt1, dt2, prio in cr.fetchall():
            res[pick]['min_date'] = dt1
            res[pick]['max_date'] = dt2
            res[pick]['priority'] = prio
        return res

    def _set_min_date(self, cr, uid, id, field, value, arg, context=None):
        move_obj = self.pool.get("stock.move")
        if value:
            move_ids = [move.id for move in self.browse(cr, uid, id, context=context).move_lines]
            move_obj.write(cr, uid, move_ids, {'date_expected': value}, context=context)

    def _get_pickings_dates_priority(self, cr, uid, ids, context=None):
        res = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.picking_id and (not (
                            move.picking_id.min_date < move.date_expected < move.picking_id.max_date) or move.priority > move.picking_id.priority):
                res.add(move.picking_id.id)
        return list(res)

    _columns = {
        # 'purchase_id': fields.many2one('purchase.order', 'Commande',states={'done':[('readonly',True)]},),
        # 'do_filter':fields.boolean('Filtrer les produits selon BC'),



        'discount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), method=True,
                                          string='Total Remise',
                                          store=True,
                                          multi='all'),
        'undiscount_total': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'),
                                            string='Total HT',
                                            store=True,
                                            multi='all'),
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'),
                                          string='Untaxed',
                                          store={
                                              'stock.picking': (
                                                  lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                                              'stock.picking.tax': (_get_picking_tax, None, 20),
                                              'stock.move': (_get_move,
                                                             ['price_unit', 'move_tax_id', 'quantity', 'discount',
                                                              'picking_id'], 20),
                                          },
                                          multi='all'),
        'amount_tax': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'),
                                      string='Tax',
                                      store={
                                          'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                                          'stock.picking.tax': (_get_picking_tax, None, 20),
                                          'stock.move': (_get_move,
                                                         ['price_unit', 'move_tax_id', 'quantity', 'discount',
                                                          'picking_id'], 20),
                                      },
                                      multi='all'),
        'amount_total': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'),
                                        string='Total',
                                        store={
                                            'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                                            'stock.picking.tax': (_get_picking_tax, None, 20),
                                            'stock.move': (_get_move,
                                                           ['price_unit', 'move_tax_id', 'quantity', 'discount', 'picking_id'], 20),
                                        },
                                        multi='all'),

        'account_id': fields.many2one('account.account', 'Account', readonly=True,
                                      states={'draft': [('readonly', False)]},
                                      help="The partner account used for this invoice."),
        'tax_line': fields.one2many('stock.picking.tax', 'picking_id', 'Tax Lines', readonly=True,
                                    states={'draft': [('readonly', False)]}),
        # TODO à vérifier ces 2 champs s ils sont necessaires
        'number_invoice': fields.char('Code Facture', size=32, help="Unique number of the invoice"),
        'internal_number_invoice': fields.char('Numéro', size=32, readonly=True,
                                               states={'draft': [('readonly', False)]},
                                               help="Unique number of the invoice"),
        'supplier_ref': fields.char('Référence Fournisseur'),
        'ref_description': fields.char('Référence / Description'),
        'sale_order_id': fields.many2one('sale.order', 'Bon Commande', ondelete='cascade', readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'purchase_order_id': fields.many2one('purchase.order', 'Bon Commande', ondelete='cascade', readonly=True,
                                             states={'draft': [('readonly', False)]}),
        'currency_id': fields.many2one('res.currency', 'Devise', ),  # required=True


        'date': fields.datetime('Creation Date', help="Creation Date, usually the time of the order", select=True,
                                states={'done': [('readonly', False)], 'cancel': [('readonly', False)]},
                                track_visibility='onchange'),
    }

    _defaults = {
        'currency_id': 137,
    }

    def onchange_sale_order_id(self, cr, uid, ids, sale_order_id, context=None):
        value = {
            'currency_id': self.pool.get('sale.order').browse(cr, uid, sale_order_id, context=context).currency_id.id
        }

        return {'value': value}

    def onchange_purchase_order_id(self, cr, uid, ids, purchase_order_id, context=None):
        value = {
            'currency_id': self.pool.get('purchase.order').browse(cr, uid, purchase_order_id,
                                                                  context=context).currency_id.id
        }

        return {'value': value}

    def button_add_order(self, cr, uid, ids, context=None):

        obj_move = self.pool.get('stock.move')

        picking_obj = self.browse(cr, uid, ids)

        if picking_obj.picking_type_id.id == 2:

            sale_lines = self.pool.get('sale.order.line').search(cr, uid,
                                                                 [('order_id', '=', picking_obj['sale_order_id'].name)])

            sale_line = self.pool.get('sale.order.line').browse(cr, uid, sale_lines)

            for line in sale_line:
                user = self.pool.get('res.users').browse(cr, uid, uid)
                lang = user and user.lang or False

                ctx = {'lang': lang}

                product = self.pool.get('product.product').browse(cr, uid, line.product_id.id, context=ctx)

                taxes = product.taxes_id

                fposition_id = False
                fpos_obj = self.pool.get('account.fiscal.position')
                fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False
                tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)

                val = {
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                    'product_uom_qty': line.product_uom_qty,
                    'discount': line.discount,
                    'product_uom': line.product_uom.id,
                    'location_id': 12,
                    'location_dest_id': 9,
                    'default_code': line.default_code,
                    'picking_id': ids[0],
                    'picking_type_id': picking_obj.picking_type_id.id,
                    'move_tax_id': [(6, 0, tax_id)],
                }
                inv_id = obj_move.create(cr, uid, val)

        else:
            if picking_obj.picking_type_id.id == 1:

                purchases_lines = self.pool.get('purchase.order.line').search(cr, uid, [
                    ('order_id', '=', picking_obj['purchase_order_id'].name)])

                purchase_line = self.pool.get('purchase.order.line').browse(cr, uid, purchases_lines)
                order_ids = self.pool.get('purchase.order').search(cr, uid, [
                    ('name', '=', picking_obj['purchase_order_id'].name)])
                order = self.pool.get('purchase.order').browse(cr, uid, order_ids)

                for line in purchase_line:
                    user = self.pool.get('res.users').browse(cr, uid, uid)
                    lang = user and user.lang or False

                    ctx = {'lang': lang}

                    product = self.pool.get('product.product').browse(cr, uid, line.product_id.id, context=ctx)

                    taxes = product.supplier_taxes_id

                    fposition_id = False
                    fpos_obj = self.pool.get('account.fiscal.position')
                    fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False
                    tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)

                    val = {
                        'name': line.name,
                        'product_id': line.product_id.id,
                        'price_unit': line.price_unit,
                        'price_subtotal': line.price_subtotal,
                        'product_uom_qty': line.product_qty,
                        # 'product_qty':line.product_qty,
                        'discount': line.discount,
                        'product_uom': line.product_uom.id,
                        'location_id': order.partner_id.property_stock_supplier.id,
                        'location_dest_id': order.location_id.id,
                        'picking_id': ids[0],
                        'default_code': line.default_code,
                        'move_tax_id': [(6, 0, tax_id)],
                        'picking_type_id': picking_obj.picking_type_id.id,
                    }
                    inv_id = obj_move.create(cr, uid, val)

        return True

    def create_facture_bl(self, cr, uid, ids, context=None):
        bl_obj = self.browse(cr, uid, ids)
        invoice_obj = self.pool.get('invoice.picking')

        invoice_line_obj = self.pool.get('invoice.picking.line')

        ctx = context.copy()
        ctx.update({
            'type': 'out_invoice',

        })

        invoice_vals = {

            'partner_id': bl_obj.partner_id.id,
            'date_invoice_picking': bl_obj.date,
            # 'invoice_picking_line':
            'amount_untaxed': bl_obj.amount_untaxed,
            'undiscount_total': bl_obj.undiscount_total,
            'discount_total': bl_obj.discount_total,
            # 'type':'in_invoice',
            # 'internal_number':' '
        }

        inv_id = invoice_obj.create(cr, uid, invoice_vals, context=ctx)

        invoice_line_vals = {
            'picking_id': ids[0],
            'invoice_picking_id': inv_id,
            'amount_untaxed': bl_obj.amount_untaxed,
            'amount_total': bl_obj.amount_total,
            'date_picking': bl_obj.date,
            'discount_total': bl_obj.discount_total,
            'undiscount_total': bl_obj.undiscount_total,

        }
        invoice_line_obj.create(cr, uid, invoice_line_vals)

        invoice_obj.write(cr, uid, [inv_id], invoice_vals)
        invoice_obj.inv_open(cr, uid, [inv_id], context=None)

        return True

    def returntodraft(self, cr, uid, ids, context=None):
        for picking in self.browse(cr, uid, ids, context=context):
            for move in picking.move_lines:
                self.pool.get('stock.move').write(cr, uid, [move.id], {'state': 'draft'})
        self.write(cr, uid, ids, {'state': 'draft'})

        return True

    def returntodone(self, cr, uid, ids, context=None):

        for picking in self.browse(cr, uid, ids, context=context):
            for move in picking.move_lines:
                self.pool.get('stock.move').write(cr, uid, [move.id], {'state': 'done'})
        self.write(cr, uid, ids, {'state': 'done'})

        return True

    def _prepare_pack_ops(self, cr, uid, picking, quants, forced_qties, context=None):
        """ returns a list of dict, ready to be used in create() of stock.pack.operation.

        :param picking: browse record (stock.picking)
        :param quants: browse record list (stock.quant). List of quants associated to the picking
        :param forced_qties: dictionary showing for each product (keys) its corresponding quantity (value) that is not covered by the quants associated to the picking
        """

        def _picking_putaway_apply(product):
            location = False
            # Search putaway strategy
            if product_putaway_strats.get(product.id):
                location = product_putaway_strats[product.id]
            else:
                location = self.pool.get('stock.location').get_putaway_strategy(cr, uid, picking.location_dest_id,
                                                                                product, context=context)
                product_putaway_strats[product.id] = location
            return location or picking.location_dest_id.id

        # If we encounter an UoM that is smaller than the default UoM or the one already chosen, use the new one instead.
        product_uom = {}  # Determines UoM used in pack operations
        location_dest_id = None
        location_id = None
        for move in [x for x in picking.move_lines if x.state not in ('done', 'cancel')]:
            if not product_uom.get(move.product_id.id):
                product_uom[move.product_id.id] = move.product_id.uom_id
            if move.product_uom.id != move.product_id.uom_id.id and move.product_uom.factor > product_uom[
                move.product_id.id].factor:
                product_uom[move.product_id.id] = move.product_uom
            if not move.scrapped:
                # if location_dest_id and move.location_dest_id.id != location_dest_id:
                # raise Warning(_('The destination location must be the same for all the moves of the picking.'))
                location_dest_id = move.location_dest_id.id
                # if location_id and move.location_id.id != location_id:
                # raise Warning(_('The source location must be the same for all the moves of the picking.'))
                location_id = move.location_id.id

        pack_obj = self.pool.get("stock.quant.package")
        quant_obj = self.pool.get("stock.quant")
        vals = []
        qtys_grouped = {}
        # for each quant of the picking, find the suggested location
        quants_suggested_locations = {}
        product_putaway_strats = {}
        for quant in quants:
            if quant.qty <= 0:
                continue
            suggested_location_id = _picking_putaway_apply(quant.product_id)
            quants_suggested_locations[quant] = suggested_location_id

        # find the packages we can movei as a whole
        top_lvl_packages = self._get_top_level_packages(cr, uid, quants_suggested_locations, context=context)
        # and then create pack operations for the top-level packages found
        for pack in top_lvl_packages:
            pack_quant_ids = pack_obj.get_content(cr, uid, [pack.id], context=context)
            pack_quants = quant_obj.browse(cr, uid, pack_quant_ids, context=context)
            vals.append({
                'picking_id': picking.id,
                'package_id': pack.id,
                'product_qty': 1.0,
                'location_id': pack.location_id.id,
                'location_dest_id': quants_suggested_locations[pack_quants[0]],
                'owner_id': pack.owner_id.id,
            })
            # remove the quants inside the package so that they are excluded from the rest of the computation
            for quant in pack_quants:
                del quants_suggested_locations[quant]

        # Go through all remaining reserved quants and group by product, package, lot, owner, source location and dest location
        for quant, dest_location_id in quants_suggested_locations.items():
            key = (quant.product_id.id, quant.package_id.id, quant.lot_id.id, quant.owner_id.id, quant.location_id.id,
                   dest_location_id)
            if qtys_grouped.get(key):
                qtys_grouped[key] += quant.qty
            else:
                qtys_grouped[key] = quant.qty

        # Do the same for the forced quantities (in cases of force_assign or incomming shipment for example)
        for product, qty in forced_qties.items():
            if qty <= 0:
                continue
            suggested_location_id = _picking_putaway_apply(product)
            key = (product.id, False, False, picking.owner_id.id, picking.location_id.id, suggested_location_id)
            if qtys_grouped.get(key):
                qtys_grouped[key] += qty
            else:
                qtys_grouped[key] = qty

        # Create the necessary operations for the grouped quants and remaining qtys
        uom_obj = self.pool.get('product.uom')
        prevals = {}
        for key, qty in qtys_grouped.items():
            product = self.pool.get("product.product").browse(cr, uid, key[0], context=context)
            uom_id = product.uom_id.id
            qty_uom = qty
            if product_uom.get(key[0]):
                uom_id = product_uom[key[0]].id
                qty_uom = uom_obj._compute_qty(cr, uid, product.uom_id.id, qty, uom_id)
            val_dict = {
                'picking_id': picking.id,
                'product_qty': qty_uom,
                'product_id': key[0],
                'package_id': key[1],
                'lot_id': key[2],
                'owner_id': key[3],
                'location_id': key[4],
                'location_dest_id': key[5],
                'product_uom_id': uom_id,
            }
            if key[0] in prevals:
                prevals[key[0]].append(val_dict)
            else:
                prevals[key[0]] = [val_dict]
        # prevals var holds the operations in order to create them in the same order than the picking stock moves if possible
        processed_products = set()
        for move in [x for x in picking.move_lines if x.state not in ('done', 'cancel')]:
            if move.product_id.id not in processed_products:
                vals += prevals.get(move.product_id.id, [])
                processed_products.add(move.product_id.id)
        return vals

    # def onchange_filter(self, cr, uid, ids, do_filter, purchase_id, context=None):
    #    if (do_filter == True and purchase_id != False):
    #        #maj du domain
    #        cr.execute("select * from purchase_order_line where order_id = %s",(purchase_id,))
    #        products = cr.dictfetchall() 
    #        if len(products) != 0:
    #            if len(products) == 1:
    #                for product in products:
    #                    pick = "('id','=',"+str(product['product_id'])+")"   
    #            else : 
    #                pick='('
    #                for product in products:
    #                    pick=pick+str(product['product_id'])+','
    #                pick = pick[:-1]
    #                pick=pick+')'
    #                pick = "('id','in',"+pick+")"
    #        else :  
    #            pick = "('id','=',0)"
    #        return {'value':{'product_domain': pick}}
    #    return {'value':{'product_domain': "('id','>',0)"}}    

    @api.cr_uid_ids_context
    def do_enter_transfer_details(self, cr, uid, picking, context=None):
        '''
           Modifier la methode pour mettre à jour les taxes
        '''
        if not context:
            context = {}

        context.update({
            'active_model': self._name,
            'active_ids': picking,
            'active_id': len(picking) and picking[0] or False
        })

        created_id = self.pool['stock.transfer_details'].create(cr, uid,
                                                                {'picking_id': len(picking) and picking[0] or False},
                                                                context)
        # rimbd
        self.button_reset_taxes(cr, uid, picking, context)
        self.reset_taxes(cr, uid, picking, context)
        return self.pool['stock.transfer_details'].wizard_view(cr, uid, created_id, context)

    def button_reset_taxes(self, cr, uid, ids, context=None):
        self.reset_taxes(cr, uid, ids, context)
        return True

    def reset_taxes(self, cr, uid, ids, context=None):
        val = self.pool.get('stock.picking').browse(cr, uid, ids[0]).name
        if context is None:
            context = {}
        ctx = context.copy()
        ait_obj = self.pool.get('stock.picking.tax')
        for id in ids:
            partner = self.browse(cr, uid, id, context=ctx).partner_id
            if partner.lang:
                cr.execute("DELETE FROM stock_picking_tax WHERE picking_id=%s AND manual is False", (id,))
                ctx.update({'lang': partner.lang})
            for taxe in ait_obj.compute(cr, uid, id, context=ctx).values():
                ait_obj.create(cr, uid, taxe)
                # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('stock.picking').write(cr, uid, ids, {'move_lines': []}, context=ctx)
        self.pool.get('stock.picking').write(cr, uid, ids, {'state': 'draft'},
                                             context=ctx)  # 29/07 modification etat du bon reception cree a partir du purchase order
        return True


class stock_move(osv.osv):
    _name = 'stock.move'
    _inherit = 'stock.move'

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.move_tax_id.compute_all(price, line.product_uom_qty, product=line.product_id,
                                                 partner=line.picking_id.partner_id)

            res[line.id] = taxes['total']
            # if line.picking_id:
            #   cur = line.picking_id.currency_id

        # if self.invoice_id:
        #    self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)

        return res

    # def create(self, cr, uid, vals, context=None):
    #    origin = vals['origin']
    #    po_object = self.pool.get('purchase.order')
    #    po_ids = po_object.search(cr, uid, [('name', '=', origin)], context=context)
    #    
    #    picking_id = self.pool.get('stock.picking').browse(cr, uid,vals['picking_id'], context=context)
    #    
    #    if (len(po_ids) > 0):
    #        purchase_id = po_ids[0]
    #        po = po_object.browse(cr, uid, purchase_id, context=context)
    #        cr.execute('''SELECT purchase_order_line.id as pol_id FROM purchase_order, purchase_order_line WHERE purchase_order.id = purchase_order_line.order_id
    #    AND purchase_order.id =%s
    #    AND purchase_order_line.product_id=%s
    #    ''',(purchase_id,vals['product_id'],))
    #        do_filter = picking_id.do_filter
    #        result = cr.dictfetchone()
    #        
    #        if result:

    #            purchase_line_id = result['pol_id']
    #            if (do_filter != False and purchase_id != False and vals['purchase_line_id'] == False):
    #                vals['purchase_line_id'] = result['pol_id']         

    #    res = super(stock_move, self).create(cr, uid, vals, context)
    #    return res 

    _columns = {

        'price_unit': fields.float('Prix unitaire', digits_compute=dp.get_precision('Account'),
                                   help="Technical field used to record the product cost set by the user during a picking confirmation (when average price costing method is used)"),
        # 'product_reste_qty':fields.float('Qte Non Livrée', digits_compute= dp.get_precision('Account')),
        # 'product_order_qty':fields.float('Qte Commandee', digits_compute= dp.get_precision('Account')),
        'price_subtotal': fields.function(_amount_line, method=True, digits_compute=dp.get_precision('Account'),
                                          string='Sous total', type="float", store=True, ),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True,
                                      domain=[('type', 'in', ['service', 'product'])],
                                      states={'done': [('readonly', True)]}),
        'discount': fields.float('Remise', digits=(16, 2)),
        'move_tax_id': fields.many2many('account.tax', 'stock_move_tax', 'move_id', 'tax_id', 'Taxes',
                                        domain=[('parent_id', '=', False)]),
        'account_id': fields.many2one('account.account', 'Account',
                                      domain=[('type', '<>', 'view'), ('type', '<>', 'closed')],
                                      help="The income or expense account related to the selected product."),
        'default_code': fields.char('Reference', size=64),
        # 'prod_qty_stock':fields.float('Qte Disponible', digits_compute= dp.get_precision('Account')),

    }

    def create(self, cr, uid, vals, context=None):

        if 'picking_type_id' in vals:
            picking_type_id = vals['picking_type_id']

            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])

            if product.type == "service" and picking_type_id == 2:
                vals['location_id'] = 10

            if product.type == 'service' and picking_type_id == 1:
                vals['location_dest_id'] = 10
        res = super(stock_move, self).create(cr, uid, vals, context)
        return res

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, partner_id=False,
                            picking_type_id=False):  # ,purchase_order=False,bc_filter = False):

        """
        Modifier cette methode pour prendre en considération les propositions de (prix, remise) fournisseurs 
        On change of product id, if finds UoM, UoS, quantity and UoS quantity.
        @param prod_id: Changed Product id
        @param loc_id: Source location id
        @param loc_dest_id: Destination location id
        @param partner_id: Address id of partner
        @return: Dictionary of values
        """
        if not prod_id:
            return {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        lang = user and user.lang or False
        if partner_id:
            addr_rec = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if addr_rec:
                lang = addr_rec and addr_rec.lang or False
        ctx = {'lang': lang}

        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]
        uos_id = product.uos_id and product.uos_id.id or False
        # result = {
        #    'name': product.partner_ref,
        #    'product_uom': product.uom_id.id,
        #    'product_uos': uos_id,
        #    'product_uom_qty': 1.00,
        #    'product_uos_qty': self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty'],
        # }
        # if loc_id:
        #    result['location_id'] = loc_id
        # if loc_dest_id:
        #    result['location_dest_id'] = loc_dest_id

        # rimbd
        price = 0
        partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_id)

        if picking_type_id == 2:
            taxes = product.taxes_id
            price = product.lst_price

        else:
            taxes = product.supplier_taxes_id

        fposition_id = False
        fpos_obj = self.pool.get('account.fiscal.position')
        fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False
        tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
        # product_reste_qty = 0
        # product_order_qty = 0

        remise = 0

        if prod_id != False:
            cr.execute("""
                      SELECT prix,supplier_discount
		      FROM product_supplierinfo, product_product
		      WHERE 
		      product_product.product_tmpl_id = product_supplierinfo.product_tmpl_id 
		      AND product_supplierinfo.name=%s AND product_product.id=%s 
		      """, (partner_id, prod_id))
            line = cr.dictfetchone()
            if line:
                price = line['prix']
                remise = line['supplier_discount']

        result = {
            # 'name': product.partner_ref,
            'name': product.name,
            'default_code': product.default_code,
            'product_uom': product.uom_id.id,
            'product_uom_qty': 1.00,
            'product_uos': uos_id,
            'move_tax_id': tax_id,
            'product_qty': 1.00,
            'product_uos_qty':
                self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)[
                    'value']['product_uos_qty'],
            # 'product_reste_qty': product_reste_qty,
            # 'product_order_qty': product_order_qty,
            'price_unit': price,
            'discount': remise,
        }
        if loc_id:
            result['location_id'] = loc_id
        if loc_dest_id:
            result['location_dest_id'] = loc_dest_id
        return {'value': result}

    def action_assign(self, cr, uid, ids, context=None):
        """ Checks the product type and accordingly writes the state.
        """
        context = context or {}
        quant_obj = self.pool.get("stock.quant")
        to_assign_moves = set()
        main_domain = {}
        todo_moves = []
        operations = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.state not in ('confirmed', 'waiting', 'assigned'):
                continue
            if move.location_id.usage in ('supplier', 'inventory', 'production'):
                to_assign_moves.add(move.id)
                # in case the move is returned, we want to try to find quants before forcing the assignment
                if not move.origin_returned_move_id:
                    continue
            if move.product_id.type == 'consu' or move.product_id.type == 'service':
                to_assign_moves.add(move.id)
                continue
            else:
                todo_moves.append(move)

                # we always keep the quants already assigned and try to find the remaining quantity on quants not assigned only
                main_domain[move.id] = [('reservation_id', '=', False), ('qty', '>', 0)]

                # if the move is preceeded, restrict the choice of quants in the ones moved previously in original move
                ancestors = self.find_move_ancestors(cr, uid, move, context=context)
                if move.state == 'waiting' and not ancestors:
                    # if the waiting move hasn't yet any ancestor (PO/MO not confirmed yet), don't find any quant available in stock
                    main_domain[move.id] += [('id', '=', False)]
                elif ancestors:
                    main_domain[move.id] += [('history_ids', 'in', ancestors)]

                # if the move is returned from another, restrict the choice of quants to the ones that follow the returned move
                if move.origin_returned_move_id:
                    main_domain[move.id] += [('history_ids', 'in', move.origin_returned_move_id.id)]
                for link in move.linked_move_operation_ids:
                    operations.add(link.operation_id)
        # Check all ops and sort them: we want to process first the packages, then operations with lot then the rest
        operations = list(operations)
        operations.sort(key=lambda x: ((x.package_id and not x.product_id) and -4 or 0) + (x.package_id and -2 or 0) + (
            x.lot_id and -1 or 0))
        for ops in operations:
            # first try to find quants based on specific domains given by linked operations
            for record in ops.linked_move_operation_ids:
                move = record.move_id
                if move.id in main_domain:
                    domain = main_domain[move.id] + self.pool.get('stock.move.operation.link').get_specific_domain(cr,
                                                                                                                   uid,
                                                                                                                   record,
                                                                                                                   context=context)
                    qty = record.qty

                    if qty:
                        quants = quant_obj.quants_get_prefered_domain(cr, uid, ops.location_id, move.product_id, qty,
                                                                      domain=domain, prefered_domain_list=[],
                                                                      restrict_lot_id=move.restrict_lot_id.id,
                                                                      restrict_partner_id=move.restrict_partner_id.id,
                                                                      context=context)
                        quant_obj.quants_reserve(cr, uid, quants, move, record, context=context)
        for move in todo_moves:

            # then if the move isn't totally assigned, try to find quants without any specific domain
            if move.state != 'assigned':
                qty_already_assigned = move.reserved_availability

                qty = move.product_qty - qty_already_assigned

                quants = quant_obj.quants_get_prefered_domain(cr, uid, move.location_id, move.product_id, qty,
                                                              domain=main_domain[move.id], prefered_domain_list=[],
                                                              restrict_lot_id=move.restrict_lot_id.id,
                                                              restrict_partner_id=move.restrict_partner_id.id,
                                                              context=context)
                quant_obj.quants_reserve(cr, uid, quants, move, context=context)

        # force assignation of consumable products and incoming from supplier/inventory/production
        if to_assign_moves:
            self.force_assign(cr, uid, list(to_assign_moves), context=context)


class stock_picking_tax(osv.osv):
    _name = "stock.picking.tax"
    _description = "Picking Tax"

    def _count_factor(self, cr, uid, ids, name, args, context=None):
        res = {}
        for picking_tax in self.browse(cr, uid, ids, context=context):
            res[picking_tax.id] = {
                'factor_base': 1.0,
                'factor_tax': 1.0,
            }
            if picking_tax.amount <> 0.0:
                factor_tax = picking_tax.tax_amount / picking_tax.amount
                res[picking_tax.id]['factor_tax'] = factor_tax

            if picking_tax.base <> 0.0:
                factor_base = picking_tax.base_amount / picking_tax.base
                res[picking_tax.id]['factor_base'] = factor_base
        return res

    _columns = {
        'picking_id': fields.many2one('stock.picking', 'Move', ondelete='cascade', select=True),
        'name': fields.char('Tax Description', size=64, required=True),
        'account_id': fields.many2one('account.account', 'Tax Account', required=True,
                                      domain=[('type', '<>', 'view'), ('type', '<>', 'income'),
                                              ('type', '<>', 'closed')]),
        'base': fields.float('Base', digits_compute=dp.get_precision('Account')),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'manual': fields.boolean('Manual'),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of invoice tax."),
        'base_code_id': fields.many2one('account.tax.code', 'Base Code',
                                        help="The account basis of the tax declaration."),
        'base_amount': fields.float('Base Code Amount', digits_compute=dp.get_precision('Account')),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Code', help="The tax basis of the tax declaration."),
        'tax_amount': fields.float('Tax Code Amount', digits_compute=dp.get_precision('Account')),
        'company_id': fields.related('account_id', 'company_id', type='many2one', relation='res.company',
                                     string='Company', store=True, readonly=True),
        'factor_base': fields.function(_count_factor, method=True, string='Multipication factor for Base code',
                                       type='float', multi="all"),
        'factor_tax': fields.function(_count_factor, method=True, string='Multipication factor Tax code', type='float',
                                      multi="all")
    }

    def base_change(self, cr, uid, ids, base, currency_id=False, company_id=False, date_picking=False):
        cur_obj = self.pool.get('res.currency')
        company_obj = self.pool.get('res.company')
        company_currency = False
        factor = 1
        if ids:
            factor = self.read(cr, uid, ids[0], ['factor_base'])['factor_base']
        if company_id:
            company_currency = company_obj.read(cr, uid, [company_id], ['currency_id'])[0]['currency_id'][0]
        if currency_id and company_currency:
            base = cur_obj.compute(cr, uid, currency_id, company_currency, base * factor,
                                   context={'date': date_picking or time.strftime('%Y-%m-%d')}, round=False)
        return {'value': {'base_amount': base}}

    def amount_change(self, cr, uid, ids, amount, currency_id=False, company_id=False, date_picking=False):
        cur_obj = self.pool.get('res.currency')
        company_obj = self.pool.get('res.company')
        company_currency = False
        factor = 1
        if ids:
            factor = self.read(cr, uid, ids[0], ['factor_tax'])['factor_tax']
        if company_id:
            company_currency = company_obj.read(cr, uid, [company_id], ['currency_id'])[0]['currency_id'][0]
        if currency_id and company_currency:
            amount = cur_obj.compute(cr, uid, currency_id, company_currency, amount * factor,
                                     context={'date': date_picking or time.strftime('%Y-%m-%d')}, round=False)
        return {'value': {'tax_amount': amount}}

    _order = 'sequence'
    _defaults = {
        'manual': 1,
        'base_amount': 0.0,
        'tax_amount': 0.0,
    }

    def compute(self, cr, uid, picking_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
        # cur = picking.currency_id
        company_currency = picking.company_id.currency_id.id

        for line in picking.move_lines:
            prod = self.pool.get('product.product').browse(cr, uid, line.product_id, context=context)
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            for tax in tax_obj.compute_all(cr, uid, line.move_tax_id, price, line.product_qty, line.product_id,
                                           picking.partner_id)['taxes']:
                val = {}
                val['picking_id'] = picking.id
                # val['name'] = tax['name'][-5:].replace('-','')
                val['name'] = tax['name'][-3:].replace('-', '')
                val['amount'] = tax['amount']
                val['manual'] = False
                val['sequence'] = tax['sequence']
                val['base'] = tax['price_unit'] * line['product_qty']

                if picking.picking_type_id in (1, 2):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']

                    val['base_amount'] = cur_obj.compute(cr, uid, company_currency, company_currency,
                                                         val['base'] * tax['base_sign'],
                                                         context={'date': picking.date or time.strftime('%Y-%m-%d')},
                                                         round=False)

                    val['tax_amount'] = cur_obj.compute(cr, uid, company_currency, company_currency,
                                                        val['amount'] * tax['tax_sign'],
                                                        context={'date': picking.date or time.strftime('%Y-%m-%d')},
                                                        round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']

                    val['base_amount'] = cur_obj.compute(cr, uid, company_currency, company_currency,
                                                         val['base'] * tax['ref_base_sign'],
                                                         context={'date': picking.date or time.strftime('%Y-%m-%d')},
                                                         round=False)

                    val['tax_amount'] = cur_obj.compute(cr, uid, company_currency, company_currency,
                                                        val['amount'] * tax['ref_tax_sign'],
                                                        context={'date': picking.date or time.strftime('%Y-%m-%d')},
                                                        round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        return tax_grouped


stock_picking_tax()


class stock_inventory(osv.osv):
    _name = "stock.inventory"
    _inherit = "stock.inventory"

    def create(self, cr, uid, vals, context=None):
        '''
           Add inventory reference sequence
           @return: new created stock_inventory id
        '''
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'stock.inventory')
        return super(stock_inventory, self).create(cr, uid, vals, context)

    INVENTORY_STATE_SELECTION = [
        ('draft', 'Draft'),
        ('cancel', 'Annulé'),
        ('confirm', 'En cours'),
        ('done', 'Validé'),
    ]

    _columns = {
        'name': fields.char('Inventory Reference', size=64, readonly=True, required=False),
        'state': fields.selection(INVENTORY_STATE_SELECTION, 'Status', readonly=True, select=True, copy=False),
    }


class stock_inventory_line(osv.osv):
    _name = "stock.inventory.line"
    _inherit = "stock.inventory.line"

    def _get_product_name_change(self, cr, uid, ids, context=None):
        return self.pool.get('stock.inventory.line').search(cr, uid, [('product_id', 'in', ids)], context=context)

    def _quantity_compute(self, cr, uid, ids, field, args, context=None, ):
        '''
           Calculer l'écart entre la quantité théorique et la quentité réelle
        '''
        res = {}
        for inv_obj in self.browse(cr, uid, ids, context=context):
            if (inv_obj.theoretical_qty - inv_obj.product_qty) >= 0:
                quantity_difference = inv_obj.theoretical_qty - inv_obj.product_qty
            else:
                quantity_difference = inv_obj.product_qty - inv_obj.theoretical_qty

        res[inv_obj.id] = quantity_difference
        return res

    @api.onchange('product_qty')
    def check_product_qty_change(self):
        if (self.theoretical_qty - self.product_qty) >= 0:
            self.quantity_difference = self.theoretical_qty - self.product_qty
        else:
            self.quantity_difference = self.product_qty - self.theoretical_qty

    _columns = {
        'quantity_difference': fields.function(_quantity_compute, method=True, string='Quantity difference',
                                               type='float', store=True),
        'product_price': fields.related('product_id', 'purchase_price',
                                        digits_compute=dp.get_precision('Product Price'), type='float',
                                        string='Product Price', store={
                'product.product': (_get_product_name_change, ['name', 'default_code'], 20),
                'stock.inventory.line': (lambda self, cr, uid, ids, c={}: ids, ['product_id'], 20), }),

    }


stock_inventory_line()


class stock_picking_type(osv.osv):
    _name = "stock.picking.type"
    _inherit = "stock.picking.type"

    _columns = {

        'code': fields.selection([('incoming', 'Suppliers'), ('outgoing', 'Customers'), ('internal', 'Internal'),
                                  ('entree', 'Entree'), ('sortie', 'Sortie')],
                                 'Type of Operation', required=True),
    }
