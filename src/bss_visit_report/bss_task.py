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

class bss_task(osv.osv):
    _inherit = 'project.task'
    
    def _available_for_visit(self, cr, uid, ids, name, args, context=None):
        vis_obj = self.pool.get('bss_visit_report.visit')
        locked_by_visit_task_ids = []
        open_visit_ids = vis_obj.search(cr, uid, [('state', '!=', 'terminated')])
        for visit in vis_obj.browse(cr, uid, open_visit_ids, context):
            locked_by_visit_task_ids.extend([visit_task_id.task_id.id for visit_task_id in visit.visit_task_ids])
            locked_by_visit_task_ids.append(visit.linked_task_id.id)
            
        locked_by_visit_task_ids = list(set(locked_by_visit_task_ids))
        
        res = {}
        for task in self.browse(cr, uid, ids, context):
            if task.state in ['cancelled', 'done']:
                res[task.id] = False
            else:
                res[task.id] = task.id not in locked_by_visit_task_ids
            
        return res

    def _get_visit_task_ids(self, cr, uid, ids, context=None):
        task_obj = self.pool.get('project.task')
        task_ids = set()
        for visit in self.browse(cr, uid, ids, context):
            task_ids = task_ids.union(set(task_obj.search(cr, uid, [('project_id', '=', visit.project_id.id)], 
                                                                    context=context)))
            
        return list(task_ids)

    _columns = {
        'available_for_visit' : fields.function(_available_for_visit, type='boolean', store={
            'bss_visit_report.visit' : (_get_visit_task_ids, ['visit_task_ids', 'state'], 10),  
 
        }),
        'bss_visit_task_ids': fields.one2many('bss_visit_report.visit_task', 'task_id', string='Visit tasks'), 
    }
    
bss_task()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
