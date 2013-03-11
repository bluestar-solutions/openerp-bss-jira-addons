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
from openerp.tools.translate import _

class bss_holidays(osv.osv):
    _inherit = "hr.holidays"
    
    def _label(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.user_id:
                res[holiday.id] = '%s, %s' % (holiday.user_id.name, holiday.holiday_status_id.name)
            elif holiday.category_id:
                res[holiday.id] = '%s, %s' % (holiday.name, holiday.category_id.name)
            else:
                res[holiday.id] = '%s' % (holiday.name)
            
        return res

    def _date_from_day(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for holiday in self.read(cr, uid, ids, ['id', 'date_from'], context=context):
            if holiday['date_from']:
                res[holiday['id']] = holiday['date_from'][:10]
            else:
                res[holiday['id']] = None
            
        return res
    
    def _date_from_day_inv(self, cr, uid, ids, field_name, field_value, arg, context):
        if type(ids) is not list:
            ids = [ids]
            
        for holiday in self.read(cr, uid, ids, ['id', 'date_from'], context=context):
            if not holiday['date_from']:
                holiday['date_from'] = '08:00:00'
            self.write(cr, uid, [holiday['id']], {'date_from': '%s %s' % (field_value[:10], holiday['date_from'][-8:])} , context)

    def _date_to_day(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for holiday in self.read(cr, uid, ids, ['id', 'date_to'], context=context):
            if holiday['date_to']:
                res[holiday['id']] = holiday['date_to'][:10]
            else:
                res[holiday['id']] = None
            
        return res
    
    def _date_to_day_inv(self, cr, uid, ids, field_name, field_value, arg, context):
        if type(ids) is not list:
            ids = [ids]

        for holiday in self.read(cr, uid, ids, ['id', 'date_to'], context=context):
            if not holiday['date_to']:
                holiday['date_to'] = '18:00:00'
            self.write(cr, uid, [holiday['id']], {'date_to': '%s %s' % (field_value[:10], holiday['date_to'][-8:])} , context)
    
    def _date_from_period(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for holiday in self.read(cr, uid, ids, ['id', 'date_from'], context=context):
            if 'date_from' in holiday and holiday['date_from']:
                if holiday['date_from'][-8:] >= '12:00:00':
                    res[holiday['id']] = 'half'
                else:
                    res[holiday['id']] = 'full'
            else:
                res[holiday['id']] = None
            
        return res
    
    def _date_from_period_inv(self, cr, uid, ids, field_name, field_value, arg, context):
        if type(ids) is not list:
            ids = [ids]
        
        value = '08:00:00'
        if field_value == 'half':
            value = '12:00:00'
        for holiday in self.read(cr, uid, ids, ['id', 'date_from'], context=context):
            if not holiday['date_from']:
                holiday['date_from'] = '1970-01-01'
            self.write(cr, uid, [holiday['id']], {'date_from': '%s %s' % (holiday['date_from'][:10], value)} , context)

    def _date_to_period(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for holiday in self.read(cr, uid, ids, ['id', 'date_to'], context=context):
            if 'date_to' in holiday and holiday['date_to']:
                if holiday['date_to'][-8:] <= '12:00:00':
                    res[holiday['id']] = 'half'
                else:
                    res[holiday['id']] = 'full'
            else:
                res[holiday['id']] = None
            
        return res
    
    def _date_to_period_inv(self, cr, uid, ids, field_name, field_value, arg, context):
        if type(ids) is not list:
            ids = [ids]

        value = '18:00:00'
        if field_value == 'half':
            value = '12:00:00'
        for holiday in self.read(cr, uid, ids, ['id', 'date_to'], context=context):
            if not holiday['date_to']:
                holiday['date_to'] = '1970-01-01'
            self.write(cr, uid, [holiday['id']], {'date_to': '%s %s' % (holiday['date_to'][:10], value)} , context)
            
    def default_get(self, cr, uid, fields, context=None):            
        res = super(bss_holidays, self).default_get(cr, uid, fields, context)
        print str(context)
        
        if 'default_date_from' in context:
            res['date_from_day'] = context['default_date_from']
            res['date_from_period'] = 'full'

        if 'default_date_to' in context:
            res['date_to_day'] = context['default_date_to']
            res['date_to_period'] = 'full'

        return res     

    _columns = {
        'label': fields.function(_label, type="char", readonly=True, required=True),
        'date_from_day': fields.function(_date_from_day, fnct_inv=_date_from_day_inv, type="date", readonly=True,
                                         states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'date_to_day': fields.function(_date_to_day, fnct_inv=_date_to_day_inv, type="date", readonly=True,
                                       states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'date_from_period': fields.function(_date_from_period, fnct_inv=_date_from_period_inv, type="selection",
                                            selection=[('full', 'from morning'), ('half', 'from noon')], readonly=True,
                                            states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'date_to_period': fields.function(_date_to_period, fnct_inv=_date_to_period_inv, type="selection",
                                          selection=[('full', 'until evening'), ('half', 'until noon')], readonly=True,
                                          states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
    }
    
    def get_holiday_factor(self, cr, uid, employee_id, day):
        ids = self.search(cr, uid, [('state', '=', 'validate'),
                                    ('employee_id', '=', employee_id),
                                    ('date_from', '<=', '%s 24:00:00' % day),
                                    ('date_to', '>=', '%s 00:00:00' % day)], limit=1)
        if ids:
            period = self.read(cr, uid, ids[0], ['date_from_day', 'date_to_day', 'date_from_period', 'date_to_period'])
            if day == period['date_from_day'] and period['date_from_period'] == 'half':
                return 0.5
            if day == period['date_to_day'] and period['date_to_period'] == 'half':
                return 0.5
            return 1.0
        return 0.0
    
    def holidays_validate(self, cr, uid, ids, context=None):
        for hol in self.browse(cr, uid, ids, context):
            if hol.employee_id.user_id.id == uid and uid != 5:
                raise osv.except_osv(_('Warning!'),_('You cannot validate your request. Contact a human resource manager.'))
        return super(bss_holidays, self).holidays_validate(cr, uid, ids, context)

bss_holidays()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
