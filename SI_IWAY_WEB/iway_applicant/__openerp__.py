# -*- coding: utf-8 -*-
{
    'name': "iway_applicant",

    'summary': """
CE MODULE HÉRITE DU MODULE hr_recruitement
        """,

    'description': """
    """,

    'author': "Ghaida YAAKOUBI",
    'website': "http://www.iway-tn.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'recruitement',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_recruitment','iway_entretien'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
	#'iway_pfe_workflow.xml',
        'iway_applicant.xml',
	'hr_applicant_data.xml',
	'iway_applicant_sequence.xml',
	'iway_applicant_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
