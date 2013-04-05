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
from openerp.netsvc import logging

class bss_visit_task_continue(osv.TransientModel):
    _name = 'visit.report.task.continue'
    _description = 'Task continue'
    _logger = logging.getLogger(_name)

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        visit_task_obj = self.pool.get('bss_visit_report.visit_task')
        res = dict()
        for field in self._columns.keys():
            if field in context:
                res[field] = context[field]
        visit_task = visit_task_obj.browse(cr, uid, [context['visit_task_id']], context=context)[0]
        res['new_name'] = "%s (Suite)" % visit_task.task_id.name
        res['old_description'] = visit_task.task_id.description
        res['new_description'] = visit_task.task_id.description
        return res
    
    _columns = {
        'visit_task_id': fields.many2one('bss_visit_report.visit_task', string="Visit Task", ondelete='cascade'),        
        'new_name': fields.char('Task Summary', size=128),
        'old_description': fields.text('Old description'),
        'new_description': fields.text('New description'),        
        'comment': fields.char('Comment', size=255),
    }
        
    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self._logger.debug('ids=%s, context=%s',str(ids),str(context))  
        form = self.browse(cr, uid, ids)[0]
        task_obj = self.pool.get('project.task')
        visit_task_obj = self.pool.get('bss_visit_report.visit_task')
        visit_task_id = context['visit_task_id']
#2013-04-04 13:57:52,778 3189 DEBUG openerp_bluestar visit.report.task.continue: ids=[1], context={'lang': 'fr_CH', 'tz': 'Europe/Zurich', 'uid': 18, 'active_model': 'bss_visit_report.visit_task', 'search_disable_custom_filters': True, 'default_project_id': 6, 'visit_task_id': 54, 'active_ids': [54], 'active_id': 54}
        #create new task
        visit_task = visit_task_obj.browse(cr, uid, [visit_task_id], context)[0]
        task_id = visit_task.task_id.id
        new_task_map = task_obj.copy_data(cr, uid, task_id, {'name':form.new_name,'description':form.new_description,'bss_visit_task_ids':[]})
        self._logger.debug('new_task_map=%s',str(new_task_map))
        new_task_id = task_obj.create(cr, uid,new_task_map,context=None)
        task_obj.do_reopen(cr, uid, [new_task_id], context)
        visit_task_obj.create(cr, uid, {'visit_id':visit_task.visit_id.id,'task_id':new_task_id,'state': 'todo'},context=None)
        
        #old task
        task_obj.write(cr, uid, [task_id], {'description':form.old_description,})
        task_obj.do_close(cr, uid, [task_id], context)
        visit_task_obj.write(cr, uid, [visit_task_id], {'state': 'done','comment':form.comment})

        return {
            'name': form.visit_task_id.visit_id.ref,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'bss_visit_report.visit',
            'res_id': int(form.visit_task_id.visit_id.id),
            'context': context,
            'type': 'ir.actions.act_window'
        }    


bss_visit_task_continue()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
