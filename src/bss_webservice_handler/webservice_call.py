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
from datetime import datetime
import re

CALL_RESULT = [('ok','OK'),('warn','Warning'),('error','Error')]
RETURN_CODES = {
                r"(?!^206$)^[2]{1}[0-9]{2}$":'ok',      # 200 except 206
                r"(?!^310$)^[3]{1}[0-9]{2}$":'warn',    # 300 except 310
                r"^[4]{1}[0-9]{2}$":'error',            # 400
                r"(?!^503$)^[5]{1}[0-9]{2}$":'error',   # 500 except 503
                r"^(206|503)$":'warn',                  # 206 or 503
                r"^310$":'error',                       # 310
                }

class webservice_call(osv.osv):
    _name = 'bss.webservice_call'
    _description = 'Webservice Call'
    _logger = logging.getLogger(_name)
    
    def _success(self, cr, uid, ids, field_name, args, context=None):
        if context is None:
            context = {}
        
        res = {}
        
        for call in self.browse(cr, uid, ids, context):
            res[call.id] = (call.call_result == 'ok')
        
        return res
    
    def _return_code_parser(self, code):
        for k,v in RETURN_CODES.iteritems():
            if re.compile(k).search(str(code)) is not None:
                return v
        return 'error'
    
    def _get_most_serious(self, pcode, gcode):
        res = [self._return_code_parser(pcode),self._return_code_parser(gcode)]
        if 'error' in res:
            return 'error'
        elif 'warn' in res:
            return 'warn'
        return 'ok'

    _columns= {
        'service_id': fields.many2one('bss.webservice', 'Webservice', required=True, ondelete='cascade'),
        'call_moment': fields.datetime('Call'),
        'success': fields.function(_success, method=True, store=True, type="boolean", string='Success'),
        'call_result': fields.selection(CALL_RESULT, 'Call result'),
        'get_status': fields.integer('Get Status'),
        'push_status': fields.integer('Push Status'),
        'get_reason': fields.text('Get Reason'),
        'push_reason': fields.text('Push Reason'),
        'get_body': fields.text('Get Body'),
        'push_body': fields.text('Push Body'),
    }
    _defaults = {
        'call_moment': lambda *x: datetime.now(),
    }
    _order = "call_moment desc"
    
    def create(self, cr, uid, vals, context=None):
        if 'push_status' in vals.keys() and 'get_status' in vals.keys():
            vals['call_result'] = self._get_most_serious(vals['push_status'], vals['get_status'])
        elif 'get_status' in vals.keys():
            vals['call_result'] = self._return_code_parser(vals['get_status'])
        elif 'push_status' in vals.keys():
            vals['call_result'] = self._return_code_parser(vals['push_status'])
        super(webservice_call, self).create(cr, uid, vals, context)
    
webservice_call()
