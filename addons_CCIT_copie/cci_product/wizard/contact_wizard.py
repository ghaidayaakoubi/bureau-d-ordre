# -*- coding: utf-8 -*-

from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp.exceptions import Warning

class wizard_product(osv.osv_memory):
    _name = "cci.contact.wizard"
    _description = "lancer Compagne Marketing"

    def _get_partner(self, cr, uid, ids, context=None):
        return context.get('partner_id', False)

    _columns = {
	'contact_ids':fields.one2many('res.partner','id','contact'),
    }    

    def _charger_contact(self, cr, uid, ids, context=None):
        return True


