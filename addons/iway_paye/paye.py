#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class hr_contract(osv.osv):
    _inherit = 'hr.contract'

    _columns = {
        'nationalite': fields.char('Nationalite', size=64),
        'qualif': fields.char('Qualification', size=64),
        'niveau': fields.char('Niveau', size=64),
        'coef': fields.char('Coefficient', size=64),
        'type_avance': fields.selection([('1', 'Une fois/mois'),('2','Suiant salaire')], 'Plafond Avance', required=True, ),
        #'nombre': fields.selection([('1', '1 fois par mois'),('2','Suiant salaire')], 'Plafond Avance', required=True, ),
        'wage': fields.float('Wage', digits_compute=dp.get_precision('Payroll'), required=True, help="Basic Salary of the employee"),
    }
hr_contract()



class res_company(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'plafond_secu': fields.float('Plafond de la Securite Sociale', digits_compute=dp.get_precision('Payroll')),
        'nombre_employes': fields.integer('Nombre d\'employes'),
        'cotisation_prevoyance': fields.float('Cotisation Patronale Prevoyance', digits_compute=dp.get_precision('Payroll')),
        'org_ss': fields.char('Organisme de securite sociale', size=64),
        'conv_coll': fields.char('Convention collective', size=64),
    }

res_company()



class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'

    _columns = {
        'payment_mode': fields.char('Mode de paiement', size=64),
    }
    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        res = []
        contract_obj = self.pool.get('hr.contract')
        rule_obj = self.pool.get('hr.salary.rule')

        structure_ids = contract_obj.get_all_structures(cr, uid, contract_ids, context=context)

        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)

        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        montant=0.0

        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):
            #emplyee_id = self.pool.get('hr.employee').search(cr, uid, [('contract_id','=',contract.id)])
            contract_employee = self.pool.get('hr.contract').browse(cr, uid, contract.id)
            print "************************contract_employee",contract_employee
            for contr in contract_employee :
		        avance_ids = self.pool.get('hr.avance').search(cr, uid, [('employee_id','=',contr.employee_id.id),('state','=','done'),('date','>=',date_from),('date','<=',date_to)])#('date','<=',date_to)
		        avance_obj = self.pool.get('hr.avance').browse(cr, uid, avance_ids)
		        print "avance =======================",avance_obj 
            for rule in rule_obj.browse(cr, uid, sorted_rule_ids, context=context):
        

                if rule.input_ids:

                    for input in rule.input_ids:
                        if input.name=='Avance' and avance_obj:
							for avance in avance_obj :
								montant+=avance.montant
								print "***********************",montant
							inputs = {
								'name':input.name,
								'code':input.code,
								'contract_id':contract.id,
								'amount':montant,
							}
							res += [inputs]
                        		
                        else :
		                    inputs = {
		                         'name': input.name,
		                         'code': input.code,
		                         'contract_id': contract.id,
		                    }
		                    res += [inputs]
                        	
        return res
hr_payslip()

class hr_employee(osv.osv):
	_inherit = 'hr.employee'
	
	
	def _type_contract(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for employee in self.browse(cr, uid, ids, context=context):

		    res[employee.id] = False

		    if employee.contract_id.type_id.name=='CDI' or employee.contract_id.type_id.name=='CDD':
				res[employee.id] = True
			
		return  res
		

	_columns = {
		'matricule_cnss':fields.char('Matricule CNSS', size=10),
		'num_cin':fields.char('Numéro CIN', size=8,required=True),
		'num_chezemployeur':fields.char('Numero chez l\'employeur'),
		'chef_famille':fields.boolean('Chef de famille '),
		#'type_contract':fields.function(_type_contract, type="boolean", method=True),
		'street': fields.char(size=128, string="Street"),
        	'street2': fields.char(size=128,string="Street2"),
        	'zip': fields.char(size=24, string="Zip"),
        	'city': fields.char(size=24, string="City"),
	}
hr_employee()

		
		
		
		
		
		
		
		
		
		
	
