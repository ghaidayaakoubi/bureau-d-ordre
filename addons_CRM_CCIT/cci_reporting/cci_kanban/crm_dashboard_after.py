#-*- coding:utf-8 -*-
import json
from datetime import datetime, timedelta
import calendar
from babel.dates import format_datetime, format_date

from openerp import models, api, _, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class crm_dashboard(models.Model):
    _name = "crm.dashboard.after"

    @api.one
    def _kanban_dashboard(self):
        self.kanban_dashboard = json.dumps(self.get_journal_dashboard_datas())
	#tableau de bord avant vente
    @api.one
    def _kanban_dashboard_graph(self):
	self.kanban_dashboard_graph = json.dumps(self.get_line_graph_datas())

    @api.one
    def _kanban_dashboard_graph_act(self):
	self.kanban_dashboard_graph_act = json.dumps(self.get_bar_graph_datas())

    @api.one
    def _kanban_dashboard_graph_pro(self):
	self.kanban_dashboard_graph_pro = json.dumps(self.get_rect_graph_datas())

	#tableau de bord 30-10-2017
    @api.one
    def _kanban_dashboard_graph_ca(self):
	self.kanban_dashboard_graph_ca = json.dumps(self.get_rect_graph_datas_ca())

    @api.one
    def _kanban_dashboard_graph_ca_cm(self):
	self.kanban_dashboard_graph_ca_cm = json.dumps(self.get_line_graph_ca_cm())

    @api.one
    def _kanban_dashboard_bar_ca(self):
	self.kanban_dashboard_bar_ca = json.dumps(self.get_kanban_dashboard_bar_ca())






    #fields
    name = fields.Char(string='Name')      
    type = fields.Selection([('opportunity_after', "opportunity_after"),('activity_after', "activity_after"),('product_after', "product_after"),('departement_after', "departement_after"),('commercial_after', "commercial_after")]) 

   
    kanban_dashboard = fields.Text(compute='_kanban_dashboard')

    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')
    kanban_dashboard_graph_act = fields.Text(compute='_kanban_dashboard_graph_act')
    kanban_dashboard_graph_pro = fields.Text(compute='_kanban_dashboard_graph_pro')
	#tableau de bord 30-10-2017
    kanban_dashboard_graph_ca = fields.Text(compute='_kanban_dashboard_graph_ca')
    kanban_dashboard_graph_ca_cm = fields.Text(compute='_kanban_dashboard_graph_ca_cm')

    	#get the object of dep
    kanban_dashboard_bar_ca = fields.Text(compute='_kanban_dashboard_bar_ca')



    show_on_dashboard = fields.Boolean(string='Show journal on dashboard', help="Whether this journal should be displayed on the dashboard or not", default=True) 

    #progress_rate = fields.Integer()
    #maximum_rate = fields.Integer()
  

    
    @api.multi
    def get_journal_dashboard_datas(self):
	print "u call get_journal_dashboard_datas"
	name_departement=''
	#Somme total de revunue crm.lead
	query1 = "SELECT SUM(planned_revenue) FROM crm_lead"
	self.env.cr.execute(query1)
	res = self.env.cr.dictfetchall()
	for i in res:
		planned_revenue=i['sum']

	#Somme total de revunue crm.lead par type
	query3 = "SELECT SUM(planned_revenue) FROM crm_lead WHERE type_act IN ('Appel','Mail','Reunion')"
	self.env.cr.execute(query3)
	res3 = self.env.cr.dictfetchall()
	for i in res3:
		planned_revenue_act=i['sum']

	#Somme total de revunue product
	query4 = "SELECT SUM(list_price) FROM product_template"
	self.env.cr.execute(query4)
	res4 = self.env.cr.dictfetchall()
	for i in res4:
		planned_revenue_pro=i['sum']

	#Nombre des activités prochaine
	query2 = "SELECT COUNT(id) FROM crm_lead WHERE type_act != ''"
	self.env.cr.execute(query2)
	count = self.env.cr.dictfetchall()
	for i in count:
		number_activity=i['count'] 
		number_activity_pro=i['count']

	#nombre de département
	query11 = "SELECT COUNT(id) FROM crm_case_section"
	self.env.cr.execute(query11)
	count_dep = self.env.cr.dictfetchall()
	for i in count_dep:
		number_departement=i['count']

	#nom de département pour chaque commercial et chef
	user_id=self.env['res.users'].browse(self.env.uid).id
	if user_id != 1 :
		dep_chef_ids=self.env['crm.case.section'].search([('user_id','=',user_id)])
		dep_comm_ids=self.env['crm.case.section'].search([('member_ids','=',user_id)])
		if dep_chef_ids:
			for dep_id in dep_chef_ids:
				name_departement=self.env['crm.case.section'].browse(dep_id.id).complete_name

		elif dep_comm_ids :
			for dep_id in dep_comm_ids:
				name_departement=self.env['crm.case.section'].browse(dep_id.id).complete_name
		else :
			name_departement=''
	else:
		name_departement=''

	return {
		'planned_revenue': planned_revenue,
		'number_activity':number_activity,
		'planned_revenue_act':planned_revenue_act,
		'planned_revenue_pro':planned_revenue_pro,
		'number_activity_pro':number_activity_pro,
		'number_departement':number_departement,
		'name_departement':name_departement,
	}

    #	Nombre d'opportunités courantes par produit
    @api.multi
    def get_line_graph_datas(self):
	data = []
	list_prod = []
	list_opportunity = []
	list_section = []
	list_opportunity_chef = []
	list_opportunity_comm = []
	list_section_comm = []
 	if self.type == 'opportunity_after' :
		user_id = self.env['res.users'].browse(self.env.uid).id ##user en cours
		##Liste des produits à suivre
		product_ids = self.env['product.template'].search([('a_suivre','=',True)])
	        print 'product_ids.....',product_ids
		if product_ids :
			for product in product_ids :
				list_prod.append(product.id)

		section_ids = self.env['crm.case.section'].search([('user_id','=',user_id),('active','=','True')])
	        #print 'section_ids.....',section_ids
