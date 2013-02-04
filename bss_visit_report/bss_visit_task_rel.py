# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

MODE = (('existing', 'Existing'), 
        ('new', 'New'))

class bss_visit(osv.osv):

    _name = 'bss_visit_report.visit_task_rel'
    _description = "Visit And Task Relation"

    _columns = {
        'visit_id': fields.many2one('bss_visit_report.visit', string="Visit"),
        'task_id': fields.many2one('project.task', string="Task"),
        'mode': fields.selection(MODE, string="Mode"),
        'terminated': fields.boolean(string="Terminated")
    }

    _defaults = {

    }

bss_visit()
