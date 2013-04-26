# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

class bluestar_country_state(osv.osv):
    
    _description="Bluestar country state"
    _inherit = 'res.country.state'
    
    def _get_unique_code(self, cr, uid, ids, field_name, arg, context):
        result={}
        for state in self.browse(cr, uid, ids, context=context):
            result[state.id] = '%(cc)s_%(sc)s' % {'cc': state.country_id.code ,'sc': state.code}
        return result
    
    _columns = {
        'name': fields.char('State Name', size=64, required=True, translate=True),
        'unique_code': fields.function(_get_unique_code, type='char', method=True, store=True, string='Unique code'),
    }
    
    def name_search(self, cr, user, name='', args=None, operator='ilike',
            context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        ids = self.search(cr, user, [('unique_code', 'ilike', name)] + args, limit=limit,
                context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args,
                    limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
bluestar_country_state()