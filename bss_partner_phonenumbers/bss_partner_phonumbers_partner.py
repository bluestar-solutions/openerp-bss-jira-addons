# -*- encoding: utf-8 -*-

from openerp.osv import osv
from bss_phonenumbers import bss_phonumbers_fields as pnfields

class bss_partner_phonenumbers_partner(osv.osv):
    
    _inherit = 'res.partner'
    _description = "Bluestar Partner Phonenumbers"
    
    _columns = {
        'phone': pnfields.phonenumber('Phone'),
        'mobile' : pnfields.phonenumber('Mobile'),
        'fax' : pnfields.phonenumber('Fax'),
    }

bss_partner_phonenumbers_partner()



