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

class bss_phonenumbers_converter(osv.TransientModel):
    
    _name = 'bss.phonenumbers.converter'

    @staticmethod
    def _parse(number, country):           
        if not number or number == '':
            return None
        
        pn = phonenumbers.parse(number, country)  
        return phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)  
    
    def parse(self, cr, uid, number, country, context=None):
        try:
            return bss_phonenumbers_converter._parse(number, country)
        except phonenumbers.NumberParseException:
            return None

    @staticmethod
    def _format(number):           
        if not number or number == '':
            return {
                'e164': None,
                'international': None,
                'rfc3966': None,
            } 
        
        print str(number)
        pn = phonenumbers.parse(number, None)  
        return {
            'e164': phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164),
            'international': phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            'rfc3966': phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.RFC3966),
        }   

    def format(self, cr, uid, number, context=None): 
        try:
            return bss_phonenumbers_converter._format(number)   
        except phonenumbers.NumberParseException:
            return {
                'e164': None,
                'international': None,
                'rfc3966': None,
            } 

bss_phonenumbers_converter()

class phonenumber(fields.char):
    _type = 'phonenumber'
    
    def __init__(self, string="unknown", **args):
        fields.char.__init__(self, string=string, size=64, **args)
        
    def _symbol_set_char(self, vals):
        if isinstance(vals, dict):
            number = [vals['e164'], None]
        elif vals:
            number = vals.split(',')
            if len(number) == 1:
                number = [number[0], None]
        else:
            return None           
            
        try:
            res = bss_phonenumbers_converter._parse(*number)
        except phonenumbers.NumberParseException:
            raise osv.except_osv('Error', 'Invalid phone number for field : %s' % self.string)
        
        return res
        
    def _symbol_get(self, number):
        result = {}
        if number:
            pn = phonenumbers.parse(number, None)
            result = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        else:
            result = None
        return result
    
    @classmethod
    def _as_display_name(cls, field, cr, uid, obj, value, context=None):
        return tools.ustr(value['international'])




