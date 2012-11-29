# -*- encoding: utf-8 -*-

from openerp.osv import osv
import pn_fields

class bss_partner_phonenumbers(osv.osv):
    
    _inherit = 'res.partner'
    _description = "Bluestar Partner Phonenumbers"
    
    _columns = {
        'phone': pn_fields.phonenumber('Phone'),
        'mobile' : pn_fields.phonenumber('Mobile'),
        'fax' : pn_fields.phonenumber('Fax'),
    }

bss_partner_phonenumbers()