###########################default_code####################""""""
		if list_prod and user_id == 1:
			#pour l'administrateur:
			self.env.cr.execute('SELECT COUNT(c.id), default_code, p.id FROM crm_lead c, product_product p where c.product_id = p.product_tmpl_id AND c.stage_id IN %s AND product_id IN %s GROUP BY (default_code,p.id)',((6,7),tuple(list_prod)))
			##self.env.cr.execute('SELECT COUNT(id), name FROM crm_lead WHERE stage_id NOT IN %s AND product_id IN %s GROUP BY name',((6,7),tuple(list_prod)))
			res1 = self.env.cr.dictfetchall()
			for j in res1:
				label=j['default_code']
				value=j.get('count')
				data.append({'label':label , 'value':value ,'id':self.id})
			return [{'values': data, 'area': True,'id': self.id}]

#########################default_code######################""""""
		elif section_ids :  #pour le chef du département.
			product_ids = self.env['product.template'].search([('a_suivre','=',True)])
			for product in product_ids :
				list_prod.append(product.id)
			
			for section in section_ids:
				list_section.append(section.id)

			if list_prod :
				self.env.cr.execute('SELECT COUNT(id), name FROM crm_lead WHERE stage_id IN %s AND product_id IN %s AND section_id in %s GROUP BY name',((6,7),tuple(list_prod),tuple(list_section)))
				res1 = self.env.cr.dictfetchall()
				for j in res1:
					label=j['name']
					value=j.get('count')
					data.append({'label':label , 'value':value ,'id':self.id})
				return [{'values': data, 'area': True,'id': self.id}]
		else : #pour le commercial
			print 'pour le commercial..'
			product_ids = self.env['product.template'].search([('a_suivre','=',True)])
			for product in product_ids :
				list_prod.append(product.id)

			section_ids = self.env['crm.case.section'].search([('member_ids','=',user_id),('active','=','True')])
			
			for section in section_ids:
				list_section.append(section.id)

			if list_prod :
				self.env.cr.execute('SELECT COUNT(id), name FROM crm_lead WHERE stage_id IN %s AND product_id IN %s AND section_id IN %s  AND user_id =%s GROUP BY name',((6,7),tuple(list_prod),tuple(list_section),user_id))
				commercial = self.env.cr.dictfetchall()
				for i in commercial:
					print 'Commercial resultat :',i
					label=i['name']
					value=i.get('count')
					data.append({'label':label , 'value':value ,'id':self.id})
				return [{'values': data, 'area': True,'id': self.id}]



    #Nombre des activités planifié par Produit
    @api.multi
    def get_bar_graph_datas(self):
	data = []
	list_prod = []
	list_opportunity = []
	list_section = []
	list_opportunity_chef = []
	list_opportunity_comm = []
	list_section_comm = []

	if self.type == 'activity_after' :
		user_id = self.env['res.users'].browse(self.env.uid).id ##user en cours
		##Liste des produits à suivre
		product_ids = self.env['product.template'].search([('a_suivre','=',True)])
		if product_ids :
			for product in product_ids :
				list_prod.append(product.id)

		section_ids = self.env['crm.case.section'].search([('user_id','=',user_id),('active','=','True')])
