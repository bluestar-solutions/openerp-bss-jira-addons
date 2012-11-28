# -*- encoding: utf-8 -*-

from osv import osv, fields

class bss_config(osv.osv_memory):
    
    _name = 'bss.config'
    _inherit = 'res.config'

    _columns = {
    }

    def execute(self, cr, uid, ids, context=None):
        return
        
bss_config()

