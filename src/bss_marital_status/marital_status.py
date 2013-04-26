# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

class bluestar_marital_status(osv.osv):

    _name = 'bluestar.marital_status'
    _description = "Marital status"

    _columns = {
        'name': fields.char('Nom', size=20, required=True, translate=True),
    }

    _defaults = {

    }

bluestar_marital_status()