###########################################################""
		if list_prod and user_id == 1:
			#pour l'administrateur:
			#query5 = "SELECT type_act FROM crm_lead"

			#self.env.cr.execute(query5)
			#res5 = self.env.cr.dictfetchall()
			#for i in res5:
			#	label=i['type_act']
				#self.env.cr.execute("SELECT COUNT(id), stage_id FROM crm_lead WHERE type_act != '' AND name =%s AND stage_id NOT IN %s GROUP BY stage_id",(label,(6,7)))
			self.env.cr.execute("SELECT COUNT(c.id), default_code, p.id FROM crm_lead c, product_product p where c.type != '' AND c.product_id = p.product_tmpl_id AND c.stage_id IN %s AND product_id IN %s GROUP BY (default_code,p.id)",((6,7),tuple(list_prod)))
			res6 = self.env.cr.dictfetchall()
                        print 'res6.....',res6

			if res6:
				for i in res6:
					value=i.get('count')
					label=i['default_code']
					#number_activity_pro=value.get('count')
					data.append({'label': label, 'value':value, 'id':self.id})
				return [{'values': data, 'area': True, 'id': self.id}]
		elif section_ids :  #pour le chef du département.
			product_ids = self.env['product.template'].search([('a_suivre','=',True)])
			for product in product_ids :
				list_prod.append(product.id)
			
			for section in section_ids:
				list_section.append(section.id)

			if list_prod :
				query5 = "SELECT name FROM crm_lead"
				self.env.cr.execute(query5)
				res5 = self.env.cr.dictfetchall()
				for i in res5:
					label=i['name']
					self.env.cr.execute("SELECT COUNT(id), stage_id FROM crm_lead WHERE type_act != '' AND name =%s AND stage_id IN %s AND section_id IN %s GROUP BY stage_id",(label,(6,7),tuple(list_section)))
					res6 = self.env.cr.dictfetchall()
					if res6:
						value=res6[0]
						number_activity_pro=value.get('count')
						data.append({'label': label, 'value':number_activity_pro, 'id':self.id})
				return [{'values': data, 'area': True, 'id': self.id}]
		else : #pour le commercial
			print '#pour le commercial'
			product_ids = self.env['product.template'].search([('a_suivre','=',True)])
			for product in product_ids :
				list_prod.append(product.id)

			section_ids = self.env['crm.case.section'].search([('member_ids','=',user_id),('active','=','True')])
			for section in section_ids:
				list_section.append(section.id)
			if list_prod :
				self.env.cr.execute("SELECT COUNT(id), name, stage_id FROM crm_lead WHERE type_act != '' AND stage_id IN %s AND section_id IN %s AND user_id =%s GROUP BY stage_id, name",((6,7),tuple(list_section),user_id))
				res6 = self.env.cr.dictfetchall()
				if res6:
					value=res6[0]
					label=value.get('name')
					number_activity_pro=value.get('count')
					data.append({'label': label, 'value':number_activity_pro, 'id':self.id})
				return [{'values': data, 'area': True, 'id': self.id}]
