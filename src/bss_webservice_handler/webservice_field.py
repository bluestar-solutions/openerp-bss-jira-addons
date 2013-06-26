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

class webservice_field(osv.osv):
    _name = 'bss.webservice_field'
    _description = 'Webservice Field'
    _logger = logging.getLogger(_name)

    _columns= {
        'service_id': fields.many2one('bss.webservice', 'Webservice', required=True),
        'web_field_names': fields.text('Web Field Names', required=True),
        'model_name': fields.char('Object', size=64, required=True),
        'oe_field_names': fields.text('OE Field Names', required=True),
        'web_oe_method_name': fields.char('Web - OE Translation', size=256, required=True),
        'oe_web_method_name': fields.char('OE - Web Translation', size=256, required=True),      
    }

webservice_field()