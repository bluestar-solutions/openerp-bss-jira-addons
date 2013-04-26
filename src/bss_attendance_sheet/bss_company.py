# -*- coding: utf-8 -*-
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

from openerp.osv import fields, osv

class breaks_settings(osv.osv):
    _name = 'bss_attendance_sheet.breaks_settings'

    _columns = {
        'company_id': fields.many2one('res.company', string='Company'),
        'name': fields.date('Date from'),
        'break_offered': fields.float('Offered'),
        'minimum_break': fields.float('Minimum'),
        'midday_break_from': fields.float('Midday From'),
        'minimum_midday': fields.float('Midday Minimum'),
    }
    
    _order_by = 'name desc'
    
breaks_settings()

class bss_company(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'breaks_settings_ids': fields.one2many('bss_attendance_sheet.breaks_settings', 'company_id', string='Breaks Settings'),
    }
    
bss_company()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
