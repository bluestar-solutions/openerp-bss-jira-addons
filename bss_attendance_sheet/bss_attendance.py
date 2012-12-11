# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

class hr_attendance(osv.osv):
    _inherit = "hr.attendance"
    
    def _attendance_sheet(self, cr, uid, ids, name, args, context=None):
        sheet_obj = self.pool.get('bss_attendance_sheet.sheet')
        
        res = {}
        for attendance in self.browse(cr, uid, ids, context=context):
            res[attendance.id] = None
            sheets = sheet_obj.search(cr, uid, [('employee_id', '=', attendance.employee_id.id), 
                                                ('name', '=', attendance.name[:10])], 
                                      limit=1, context=context)
            if sheets:
                res[attendance.id] = sheets[0]
                
        return res

    _columns = {
        'test': fields.boolean('Test'),
        'type': fields.selection([('std', 'Standard'), ('break', 'Break'), ('midday', 'Midday Break')], 'Type', required=True),
        'attendance_sheet_id': fields.function(_attendance_sheet, type="many2one", obj="hr.attendance", method=True, string='Attendances', store={
            'hr.attendance': (lambda self, cr, uid, ids, c={}: ids,
                              ['test'], 
                              1)
        }),
    }
    _defaults = {
        'type': 'std'
    }

    def _altern_same_type(self, cr, uid, ids, context=None):
        for att in self.browse(cr, uid, ids, context=context):
            # search and browse for first previous and first next records
            prev_att_ids = self.search(cr, uid, [('employee_id', '=', att.employee_id.id), ('name', '<', att.name), ('action', 'in', ('sign_in', 'sign_out'))], limit=1, order='name DESC')
            next_add_ids = self.search(cr, uid, [('employee_id', '=', att.employee_id.id), ('name', '>', att.name), ('action', 'in', ('sign_in', 'sign_out'))], limit=1, order='name ASC')
            prev_atts = self.browse(cr, uid, prev_att_ids, context=context)
            next_atts = self.browse(cr, uid, next_add_ids, context=context)

            if att.type != 'std':
                if prev_atts and att.action == 'sign_in' and prev_atts[0].type != att.type:
                    return False
                if next_atts and att.action == 'sign_out' and next_atts[0].type != att.type:
                    return False
        return True

    _constraints = [(_altern_same_type, 'Error ! Sign out must follow Sign out with same type', ['type'])]

hr_attendance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

