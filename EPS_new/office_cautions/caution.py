# -*- encoding: utf-8 -*-

from openerp import models, fields

class office_caution(models.Model):
    _name = 'office.caution'

    partner_id = fields.Many2one('res.partner', required=True, string='Partenaire')
    banque = fields.Many2one('reglement.banque', required=True)
    montant = fields.Float(digits=(6, 3))
    date_caution = fields.Date(string='Date Caution')
    date_fin_caution = fields.Date(string='Date fin Caution')
    date_liberation = fields.Date(string='Date Libération')
    tt = fields.Selection([('caution', 'Caution'),('garantie', 'Garantie'),],string= 'Type')
    description = fields.Text()
    libere = fields.Boolean('Libere')

    _defaults = {
     'libere': False, # les caution sont bloqué par defaut
    }

