# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

CB_NUMBER_TYPES = [('1', 'Headquarters'),
                  ('2', 'Central'),
                  ('3', 'Branch')]

SIC_CODES = [('0', 'No participation in SIC'),
             ('1', 'Participation in SIC and LSV / BDD as DEB-FI'),
             ('2', 'Participation in SIC without technical connection'),
             ('3', 'Participation in SIC')]

EUROSIC_CODES = [('0', 'No participation in euroSIC'),
                 ('1', 'Participation in euroSIC and LSV / BDD as DEB-FI'),
                 ('3', 'Participation in euroSIC')]

LANGUAGES = [('1', 'German'),
             ('2', 'French'),
             ('3', 'Italian')]

class bluestar_bank_ch(osv.osv):
    
    _name = 'bluestar.bank_ch'
    _description = "Swiss Banks"
    
    def _get_current_cb_number(self, cr, uid, ids, field_name, arg, context):
        result={}
        for bank in self.browse(cr, uid, ids, context=context):
            if bank.new_cb_number:
                result[bank.id] = bank.new_cb_number
            else:
                result[bank.id] = bank.cb_number
        return result
    
    def _get_name(self, cr, uid, ids, field_name, arg, context):
        result={}
        for bank in self.browse(cr, uid, ids, context=context):
            if bank.swift:
                result[bank.id] = '%(cb)s %(branch)s | %(name)s | %(zip)s %(location)s | %(swift)s' %\
                        {'cb': bank.current_cb_number,
                         'branch': bank.branch_id,
                         'name': bank.long_name,
                         'zip': bank.zip,
                         'location': bank.location,
                         'swift': bank.swift}
            else:
                result[bank.id] = '%(cb)s %(branch)s | %(name)s | %(zip)s %(location)s' %\
                        {'cb': bank.current_cb_number,
                         'branch': bank.branch_id,
                         'name': bank.long_name,
                         'zip': bank.zip,
                         'location': bank.location}
        return result

    _columns = {
        'group': fields.char('Group', size=2),
        'cb_number': fields.char('CB Number', size=5),
        'branch_id': fields.char('Branch ID', size=4),
        'new_cb_number': fields.char('New CB Number', size=5),
        'current_cb_number' : fields.function(_get_current_cb_number, type='char', method=True, store=True, string="Current CB Number"),
        'sic_number': fields.char('SIC Number', size=6),
        'headquarters': fields.char('Headquarters', size=5),
        'cb_number_type': fields.selection(CB_NUMBER_TYPES, 'CB Number Type'),
        'valid_from': fields.date('Valid From'),
        'sic_code': fields.selection(SIC_CODES, 'SIC Code'),
        'eurosic_code': fields.selection(EUROSIC_CODES, 'euroSIC Code'),
        'language': fields.selection(LANGUAGES, 'Language'),
        'short_name': fields.char('Short Name', size=15),
        'long_name': fields.char('Name', size=60),
        'home_address': fields.char('Home Address', size=35),
        'postal_address': fields.char('Postal Address', size=35),
        'zip': fields.char('Zip', size=10),
        'location': fields.char('Location', size=35),
        'phone': fields.char('Phone', size=18),
        'fax': fields.char('Fax', size=18),
        'telephone_code': fields.char('Telephone Code', size=5),
        'country_code': fields.char('Country Code', size=2),
        'postal_code': fields.char('Postal Code', size=12),
        'swift': fields.char('SWIFT', size=14),
        'name': fields.function(_get_name, type='char', method=True, store=True, string="Full Name"),
    }
    
bluestar_bank_ch()
