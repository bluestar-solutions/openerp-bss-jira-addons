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
from openerp.tools.translate import _
from openerp.netsvc import logging

class bss_holidays(osv.osv):
    _inherit = "hr.holidays"
    _logger = logging.getLogger('hr.holidays')
    
    def __init__(self, cr, uid):
        super(bss_holidays, self)._track.clear()
        super(bss_holidays, self)._columns['state'].track_visibility = None
        super(bss_holidays, self).__init__(cr, uid)
        
    def _parse_message(self, new_value, message_description=None, old_value=None):
        message = ''
        if message_description:
            message = '<span>%s</span>' % message_description

        message += '<div> &nbsp; &nbsp; &bull; <b>Status</b>: '
        if old_value:
            message += '%s &rarr; ' % old_value
        message += '%s</div>' % new_value
        
        return message
        
    def create(self, cr, uid, values, context=None):
        res = super(bss_holidays, self).create(cr, uid, values, context)
        
        subtp = self.pool.get('mail.message.subtype').browse(cr, uid, self.pool.get('mail.message.subtype').search(cr, uid, [('name','=','To Approve'),('res_model','=','hr.holidays')]))
        message_body = self._parse_message('To Approve', subtp[0].description, 'To Submit')
        self.message_post(cr, uid, res, body=message_body, type='holidays', subtype='hr_holidays.mt_holidays_confirmed')
        
        return res
        
    def write(self, cr, uid, ids, vals, context=None):
        send_mess = False
        if 'state' in vals.keys() and vals['state'] != 'confirm':
            subtp = self.pool.get('mail.message.subtype').browse(cr, uid, self.pool.get('mail.message.subtype').search(cr, uid, [('name','=','Refused' if vals['state'] == 'refuse' else 'Approved'),('res_model','=','hr.holidays')]))
            message_body = self._parse_message('Refused' if vals['state'] == 'refuse' else 'Approved', subtp[0].description, 'To approve')
            send_mess = True
            
        res = super(bss_holidays, self).write(cr, uid, ids, vals, context)
        
        if send_mess:
            self.message_post(cr, uid, ids[0], body=message_body, type='holidays', subtype='hr_holidays.mt_holidays_%s' % ('refused' if vals['state'] == 'refuse' else 'approved'))
            
        return res
    
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
            if hol.employee_id:
                if hol.employee_id.user_id.id == uid and uid != 9:
                    raise osv.except_osv(_('Warning!'),_('You cannot validate your request. Contact a human resource manager.'))
        return super(bss_holidays, self).holidays_validate(cr, uid, ids, context)

bss_holidays()

class bss_res_partner_mail(osv.Model):
    _name = "res.partner"
    _inherit = ['res.partner', 'mail.thread']
    
    def __init__(self, cr, uid):
        super(bss_res_partner_mail, self)._columns['notification_email_send'].selection.append(('holidays','Holidays notifications only'))
        
class bss_mail_message(osv.Model):
    _name = "mail.message"
    _inherit = 'mail.message'
    
    def __init__(self, cr, uid):
        super(bss_mail_message, self)._columns['type'].selection.append(('holidays','Holidays notifications'))
        
class bss_mail_notification(osv.Model):
    _name = "mail.notification"
    _inherit = 'mail.notification'
    
    def get_partners_to_notify(self, cr, uid, message, partners_to_notify=None, context=None):
        notify_pids = []
        
        for notification in message.notification_ids:
            if notification.read:
                continue
            
            partner = notification.partner_id
            
            if partners_to_notify and partner.id not in partners_to_notify:
                continue
            
            if partner.notification_email_send == 'holidays' and message.type != 'holidays':
                continue
            
            notify_pids.append(partner.id)
        
        ids = super(bss_mail_notification, self).get_partners_to_notify(cr, uid, message, partners_to_notify, context)
        notify_pids += ids
        
        return notify_pids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
