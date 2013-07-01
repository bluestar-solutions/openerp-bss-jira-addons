# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2013 Bluestar Solutions Sàrl (<http://www.blues2.ch>).
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
from openerp.addons.base.res.res_company import res_company
from openerp.addons.bss_phonenumbers import bss_phonumbers_fields as pnfields #@UnresolvedImport

class bss_partner_phonenumbers_partner(osv.osv):
    
    _inherit = 'res.partner'
    _description = "Bluestar Partner Phonenumbers"
    
    _columns = {
        'phone': pnfields.phonenumber('Phone'),
        'mobile' : pnfields.phonenumber('Mobile'),
        'fax' : pnfields.phonenumber('Fax'),
    }

bss_partner_phonenumbers_partner()

class bss_partner_phonenumbers_company(osv.osv):

    _inherit = 'res.company'
    _description = "Bluestar Company Phonenumbers"

    _columns = {
        'phone': fields.function(res_company._get_address_data, 
                                 fnct_inv=res_company._set_address_data, 
                                 size=64, type='phonenumber', string="Phone", multi='address'),
        'fax': fields.function(res_company._get_address_data, 
                               fnct_inv=res_company._set_address_data, 
                               size=64, type='phonenumber', string="Fax", multi='address'),
    }

bss_partner_phonenumbers_company()


