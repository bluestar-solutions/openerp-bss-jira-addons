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
from bss_phonenumbers import bss_phonumbers_fields as pnfields
import phonenumbers

class bluestar_partner_phonenumbers_failed(osv.AbstractModel):
    
    _name = 'bss.partner.phonenumbers.failed'
    _description = 'Failed Phone Numbers'
    
    _columns = {
        'config_id': fields.many2one('bss.partner.phonenumbers.config', 'Config', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'phone': fields.char('Phone', size=64),
        'mobile': fields.char('Mobile', size=64),
        'fax': fields.char('Fax', size=64),
    }
    
bluestar_partner_phonenumbers_failed()

class bluestar_partner_phonenumbers_config(osv.AbstractModel):
    
    _name = 'bss.partner.phonenumbers.config'
    _description = 'Partner Phonenumbers Configuration'

    _columns = {
        'country_id': fields.many2one('res.country', 'Default Country', required=True),
        'failed_id': fields.one2many('bss.partner.phonenumbers.failed', 'config_id', string='Failed Phone Numbers')
    }
    
    def execute(self, cr, uid, ids, context=None):
        partner_pool = self.pool.get('res.partner')
        failed_pool = self.pool.get('bss.partner.phonenumbers.failed')
        
        config = self.browse(cr, uid, ids, context)[0]
        
        ids = partner_pool.search(cr, uid, [])
        for partner in partner_pool.browse(cr, uid, ids):
            failed = {}
            
            vals = {}
            try:
                vals['phone'] = pnfields.phonenumber.parse_to_db(partner.phone, config.country_id.code)
            except phonenumbers.NumberParseException:
                failed['phone'] = partner.phone  
                pass  
            try:
                vals['mobile'] = pnfields.phonenumber.parse_to_db(partner.mobile, config.country_id.code)
            except phonenumbers.NumberParseException:
                failed['mobile'] = partner.phone
                pass
            try:
                vals['fax'] = pnfields.phonenumber.parse_to_db(partner.fax, config.country_id.code)
            except phonenumbers.NumberParseException:
                failed['fax'] = partner.phone
                pass
          
            if failed:
                failed['config_id'] = config.id     
                failed['partner_id'] = partner.id   
                failed_pool.create(cr, uid, failed)

            partner_pool.write(cr, uid, [partner.id], vals)
    
        return {
            'name': '2',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': 'form',
            'res_model': 'bss.partner.phonenumbers.config',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        
bluestar_partner_phonenumbers_config()



