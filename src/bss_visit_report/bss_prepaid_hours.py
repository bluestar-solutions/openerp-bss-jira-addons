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

        return res
    
    _columns = {
        'amount' : fields.integer('Time amount'),
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
            'processed_date' : time.strftime('%Y-%m-%d'),
            }, context=None)
        
        return {'type' : 'ir.actions.act_window_close'}

class bss_prepaid_time(osv.osv):
    _name = 'bss_visit_report.prepaid_time'
    _description = 'Prepaid time'
    
    _columns = {
        'amount' : fields.integer('Time amount'),
        'processed_date' : fields.date('Processed date'),
        'related_visit' : fields.many2one('bss_visit_report.visit', string='Related visit report', required=False),
        'prepaid_hours_id' : fields.many2one('bss_visit_report.prepaid_hours', select=True)
    }
    
    _sql_constraints = [('check_amount','CHECK(amount > 0)','Time amount must be greater than 0 !')]
    _default = {'processed_date' : lambda *a: time.strftime('%Y-%m-%d')}
    
bss_prepaid_time()

class bss_prepaid_hours(osv.osv):
    _name = 'bss_visit_report.prepaid_hours'
    _description = 'Prepaid hours'
        
    def _get_validated_hours(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for pph in self.browse(cr, uid, ids, context):
            res[pph.id] = []
            for ppt in pph.related_hours:
                if ppt.related_visit:
                    res[pph.id].append(ppt.id)
        
        return res
    
    def _get_added_hours(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for pph in self.browse(cr, uid, ids, context):
            res[pph.id] = []
            for ppt in pph.related_hours:
                if not ppt.related_visit:
                    res[pph.id].append(ppt.id)
        
        return res
    
    def _get_av_amount(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for pph in self.browse(cr, uid, ids, context):
            res[pph.id] = 0
            for ppt in pph.related_hours:
                if ppt.related_visit:
                    res[pph.id] -= ppt.amount
                else:
                    res[pph.id] += ppt.amount
                
        return res
    
    _columns = {
        'related_hours' : fields.one2many('bss_visit_report.prepaid_time', 'prepaid_hours_id', 'Related hours'),
        'validated_hours' : fields.function(_get_validated_hours, 'Valitated hours', type='one2many', store=False, method=True, obj='bss_visit_report.prepaid_time'),
        'added_hours' : fields.function(_get_added_hours, 'Added hours', type='one2many', store=False, method=True, obj='bss_visit_report.prepaid_time'),
        'contract_id' : fields.many2one('account.analytic.account', select=True),
        'pph_name' : fields.related('contract_id', 'name', type='char', relation='account.analytic.account', string="Name", store=False),
        'av_amount' : fields.function(_get_av_amount, type="integer", string="Available amount", method=True, store=False),
    }
    
bss_prepaid_hours()

class bss_prepaid_hours_contract(osv.Model):
    _name = 'account.analytic.account'
    _inherit = 'account.analytic.account'
    
    def __init__(self, pool, cr):
        super(bss_prepaid_hours_contract, self)._columns['prepaid_hours_id'] = fields.one2many('bss_visit_report.prepaid_time', 'contract_id', 'Prepaid hours', required=False)
        super(bss_prepaid_hours_contract, self).__init__(pool, cr)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
