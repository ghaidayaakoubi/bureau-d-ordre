import xlwt

from xlsxwriter.workbook import Workbook

from cStringIO import StringIO

import base64
from openerp import models, fields, api, _




class inventory_excel_extended(models.Model):

	_name= "excel.extended"

	excel_file = fields.Binary('Dowload report Excel')

	file_name = fields.Char('Excel File', size=64)







	def print_excel_report(self, cr, uid, ids, context=None):


	    filename= 'Emails_Clients.xls'

	    workbook= xlwt.Workbook(encoding="UTF-8")

	    worksheet= workbook.add_sheet('Emails_Clients')

	    style = xlwt.easyxf('font:height 400, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')

	    worksheet.write_merge(0,1,0,7,'Emails Clients ',style)

	    style2 = xlwt.easyxf('font:height 300, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')

	    worksheet.col(0).width=600*12
	    worksheet.col(1).width=600*12
	    worksheet.write(2,0,'Nom Client ',style2)
	    worksheet.write(2,1,'Email ',style2)
	    client_ids=self.pool.get('res.partner').search(cr, uid, [('customer','=',True)])
	    client_obj=self.pool.get('res.partner').browse(cr,uid,client_ids)
	    i=3
	    if client_obj:	
		for client in client_obj:
			if client.email :
				worksheet.write(i,0,client.name)
				worksheet.write(i,1,client.email)

				i+=1
	    fp = StringIO()
	    workbook.save(fp)
	    export_id = self.pool.get('excel.extended').create(cr, uid, {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename}, context=context)

	    fp.close()

	    return{

		'view_mode': 'form',

		'res_id': export_id,

		'res_model': 'excel.extended',

		'view_type': 'form',

		'type': 'ir.actions.act_window',

		'context': context,

		'target': 'new',

	    }

