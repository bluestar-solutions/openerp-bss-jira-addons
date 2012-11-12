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
from datetime import datetime

class webservice_call(osv.osv):
    _name = 'bss.webservice_call'
    _description = 'Webservice Call'
    _logger = logging.getLogger(_name)

    _columns= {
        'service_id': fields.many2one('bss.webservice', 'Webservice', required=True),
        'call_moment': fields.datetime('Call'),
        'success': fields.boolean('Success'),
        'status': fields.integer('Status'),
        'reason': fields.text('Reason'),
    }
    _defaults = {
        'call_moment': lambda *x: datetime.now(),
    }
webservice_field()