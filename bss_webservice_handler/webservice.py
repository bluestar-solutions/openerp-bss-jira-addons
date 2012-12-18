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
from datetime import date, datetime
from time import mktime, strptime
import json
import httplib2

WEBSERVICE_TYPE = [('GET','Get'),('PUSH', 'Push'),('PUSH_GET','Push Get Sync'),('GET_PUSH','Get Push Sync'),]
#HTTP_METHOD= [('GET','GET'),('POST','POST')]
HTTP_AUTH_TYPE = [('NONE', 'None'), ('BASIC', 'Basic')]
DATETIME_FORMAT = [('TIMESTAMP','Epoch'),('ISO8601','ISO 8601'),('SWISS','Swiss "dd.mm.yyyy HH:MM:SS" format')]

class webservice(osv.osv):
    _name = 'bss.webservice'
    _description = 'Webservice'
    _logger = logging.getLogger(_name)
            
    _columns= {
        'name': fields.char('Name', size=64, required=True,),
        'service_type': fields.selection(WEBSERVICE_TYPE, 'Type', required=True),
        'ws_protocol': fields.char('Webservice Protocol', size=256, required=True),
        'ws_host': fields.char('Webservice Host', size=256, required=True),
        'ws_port': fields.char('Webservice Port', size=256, required=True),
        'ws_path': fields.char('Webservice Path', size=256, required=True),
#        'http_method': fields.selection(HTTP_METHOD, 'HTTP Method', required=True),
        'http_auth_type': fields.selection(HTTP_AUTH_TYPE, 'HTTP Authentication', required=True),
        'http_auth_login': fields.char('HTTP Login', size=64),
        'http_auth_password': fields.char('HTTP Password', size=64, invisible=True),
        'model_name': fields.char('Model Name', size=128, required=True),
        'field_ids': fields.one2many('bss.webservice_field','service_id','Service Fields Translations'),
        'before_method_name': fields.char('Before Method Name', size=128),
        'after_method_name': fields.char('After Method Name', size=128),
        'encode_method_name': fields.char('Encode Method Name', size=128),
        'decode_method_name': fields.char('Decode Method Name', size=128),
        'push_filter': fields.char('Push Filter', size=1024),
        'get_db_key': fields.char('Get DB Key', size=1024),
        'datetime_format': fields.selection(DATETIME_FORMAT, 'Date & Time Format', required = True),
        'wait_retry_minutes': fields.integer('Wait Retry', required=True),
        'wait_next_minutes': fields.integer('Wait Next', required=True),
        'priority': fields.integer('Priority', required=True, help="Defines the order of the calls, lowest number comes first."),
        'active': fields.boolean('Active'),
        'last_run': fields.datetime('Last Run'),
        'last_success': fields.datetime('Last Success'),
        'call_ids': fields.one2many('bss.webservice_call','service_id','Service Calls'),
    }
    
    _default= {
        'wait_retry_minutes': 5,
        'wait_next_minutes':720,
        'priority': 16,
        'active': True,
        'last_run': datetime(1970,1,1),        
        'last_success': datetime(1970,1,1),
        'datetime_format': 'TIMESTAMP',
    }
    _order = "priority, last_success"
    
    def str2date(self, string, type, format):
        if not string:
            return None
        if format == 'TIMESTAMP':
            if type=='date':
                return date.fromtimestamp(string)
            elif type=='datetime':
                return datetime.fromtimestamp(string)
            elif type=='time':
                return datetime.fromtimestamp(string).time()
        elif format == 'ISO8601':
            if type=='date':
                return datetime.strptime(string,'%Y-%m-%d').date()
            elif type=='datetime':
                return datetime.strptime(string,'%Y-%m-%dT%H:%M:S')
            elif type=='time':
                return datetime.strptime(string,'%H:%M:S').time()
        elif format == 'SWISS':
            if type=='date':
                return datetime.strptime(string,'%d.%m.%Y').date()
            elif type=='datetime':
                return datetime.strptime(string,'%d.%m.%Y %H:%M:S')
            elif type=='time':
                return datetime.strptime(string,'%H:%M:S').time()
        return None
      
    def date2str(self, string, type, format):
        if not string:
            return None
        if format == 'TIMESTAMP':
            if type=='date':
                return int(mktime(strptime(string,"%Y-%m-%d")))
            elif type=='datetime':
                return int(mktime(strptime(string,"%Y-%m-%d %H:%M:%S.%f")))
            elif type=='time':
                return int(mktime(strptime(string,"%H:%M:S")))
        elif format == 'ISO8601':
            if type=='datetime':
                return datetime.strftime(datetime.strptime(string,"%Y-%m-%d %H:%M:%S.%f"),'%Y-%m-%dT%H:%M:S')
            elif type in ('date','time'):
                return string
        elif format == 'SWISS':
            if type=='date':
                return datetime.strftime(datetime.strptime(string,"%Y-%m-%d"),'%d.%m.%Y')            
            elif type=='datetime':
                return datetime.strftime(datetime.strptime(string,"%Y-%m-%d %H:%M:%S.%f"),'%d.%m.%Y %H:%M:S')
            elif type=='time':
                return string
        return None
        
    def create(self, cr, user, vals, context=None):
        """Add cron if it does not exists for webservices and the webservice must be run automatically"""
        if vals['active'] and vals['wait_next_minutes'] and vals['wait_next_minutes']>0:
            self.pool.get('bss.webservice_handler').get_cron_id( cr, user, context)    
        return super(webservice, self).create(cr, user, vals, context)

    
    def default_read_encode(self, cr, uid, model, last_success, parameters, datetime_format):
        logger = logging.getLogger('bss.webservice')
        if parameters:
            search_param = "['&',"+parameters+",'|',('create_date','>=',str(last_success)),'&',('write_date','!=',False),('write_date','>=',str(last_success))]"
        else:
            search_param = "['|',('create_date','>=',str(last_success)),'&',('write_date','!=',False),('write_date','>=',str(last_success))]"
        encode_ids = model.search(cr, uid, eval(search_param))
        encodes = model.browse(cr, uid, encode_ids)
        logger.debug('model columns = %s', str(model._columns))
        logger.debug('model fields = %s', str(model.fields_get(cr,uid)))
        encode_list = list()
        field_list = model.fields_get(cr,uid)
        for encode in encodes:
            encode_dict = dict()
            for key in field_list:
                if field_list[key]['type']=='many2one':
                    if encode[key]:
                        encode_dict[key]=encode[key].id
                    else:
                        encode_dict[key]=None
                elif field_list[key]['type'] in ('date','datetime','time'):
                    if encode[key]:
                        encode_dict[key]=self.date2str(encode[key],field_list[key]['type'],datetime_format)
                    else:
                        encode_dict[key]=None                        
                else:
                    if encode[key]:
                        encode_dict[key]=encode[key]
                    else:
                        encode_dict[key]=None
                
            encode_dict['id']=encode.id
            encode_dict['openerp_id']=encode.id
            encode_list.append(encode_dict)
        
        logger.debug('result list %s',encode_list)
        return json.dumps(encode_list)
    
    def default_decode_write(self, cr, uid, model, content, db_keys, datetime_format):
        logger = logging.getLogger('bss.webservice')
        decoded_list = json.loads(content)
        logger.debug("List is : %s, length is %d",str(decoded_list),len(decoded_list))
        if not decoded_list:
            return True
        elif len(decoded_list)==0:
            logger.debug("List is empty")
            return True
        field_list = model.fields_get(cr,uid)

        for decoded in decoded_list:
            logger.debug("Decoded is : %s, length is %d",str(decoded),len(decoded))
            if db_keys:
                db_key_list = db_keys.split(',')
                param_list = []
                for key in  db_key_list:
                    param_list.append((key,'=',decoded[key]))
                id = model.search(cr, uid, param_list)
                if id:
                    id = id[0]
            else:
                id = decoded['id']
                if not id:
                    id = decoded['openerp_id']
 
            data = dict()
            for key in decoded.keys():
                logger.debug("Testing key %s",key)
                if key in field_list:
                    if decoded[key]:
                        if field_list[key]['type'] in ('date','datetime','time'):
                            data[key]=self.str2date(decoded[key],field_list[key]['type'],datetime_format)
                        else:
                            data[key]=decoded[key]
                    else:
                        data[key] = decoded[key]
            
            if id:
                model.write(cr, uid, id,data)
            else:
                model.create(cr, uid, data)
        return True
    
    def service_get(self, cr, uid, service, model):
        logger = logging.getLogger('bss.webservice')
        http = httplib2.Http(".cache")
        if service.http_auth_type != 'NONE':
            http.add_credentials(service.http_auth_login, service.http_auth_password)
        url = '%(ws_protocol)s://%(ws_host)s:%(ws_port)s%(ws_path)s' % service
        headers = {"Content-type": "application/json",
                   "Accept": "application/json",
                   }  
        if service.last_success:
            headers['Last-Success'] = self.date2str(service.last_success, 'datetime', 'ISO8601')
        logger.debug('Url : %s \\n', url)
        response, content = http.request(url, "GET", headers=headers)
        logger.debug('Response: %s \n%s', response, content)
        success = False
        if response.status == 200:
            if model and service.decode_method_name and hasattr(model, service.decode_method_name):
                method = getattr(model,service.decode_method_name)
                success = method(cr, uid, model, content, service.datetime_format)
            else:
                success = self.default_decode_write(cr, uid, model, content, service.get_db_key, service.datetime_format)
            if not success:
                response.status = -1
                response.reason = 'Decode Write Error'
        else:
            success = False
        return (success, response, content)
    
    def service_push(self, cr, uid, service, model):
        logger = logging.getLogger('bss.webservice')
        http = httplib2.Http(".cache")
        if service.http_auth_type != 'NONE':
            http.add_credentials(service.http_auth_login, service.http_auth_password)
        url = '%(ws_protocol)s://%(ws_host)s:%(ws_port)s%(ws_path)s' % service
        headers = {"Content-type": "application/json",
                   "Accept": "application/json",
                   }  

        if service.last_success:
            last_success = datetime.strptime(service.last_success,"%Y-%m-%d %H:%M:%S.%f")
            headers['Last-Success'] = self.date2str(service.last_success, 'datetime', 'ISO8601')
        else:
            last_success = datetime(1970,1,1) 
        if model and service.encode_method_name and hasattr(model, service.encode_method_name):
            method = getattr(model,service.encode_method_name)
            content = method(cr, uid, model, last_success, service.push_filter, service.datetime_format)
        else:
            content = self.default_read_encode(cr, uid, model, last_success, service.push_filter, service.datetime_format)
        logger.debug('Url : %s \nBody:\n%s\n', url, content)
        response, resp_content = http.request(url, "POST", headers=headers, body=content)
        logger.debug('Response: %s \n%s', response, resp_content)
        success = False
        if response.status == 200:
            success = True
        else:
            success = False
        return (success, response, resp_content)
    
    def do_run(self, cr, uid, service_id, context=None):
        if not context:
            context = {}
        
        logger = logging.getLogger('bss.webservice')
        db = self.pool.db
        service_cr = db.cursor()
        db_name = db.dbname
        call_obj = self.pool.get('bss.webservice_call')
        
        now = datetime.now()
        
        try:
            service = self.browse(service_cr, uid, service_id, context={})[0] 
            print str(service)
            logger.info('Model name is %s', service.model_name)
            model = self.pool.get(service.model_name)
            logger.info('Model  is %s', model)
            if model and service.before_method_name and hasattr(model,service.before_method_name):
                method = getattr(model,service.before_method_name)
                method(service_cr, uid)
            
    #        service_field_obj = self.pool.get('bss.webservice_field')
    #        service_field_ids = service_field_obj.search(cr,uid,[('service_id','=',service_id)])
    #        if service_field_ids:
    #            for service_field_id in service_field_ids:
    #                service_field = service_field_obj.browse(cr,uid,service_field_id)
    
            success = False
            response = None
            resp_content = None
            if service.service_type == 'GET':
                success, response, resp_content = self.service_get(service_cr, uid, service, model)
            elif service.service_type == 'PUSH':
                success, response, resp_content = self.service_push(service_cr, uid, service, model) 
            elif service.service_type == 'PUSH_GET':
                success, response, resp_content = self.service_push(service_cr, uid, service, model)
                if success:
                    success, response, resp_content = self.service_get(service_cr, uid, service, model)
            elif service.service_type == 'GET_PUSH':
                success, response, resp_content = self.service_get(service_cr, uid, service, model) 
                if success:
                    success, response, resp_content = self.service_push(service_cr, uid, service, model)  
                  
            if success and model and service.after_method_name and hasattr(model,service.after_method_name):
                method = getattr(model,service.after_method_name)       
                method(service_cr, uid)
            
            if success:    
                self.write(service_cr, uid, service_id, {'last_run':now,'last_success':now})
                service_cr.commit()
            else:
                service_cr.rollback()
                self.write(service_cr, uid, service_id, {'last_run':now})
                service_cr.commit()
               
            if success:
                self.write(service_cr, uid, service_id, {'last_run':now,'last_success':now})
            else:
                self.write(service_cr, uid, service_id, {'last_run':now})
            call_param = {'service_id': service_id[0], 'call_moment': now, 'success': success}
            if response:
                call_param['status']= response.status
                call_param['reason']=response.reason
                call_param['body']= resp_content
                
            call_obj.create(service_cr, uid, call_param)
            service_cr.commit()

        except Exception, e:
            logger.exception("Exception occured during webservice: %s", e)
            success= False
            service_cr.rollback()
            self.write(service_cr, uid, service_id, {'last_run':now})
            service_cr.commit()
        finally:    
            service_cr.close()   
    
webservice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    