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

def _employee_get(obj, cr, uid, context=None):
    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
    return ids and ids[0] or False

class attendance_wizard(osv.TransientModel):
    _name = 'attendance.wizard'
    _description = 'Attendance Wizard'

    _columns = {
        'date_from': fields.datetime('Date From', required=True),
        'date_to': fields.datetime('Date To', required=True),
        'employee_id': fields.many2one('hr.employee', "Employee", required=True, select=True),
        'type': fields.selection([('std', 'Standard'), ('break', 'Break'), ('midday', 'Midday Break')], 'Type', required=True),
    }
    _defaults = {
        'employee_id': _employee_get,
    }
    
    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        att_obj = self.pool.get('hr.attendance')
        form = self.browse(cr, uid, ids)[0]
            
        next_att_ids = att_obj.search(cr, uid, [('employee_id', '=', form.employee_id.id), ('name', '>', form.date_to)], order='name ASC')
        next_atts = []
        for att in att_obj.browse(cr, uid, next_att_ids, context=None):
            next_atts.append({
                'name': att.name,
                'action': att.action,
                'action_desc': att.action_desc.id,
                'employee_id': att.employee_id.id,
                'day': att.day,
                'create_date': att.create_date,
                'create_uid': att.create_uid.id,
                'write_date': att.write_date,
                'write_uid': att.write_uid.id,
                'type': att.type,
                'website_id': att.website_id
            })
            
        att_obj.unlink(cr, uid, next_att_ids, None)
        att_obj.create(cr, uid, {
            'name': form.date_from,
            'action': 'sign_in' if form.type == 'std' else 'sign_out',
            'employee_id': form.employee_id.id,
            'type': form.type,
        }, context=None)
        att_obj.create(cr, uid, {
            'name': form.date_to,
            'action': 'sign_out' if form.type == 'std' else 'sign_in',
            'employee_id': form.employee_id.id,
            'type': form.type,
        }, context=None)
        for att in next_atts:
            att_obj.create(cr, uid, att, context=None)
    
        return {
            'type': 'ir.actions.act_window_close',
        }    

attendance_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
