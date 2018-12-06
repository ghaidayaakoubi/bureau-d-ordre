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
# 
{
        "name" : "Office-Invoice",
        "version" : "0.1",
        "author" : "WASSIM CHAABOUNI & Rim BEN DHAOU & Marwa ROMDHAN",
        "website" : "http://iway-tn.com/",
        "category" : "Unknown",
        "description": """Module pour modifier account_invoice  """,
        "depends" : ['base','account','account_voucher','office_account_param','office_product','office_partner'],
        "init_xml" : [],
        "demo_xml" : [ ],
        'data': ['sequence_modification.sql'],
        "update_xml" : ['invoice_supplier_view.xml','invoice_view.xml','account_invoice_workflow.xml',
                        ],
        "test" : ['tests/tests.yml'],
        "installable": True
}
