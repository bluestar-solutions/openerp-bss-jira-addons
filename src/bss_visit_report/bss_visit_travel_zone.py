# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

class bss_visit_travel_zone(osv.osv):

    _name = 'bss_visit_report.travel_zone'
    _description = "Visit Travel Zone"

    _columns = {
        'name': fields.char('Name', size=64),    
        'amount': fields.integer('Time amount (minutes)'),
    }

bss_visit_travel_zone()
