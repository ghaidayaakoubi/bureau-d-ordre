# -*- coding: utf-8 -*-
from datetime import date, datetime
from dateutil import relativedelta
from openerp import tools
from openerp.osv import fields, osv
from datetime import datetime
from openerp.tools.translate import _
from openerp.exceptions import Warning
import openerp

class crm_phonecall(osv.Model):
    _inherit = "crm.phonecall"
    _name = 'crm.phonecall'

    _columns = {
	'partner_contact_id':fields.many2one('res.partner','Contact'),

    }


	#ajouter par salwa ksila le 11/07/2017
	#modifier par marwa bm le 15-09-2017
    def create(self, cr, uid, vals, context=None):  
	name = vals['name']
	partner_id = vals['partner_id']
	date = vals['date']
	partner_contact_id = vals['partner_contact_id']
	opportunity_id = vals['opportunity_id']


	vals = {
		'name': name,
		'partner_id': partner_id,
		'partner_contact_id': partner_contact_id,
		'date_deadline': date,
		'date_action': date,
		'type': 'Appel',
		'opportunity_id':opportunity_id,
	}

	inv_id = self.pool.get('crm.lead.activity').create(cr, uid, vals, context=context)

	res = super(crm_phonecall, self).create(cr, uid, vals, context=context)
	#rendre les champs vides
	write_id=self.pool.get('crm.lead').write(cr, uid, opportunity_id, {'date_deadline': False,'date_action': False,'title_action': False,'type_act': False})
	return res

	#add by marwa BM 14-09-2017
    # def closed_action_call(self, cr, uid, ids,context=None):
    # call_id=self.browse(cr, uid, ids,context=context).id
    # opportunity_id=self.browse(cr, uid, ids,context=context).opportunity_id.id
    # return self.pool.get('crm.lead').write(cr, uid, opportunity_id, {'date_deadline': False,'date_action': False,'title_action': False,'type_act': False})

    _default = {
	'partner_id': lambda self, cr, uid, context: context.get('partner_id', False),
    }
