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
import time
from datetime import timedelta
from openerp.netsvc import logging

HOUR_TYPE = [('add','Add'),('pending','Pending'),('validated','Validated')]

class bss_prepaid_add_hours(osv.osv_memory):
    _name = 'bss_visit_report.prepaid_hours.add_hours'
    _description = 'Add prepaid hours'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
            
        res = dict()
        for field in self._columns.keys():
            if field in context:
                res[field] = context[field]

        res['processed_date'] = time.strftime('%Y-%m-%d')
        
        return res
    
    _columns = {
        'amount' : fields.integer('Time amount', required=True),
        'processed_date' : fields.date('Processed date', required=True),
        'prepaid_hours_id' : fields.many2one('bss_visit_report.prepaid_hours', select=True),
        'pph_name' : fields.related('prepaid_hours_id', 'pph_name', type="char", relation="bss_visit_report.prepaid_hours", string="Name", store=False),
    }
    
    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        form = self.browse(cr, uid, ids)[0]
        self.pool.get('bss_visit_report.prepaid_time').create(cr, uid, {
            'amount' : form.amount,
            'prepaid_hours_id' : form.prepaid_hours_id.id,
            'processed_date' : form.processed_date,
            'type' : 'add',
            }, context=None)
        
        return {'type' : 'ir.actions.act_window_close'}

class bss_prepaid_time(osv.osv):
    _name = 'bss_visit_report.prepaid_time'
    _description = 'Prepaid time'
    
    _columns = {
        'amount' : fields.integer('Time amount'),
        'processed_date' : fields.date('Processed date'),
        'related_timesheet' : fields.many2one('hr.analytic.timesheet', string='Related timesheet', required=False),
        'description' : fields.related('related_timesheet', 'name', type="text", relation="hr.analytic.timesheet", string="Description", store=False),
        'prepaid_hours_id' : fields.many2one('bss_visit_report.prepaid_hours', select=True),
        'type' : fields.selection(HOUR_TYPE, string="Type"),
    }
    
    _sql_constraints = [('check_amount','CHECK(amount > 0)','Time amount must be greater than 0 !'),
                        ('unique_related_timesheet','unique(related_timesheet)','Can\'t validate same timesheet multiple times !')]
    _defaults = {'processed_date' : lambda *a: time.strftime('%Y-%m-%d')}
    _order = 'processed_date DESC'
    
bss_prepaid_time()

