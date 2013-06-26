# -*- coding: utf-8 -*-
# #############################################################################
# 
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2013 Bluestar Solutions Sàrl (<http://www.blues2.ch>).
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
from datetime import date, datetime, timedelta
from time import mktime, strptime
import json
import httplib2
from dateutil import parser as dateparser
import threading
import base64

WEBSERVICE_TYPE = [('GET','Get'),('PUSH', 'Push'),('PUSH_GET','Push Get Sync'),('GET_PUSH','Get Push Sync'),]
HTTP_AUTH_TYPE = [('NONE', 'None'), ('BASIC', 'Basic')]
DATETIME_FORMAT = [('TIMESTAMP','Epoch'),('ISO8601','ISO 8601'),('SWISS','Swiss "dd.mm.yyyy HH:MM:SS" format')]

webservice_lock = threading.Lock()

class DuplicateCallException(Exception):
    pass

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
        'ws_path': fields.char('Webservice Path', size=1024, required=True),
        'http_auth_type': fields.selection(HTTP_AUTH_TYPE, 'HTTP Authentication', required=True),
        'http_auth_login': fields.char('HTTP Login', size=64),
        'http_auth_password': fields.char('HTTP Password', size=64),
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
        'next_service': fields.many2one('bss.webservice', 'Next Service'),
        'is_running': fields.boolean('Is Running'),
        'call_limit': fields.integer('Soft log limit', required=True, help="Defines how many log entries to keep when no errors are detected."),
        'call_limit_in_error': fields.float('Error log limit', required=True, help="Defines how many hours the log entries with errors must be kept."),
    }
    
    _default= {
        'wait_retry_minutes': 5,
        'wait_next_minutes':720,
        'priority': 16,
        'active': True,
        'last_run': datetime(1970,1,1),        
        'last_success': datetime(1970,1,1),
        'datetime_format': 'TIMESTAMP',
        'call_limit': 0,
        'call_limit_in_error': 1.0,
    }
    _order = "priority, last_success"
    
    @staticmethod
    def purge_data(field_list, decoded, datetime_format):
        if not datetime_format:
            datetime_format='TIMESTAMP'
        data = dict()
        for key in decoded.keys():
            if key in field_list:
                if decoded[key]:
                    if field_list[key]['type'] in ('date','datetime','time'):
                        data[key]=webservice.str2date(decoded[key],field_list[key]['type'],datetime_format)
                    else:
                        data[key]=decoded[key]
                else:
                    data[key] = decoded[key]
        return data
    
    @staticmethod
    def str2date(string, date_type, date_format):
        if not string:
            return None
        if date_format == 'TIMESTAMP':
            if date_type=='date':
                return date.fromtimestamp(string)
            elif date_type=='datetime':
                return datetime.fromtimestamp(string)
            elif date_type=='time':
                return datetime.fromtimestamp(string).time()
        elif date_format == 'ISO8601':
            if date_type=='date':
                return dateparser.parse(string).date()
            elif date_type=='datetime':
                return dateparser.parse(string)
            elif date_type=='time':
                return dateparser.parse(string).time()
        elif date_format == 'SWISS':
            if date_type=='date':
                return datetime.strptime(string,'%d.%m.%Y').date()
            elif date_type=='datetime':
                return datetime.strptime(string,'%d.%m.%Y %H:%M:S')
            elif date_type=='time':
                return datetime.strptime(string,'%H:%M:S').time()
        return None
      
    @staticmethod
    def date2str(string, date_type, date_format):
        if not string:
            return None
        if date_format == 'TIMESTAMP':
            if date_type=='date':
                return int(mktime(strptime(string,"%Y-%m-%d")))
            elif date_type=='datetime':
                return int(mktime(strptime(string,"%Y-%m-%d %H:%M:%S.%f")))
            elif date_type=='time':
                return int(mktime(strptime(string,"%H:%M:S")))
        elif date_format == 'ISO8601':
            if date_type=='datetime':
                return datetime.strftime(datetime.strptime(string,"%Y-%m-%d %H:%M:%S.%f"),'%Y-%m-%dT%H:%M:S')
            elif date_type in ('date','time'):
                return string
        elif date_format == 'SWISS':
            if date_type=='date':
                return datetime.strftime(datetime.strptime(string,"%Y-%m-%d"),'%d.%m.%Y')            
            elif date_type=='datetime':
                return datetime.strftime(datetime.strptime(string,"%Y-%m-%d %H:%M:%S.%f"),'%d.%m.%Y %H:%M:S')
            elif date_type=='time':
                return string
        return None
            
    def create(self, cr, user, vals, context=None):
        """Add cron if it does not exists for webservices and the webservice must be run automatically"""
        if vals['active'] and vals['wait_next_minutes'] and vals['wait_next_minutes']>0:
            self.pool.get('bss.webservice_handler').get_cron_id( cr, user, context)    
        return super(webservice, self).create(cr, user, vals, context)

    
    def default_read_encode(self, cr, uid, model, last_success, parameters, datetime_format):
        logger = logging.getLogger('bss.webservice')
        str_last_success = str(last_success)
        if parameters:
            search_param = "['&', "+parameters+", '|' ,('create_date', '>=', '"+str_last_success+"'), '&', ('write_date', '!=', False), ('write_date', '>=', '"+str_last_success+"')]"
        else:
            search_param = "['|' ,('create_date', '>=', '"+str_last_success+"'), '&', ('write_date', '!=', False), ('write_date', '>=', '"+str_last_success+"')]"
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
                        encode_dict[key]=webservice.date2str(encode[key],field_list[key]['type'],datetime_format)
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
                oid = model.search(cr, uid, param_list)
                if oid:
                    oid = oid[0]
            else:
                oid = decoded['id']
                if not oid:
                    oid = decoded['openerp_id']
 
            data = webservice.purge_data(field_list, decoded, datetime_format)
            
            if oid:
                logger.info('oid is %s, data is %s',oid,data)
                model.write(cr, uid, oid,data)
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
        if service.http_auth_type == 'BASIC':
            headers["Authorization"] = "Basic {0}".format(base64.b64encode("{0}:{1}".format(service.http_auth_login, service.http_auth_password)))
        if service.last_success:
            headers['Last-Success'] = webservice.date2str(service.last_success, 'datetime', 'ISO8601')
        logger.debug('Url : %s \\n', url)
        response, content = http.request(url, "GET", headers=headers)
