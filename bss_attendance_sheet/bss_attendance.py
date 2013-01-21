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
from bss_webservice_handler.webservice import webservice 
import json as nson
from datetime import datetime, timedelta
import logging
from bss_utils.logging_template import *
from bss_utils.dateutils import orm_datetime
from pytz import timezone
import pytz

WS_ACTIONS = {'IN': 'sign_in',
              'OUT': 'sign_out'}

WS_TYPES = {'STD': 'std',
            'BREAK': 'break',
            'MIDDAY': 'midday'}

_logger = logging.getLogger(__name__)

class bss_attendance_import_log(osv.osv):
    _name = "bss_attendance_sheet.attendance_log"
    
    _columns = {
        'create_date': fields.datetime(),
        'website_id': fields.integer('Website ID', required=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', readonly=True),
        'status': fields.selection([('OK', 'Success'), ('ERROR', 'Error')], 'Status', required=True),
        'cause': fields.char('Cause', Size=255)
    }    
    
bss_attendance_import_log()

class bss_attendance(osv.osv):
    _inherit = "hr.attendance"
    
    def _attendance_sheet(self, cr, uid, ids, name, args, context=None):
        if not isinstance(ids, list):
            ids = [ids]
            
        sheet_obj = self.pool.get('bss_attendance_sheet.sheet')
        
        res = {}
        for attendance in self.browse(cr, uid, ids, context=context):
            server_tz = pytz.UTC
            employee_tz = timezone(attendance.employee_id.tz)
            
            res[attendance.id] = None
            attendance_time = server_tz.localize(datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S')).astimezone(employee_tz)
            sheet_ids = sheet_obj.search(cr, uid, [('employee_id', '=', attendance.employee_id.id), 
                                                   ('name', '=', attendance_time.strftime('%Y-%m-%d'))], 
                                         limit=1, context=context)
            if sheet_ids:
                res[attendance.id] = sheet_ids[0]
                
        _logger.debug('Update attendance_sheet_id of hr.attendance : %s' % str(res))
        return res
    
    def _get_sheet_attendance_ids(self, cr, uid, ids, context=None):
        attendance_obj = self.pool.get('hr.attendance')
        attendance_ids = set()
        for sheet in self.browse(cr, uid, ids, context):
            server_tz = pytz.UTC
            employee_tz = timezone(sheet.employee_id.tz)
            sheet_start = employee_tz.localize(datetime.strptime('%s 00:00:00' % sheet.name, '%Y-%m-%d %H:%M:%S')).astimezone(server_tz)
            sheet_end = sheet_start + timedelta(days=1)
            
            attendance_ids = attendance_ids.union(set(attendance_obj.search(cr, uid, [('employee_id', '=', sheet.employee_id.id),
                                                                                      ('name', '>=', sheet_start.strftime('%Y-%m-%d %H:%M:%S')),
                                                                                      ('name', '<=', sheet_end.strftime('%Y-%m-%d %H:%M:%S'))], context=context)))
        log_debug_trigger(_logger, 'hr.attendance', attendance_ids, 'bss_attendance_sheet.sheet')
        return list(attendance_ids)

    def _is_vector_phone(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for attendance in self.browse(cr, uid, ids, context=context):
            res[attendance.id] = attendance.website_id and attendance.create_uid.id == 1 \
                    and (not attendance.write_uid.id or attendance.write_uid.id == 1)
                                
        return res
    

    _columns = {
        'create_date': fields.datetime(readonly=True),
        'create_uid': fields.many2one('res.users', 'User', readonly=True),
        'write_date': fields.datetime(readonly=True),
        'write_uid': fields.many2one('res.users', 'User', readonly=True),
        'type': fields.selection([('std', 'Standard'), ('break', 'Break'), ('midday', 'Midday Break')], 'Type', required=True),
        'attendance_sheet_id': fields.function(_attendance_sheet, type="many2one", obj="bss_attendance_sheet.sheet", method=True, string='Sheet', store={
            'bss_attendance_sheet.sheet' : (_get_sheet_attendance_ids, ['name'], 1),   
            'hr.attendance': (lambda self, cr, uid, ids, context=None: ids, ['name'], 1),                                                                                                                                       
        }),
        'website_id': fields.integer('Website ID'),
        'is_vector_phone': fields.function(_is_vector_phone, type="boolean", method=True, string='Vector'),
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

            if att.action == 'sign_in':
                if prev_atts and att.action == 'sign_out' and prev_atts[0].type != att.type:
                    return False
            if att.action == 'sign_out':
                if next_atts and att.action == 'sign_in' and next_atts[0].type != att.type:
                    return False
        return True

    def _is_locked(self, cr, uid, ids, context=None):
        return True
        for att in self.browse(cr, uid, ids, context=context):
            if (datetime.today() -  orm_datetime(att.name)).days > 3:
                return False
        return True

    _constraints = [(_altern_same_type, 'Error ! Sign in must follow Sign out with same type', ['type']),
                    (_is_locked, 'Error ! This date is locked', ['date'])]
    
    def ws_decode_attendance(self, cr, uid, model, content, datetime_format):
        log_obj = self.pool.get('bss_attendance_sheet.attendance_log')
        
        datas = nson.loads(content)
        for data in sorted(datas, key=lambda k: k['name']) :
            log_ids = log_obj.search(cr, uid, [('website_id', '=', data['id'])])
            if not log_ids:
                vals = {
                    'name': webservice.str2date(data['time'][:-6], 'datetime', datetime_format).isoformat(' '),
                    'type': WS_TYPES[data['attendance_type']],
                    'action': WS_ACTIONS[data['status']],
                    'action_desc': None,
                    'employee_id': data['openerp_id'],      
                    'website_id': data['id'],                         
                }   
                try:
                    self.create(cr, uid, vals)
                except Exception as e:
                    _logger.error(str(e))
                    cr.rollback()
                    
                    log_obj.create(cr, uid, {
                        'website_id': data['id'],
                        'employee_id': data['openerp_id'],
                        'status': 'ERROR',
                        'cause': str(e),                  
                    })
                    cr.commit()
                else:
                    log_obj.create(cr, uid, {
                        'website_id': data['id'],
                        'employee_id': data['openerp_id'],
                        'status': 'OK',
                        'cause': '',                   
                    })
                    cr.commit()          
            
        return True
    
    def ws_encode_attendance(self, cr, uid, model, last_success, parameters, datetime_format):
        log_obj = self.pool.get('bss_attendance_sheet.attendance_log')
        
        attendance_list = []
        search_param = [('create_date', '>=', last_success.isoformat(' '))]

        for log in log_obj.browse(cr, uid, log_obj.search(cr, uid, search_param)):
            attendance_list.append({
                "id": log.website_id,
                "error": log.status if log.status == 'ERROR' else '',
                "message": log.cause,
            })

        return nson.dumps(attendance_list)
    
    def _check_sheet(self, cr, uid, ids, context=None):
        sheet_obj = self.pool.get('bss_attendance_sheet.sheet')
        
        if not isinstance(ids, list):
            ids = [ids]
        
        value_set = set()
        for vals in self.read(cr, 1, ids, ['employee_id', 'name'], context):
            value_set.add((vals['employee_id'][0], vals['name'][:10]))
            
        for value in value_set:
            sheet_obj._check_sheet(cr, 1, value[0], value[1], context)  
    
    def _round_minute(self, vals):
        if 'name' in vals:
            vals['name'] = datetime.strptime(vals['name'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:00')
        return vals
    
    def create(self, cr, uid, vals, context=None):
        res = super(bss_attendance,self).create(cr, uid, self._round_minute(vals), context)
        self._check_sheet(cr, uid, [res], context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(bss_attendance,self).write(cr, uid, ids, self._round_minute(vals), context)
        self._check_sheet(cr, uid, ids, context)
        return res

bss_attendance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