#===================================================================

    #Revenu espéré par produit
    @api.multi
    def get_rect_graph_datas(self):
	data = []
	list_prod = []
	list_opportunity = []
	list_section = []
 	if self.type == 'product_after' :
		user_id = self.env['res.users'].browse(self.env.uid).id ##user en cours
		##Liste des produits à suivre
		product_ids = self.env['product.template'].search([('a_suivre','=',True)])
		if product_ids :
			for product in product_ids :
				list_prod.append(product.id)

		section_ids = self.env['crm.case.section'].search([('user_id','=',user_id),('active','=','True')])
		if list_prod and user_id == 1:
			#pour l'administrateur:
			#self.env.cr.execute("SELECT SUM(planned_revenue), name FROM crm_lead WHERE stage_id NOT IN %s AND product_id IN %s GROUP BY name",((6,7),tuple(list_prod)))
			self.env.cr.execute("SELECT SUM(c.planned_revenue), default_code, p.id FROM crm_lead c, product_product p WHERE c.product_id = p.product_tmpl_id AND stage_id = 6 AND product_id IN %s GROUP BY (default_code,p.id)",(tuple(list_prod),))

				###self.env.cr.execute("SELECT SUM(planned_revenue) FROM crm_lead WHERE stage_id = 6 AND section_id =%s",(section_id,))
		


			admin = self.env.cr.dictfetchall()
			for i in admin:
				label=i['default_code']
				#value=i.get('count')
				price=i['sum']
				data.append({'label':label , 'value':price ,'id':self.id})
			return [{'values': data, 'area': True, 'id': self.id}]

		elif section_ids :  #pour le chef du département.
			print '#pour le chef du département.'
			product_ids = self.env['product.template'].search([('a_suivre','=',True)])
			for product in product_ids :
				list_prod.append(product.id)
			
			for section in section_ids:
				list_section.append(section.id)

			if list_prod :
				self.env.cr.execute("SELECT SUM(planned_revenue), name FROM crm_lead WHERE stage_id IN %s AND product_id IN %s AND section_id IN %s GROUP BY name",((6,7),tuple(list_prod),tuple(list_section)))
				chef = self.env.cr.dictfetchall()
				for i in chef:
					label=i['name']
					price=i['sum']
					data.append({'label':label , 'value':price ,'id':self.id})
				return [{'values': data, 'area': True, 'id': self.id}]

		else : #pour le commercial
			print '#pour le commercial'
			product_ids = self.env['product.template'].search([('a_suivre','=',True)])
			for product in product_ids :
				list_prod.append(product.id)

			section_ids = self.env['crm.case.section'].search([('member_ids','=',user_id),('active','=','True')])
			for section in section_ids:
				list_section.append(section.id)
			if list_prod :
				self.env.cr.execute("SELECT SUM(planned_revenue), name FROM crm_lead WHERE stage_id IN %s AND product_id IN %s AND section_id IN %s AND user_id =%s GROUP BY name",((6,7),tuple(list_prod),tuple(list_section),user_id))
				commercial = self.env.cr.dictfetchall()
				for i in commercial:
					label=i['name']
					price=i['sum']
					data.append({'label':label , 'value':price ,'id':self.id})
				return [{'values': data, 'area': True, 'id': self.id}]


