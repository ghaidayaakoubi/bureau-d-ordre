# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
from datetime import datetime
from openerp import api

class wizard_etat_caution(osv.osv_memory):
    _name = "wizard.etat.caution"
    _description = "Wizard Etat Caution "

    
	

    _columns = { 

        #'date_debut': fields.date('Date Debut', required=True, select=True), 
        #'date_fin': fields.date('Date Fin', required=True, select=True),
	

    }
    _defaults = {
	#'date_aujourd': fields.datetime.now,
	
    }
	

    

    def create_report(self, cr, uid, ids, context={}):
        #data = self.read(cr,uid,ids,)[0]
	data = self.read(cr,uid,ids,)[-1] 
        print data,' create_report('
	res={}
	res={
            'type'         : 'ir.actions.report.xml',
            'report_name'   : 'jasper_etat_caution_print',
            'datas': {
                    'model':'office.caution',
                    'id': context.get('active_ids') and context.get('active_ids')[0] or False,
                    'ids': context.get('active_ids') and context.get('active_ids') or [],
                    
                    'form':data
                    },
            'nodestroy': False
        }
        return res


wizard_etat_caution()
