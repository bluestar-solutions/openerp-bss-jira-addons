# -*- encoding: utf-8 -*-

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
            pn = phonenumbers.parse(number, 'CH')
            result = {'e164': number,
                      'rfc3966': phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.RFC3966),
                      'international': phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}
        else:
            result = {'e164': None,
                      'rfc3966': None,
                      'international': None}
        return result
    
    @classmethod
    def _as_display_name(cls, field, cr, uid, obj, value, context=None):
        return tools.ustr(value['international'])
    
    




