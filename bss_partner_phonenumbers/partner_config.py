# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

class bluestar_partner_phonenumbers_config(osv.osv_memory):
    
    _inherit = 'bss.config'

    _columns = {
        'process_phone_numbers' : fields.boolean('Process existing phone numbers'),
    }

    def execute(self, cr, uid, ids, context=None):
        partner_pool = self.pool.get('res.partner')
        
        for config in self.read(cr, uid, ids, ['process_phone_numbers']):   
            if config['process_phone_numbers']:
                ids = partner_pool.search(cr, uid, [])
                for partner in partner_pool.browse(cr, uid, ids):
                    vals = {'phone': partner.phone,
                            'mobile': partner.mobile,
                            'fax': partner.fax}
                    partner_pool.write(cr, uid, [partner.id], vals)
                    
        return super(bluestar_partner_phonenumbers_config, self).execute(cr, uid, ids, context=context)
        
bluestar_partner_phonenumbers_config()


