# -*- coding: utf-8 -*-

from datetime import date, datetime
from dateutil import relativedelta
from openerp import tools, api
from openerp.osv import fields, osv
from openerp.exceptions import Warning
from openerp.exceptions import except_orm

class product(osv.osv):
    _name = 'product'
#---------------------------colonnes
    _columns = {
	'product_id':fields.integer('Produit',ondelete='cascade'),
	'name':fields.char('Nom du produit'),
	
	}

