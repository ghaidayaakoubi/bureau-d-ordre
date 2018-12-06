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
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import Number_To_Word

class reglement_banque(osv.osv):
    _name = "reglement.banque"
    _rec_name = "designation"
    _description = "Reglement Banque"   	
    _columns = {
	'code': fields.char('Reference', size=64),
	'designation': fields.char('Designation', size=254),	           			
    }
	
reglement_banque()

class reglement_mode(osv.osv):
    _name = "reglement.mode"
    _rec_name = "designation"
    _description = "Reglement Mode"
    _columns = {
	'code': fields.char('Reference', size=10),
	'designation': fields.char('Designation', size=254),
    }
		
reglement_mode()

class reglement_piece(osv.osv):
    
	_name = "reglement.piece"
	_description = "Reglement Piece"	
	_rec_name = "num_cheque_traite"

        def create(self, cr, uid, vals, context=None):
            vals['type']=context['type']
            res = super(reglement_piece, self).create(cr, uid, vals, context)
	    return res

	_columns = {
		'code_piece': fields.char('Reference', size=64, select=True, readonly=True),
        	#'num_cheque_traite': fields.integer('N Cheque/Traite', size=254, required=True,readonly=True,states={'draft':[('readonly',False)],'free':[('readonly',False)]}),
                'num_cheque_traite': fields.integer('N Cheque/Traite', size=254, readonly=False,states={'cashed':[('readonly',True)],'impaid':[('readonly',True)]}),
        	'num_compte': fields.char('Account Number', size=254,readonly=True,states={'draft':[('readonly',False)],'free':[('readonly',False)]}),
        	'agence': fields.char('Bank Agency', size=254,readonly=True,states={'draft':[('readonly',False)],'free':[('readonly',False)]}),
        	'titulaire': fields.char('Holder', size=254,readonly=True,states={'draft':[('readonly',False)],'free':[('readonly',False)]}),
		'date_echance': fields.date('Maturity Date',readonly=True,states={'draft':[('readonly',False)],'free':[('readonly',False)]}),
		'montant_piece': fields.float('Amount', digits_compute=dp.get_precision('Account'),readonly=True,states={'draft':[('readonly',False)],'free':[('readonly',False)]}),
		'partner_id': fields.many2one('res.partner', 'Partner',required=True,readonly=True,states={'draft':[('readonly',False)],'free':[('readonly',False)]}),		
		'mode_reglement': fields.many2one('reglement.mode', 'Payment Mode', ondelete='set null',readonly=True,states={'draft':[('readonly',False)],'free':[('readonly',False)]}),		
		#'banque_id': fields.many2one('reglement.banque', 'Bank', ondelete='set null', required=True,readonly=True,states={'draft':[('readonly',False)],'free':[('readonly',False)]}),
                'banque_id': fields.many2one('reglement.banque', 'Bank', ondelete='set null', readonly=False,states={'cashed':[('readonly',True)],'impaid':[('readonly',True)]}),
		'state': fields.selection([('draft', 'Draft'),('free', 'Free'),('integrated', 'Integrated'),('pimpaid', 'Partially Impaid'),('impaid', 'Impaid'),('cashed', 'Cashed')], 'State',readonly=True),
		
		'montant_paye': fields.float('Montant Restant', digits_compute=dp.get_precision('Account')),
		'nature_piece': fields.selection([('piece_client', 'Piece Client'),('notre_piece', 'Notre Propre Piece')], 'Nature Piece',states={'draft':[('readonly',False)],'free':[('readonly',False)]}),
                'type':fields.selection([('in', 'in'),('out', 'out'),], 'Type'),
                'date_encaissement': fields.date('Date Encaissement',),

	}
	_defaults = {
        'state': lambda *a: 'draft',
        'montant_paye': 0.0,
        'type': 'out',
	}

        def reg_draft(self, cr, uid, ids):
            self.write(cr, uid, ids, { 'state': 'draft' })
            return True

        def reg_impaid(self, cr, uid, ids):
             
            self.write(cr, uid, ids, { 'state': 'impaid' })
            return True

        def reg_free(self, cr, uid, ids):

            for id in ids:
               montant = self.browse(cr, uid, id,).montant_piece
               if montant==0:
		  raise osv.except_osv(_('le montant du cheque ne peut pas etre nul !'),_("Veuillez verifier la piece"))
	    
            self.write(cr, uid, ids, { 'state': 'free' })
            return True

	def reg_cashed(self, cr, uid, ids):            
            self.write(cr, uid, ids, { 'state': 'cashed' })
            return True        

	def reg_integrated(self, cr, uid, ids):
            self.write(cr, uid, ids, { 'state': 'integrated' })
            return True
        

reglement_piece()
class reglement_retenu(osv.osv):   	 
	_name = "reglement.retenu"
	_rec_name = "code"
	_description = "Retenu A La Source"   	
	_columns = {
		'code': fields.char('Designation', size=64,),
		'designation': fields.float('Taux',digits_compute=dp.get_precision('Account')),
                #rim modif on 22 july 2013
                'type':fields.selection([('TTC', 'TTC'),('TVA', 'TVA'),], 'Type'),
                #rim modif on 22 july 2013
	}


reglement_retenu()
