# -*- coding: utf-8 -*-

from openerp import models, fields, api

class courriel_mode_reception(models.Model):
	_name = 'courriel.mode'

	name =fields.Char(string="Mode reception")