class bss_prepaid_hours(osv.osv):
    _name = 'bss_visit_report.prepaid_hours'
    _description = 'Prepaid hours'
    _rec_name = 'pph_name'
        
    def _get_billable_hours(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for pph in self.browse(cr, uid, ids, context):
            res[pph.id] = []
            for ppt in pph.related_hours:
                if ppt.type in ('pending', 'validated'):
                    res[pph.id].append(ppt.id)
        
        return res
    
    def _get_added_hours(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for pph in self.browse(cr, uid, ids, context):
            res[pph.id] = []
            for ppt in pph.related_hours:
                if ppt.type == 'add':
                    res[pph.id].append(ppt.id)
        
        return res
    
    def _total_validated_hours(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for pph in self.browse(cr, uid, ids, context):
            res[pph.id] = 0
            for ppt in pph.related_hours:
                if ppt.type == 'validated':
                    res[pph.id] += ppt.amount
                
        return res
    
    def _total_added_hours(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for pph in self.browse(cr, uid, ids, context):
            res[pph.id] = 0
            for ppt in pph.related_hours:
                if ppt.type == 'add':
                    res[pph.id] += ppt.amount
                
        return res
            
    
    def _get_av_amount(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for pph in self.browse(cr, uid, ids, context):
            res[pph.id] = pph.total_added_hours - pph.total_validated_hours
                
        return res
    
    def get_prepaid_hours_for_contract(self, cr, uid, context):
        return 2
    
    _columns = {
        'related_hours' : fields.one2many('bss_visit_report.prepaid_time', 'prepaid_hours_id', 'Related hours'),
        'billable_hours' : fields.function(_get_billable_hours, 'Billable hours', type='one2many', store=False, method=True, obj='bss_visit_report.prepaid_time'),
        'added_hours' : fields.function(_get_added_hours, 'Added hours', type='one2many', store=False, method=True, obj='bss_visit_report.prepaid_time'),
        'contract_id' : fields.many2one('account.analytic.account', select=True),
        'pph_name' : fields.related('contract_id', 'name', type='char', relation='account.analytic.account', string="Name", store=False),
        'total_validated_hours' : fields.function(_total_validated_hours, string='Amount of validated hours', type="integer", store=False, method=True),
        'total_added_hours' : fields.function(_total_added_hours, string='Amount of added hours', type="integer", store=False, method=True),
        'av_amount' : fields.function(_get_av_amount, type="integer", string="Available amount", method=True, store=False),
    }
    
    _sql_constraints = [('uniq_contract_id','unique(contract_id)','Contracts can\'t have multiple prepaid hours !')]
    
bss_prepaid_hours()

class bss_aaa(osv.osv):
    _inherit = 'account.analytic.account'
    
    _columns = {
        'use_prepaid_hours': fields.boolean('Prepaid hours', help="Check this field if this project manages prepaid hours"),
        'prepaid_hours_id' : fields.many2one('bss_visit_report.prepaid_hours', 'Prepaid hours', required=False),
    }
    
    def create(self, cr, uid, vals, context=None):
        res = super(bss_aaa, self).create(cr, uid, vals, context)
        
        pph_pool = self.pool.get('bss_visit_report.prepaid_hours')
        pph_id = pph_pool.create(cr, uid, {'contract_id' : res}, context)
        
        self.write(cr, uid, [res], {'prepaid_hours_id' : pph_id}, context)
        
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        for cc in self.browse(cr, uid, ids, context):
            if cc.use_prepaid_hours and cc.prepaid_hours_id:
                self.pool.get('bss_visit_report.prepaid_hours').unlink(cr, uid, cc.prepaid_hours_id.id, context)
        return super(bss_aaa, self).unlink(cr, uid, ids, context)
        
    def on_change_template(self, cr, uid, ids, template_id, context=None):
        res = super(bss_aaa, self).on_change_template(cr, uid, ids, template_id, context=context)
        if template_id and 'value' in res:
            template = self.browse(cr, uid, template_id, context=context)
            res['value']['use_prepaid_hours'] = template.use_prepaid_hours
        return res
    
    def act_show_prepaid_hours_for_contract(self, cr, uid, ids, context=None):
        contract_id = self.browse(cr, uid, ids, context)[0]
        prepaid_id = self.pool.get('bss_visit_report.prepaid_hours').search(cr, uid, [('contract_id','=',contract_id.id)])[0]
        
        return {
            'name': 'Prepaid hours for %s ' % contract_id.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bss_visit_report.prepaid_hours',
            'type': 'ir.actions.act_window',
            'res_id' : prepaid_id,
        }
        
bss_aaa()
        
class bss_prepaid_hours_hr_timesheet(osv.osv):
    _name = 'hr_timesheet_sheet.sheet'
    _inherit = 'hr_timesheet_sheet.sheet'
    _logger = logging.getLogger(_name)
    
    def prepaid_draft(self, cr, uid, ids):
        ppt_pool = self.pool.get('bss_visit_report.prepaid_time')
        
        for tss in self.browse(cr, uid, ids):
            for timesheet in tss.timesheet_ids:
                ppt_pool.unlink(cr, uid, ppt_pool.search(cr, uid, [('related_timesheet','=',timesheet.id)]))
                
        return self.write(cr, uid, ids, {'state' : 'draft'})
    
    def prepaid_validate(self, cr, uid, ids):
        ppt_pool = self.pool.get('bss_visit_report.prepaid_time')
        
        for tss in self.browse(cr, uid, ids):
            for timesheet in tss.timesheet_ids:
                ppt_ids = ppt_pool.search(cr, uid, [('related_timesheet','=',timesheet.id)])
                ppt_pool.write(cr, uid, ppt_ids, {'type' : 'validated'})
                
        return self.write(cr, uid, ids, {'state' : 'done'})
    
    def button_confirm(self, cr, uid, ids, context=None):
        res = super(bss_prepaid_hours_hr_timesheet, self).button_confirm(cr, uid, ids, context)
        
        pph_pool = self.pool.get('bss_visit_report.prepaid_hours')
        ppt_pool = self.pool.get('bss_visit_report.prepaid_time')
        
        for tss in self.browse(cr, uid, ids):
            for timesheet in tss.timesheet_ids:
                pph = pph_pool.browse(cr, uid, pph_pool.search(cr, uid, [('contract_id','=',timesheet.account_id.id)]))
                if not pph or timesheet.name == '/':
                    continue
                if timesheet.to_invoice:
                    factor = timesheet.to_invoice.factor
                    if factor < 100:
                        ppt_pool.create(cr, uid, {
                                'prepaid_hours_id' : pph[0].id,
                                'related_timesheet' : timesheet.id,
                                'amount' : int(timedelta(hours=timesheet.unit_amount*(1-factor/100.0)).total_seconds() // 60),
                                'type' : 'pending',
                                })
        
        return res
    
bss_prepaid_hours_hr_timesheet()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
