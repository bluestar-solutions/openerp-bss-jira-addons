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

import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _

class bss_attendance_sheet(osv.osv):
    _name = "bss_attendance_sheet.sheet"
    _description = "Attendance Sheet"
    
    @staticmethod
    def _td2str(td):
        return ':'.join(str(td).split(':')[:2])
    
    def _total(self, cr, uid, ids, name, args, context=None):
        contract_obj = self.pool.get('hr.contract')
             
        res = {}
        for sheet in self.browse(cr, uid, ids, context=context):
            res.setdefault(sheet.id, {
                'total_attendance': 0.0,
                'total_break': 0.0,
                'total_midday': 0.0,
                'total_recorded': 0.0,
                'expected_time': 0.0,
                'total_attendance_str': '00:00',
                'total_break_str': '00:00',
                'total_midday_str': '00:00',
                'total_recorded_str': '00:00',
                'expected_time_str': '00:00',
            })
            day_start = datetime.strptime('%s 00:00:00' % sheet.name, '%Y-%m-%d %H:%M:%S')
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
                        print str(last_sign_in)
                        
                        if attendance.type == 'std':
                            last_arrival = datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S')
                        elif attendance.type == 'break':
                            break_time += datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S') - last_pause_start
                        elif attendance.type == 'midday':
                            midday_time += datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S') - last_pause_start
                            
                    elif attendance.action == 'sign_out':
                        ttt = datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S') - last_sign_in
                        print str(ttt)
                        attendance_time += ttt
                        print str(attendance_time)
                        
                        if attendance.type == 'std':
                            day_time += datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S') - last_arrival
                        else:
                            last_pause_start = datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S')
                            
                if break_time >= timedelta(minutes=15):
                    break_time -= timedelta(minutes=15)
                else:
                    break_time = timedelta(0)
                            
                if midday_time < timedelta(minutes=30):
                    midday_time = timedelta(minutes=30)            
                    
                for contract in sheet.employee_id.contract_ids:
                    if contract.date_start <= sheet.name and (not contract.date_end or contract.date_end >= sheet.name):
                        
                
                res[sheet.id]['total_attendance_str'] = bss_attendance_sheet._td2str(attendance_time)
                res[sheet.id]['total_attendance'] = attendance_time.seconds / 3600.0
                res[sheet.id]['total_break_str'] = bss_attendance_sheet._td2str(break_time)
                res[sheet.id]['total_break'] = break_time.seconds / 3600.0
                res[sheet.id]['total_midday_str'] = bss_attendance_sheet._td2str(midday_time)
                res[sheet.id]['total_midday'] = midday_time.seconds / 3600.0
                recorded_time = day_time - midday_time - break_time
                res[sheet.id]['total_recorded_str'] = bss_attendance_sheet._td2str(recorded_time)
                res[sheet.id]['total_recorded'] = recorded_time.seconds / 3600.0
        return res
    
    _columns = {
        'name': fields.date('Date', readonly=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', readonly=True),
        'attendance_ids': fields.one2many('hr.attendance', 'attendance_sheet_id', string="Attendances"),
        'total_attendance': fields.function(_total, type="float", method=True, string='Total Attendance', multi=True, store=True),
        'total_break': fields.function(_total, type="float", method=True, string='Total Breaks', multi=True, store=True),
        'total_midday': fields.function(_total, type="float", method=True, string='Midday Break', multi=True, store=True),
        'total_recorded': fields.function(_total, type="float", method=True, string='Total Recorded', multi=True, store=True),
        'expected_time': fields.function(_total, type="float", method=True, string='Expected Time', multi=True, store=True),
        'total_attendance_str': fields.function(_total, type="char", method=True, string='Total Attendance', multi=True, store=True),
        'total_break_str': fields.function(_total, type="char", method=True, string='Total Breaks', multi=True, store=True),
        'total_midday_str': fields.function(_total, type="char", method=True, string='Midday Break', multi=True, store=True),
        'total_recorded_str': fields.function(_total, type="char", method=True, string='Total Recorded', multi=True, store=True),
        'expected_time_str': fields.function(_total, type="char", method=True, string='Expected Time', multi=True, store=True),
    }
    
    def recalculate(self, cr, uid, employee_ids, day, context=None):
        for employee in self.pool.get('hr.employee').browse(cr, uid, employee_ids, context=context):
            sheet_id = self.search(cr, uid, [('employee_id', '=', employee.id), 
                                             ('name', '=', day.strftime('%Y-%m-%d'))], 
                                   limit=1, context=context)[0]
            if sheet_id:
                self.write(cr, uid, [sheet_id], {}, context=context)
            else:
                self.create(cr, uid, {'name': day.strftime('%Y-%m-%d'),
                                      'employee_id': employee.id}, context=context)
            
    def recalculate_all(self, cr, uid, day=None, context=None):
        if not day:
            day = date.today()
        self.recalculate(cr, uid, self.pool.get('hr.employee').search(cr, uid, [], context=context), day, context=context)
        
        att_ids = self.pool.get('hr.attendance').search(cr, uid, [])
        self.pool.get('hr.attendance').write(cr, uid, att_ids, {'test': 1})
        print 'OK!!!!'

bss_attendance_sheet()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