#        logger.debug('Response: %s \n%s', response, content)
        logger.debug('Response: %s ', response)
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
            headers['Last-Success'] = webservice.date2str(service.last_success, 'datetime', 'ISO8601')
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
            context={}
        if isinstance(service_id, list):
            service_id = service_id[0]
        logger = logging.getLogger('bss.webservice')
        
        service_cr = self.pool.db.cursor()
#        db_name = db.dbname
        call_obj = self.pool.get('bss.webservice_call')
        
        now = datetime.now()
        
        try:
            with webservice_lock:
                service = self.browse(service_cr, uid, [service_id], context)[0]
                if service.is_running:
                    logger.error('Duplicate webservice %s call',service_id)
                    raise DuplicateCallException()
                else:
                    self.write(service_cr, uid, service_id, {'is_running':True})
                    service_cr.commit()
                         
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
            get_response = None
            get_resp_content = None
            push_response = None
            push_resp_content = None
            
            if service.service_type == 'GET':
                success, get_response, get_resp_content = self.service_get(service_cr, uid, service, model)
            elif service.service_type == 'PUSH':
                success, push_response, push_resp_content = self.service_push(service_cr, uid, service, model) 
            elif service.service_type == 'PUSH_GET':
                success, push_response, push_resp_content = self.service_push(service_cr, uid, service, model)
                if success:
                    success, get_response, get_resp_content = self.service_get(service_cr, uid, service, model)
            elif service.service_type == 'GET_PUSH':
                success, get_response, get_resp_content = self.service_get(service_cr, uid, service, model) 
                if success:
                    success, push_response, push_resp_content = self.service_push(service_cr, uid, service, model)  
                  
            if success and model and service.after_method_name and hasattr(model,service.after_method_name):
                method = getattr(model,service.after_method_name)       
                method(service_cr, uid, get_resp_content, push_resp_content)
            
            if success:    
                with webservice_lock:
                    self.write(service_cr, uid, service_id, {'last_run':now,'last_success':now, 'is_running': False})
                    service_cr.commit()
            else:
                service_cr.rollback()
                with webservice_lock:
                    self.write(service_cr, uid, service_id, {'last_run':now, 'is_running': False})
                    service_cr.commit()
                               
            call_param = {'service_id': service_id, 'call_moment': now, 'success': success}
            if get_response:
                call_param['get_status']= get_response.status
                call_param['get_reason']=get_response.reason
                call_param['get_body']= get_resp_content
            if push_response:
                call_param['push_status']= push_response.status
                call_param['push_reason']=push_response.reason
                call_param['push_body']= push_resp_content
                
            call_obj.create(service_cr, uid, call_param)
            self.clear_call(service_cr, uid, [service_id], context)
            service_cr.commit()
        except DuplicateCallException, e:
            logger.exception("DuplicateCallException occured during webservice: %s", e)
            success= False
            service_cr.rollback()
        except Exception, e:
            logger.exception("Exception occured during webservice: %s", e)
            success= False
            service_cr.rollback()
            with webservice_lock:
                self.write(service_cr, uid, service_id, {'last_run':now, 'is_running': False})
                service_cr.commit()
        finally:
            service_cr.close()  
        if success and service and service.next_service:
            success = success and self._run_service(cr, uid, [service.next_service.id], context)
        return success

    def _run_service(self, cr, uid, ids, context=None):
        if not context:
            context={}
        success = True
        for service_id in ids:
            success = success and self.do_run(cr, uid, service_id, context)
        return success

    def run_service_multithread(self, cr, uid, ids, context=None):
        try:
            # Spawn a thread to execute the webservices
            task_thread = threading.Thread(target=self._run_service, args=(cr, uid, ids))
            task_thread.setDaemon(False)
            task_thread.start()
            self._logger.debug('Webservice thread spawned')
        except Exception:
            self._logger.warning('Exception in webservice multithread:', exc_info=True)
        return False

    
    def run_service(self, cr, uid, ids, context=None):
        return self._run_service(cr, uid, ids, context)
    
    def clear_call(self, cr, uid, ids, context=None):
        call_pool = self.pool.get('bss.webservice_call')
        if not context:
            context = {}
        
        for ws in self.browse(cr, uid, ids, context):
            if 'force' in context.keys() and context['force'] == 1:
                cr.execute("""
                    DELETE FROM bss_webservice_call
                    WHERE id NOT IN (
                        SELECT id
                        FROM bss_webservice_call
                        WHERE service_id = %s
                        ORDER BY call_moment DESC
                        LIMIT 1
                        )
                        AND service_id = %s
                           """ % (ws.id,ws.id))
                continue
                
            if ws.call_limit == 0:
                continue
            
            if call_pool.search(cr, uid, [('service_id','=',ws.id),('success','=',False)]):
                cr.execute("""
                    DELETE FROM bss_webservice_call
                    WHERE call_moment < '%s'
                        and service_id = %s
                           """ % ((datetime.now() - timedelta(hours=ws.call_limit_in_error)).isoformat(),ws.id))
            else:
                cr.execute("""
                    DELETE FROM bss_webservice_call
                    WHERE id NOT IN (
                        SELECT id
                        FROM bss_webservice_call
                        WHERE service_id = %s
                        ORDER BY call_moment DESC
                        LIMIT %s
                        )
                        AND service_id = %s
                           """ % (ws.id,ws.call_limit,ws.id))
                
        return True
        
webservice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
