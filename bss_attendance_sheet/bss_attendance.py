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
from openerp.exceptions import AccessError
from bss_webservice_handler.webservice import webservice 
import json as nson

WS_ACTIONS = {'IN': 'sign_in',
              'OUT': 'sign_out'}

WS_TYPES = {'STD': 'std',
            'BREAK': 'break',
            'MIDDAY': 'midday'}

class bss_attendance_import_log(osv.osv):
    _name = "bss_attendance_sheet.attendance_log"
    
    _columns = {
        'website_id': fields.integer('Website ID', required=True),
        'status': fields.selection([('OK', 'Success'), ('ERROR', 'Error')], 'Status', required=True),
        'cause': fields.char('Cause', Size=255)
    }    
    
bss_attendance_import_log()

class bss_attendance(osv.osv):
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
        'create_date': fields.datetime(),
        'write_date': fields.datetime(),
        'type': fields.selection([('std', 'Standard'), ('break', 'Break'), ('midday', 'Midday Break')], 'Type', required=True),
        'attendance_sheet_id': fields.function(_attendance_sheet, type="many2one", obj="hr.attendance", method=True, string='Attendances', store=True),
        'website_id': fields.integer('Website ID')
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
    
    def ws_decode_attendance(self, cr, uid, model, content, datetime_format):
        log_obj = self.pool.get('bss_attendance_sheet.attendance_log')
        
        datas = nson.loads(content)
        for data in datas :
            log_ids = log_obj.search(cr, uid, [('website_id', '=', data['id'])])
            if not log_ids:
                try:
                    self.create(cr, uid, {
                        'name': webservice.str2date(data['time'], 'datetime', datetime_format),
                        'type': WS_TYPES[data['attendance_type']],
                        'action': WS_ACTIONS[data['status']],
                        'action_desc': None,
                        'employee_id': data['openerp_id'],      
                        'website_id': data['id'],                         
                    })
                except Exception as e:
                    cr.rollback()
                    log_obj.create(cr, uid, {
                        'website_id': data['id'],
                        'status': 'ERROR',
                        'cause': str(e),                  
                    })
                    cr.commit()
                else:
                    log_obj.create(cr, uid, {
                        'website_id': data['id'],
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

bss_attendance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

