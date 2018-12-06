# -*- coding: utf-8 -*-



from openerp.osv import fields, osv


class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"

    _columns = {
        # changement de nom des champs Sales Team ___ Departement et Salesperson ____
        'user_id': fields.many2one('res.users', 'Commercial',
                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True,
                                   track_visibility='onchange'),
        'section_id': fields.many2one('crm.case.section', 'Départements'),

    }
