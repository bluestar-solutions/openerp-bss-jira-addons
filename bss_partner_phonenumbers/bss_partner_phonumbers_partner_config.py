# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Bluestar Solutions Sàrl (<http://www.blues2.ch>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

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


