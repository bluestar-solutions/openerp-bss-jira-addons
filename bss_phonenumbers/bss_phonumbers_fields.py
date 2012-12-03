# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Bluestar Solutions Sàrl (<http://www.blues2.ch>).
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
##############################################################################

from openerp.osv import osv, fields
from openerp import tools
import phonenumbers

class phonenumber(fields._column):
    _type = 'phonenumber'
    _symbol_c = '%s'
    
    def __init__(self, string="unknown", **args):
        fields._column.__init__(self, string=string, size=64, **args)
        self._symbol_set = (self._symbol_c, self._symbol_set_number)
        
    def _symbol_set_number(self, vals):
        if isinstance(vals, dict):
            number = [vals['e164'], None]
        else:
            number = vals.split(',')
            
        if not number[0] or number[0] == '':
            return None
            
        try:
            pn = phonenumbers.parse(*number)
        except phonenumbers.NumberParseException:
            raise osv.except_osv('Error', 'Invalid phone number for field : %s' % self.string)
        
        return phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
        
    def _symbol_get(self, number):
        result = {}
        if number:
            pn = phonenumbers.parse(number, None)
            result = {'e164': number,
                      'rfc3966': phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.RFC3966),
                      'international': phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}
        else:
            result = None
        return result
    
    @classmethod
    def _as_display_name(cls, field, cr, uid, obj, value, context=None):
        return tools.ustr(value['international'])
    
    




