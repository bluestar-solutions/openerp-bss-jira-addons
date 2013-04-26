# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

ZIP_TYPES = [('10', 'Home addresses and PO Box'),
             ('20', 'Home addresses only'),
             ('30', 'PO Box only'),
             ('40', 'Business'),
             ('80', 'Internal for the Post')]

class bluestar_city(osv.osv):
   
    _name = "bluestar.city"
    _description = "City"

    def _get_name(self, cr, uid, ids, field_name, arg, context):
        result={}
        for city in self.browse(cr, uid, ids, context=context):
            result[city.id] = '%(zip)s %(city)s' % {'zip': city.zip ,'city': city.long_name}
        return result

    _columns = {
        'zip_type': fields.selection(ZIP_TYPES, 'Zip types'),
        'zip': fields.char('Zip', size=10),
        'zip_complement': fields.char('Zip complement', size=2),
        'short_name': fields.char('Short name', size=18),
        'long_name': fields.char('Long name', size=27),
        'state_id': fields.many2one('res.country.state', 'State'),
        'country_id': fields.many2one('res.country', 'Country'),
        'name': fields.function(_get_name, type='char', method=True, store=True, string='Name'),
    }
    
    _order = 'country_id, name asc'
                    
bluestar_city()

class bluestar_partner(osv.osv):

    _inherit = 'res.partner'
    _description = "Bluestar City Partner"

    _columns = {
        'city_id': fields.many2one('bluestar.city', 
                                   'City Search',
                                   domain="[('zip_type', 'not in', ['80'])]", 
                                   required=False, store=False),
    }

    def onchange_city_id(self, cr, uid, ids, city_id): 
        v={}
        
        if city_id:
            city = self.pool.get('bluestar.city').browse(cr, uid, city_id)
            v['zip'] = city.zip
            v['city'] = city.long_name
            v['country_id'] = city.country_id.id 
            v['state_id'] = city.state_id.id 
            v['city_id'] = None
        
        return {'value': v} 
    
bluestar_partner()