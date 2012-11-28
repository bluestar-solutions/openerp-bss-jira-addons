# -*- encoding: utf-8 -*-

from osv import osv, fields
import phonenumbers

class bluestar_partner_address(osv.osv):
    
    _inherit = 'res.partner.address'
    _description = "Bluestar partner address phonenumbers"
    
    def phoneformat(self, cr, uid, vals):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if 'phone' in vals and vals['phone']:
            try:
                pn = phonenumbers.parse(vals['phone'], user.context_lang[-2:])
                vals['phone'] = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            except phonenumbers.NumberParseException:
                raise osv.except_osv('Error', 'Invalid phone number')
        if 'mobile' in vals and vals['mobile']:
            try:
                pn = phonenumbers.parse(vals['mobile'], user.context_lang[-2:])
                vals['mobile'] = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            except phonenumbers.NumberParseException:
                raise osv.except_osv('Error', 'Invalid mobile number')
        if 'fax' in vals and vals['fax']:
            try:
                pn = phonenumbers.parse(vals['fax'], user.context_lang[-2:])
                vals['fax'] = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            except phonenumbers.NumberParseException:
                raise osv.except_osv('Error', 'Invalid fax number')
        return vals
    
    def create(self, cr, uid, vals, context=None):
        return super(bluestar_partner_address, self).\
            create(cr, uid, self.phoneformat(cr, uid, vals), context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        return super(bluestar_partner_address, self).\
            write(cr, uid, ids, self.phoneformat(cr, uid, vals), context=context)

bluestar_partner_address()

class bluestar_partner_phonenumbers_config(osv.osv_memory):
    
    _inherit = 'bss.config'

    _columns = {
        'process_phone_numbers' : fields.boolean('Process existing phone numbers'),
    }

    def execute(self, cr, uid, ids, context=None):
        for config in self.read(cr, uid, ids, ['generate_ref', 'process_phone_numbers']):   
            if config['process_phone_numbers']:
                ids = self.pool.get('res.partner.address').search(cr, uid, [])
                for address in self.pool.get('res.partner.address').browse(cr, uid, ids):
                    vals = self.pool.get('res.partner.address').phoneformat(cr, uid, {'phone': address.phone,
                                                                                      'mobile': address.mobile,
                                                                                      'fax': address.fax})
                    self.pool.get('res.partner.address').write(cr, uid, [address.id], vals)
                    
        return super(bluestar_partner_phonenumbers_config, self).execute(cr, uid, ids, context=context)
        
bluestar_partner_phonenumbers_config()


