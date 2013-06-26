# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################

from openerp.osv import osv, fields
from openerp.addons.base.ir.ir_fields import ir_fields_converter
import phonenumbers

class bss_phonenumbers_converter(osv.TransientModel):
    
    _name = 'bss.phonenumbers.converter'

    @staticmethod
    def _parse(vals, region=''):
        if isinstance(vals, dict):
            number = [vals['e164'], region]
        elif vals:
            if 'xxx' in vals:
                return vals
            number = vals.split(',')
            if len(number) == 1:
                number = [number[0], region]
        else :
            return None
        
        if not number[0] or number[0] == '':
            return None
        
        return phonenumbers.parse(*number)  
    
    def parse(self, cr, uid, vals, context=None):
        try:
            return bss_phonenumbers_converter._parse(vals)
        except phonenumbers.NumberParseException:
            return None

    @staticmethod
    def _format(vals):
        if isinstance(vals, unicode) and vals.startswith('xxx'):
            return {
                'e164': vals,
                'international': vals,
                'rfc3966': vals,
            }
            
        pn = bss_phonenumbers_converter._parse(vals)
        if not pn:          
            return {
                'e164': None,
                'international': None,
                'rfc3966': None,
            }   
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
        vals = super(phonenumber, self)._symbol_set_char(vals)
        try:
            res = bss_phonenumbers_converter._format(vals)
        except phonenumbers.NumberParseException:
            raise osv.except_osv('Error', 'Invalid phone number for field : %s' % self.string)
        
        return res['e164']
        
    def _symbol_get(self, number):
        result = {}
        if number:
            pn = bss_phonenumbers_converter._format(number)
            result = pn['international']
        else:
            result = None
        return result

class pn_fields_converter(ir_fields_converter):
    def _str_to_phonenumber(self, cr, uid, model, column, value, context=None):
        return super(pn_fields_converter, self)._str_to_char(cr, uid, model, column, value, context)




