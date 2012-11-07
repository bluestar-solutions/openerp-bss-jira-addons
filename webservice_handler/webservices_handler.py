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
WEBSERVICE_RESULT_TYPE = [('success','Success'),('no_answer','No Answer'),('fail','Fail'),]

class webservice(osv.osv):
    _name = 'ws.webservice'
    _description = 'Webservice'
    _logger = logging.getLogger(_name)
            
    _columns= {
        'name': fields.char('Name', size=64, required=True,),
        'service': fields.char('Service', size=128, required=True,),
        'active': fields.boolean('Active'),
        'wait_retry_s': fields.integer('Wait Retry', required=True),
        'wait_next_s': fields.integer('Wait Next', required=True),
        'order': fields.integer('Wait Next', required=True),
    }
    
    _default= {
        'wait_retry_s': 300,
        'wait_next_s':3600,
        'order': 16,
    }
    
webservice()

class webservice_call(osv.osv):
    _name = 'ws.webservice_call'
    _description = 'Webservice Call'
    _logger = logging.getLogger(_name)
            
    _columns= {
        'webservice_id': fields.many2one('pgeam.webservice', 'Webservice', required=True),
        'call_time': fields.datetime('Call Time'),
        'result': fields.selection(WEBSERVICE_RESULT_TYPE, 'Result'),
        'error': fields.text('Error'),
    }
    
    _default= {
        'last_call': lambda *x: fields.datetime.now,
    }
           
webservice_call()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    