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


{
    'name': 'Office HR Holiday',
    'version': '1.0',
    'author': 'Marwa ROMDHAN',
    'category': 'Human Resources',


    'website': 'http://www.iway-tn.com',
    'description': "Module modifie le module hr holiday",
    'depends': ['base','share','mail','hr_contract','hr_holidays', ],
    'update_xml':[  'wizard/wizard_conge.xml',
                   'hr_holidays_view.xml',
                   'res_users_view.xml',],
    'data': [
        'security/ir.model.access.csv',
        'hr_holidays_data.xml',
'hr_holidays_schedule.xml',
        'hr_holidays_view.xml',

        ],


    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
