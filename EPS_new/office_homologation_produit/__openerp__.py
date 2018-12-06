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
        "name" : "Office Homologation Produit",
        "version" : "0.1",
        "author" : "Marwa ROMDHAN",
        "website" : "http://iway-tn.com/",
        "category" : "Purchase",

        "description": """Module pour gestion des homologations produit""",
        "depends" : ['office_invoice','office_product'],
        "init_xml" : [ ],
        "test" : [],
        "demo_xml" : [ ],
        "update_xml" : ['homologation_produit_view.xml','product_view.xml','homologation_sequence.xml'],#'security/ir.model.access.csv'
        "data": [
        	'security/ir.model.access.csv',

        	'frais_product_data.xml',

    	],


    	"installable": True,


}
