# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.addons import decimal_precision as dp

class bss_visit_travel_zone(osv.osv):

    _name = 'bss_visit_report.travel_zone'
    _description = "Visit Travel Zone"

    _columns = {
        'name': fields.char('Name', size=64),    
        'amount': fields.float('Travel Amount', digits_compute=dp.get_precision('Account')),
    }

bss_visit_travel_zone()
