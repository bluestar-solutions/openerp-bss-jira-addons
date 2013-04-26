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
import json
import pytz
from openerp import netsvc
from datetime import datetime

WS_ACTIONS = {'sign_in': 'IN',
              'sign_out': 'OUT'}

WS_TYPES = {'std': 'STD',
            'break': 'BREAK',
            'midday': 'MIDDAY'}

def _tz_get(self,cr,uid, context=None):
    return [(x, x) for x in pytz.all_timezones]

class bss_employee(osv.osv):
    _inherit = 'hr.employee'
    
    _columns = {
        'create_date': fields.datetime(),
        'write_date': fields.datetime(),
        'mobile_device_id': fields.char('Mobile IMEI', size=128),
        'last_cumul_check': fields.datetime('Last Cumul. Check'),
        'tz': fields.selection(_tz_get,  'Timezone', size=64, required=True,
            help="The employee Timezone. Used to decide the time to switch day for consolidate attendance."),
        'attendance_start': fields.float('Attendance Start', required=True),
    }
    
    _defaults = {
        'tz': pytz.UTC.zone,
        'attendance_start': 0
    }
    
    def _update_tags_holidays(self, cr, uid, ids):
        hol_obj = self.pool.get('hr.holidays')    
        leave_ids = []
        for employee in self.browse(cr, uid, ids):
            hol_ids = hol_obj.search(cr, uid, [('category_id', 'in', [cat.id for cat in employee.category_ids]), 
                                               ('date_to', '>=', employee.contract_id.date_start)])
            for holidays in hol_obj.browse(cr, uid, hol_ids):
                hol_child_ids = hol_obj.search(cr, uid, [('employee_id', '=', employee.id),
                                                         ('parent_id', '=', holidays.id)])
                if not hol_child_ids:
                    vals = {
                        'name': holidays.name,
                        'type': holidays.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': holidays.holiday_status_id.id,
                        'date_from': holidays.date_from,
                        'date_to': holidays.date_to,
                        'notes': holidays.notes,
                        'number_of_days_temp': holidays.number_of_days_temp,
                        'parent_id': holidays.id,
                        'employee_id': employee.id
                    }
                    leave_ids.append(hol_obj.create(cr, uid, vals, context=None)) 
                    
        wf_service = netsvc.LocalService("workflow")
        for leave_id in leave_ids:
            wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
            wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
            wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
            
    def create(self, cr, uid, data, context=None):
        employee_id = super(bss_employee, self).create(cr, uid, data, context=context)
        if 'category_ids' in data and data['category_ids']:    
            self._update_tags_holidays(cr, uid, [employee_id])
        return employee_id

    def write(self, cr, uid, ids, data, context=None):
        res = super(bss_employee, self).write(cr, uid, ids, data, context=context)
        if 'category_ids' in data and data['category_ids']:
            self._update_tags_holidays(cr, uid, ids)
        return res

    def ws_encode_employee(self, cr, uid, model, last_success, parameters, datetime_format):
        sheet_obj = self.pool.get('bss_attendance_sheet.sheet')
        log_obj = self.pool.get('bss_attendance_sheet.attendance_log')
        att_obj = self.pool.get('hr.attendance')
        
        employee_list = []
        for employee in self.browse(cr, uid, self.search(cr, uid, [])):
            sheet_obj._check_sheet(cr, uid, employee.id, datetime.today().isoformat()[:10])
            
            sheet = {'create_date': '1900-01-01 00:00:00',
                     'write_date': None,
                     'expected_time': 0.0,
                     'total_recorded': 0.0,
                     'cumulative_difference': 0.0}
            attendance = {'create_date': '1900-01-01 00:00:00',
                          'write_date': None,
                          'action': 'sign_out',
                          'type': 'std'}
            
            process = False
            
            sheet_ids = sheet_obj.search(cr, uid, [('employee_id', '=', employee.id)], limit=1, order='name desc')
            if sheet_ids:
                sheet = sheet_obj.browse(cr, uid, sheet_ids)[0]
                if sheet.create_date >= last_success.isoformat(' ') or sheet.write_date and sheet.write_date >= last_success.isoformat(' '):
                    process = True
            
            log_ids = log_obj.search(cr, uid, [('employee_id', '=', employee.id)], limit=1, order='create_date desc')
            if log_ids:
                log = log_obj.browse(cr, uid, log_ids)[0]
                if log.create_date >= last_success.isoformat(' '):
                    process = True

            att_ids = att_obj.search(cr, uid, [('employee_id', '=', employee.id)], limit=1, order='name desc')
            if att_ids:
                attendance = att_obj.browse(cr, uid, att_ids)[0]
                if attendance.create_date >= last_success.isoformat(' ') or attendance.write_date and attendance.write_date >= last_success.isoformat(' '):
                    process = True
            
            if employee.create_date >= last_success.isoformat(' ') or employee.write_date and employee.write_date >= last_success.isoformat(' '):
                process = True
                
            if not process:
                continue
             
            employee_list.append({
                "openerp_id": employee.id,
                "status": WS_ACTIONS[attendance['action']],
                "attendance_type": WS_TYPES[attendance['type']],
                "device_id": employee.mobile_device_id,
                "name": employee.name,
                "todo_time": sheet['expected_time'],
                "done_time": sheet['total_recorded'],
                "dt_todo_done": sheet['time_difference']
            })
        return json.dumps(employee_list) 
        
bss_employee()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
