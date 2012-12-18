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

from openerp.osv import fields, osv
import calendar

DAY_FIELDS = {1: 'monday_hours',
              2: 'tuesday_hours',
              3: 'wednesday_hours',
              4: 'thursday_hours',
              5: 'friday_hours',
              6: 'saturday_hours',
              7: 'sunday_hours'}

class bss_contract_week(osv.osv):
    _name = 'bss_attendance_sheet.contract_week'
    
    def _total(self, cr, uid, ids, name, args, context=None):
        print str(context)
        res = {}
        for contract in self.read(cr, uid, ids, DAY_FIELDS.values() + ['id'], context=context):
            res[contract['id']] = 0.0
            for v in DAY_FIELDS.values():
                res[contract['id']] += contract[v]
        return res

    _columns = {
        'name': fields.date('From', required=True),
        'contract_id': fields.many2one('hr.contract', string='Contract'),
        'sunday_hours': fields.float('Sunday'),
        'monday_hours': fields.float('Monday'),
        'tuesday_hours': fields.float('Tuesday'),
        'wednesday_hours': fields.float('Wednesday'),
        'thursday_hours': fields.float('Thursday'),
        'friday_hours': fields.float('Friday'),
        'saturday_hours': fields.float('Saturday'),
        'total_hours': fields.function(_total, type="float", string="Total"),
    }

    _defaults = {
        'sunday_hours': 0.0,
        'monday_hours': 8.5,
        'tuesday_hours': 8.5,
        'wednesday_hours': 8.5,
        'thursday_hours': 8.5,
        'friday_hours': 8.5,
        'saturday_hours': 0.0,
    }

    _sql_constraints = [ 
        ('sunday_hours', 'CHECK (sunday_hours >= 0.0 AND sunday_hours <= 24.0)', 'Hours must be between 00:00 and 24:00 !'),
        ('monday_hours', 'CHECK (monday_hours >= 0.0 AND monday_hours <= 24.0)', 'Hours must be between 00:00 and 24:00 !'),
        ('tuesday_hours', 'CHECK (tuesday_hours >= 0.0 AND tuesday_hours <= 24.0)', 'Hours must be between 00:00 and 24:00 !'), 
        ('wednesday_hours', 'CHECK (wednesday_hours >= 0.0 AND wednesday_hours <= 24.0)', 'Hours must be between 00:00 and 24:00 !'), 
        ('thursday_hours', 'CHECK (thursday_hours >= 0.0 AND thursday_hours <= 24.0)', 'Hours must be between 00:00 and 24:00 !'),
        ('friday_hours', 'CHECK (friday_hours >= 0.0 AND friday_hours <= 24.0)', 'Hours must be between 00:00 and 24:00 !'),
        ('saturday_hours', 'CHECK (saturday_hours >= 0.0 AND saturday_hours <= 24.0)', 'Hours must be between 00:00 and 24:00 !'), 
    ]
    
bss_contract_week()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
