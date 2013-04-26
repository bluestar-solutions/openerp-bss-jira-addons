# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

class bluestar_resident_permit(osv.osv):

    _name = 'bluestar.resident_permit'
    _description = "Resident permit"

    _columns = {
        'name': fields.char('Name', size=20, required=True, translate=True),
        'description': fields.char('Description', size=200, required=True, translate=True),
    }

    _defaults = {

    }

bluestar_resident_permit()
