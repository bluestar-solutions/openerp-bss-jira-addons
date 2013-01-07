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

from datetime import datetime, timedelta
from openerp.osv import fields, osv
from bss_contract_week import DAY_FIELDS

class bss_attendance_sheet(osv.osv):
    _name = "bss_attendance_sheet.sheet"
    _description = "Attendance Sheet"
    
    @staticmethod
    def _td2str(td):
        return ':'.join(str(td).split(':')[:2])
    
    def _total(self, cr, uid, ids, name, args, context=None):
        week_obj = self.pool.get('bss_attendance_sheet.contract_week')
        breaks_obj = self.pool.get('bss_attendance_sheet.breaks_settings')
        hol_obj = self.pool.get('hr.holidays')
             
        res = {}
        if not isinstance(ids, list):
            ids = [ids]
        for sheet in self.browse(cr, uid, ids, context=context):
            res.setdefault(sheet.id, {
                'total_attendance': 0.0,
                'total_break': 0.0,
                'total_midday': 0.0,
                'total_recorded': 0.0,
                'expected_time': 0.0,
                'time_difference': 0.0
            })
            day_start = datetime.strptime('%s 00:00:00' % sheet.name, '%Y-%m-%d %H:%M:%S')

            breaks = {'break_offered': 0.0,
                      'minimum_break': 0.0,
                      'midday_break_from': 0.0,
                      'minimum_midday': 0.0}
            breaks_ids = breaks_obj.search(cr, uid, 
                                           [('company_id', '=', sheet.employee_id.company_id.id),
                                            ('name', '<=', sheet.name)], 
                                           limit=1, order='name desc', context=context)
            if breaks_ids:
                breaks = breaks_obj.read(cr, uid, breaks_ids, 
                                         ['break_offered', 'minimum_break', 'midday_break_from', 'minimum_midday'], 
                                         context)[0]
                                         
            holidays_factor = hol_obj.get_holiday_factor(cr, uid, sheet.employee_id.id, sheet.name)
            
            res[sheet.id]['expected_time'] = 0.0
            for contract in sheet.employee_id.contract_ids:
                if contract.date_start <= sheet.name and (not contract.date_end or contract.date_end >= sheet.name):
                    week_ids = week_obj.search(cr, uid, [('name', '<=', sheet.name)], limit=1, order='name desc', context=context)
                    if week_ids:
                        day_field = DAY_FIELDS[datetime.strptime(sheet.name, '%Y-%m-%d').date().isoweekday()]
                        res[sheet.id]['expected_time'] += week_obj.read(cr, uid, week_ids, [day_field], context=context)[0][day_field]
            res[sheet.id]['holidays_time'] = holidays_factor * res[sheet.id]['expected_time']
            
            if sheet.attendance_ids:  
                last_sign_in = day_start
                last_arrival = day_start
                last_pause_start = day_start
                
                attendance_time = timedelta(0)
                day_time = timedelta(0)
                break_time = timedelta(0)
                midday_time = timedelta(0)
                for attendance in sorted(sheet.attendance_ids, key=lambda a: a.name):
                    if attendance.action == 'sign_in':
                        last_sign_in = datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S')
                        
                        if attendance.type == 'std':
                            last_arrival = datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S')
                        elif attendance.type == 'break':
                            break_diff = datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S') - last_pause_start
                            if break_diff < timedelta(hours=breaks['minimum_break']):
                                break_diff = timedelta(hours=breaks['minimum_break'])
                            break_time += break_diff
                        elif attendance.type == 'midday':
                            midday_time += datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S') - last_pause_start
                            
                    elif attendance.action ==  'sign_out':
                        attendance_time += datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S') - last_sign_in
                        
                        if attendance.type == 'std':
                            day_time += datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S') - last_arrival
                        else:
                            last_pause_start = datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S')
                            
                if break_time >= timedelta(hours=breaks['break_offered']):
                    break_time -= timedelta(hours=breaks['break_offered'])
                else:
                    break_time = timedelta(0)
                            
                if midday_time < timedelta(hours=breaks['minimum_midday']) \
                        and attendance_time >= timedelta(hours=breaks['midday_break_from']):
                    midday_time = timedelta(hours=breaks['minimum_midday'])            
                
                res[sheet.id]['total_attendance'] = attendance_time.seconds / 3600.0
                res[sheet.id]['total_break'] = break_time.seconds / 3600.0
                res[sheet.id]['total_midday'] = midday_time.seconds / 3600.0
                recorded_time = day_time - midday_time - break_time
                res[sheet.id]['total_recorded'] = recorded_time.seconds / 3600.0
                
            res[sheet.id]['time_difference'] = res[sheet.id]['total_recorded'] + res[sheet.id]['holidays_time'] - res[sheet.id]['expected_time']
                
        return res
    
    def _cumulative_difference(self, cr, uid, ids, name, args, context=None):
        emp_obj = self.pool.get('hr.employee')
        res = {}
        
        employee_ids = set()
        for values in self.read(cr, uid, ids, ['employee_id'], context):
            employee_ids.add(values['employee_id'][0])
        
        for employee in emp_obj.browse(cr, uid, list(employee_ids), context):
            updated_sheet_ids = self.search(cr, uid, ['&', ('employee_id', '=', employee.id), ('id', 'in', ids)], 
                                            limit=1, order="name asc", context=context)
            if updated_sheet_ids:
                start_date = self.read(cr, uid, updated_sheet_ids[0], ['name'], context)['name']
                sheet_ids = self.search(cr, uid, [('employee_id', '=', employee.id),
                                                  ('name', '>=', start_date)], 
                                    order="name asc", context=context)
                prev_sheet_ids = self.search(cr, uid, [('employee_id', '=', employee.id),
                                                       ('name', '<', start_date)], 
                                             order="name desc", limit=1, context=context)
                
                cumul = 0.0
                if prev_sheet_ids:
                    cumul = self.read(cr, uid, prev_sheet_ids[0], ['cumulative_difference'], context)['cumulative_difference']
                for sheet in self.browse(cr, uid, sheet_ids, context):                    
                    cumul += sheet.time_difference
                    res[sheet.id] = cumul
        
        return res
    
    def _get_attendance_sheet_ids(self, cr, uid, ids, context=None):
        sheet_ids = []
        for attendance in self.browse(cr, uid, ids, context):
            if attendance.attendance_sheet_id.id not in sheet_ids:
                sheet_ids.append(attendance.attendance_sheet_id.id)
        return sheet_ids

    def _get_breaks_settings_sheet_ids(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        sheet_obj = self.pool.get('bss_attendance_sheet.sheet')
        sheet_ids = set()
        for break_offered in self.browse(cr, uid, ids, context):
            employee_ids = employee_obj.search(cr, uid, [('company_id', '=', break_offered.company_id.id)], context=context)
            for employee_id in employee_ids:         
                sheet_ids = sheet_ids.union(set(sheet_obj.search(cr, uid, [('name', '>=', break_offered.name), 
                                                                           ('employee_id', '=', employee_id)], 
                                                                 order='name asc', context=context)))
        return sheet_ids

    def _get_contract_week_sheet_ids(self, cr, uid, ids, context=None):
        sheet_obj = self.pool.get('bss_attendance_sheet.sheet')
        sheet_ids = set()
        for contract_week in self.browse(cr, uid, ids, context):
            sheet_ids = sheet_ids.union(set(sheet_obj.search(cr, uid, [('name', '>=', contract_week.name), 
                                                                       ('employee_id', '=', contract_week.contract_id.employee_id.id)], 
                                                             order='name asc', context=context)))
        return sheet_ids

    def _get_holidays_sheet_ids(self, cr, uid, ids, context=None):
        sheet_obj = self.pool.get('bss_attendance_sheet.sheet')
        sheet_ids = set()
        for holidays in self.browse(cr, uid, ids, context):
            sheet_ids = sheet_ids.union(set(sheet_obj.search(cr, uid, [('name', '>=', holidays.date_from_day),
                                                                       ('name', '<=', holidays.date_to_day), 
                                                                       ('employee_id', '=', holidays.employee_id.id)], 
                                                             order='name asc', context=context)))
        return sheet_ids
    
    _columns = {
        'name': fields.date('Date', readonly=True),
        'create_date': fields.datetime(),
        'write_date': fields.datetime(),
        'employee_id': fields.many2one('hr.employee', 'Employee', readonly=True),
        'attendance_ids': fields.one2many('hr.attendance', 'attendance_sheet_id', string="Attendances"),
        'total_attendance': fields.function(_total, type="float", method=True, string='Total Attendance', multi=True, store={
            'hr.attendance' : (_get_attendance_sheet_ids, ['name', 'action'], 10),
            'bss_attendance_sheet.sheet': (lambda self, cr, uid, ids, context=None: ids, ['name'], 10),  
        }),
        'total_break': fields.function(_total, type="float", method=True, string='Total Breaks', multi=True, store={
            'hr.attendance' : (_get_attendance_sheet_ids, ['name', 'action'], 10),
            'bss_attendance_sheet.breaks_settings' : (_get_breaks_settings_sheet_ids, ['company_id', 'name', 'break_offered', 'minimum_break'], 10),
            'bss_attendance_sheet.sheet': (lambda self, cr, uid, ids, context=None: ids, ['name'], 10),
        }),
        'total_midday': fields.function(_total, type="float", method=True, string='Midday Break', multi=True, store={
            'hr.attendance' : (_get_attendance_sheet_ids, ['name', 'action'], 10),                                                        
            'bss_attendance_sheet.breaks_settings' : (_get_breaks_settings_sheet_ids, ['company_id', 'name', 'midday_break_from', 'minimum_midday'], 10),
            'bss_attendance_sheet.sheet': (lambda self, cr, uid, ids, context=None: ids, ['name'], 10),
        }),
        'total_recorded': fields.function(_total, type="float", method=True, string='Total Recorded', multi=True, store={
            'hr.attendance' : (_get_attendance_sheet_ids, ['name', 'action'], 10),
            'bss_attendance_sheet.breaks_settings' : (_get_breaks_settings_sheet_ids, ['company_id', 'name', 'break_offered', 'minimum_break', 
                                                                                       'midday_break_from', 'minimum_midday'], 10),
            'bss_attendance_sheet.sheet': (lambda self, cr, uid, ids, context=None: ids, ['name'], 10),       
        }),
        'holidays_time': fields.function(_total, type="float", method=True, string='Holidays Time', multi=True, store={
            'bss_attendance_sheet.contract_week' : (_get_contract_week_sheet_ids, 
                                                    ['sunday_hours', 'monday_hours', 'tuesday_hours', 'wednesday_hours', 
                                                     'thursday_hours', 'friday_hours', 'saturday_hours'], 10),
            'hr.holidays' : (_get_holidays_sheet_ids, ['state'], 10),
            'bss_attendance_sheet.sheet': (lambda self, cr, uid, ids, context=None: ids, ['name'], 10),
        }),
        'expected_time': fields.function(_total, type="float", method=True, string='Expected Time', multi=True, store={
            'bss_attendance_sheet.contract_week' : (_get_contract_week_sheet_ids, 
                                                    ['sunday_hours', 'monday_hours', 'tuesday_hours', 'wednesday_hours', 
                                                     'thursday_hours', 'friday_hours', 'saturday_hours'], 10),
            'bss_attendance_sheet.sheet': (lambda self, cr, uid, ids, context=None: ids, ['name'], 10),
        }),
        'time_difference': fields.function(_total, type="float", method=True, string='Difference', multi=True, store={
            'hr.attendance' : (_get_attendance_sheet_ids, ['name', 'action'], 10),
            'bss_attendance_sheet.breaks_settings' : (_get_breaks_settings_sheet_ids, ['company_id', 'name', 'break_offered', 'minimum_break', 
                                                                                       'midday_break_from', 'minimum_midday'], 10),
            'bss_attendance_sheet.contract_week' : (_get_contract_week_sheet_ids, 
                                                    ['sunday_hours', 'monday_hours', 'tuesday_hours', 'wednesday_hours', 
                                                     'thursday_hours', 'friday_hours', 'saturday_hours'], 10),
            'hr.holidays' : (_get_holidays_sheet_ids, ['state'], 10),
            'bss_attendance_sheet.sheet': (lambda self, cr, uid, ids, context=None: ids, ['name'], 10),
        }),
        'cumulative_difference': fields.function(_cumulative_difference, type="float", method=True, string='Cumulative Difference', store={
            'hr.attendance' : (_get_attendance_sheet_ids, ['name', 'action'], 20),
            'bss_attendance_sheet.breaks_settings' : (_get_breaks_settings_sheet_ids, ['company_id', 'name', 'break_offered', 'minimum_break', 
                                                                                       'midday_break_from', 'minimum_midday'], 20),
            'bss_attendance_sheet.contract_week' : (_get_contract_week_sheet_ids, 
                                                    ['sunday_hours', 'monday_hours', 'tuesday_hours', 'wednesday_hours', 
                                                     'thursday_hours', 'friday_hours', 'saturday_hours'], 20),
            'hr.holidays' : (_get_holidays_sheet_ids, ['state'], 10),
            'bss_attendance_sheet.sheet': (lambda self, cr, uid, ids, context=None: ids, ['name'], 10),
        }),
    }
    
    _order = 'name asc'
    
    def _check_sheet(self, cr, uid, employee_id, day, context=None):  
        sheet_ids = self.search(cr, uid, [('employee_id', '=', employee_id), ('name', '=', day)], 
                                limit=1, context=context)
        if not sheet_ids:
            self.create(cr, 1, {'name': day, 'employee_id': employee_id}, context)
    
    def _check_all_sheet(self, cr, uid, day, context=None):
        emp_obj = self.pool.get('hr.employee')
        for employee_id in emp_obj.search(cr, uid, [], context):
            self._check_sheet(cr, uid, employee_id, day, context)

bss_attendance_sheet()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

