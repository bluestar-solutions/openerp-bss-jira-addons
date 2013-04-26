# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.netsvc import logging

STATE = (('new', 'New'),
         ('todo', 'Todo'),
         ('cancelled', 'Cancelled'),
         ('done', 'Done'))

TASK_STATE = [('draft', 'New'),
              ('open', 'In Progress'),
              ('pending', 'Pending'), 
              ('done', 'Done'), 
              ('cancelled', 'Cancelled')]

VISIT_STATE = (('draft', 'Draft'),
               ('pending', 'Pending'),
               ('terminated', 'Terminated'))

class bss_visit_task_action(osv.TransientModel):
    
    _name = 'bss_visit_report.bss_visit_task_action'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
            
        vt_obj = self.pool.get('bss_visit_report.visit_task')
            
        res = dict()
        for field in self._columns.keys():
            if field in context:
                res[field] = context[field]
                
        if res['visit_task_id']:
            res['comment'] = vt_obj.read(cr, uid, [res['visit_task_id']], ['comment'], context)[0]['comment']

        return res  
    
    _columns = {
        'visit_task_id': fields.many2one('bss_visit_report.visit_task', string="Visit Task", ondelete='cascade'),        
        'comment': fields.char('Comment', size=255, required=True),
        'state': fields.selection(STATE, 'State', readonly=True),    
    }
    
    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        vt_obj = self.pool.get('bss_visit_report.visit_task')
        form = self.browse(cr, uid, ids)[0]
        
        vt_obj.write(cr, uid, [form.visit_task_id.id], {'comment': form.comment})
        fnct = {'todo': vt_obj.do_todo,
                'cancelled': vt_obj.do_cancel,
                'done': vt_obj.do_close}
        fnct[form.state](cr, uid, [form.visit_task_id.id], context)
        
        return {
            'name': form.visit_task_id.visit_id.ref,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'bss_visit_report.visit',
            'res_id': int(form.visit_task_id.visit_id.id),
            'context': context,
            'type': 'ir.actions.act_window'
        } 
        
    
bss_visit_task_action()

class bss_visit_task(osv.osv):
    
    _name = 'bss_visit_report.visit_task'
    _rec_name = 'task_name'
    _logger = logging.getLogger(_name)
    
    def _get_visit_visit_task_ids(self, cr, uid, ids, context=None):
        task_ids = set()
        for visit in self.browse(cr, uid, ids, context):
            task_ids = task_ids.union(set([visit_task.id for visit_task in visit.visit_task_ids]))
            
        return list(task_ids)
    
    def _description_trunc(self, cr, uid, ids, name, args, context=None):
        res = {}
        for bvt in self.browse(cr, uid, ids, context):
            if len(bvt.description) >= 50:
                res[bvt.id] = "%s..." % bvt.description[0:50]
            else:
                res[bvt.id] = bvt.description
        return res
    
    def _description_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        for bvt in self.browse(cr, uid, ids, context):
            res[bvt.id] = "%s\r\n\r\n%s" % (bvt.task_name, bvt.description)
        return res
    
    _columns = {
        'visit_id': fields.many2one('bss_visit_report.visit', string="Visit", ondelete='cascade', required=True),        
        'task_id': fields.many2one('project.task', string="Task", required=True),
        'state': fields.selection(STATE, 'State', readonly=True),
        'comment': fields.char('Comment', size=255),
        'priority': fields.related('task_id', 'priority', type="selection", string="Priority",
                                   selection=[('4','Very Low'), ('3','Low'), ('2','Medium'), ('1','Important'), ('0','Very important')],
                                   store=False, readonly=True),
        'user_id': fields.related('task_id', 'user_id', type="many2one", string="Assigned To",
                                   relation="res.users",
                                   store=False, readonly=True),    
        'task_state': fields.related('task_id', 'state', type="selection", string="Task State",
                                     selection=TASK_STATE,
                                     store=False, readonly=True),
        'task_name': fields.related('task_id', 'name', type="char", string="Task Name",
                                     store=False, readonly=True),
        'visit_state': fields.related('visit_id', 'state', type="selection", string="Visit State",
                                      selection=VISIT_STATE,
                                      store={
            'bss_visit_report.visit' : (_get_visit_visit_task_ids, ['state'], 10),
        }, readonly=True),
        'description_name' : fields.function(_description_name, store=False, method=True, type="text", string="Task description"),
        'description' : fields.related('task_id', 'description', store=False, type="text", string="Description"),
        'description_trunc' : fields.function(_description_trunc, store=False, method=True, type="text", string="Description"),
    }
    
    _defaults = {
        'state': 'new',
    }
        
    def do_todo(self, cr, uid, ids, context=None):
        task_obj = self.pool.get('project.task')
        task_obj.do_reopen(cr, uid, [visit_task.task_id.id for visit_task in self.browse(cr, uid, ids, context)], context)
        self.write(cr, uid, ids, {'state': 'todo'})
        return True
    
    def do_cancel(self, cr, uid, ids, context=None):
        task_obj = self.pool.get('project.task')
        task_obj.do_cancel(cr, uid, [visit_task.task_id.id for visit_task in self.browse(cr, uid, ids, context)], context)
        self.write(cr, uid, ids, {'state': 'cancelled'})
        return True
    
    def do_close(self, cr, uid, ids, context=None):
        task_obj = self.pool.get('project.task')
        task_obj.do_close(cr, uid, [visit_task.task_id.id for visit_task in self.browse(cr, uid, ids, context)], context)
        self.write(cr, uid, ids, {'state': 'done'})
        return True
            
    def action_view_visit(self, cr, uid, ids, context=None):
        self._logger.debug('ids = %s, context = %s', str(ids), str(context))
        return {
            'name': 'Visit report view',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'bss_visit_report.visit',
            'context': "{}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'self',
            'res_id': context['active_id']  or False,
        }

bss_visit_task()   
