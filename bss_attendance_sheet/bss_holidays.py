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

class bss_holidays(osv.osv):
    _inherit = "hr.holidays"
    
    def _date_from_day(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for holiday in self.read(cr, uid, ids, ['id', 'date_from'], context=context):
            res[holiday['id']] = holiday['date_from'][:10]
            
        return res
    
    def _date_from_day_inv(self, cr, uid, ids, field_name, field_value, arg, context):
        if type(ids) is not list:
            ids = [ids]
            
        for holiday in self.read(cr, uid, ids, ['id', 'date_from'], context=context):
            self.write(cr, uid, [holiday['id']], {'date_from': '%s %s' % (field_value, holiday['date_from'][-8:])} , context)

    def _date_to_day(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for holiday in self.read(cr, uid, ids, ['id', 'date_to'], context=context):
            res[holiday['id']] = holiday['date_to'][:10]
            
        return res
    
    def _date_to_day_inv(self, cr, uid, ids, field_name, field_value, arg, context):
        if type(ids) is not list:
            ids = [ids]

        for holiday in self.read(cr, uid, ids, ['id', 'date_to'], context=context):
            self.write(cr, uid, [holiday['id']], {'date_to': '%s %s' % (field_value, holiday['date_to'][-8:])} , context)
    
    def _date_from_period(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for holiday in self.read(cr, uid, ids, ['id', 'date_from'], context=context):
            if holiday['date_from'][-8:] >= '12:00:00':
                res[holiday['id']] = 'half'
            else:
                res[holiday['id']] = 'full'
            
        return res
    
    def _date_from_period_inv(self, cr, uid, ids, field_name, field_value, arg, context):
        if type(ids) is not list:
            ids = [ids]
        
        value = '24:00:00+00:00'
        if field_value == 'half':
            value = '12:00:00+00:00'
        for holiday in self.read(cr, uid, ids, ['id', 'date_from'], context=context):
            self.write(cr, uid, [holiday['id']], {'date_from': '%s %s' % (holiday['date_from'][:10], value)} , context)

    def _date_to_period(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for holiday in self.read(cr, uid, ids, ['id', 'date_to'], context=context):
            if holiday['date_to'][-8:] >= '12:00:00':
                res[holiday['id']] = 'half'
            else:
                res[holiday['id']] = 'full'
            
        return res
    
    def _date_to_period_inv(self, cr, uid, ids, field_name, field_value, arg, context):
        if type(ids) is not list:
            ids = [ids]

        value = '24:00:00'
        if field_value == 'half':
            value = '12:00:00'
        for holiday in self.read(cr, uid, ids, ['id', 'date_to'], context=context):
            self.write(cr, uid, [holiday['id']], {'date_to': '%s %s UTC' % (holiday['date_to'][:10], value)} , context)

    _columns = {
        'date_from_day': fields.function(_date_from_day, fnct_inv=_date_from_day_inv, type="date", 
                                         states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'date_to_day': fields.function(_date_to_day, fnct_inv=_date_to_day_inv, type="date", 
                                       states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'date_from_period': fields.function(_date_from_period, fnct_inv=_date_from_period_inv, type="selection",
                                            selection=[('full', 'from morning'), ('half', 'from noon')],
                                            states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'date_to_period': fields.function(_date_to_period, fnct_inv=_date_to_period_inv, type="selection",
                                          selection=[('full', 'until evening'), ('half', 'until noon')],
                                          states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
    }

bss_holidays()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
