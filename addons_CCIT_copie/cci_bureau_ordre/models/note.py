# -*- coding: utf-8 -*-

from openerp import models, fields, api

class courriel_note(models.Model):
	_name = 'courriel.note'

	name =fields.Text(string="Note")
	dept_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user )
	#responsable_id = fields.Many2one('res.partner', 'Responsable' , required=True)
	#responsable_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user)
	date_note = fields.Date(string='Date', default=fields.Date.today(), )
	note =fields.Text(string="Note",)


