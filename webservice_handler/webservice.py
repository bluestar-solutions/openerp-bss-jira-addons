# -*- coding: utf-8 -*-
# #############################################################################
# 
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
# #############################################################################

from openerp.osv import osv, fields
from openerp.netsvc import logging
from datetime import datetime, timedelta
import json
import httplib2
import urllib2

WEBSERVICE_TYPE = [('get','Get'),('push', 'Push'),('push_get','Push Get Sync'),('get_push','Get Push Sync'),]
HTTP_METHOD= [('GET','GET'),('POST','POST')]
HTTP_AUTH_TYPE = [('None', 'None'), ('Basic', 'Basic')]
WEBSERVICE_RESULT_TYPE = [('success','Success'),('no_answer','No Answer'),('fail','Fail'),]

class webservice(osv.osv):
    _name = 'bss.webservice'
    _description = 'Webservice'
    _logger = logging.getLogger(_name)
            
    _columns= {
        'name': fields.char('Name', size=64, required=True,),
        'service_type': fields.selection(WEBSERVICE_TYPE, 'Type', required=True),
        'url': fields.char('URL', size=256, required=True),
        'http_method': fields.selection(HTTP_METHOD, 'HTTP Method', required=True),
        'http_auth_type': fields.selection(HTTP_AUTH_TYPE, 'HTTP Authentication', required=True),
        'http_auth_login': fields.char('HTTP Login', size=64),
        'http_auth_password': fields.char('HTTP Password', size=64, invisible=True),
        'model_name': fields.char('Model Name', size=128, required=True),
        'field_ids': fields.one2many('bss.webservice_field','service_id','Service Fields Translations'),
        'before_method_name': fields.char('Before Method Name', size=128, required=True),
        'after_method_name': fields.char('After Method Name', size=128, required=True),
        'encode_method_name': fields.char('Encode Method Name', size=128, required=True),
        'decode_method_name': fields.char('Decode Method Name', size=128, required=True),
        'wait_retry_minutes': fields.integer('Wait Retry', required=True),
        'wait_next_minutes': fields.integer('Wait Next', required=True),
        'priority': fields.integer('Priority', required=True, help="Defines the order of the calls, lowest number comes first."),
        'active': fields.boolean('Active'),
        'last_run': fields.datetime('Last Run'),
        'last_success': fields.datetime('Last Success'),
    }
    
    _default= {
        'wait_retry_minutes': 5,
        'wait_next_minutes':720,
        'priority': 16,
        'active': True,
        'last_run': datetime(2000,1,1),        
        'last_success': datetime(2000,1,1),
    }
    _order = "priority, last_success"
    
    def write(cr, user, ids, vals, context=None):
        """Add cron if it does not exists for webservices and the webservice must be run automatically"""
        if vals['active'] and vals['wait_next_minutes'] and vals['wait_next_minutes']>0:
            self.pool.get('bss.webservice_handler').get_cron_id( cr, uid, context)    
        return super(insurance, self).write(cr, user, ids, vals, context)
    
    def do_run(self, cr, uid, service_id, context=None):
        service = self.browse(cr, uid, service_id, context)
         
        model = self.pool.get(service.model_name)
        if model and service.before_method_name and hasattr(model,service.before_method_name):
            method = model.getattr(model,service.before_method_name)
            method(cr, uid)
        
#        service_field_obj = self.pool.get('bss.webservice_field')
#        service_field_ids = service_field_obj.search(cr,uid,[('service_id','=',service_id)])
#        if service_field_ids:
#            for service_field_id in service_field_ids:
#                service_field = service_field_obj.browse(cr,uid,service_field_id)

        success = False
        if service.service_type == 'get':
            success = service_get(cr, uid, service, model)
        elif service.service_type == 'push':
            success = service_push(cr, uid, service, model) 
        elif service.service_type == 'push_get':
            success = service_push(cr, uid, service, model) and service_get(cr, uid, service, model)
        elif service.service_type == 'get_push':
            success = success = service_get(cr, uid, service, model) and service_push(cr, uid, service, model)  
              
        if success and model and service.after_method_name and hasattr(model,service.after_method_name):
            method = model.getattr(model,service.after_method_name)       
            method(cr, uid)
            
        now = datetime.now()
        if success:
            service.write(cr, uid, service_id, {'last_run':now,'last_success':now}, context)
        else:
            service.write(cr, uid, service_id, {'last_run':now}, context)
    
    def service_get(self, cr, uid, service, model):
        bla=1
    
    def service_push(self, cr, uid, service, model):
        bla = 1
        
    def default_read_encode(self, cr, uid, model, last_success):
        encode_ids = model.search(cr, uid, ['|',('create_date','>=',last_success),('write_date','>=',last_success)])
        encodes = model.browse(cr, uid, encode_ids)
        return json.dumps(encodes)
    
    def default_decode_write(self, cr, uid, model, content):
        decoded_list = json.loads(content)
        for decoded in decoded_list:
            id = decoded['id']
            if not id:
                id = decoded['openerp_id']
            if id:
                model.write(cr, uid, id,decoded)
            else:
                model.create(cr, uid, decoded)
        return True
    
webservice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    