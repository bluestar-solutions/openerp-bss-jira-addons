# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

STATE = (('todo', 'Todo'),
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

class bss_visit_task(osv.osv):
    
    _name = 'bss_visit_report.visit_task'
    
    def _get_visit_visit_task_ids(self, cr, uid, ids, context=None):
        task_ids = set()
        for visit in self.browse(cr, uid, ids, context):
            task_ids = task_ids.union(set([visit_task.id for visit_task in visit.visit_task_ids]))
            
        return list(task_ids)
    
    _columns = {
        'visit_id': fields.many2one('bss_visit_report.visit', string="Visit", ondelete='cascade'),        
        'task_id': fields.many2one('project.task', string="Task"),
        'state': fields.selection(STATE, 'State', readonly=True),
        'priority': fields.related('task_id', 'priority', type="selection", string="Priority",
                                   selection=[('4','Very Low'), ('3','Low'), ('2','Medium'), ('1','Important'), ('0','Very important')],
                                   store=False, readonly=True),
        'user_id': fields.related('task_id', 'user_id', type="many2one", string="Assigned To",
                                   relation="res.users",
                                   store=False, readonly=True),    
        'task_state': fields.related('task_id', 'state', type="selection", string="Task State",
                                     selection=TASK_STATE,
                                     store=False, readonly=True),
        'visit_state': fields.related('visit_id', 'state', type="selection", string="Visit State",
                                      selection=VISIT_STATE,
                                      store={
            'bss_visit_report.visit' : (_get_visit_visit_task_ids, ['state'], 10), 
        }, readonly=True),        
    }
    
    _defaults = {
        'state': 'todo',
    }
    
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

    def do_reopen(self, cr, uid, ids, context=None):
        task_obj = self.pool.get('project.task')
        task_obj.do_reopen(cr, uid, [visit_task.task_id.id for visit_task in self.browse(cr, uid, ids, context)], context)
        self.write(cr, uid, ids, {'state': 'todo'})
        return True
            
    
bss_visit_task()   