#_____________________________________________________________________________________________________________________________________#
	#31-10-2017
	#seuil=invoiced_target somme des revenus des opportunités gagnés dans un département
    @api.multi
    def get_rect_graph_datas_ca(self):
	print "u call get_rect_graph_datas_ca"
	data = []
	value = []
 	if self.type == 'departement_after' :
		#get the current uid 
		user_id=self.env['res.users'].browse(self.env.uid).id
		if user_id == 1 :
			self.env.cr.execute("SELECT id, complete_name, invoiced_target FROM crm_case_section")
			res9 = self.env.cr.dictfetchall()
			for i in res9:
				label=i['complete_name']
				ca_departement=i['invoiced_target']
				section_id=i['id']
				data.append({'label':label ,'value':ca_departement,'id':self.id})
			return [{'values': data, 'area': True, 'id': self.id}]

		else :
			dep_id=self.env['crm.case.section'].search([('user_id','=',user_id)])
			if not dep_id :
				self.env.cr.execute("SELECT section_id FROM sale_member_rel WHERE member_id=%s",(user_id,))
				res20 = self.env.cr.dictfetchall()
				for i in res20:
					section_id=i['section_id']
					name_dep=self.env['crm.case.section'].browse(section_id).complete_name
					invoiced_target=self.env['crm.case.section'].browse(section_id).invoiced_target
					data.append({'label':name_dep ,'value':invoiced_target,'id':self.id})
				return [{'values': data, 'area': True, 'id': self.id}]

			else :
				name_dep=self.env['crm.case.section'].browse(dep_id.id).complete_name
				invoiced_target=self.env['crm.case.section'].browse(dep_id.id).invoiced_target
				data.append({'label':name_dep ,'value':invoiced_target,'id':self.id})
				return [{'values': data, 'area': True, 'id': self.id}]

				#get all the departement of the chef




	#somme des revenus des opportunitées gagnées pour chaque commercial 
    @api.multi
    def get_line_graph_ca_cm(self):
	print "u call get_rect_graph_datas_ca_cm"
	data = []

 	if self.type == 'commercial_after' :
		#get the current uid 
		user_id=self.env['res.users'].browse(self.env.uid).id
		
		#Si l'utilisateur est l'administrateur
		if user_id == 1:
			self.env.cr.execute("SELECT member_id FROM sale_member_rel ")
			res20 = self.env.cr.dictfetchall()
			for i in res20:
				member_id=i['member_id']

				#les opportunité gagné pour chaque commercial
				opportunity_ids= self.env['crm.lead'].search([('stage_id','=',6),('user_id','=',member_id)])
				revenu_won=0
				for opportunity_id in opportunity_ids :
					#somme des revenus
					revenu_won=self.env['crm.lead'].browse(opportunity_id.id).planned_revenue + revenu_won

				partner_id=self.env['res.users'].browse(member_id).partner_id.id
				self.env.cr.execute("SELECT name FROM res_partner WHERE id=%s",(partner_id,))
				res10 = self.env.cr.dictfetchall()
				for i in res10:
					label=i['name']
					data.append({'label':label,'value':revenu_won,'id':self.id})
			return [{'values': data, 'area': True, 'id': self.id}]

		#Si l'utilisateur est le commercial ou le chef
		else :

			dep_id=self.env['crm.case.section'].search([('user_id','=',user_id)])
			if not dep_id :
				#les opportunité gagné pour chaque commercial
				opportunity_ids= self.env['crm.lead'].search([('stage_id','=',6),('user_id','=',user_id)])
				revenu_won=0
				for opportunity_id in opportunity_ids :
					#somme des revenus
					revenu_won=self.env['crm.lead'].browse(opportunity_id.id).planned_revenue + revenu_won
			
				#get the complete name of the user
				partner_id=self.env['res.users'].browse(user_id).partner_id.id

				self.env.cr.execute("SELECT name FROM res_partner WHERE id=%s",(partner_id,))
				res10 = self.env.cr.dictfetchall()
				for i in res10:
					label=i['name']
					data.append({'label':label,'value':revenu_won,'id':self.id})
				return [{'values': data, 'area': True, 'id': self.id}]
			else :	
				print "chef"
				#get all commercial
				member_ids=self.env['crm.case.section'].browse(dep_id.id).member_ids
				for member_id in member_ids:
					partner_id=self.env['res.users'].browse(member_id.id).partner_id.id
					#get the name of the user
					partner_name=self.env['res.partner'].browse(partner_id).name	
					#pour chaque commercial les opportunités gagnées
					opportunity_ids= self.env['crm.lead'].search([('stage_id','=',6),('section_id','=',dep_id.id),('user_id','=',member_id.id)])
					revenu_won=0
					for opportunity_id in opportunity_ids :
						#somme des revenus
						revenu_won=self.env['crm.lead'].browse(opportunity_id.id).planned_revenue + revenu_won

					data.append({'label':partner_name,'value':revenu_won,'id':self.id})
				return [{'values': data, 'area': True, 'id': self.id}]

    @api.multi
    def get_kanban_dashboard_bar_ca(self):
	print 'hello'
	data=[]
	value = []
 	if self.type == 'departement_after' :
	#get section_id pour avoir pour chaque département ces opportunités gagnées
		user_id=self.env['res.users'].browse(self.env.uid).id
		if user_id == 1 :
			self.env.cr.execute("SELECT id, complete_name FROM crm_case_section")
			res9 = self.env.cr.dictfetchall()
			for i in res9:
				label=i['complete_name']
				section_id=i['id']
				self.env.cr.execute("SELECT SUM(planned_revenue) FROM crm_lead WHERE stage_id = 6 AND section_id =%s",(section_id,))
				res12 = self.env.cr.dictfetchall()
				for i in res12:
					somme=i['sum']
					data.append({'label':label,'value':somme, 'id':self.id})
			return [{'values': data, 'area': True}]
		else :

			dep_id=self.env['crm.case.section'].search([('user_id','=',user_id)])
			if not dep_id :
				self.env.cr.execute("SELECT section_id FROM sale_member_rel WHERE member_id=%s",(user_id,))
				res20 = self.env.cr.dictfetchall()
				for i in res20:
					section_id=i['section_id']
					label=self.env['crm.case.section'].browse(section_id).complete_name

					opportunity_ids= self.env['crm.lead'].search([('stage_id','=',6),('section_id','=',section_id),('user_id','=',user_id)])
					revenu_won=0
					for opportunity_id in opportunity_ids :
						#somme des revenus
						revenu_won=self.env['crm.lead'].browse(opportunity_id.id).planned_revenue + revenu_won
						data.append({'label':label,'value':revenu_won, 'id':self.id})

				return [{'values': data, 'area': True}]

				
			else:
				self.env.cr.execute("SELECT complete_name FROM crm_case_section WHERE id=%s",(dep_id.id,))
				res1 = self.env.cr.dictfetchall()
				for i in res1:
					label=i['complete_name']
					member_ids=self.env['crm.case.section'].browse(dep_id.id).member_ids
					for member_id in member_ids:
						partner_id=self.env['res.users'].browse(member_id.id).partner_id.id
						#get the name of the user
						partner_name=self.env['res.partner'].browse(partner_id).name
						#pour chaque commercial les opportunités gagnées
						opportunity_ids= self.env['crm.lead'].search([('stage_id','=',6),('section_id','=',dep_id.id),('user_id','=',member_id.id)])
						revenu_won=0
						for opportunity_id in opportunity_ids :
							#somme des revenus
							revenu_won=self.env['crm.lead'].browse(opportunity_id.id).planned_revenue + revenu_won
							data.append({'label':label,'value':revenu_won, 'id':self.id})
				return [{'values': data, 'area': True}]

	









