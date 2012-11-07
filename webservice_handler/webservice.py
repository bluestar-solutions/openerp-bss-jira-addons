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

WEBSERVICE_TYPE = [('get','Get'),('push', 'Push'),('sync','Sync'),]
HTTP_METHOD= [('GET','GET'),('POST','POST')]
HTTP_AUTH_TYPE = [('None', 'None'), ('Basic', 'Basic')]
DATA_TYPE = [('json','Json'),]
WEBSERVICE_RESULT_TYPE = [('success','Success'),('no_answer','No Answer'),('fail','Fail'),]

class webservice(osv.osv):
    _name = 'bss.webservice'
    _description = 'Webservice'
    _logger = logging.getLogger(_name)
            
    _columns= {
        'name': fields.char('Name', size=64, required=True,),
        'type': fields.selection(WEBSERVICE_TYPE, 'Type', required=True),
        'url': fields.char('URL', size=256, required=True),
        'http_method': fields.selection(HTTP_METHOD, 'HTTP Method', required=True),
        'http_auth_type': fields.selection(HTTP_AUTH_TYPE, 'HTTP Authentication', required=True),
        'http_auth_login': fields.char('HTTP Login', size=64),
        'http_auth_password': fields.char('HTTP Password', size=64, invisible=True),
        'data_type': fields.selection(DATA_TYPE,'Data Type'),
        'model_name': fields.char('Model Name', size=128, required=True),
        'before_method_name': fields.char('Before Method Name', size=128, required=True),
        'after_method_name': fields.char('After Method Name', size=128, required=True),
        'encode_method_name': fields.char('Encode Method Name', size=128, required=True),
        'decode_method_name': fields.char('Decode Method Name', size=128, required=True),
        'wait_retry_minutes': fields.integer('Wait Retry', required=True),
        'wait_next_minutes': fields.integer('Wait Next', required=True),
        'priority': fields.integer('Priority', required=True),
        'active': fields.boolean('Active'),
        'last_run': fields.datetime('Last Run'),
    }
    
    _default= {
        'wait_retry_seconds': 300,
        'wait_next_seconds':3600,
        'priority': 16,
        'active': True,
    }
    _order = "priority, last_run"
    
webservice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    