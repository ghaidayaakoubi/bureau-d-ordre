# -*- coding: utf-8 -*-

from openerp import models, fields, api

class cci_courriel(models.Model):
	_name = 'cci.courriel'

	note_id = fields.Many2one('courriel.note', 'Note' )
	type_id = fields.Many2one('courriel.type', 'Type de courriel')
	mode_id = fields.Many2one('courriel.mode', 'Mode de réception')
	degre_id = fields.Many2one('courriel.degre', 'Degrés de confidentialité')
	importance_id = fields.Many2one('courriel.important', 'Importance')
	urgent_id = fields.Many2one('courriel.urgence', 'Urgence')
	date_courriel = fields.Date(string='Date de réception', default=fields.Date.today(), )
	objet =fields.Text(string="Objet",)
	street =fields.Char(string="Rue")
	street2 =fields.Char(string="Street2")
	city =fields.Char(string="Ville")
	zip =fields.Char(string="Code postale", size=24, change_default=True)
	country_id = fields.Many2one('res.country', 'Pays' , ondelete='restrict')
	website =fields.Char(string="Site Web", help="Website of Partner or Company")
	name =fields.Char(string="Nom")
	function =fields.Char(string="Poste occupé")
	phone =fields.Char(string="Tél.")
	email =fields.Char(string="Courriel.")
	is_company =fields.Boolean(help="Check if the contact is a company, otherwise it is a person")
	title = fields.Many2one('res.partner.title', 'Civilité')
	dept_id = fields.Many2one('res.users', 'Responsable' )
	op_eco_new = fields.Char(string="Nouvel Opérateur Économique", )
    	note_ids = fields.One2many(comodel_name="courriel.note", string='Note', inverse_name="note")
    	instruction_ids = fields.One2many(comodel_name="courriel.instruction", string='Instruction', inverse_name="instruction")
	op_eco_exist = fields.Boolean(string="Opérateur Économique Existant", )

	op_eco_id = fields.Many2one(comodel_name="res.partner", string="Opérateur Économique", )

 	#liste_dest_ids = fields.One2many(comodel_name="res.partner", string='Liste de destinataire', inverse_name="operator_id")



        


