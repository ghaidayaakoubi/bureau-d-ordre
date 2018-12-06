# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import JasperDataParser  
from openerp.jasper_reports import jasper_report
from openerp import pooler
import time
from datetime import datetime
import base64
import os
#import netsvc
from openerp.osv import fields, osv
from openerp.tools.translate import _

class jasper_client(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_client, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'records'

    def generate_parameters(self, cr, uid, ids, data, context):
        return {}

    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_records(self, cr, uid, ids, data, context):
        pool= pooler.get_pool(cr.dbname)
        result=[]
        if 'form' in data:
            #from_date = data['form']['date_from']
            survey_id = data['form']['survey_id'][1]
            print '****survey_id', survey_id
            # page_ids = data['form']['page_ids'][1]
            # print '****page_ids', page_ids
            dateAuj = time.strftime('%d-%m-%Y %H:%M')
            total=0

            sond_ids = pool.get('survey.survey').search(cr, uid, [('title', '=', survey_id)])
            sond_objs = self.pool.get('survey.survey').browse(cr, uid, sond_ids)
            if sond_objs:
                for sond in sond_objs:

                    data={
                        'dateAuj':dateAuj,
                        'title':sond.title,
                        'product_id':sond.product_id['name'],
                    }

                result.append(data)

#--------------------------------Pages-----------------------------------------------------
            #update by Marwa BM le 04-08-2017
            page_ids = pool.get('survey.page').search(cr, uid, [])
            cr.execute('SELECT id,title FROM survey_page WHERE survey_id=%s',(sond_ids[0],))
            lines_page = cr.dictfetchall()
        
            #page_objs = self.pool.get('survey.page').browse(cr, uid, page_ids)
            #print"+++++++++++++++", page_objs
            #if page_objs:
            for pag in lines_page:
                
                page_id = pag['id']

                page = pag['title']
                data = {
                    'title_page': page,
                }

                result.append(data)

#-------------------------------------Question--------------------------------------------------------

                list_quest_ids = pool.get('survey.question').search(cr, uid,[('page_id', '=', page_id)])#
                list_quest_objs = self.pool.get('survey.question').browse(cr, uid, list_quest_ids)
                if list_quest_objs:
                    for quest in list_quest_objs:
                        if quest.labels_ids:
                            for rep in quest.labels_ids:

                                data={
                                    'type':quest.type,
                                    'question':quest.question,
                                    'reponse':rep.value,
                                    'stat_path' :os.getcwd()+"/openerp/addons/cci_stat/",


                                }
                                result.append(data)
                        else:
                            data={
                                'type':quest.type,
                                'question':quest.question,
                                'reponse':'',
                                 'stat_path' :os.getcwd()+"/openerp/addons/cci_stat/",
                            }
                            result.append(data)

                    #print"..................****.data****", result.append(data)

                else :
                    data={
                                'type':'',
                                'question':'',
                                'reponse':'',
                               # 'stat_path' :'',
                                #'stat_path' :os.getcwd()+"/openerp/addons/cci_stat/",
                                 'stat_path' :os.getcwd()+"/openerp/addons/cci_stat/",

                            }
                    result.append(data)



                        
        return result

jasper_report.report_jasper('report.jasper_qestion_print', 'survey.question', parser=jasper_client, )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:c
