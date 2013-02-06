# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

STATE = (('todo', 'Todo'),
         ('cancelled', 'Cancelled'),
         ('done', 'Done'))

class bss_visit_task(osv.osv):
    
    _name = 'bss_visit_report.visit_task'
    _columns = {
        'visit_id': fields.many2one('bss_visit_report.visit', string="Visit", ondelete='cascade'),        
        'task_id': fields.many2one('project.task', string="Task"),
        'state': fields.selection(STATE, 'State'),      
    }
    
    _default = {
        'state': 'todo',
    }
    
bss_visit_task()   
