# -*- encoding: utf-8 -*-

from osv import osv, fields

class bluestar_config(osv.osv_memory):
    
    _name = 'bluestar.config'
    _inherit = 'res.config'

    _columns = {
    }

    def execute(self, cr, uid, ids, context=None):
        return
        
bluestar_config()

