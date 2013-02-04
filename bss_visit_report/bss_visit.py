# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

STATE = (('draft', 'Draft'), 
         ('terminated', 'Terminated'))

class bss_visit(osv.osv):

    _name = 'bss_visit_report.visit'
    _description = "Visit"

    _columns = {
        'name': fields.char('Nom', size=20, required=True, translate=True),
        'customer_id': fields.many2one('base.res_partner', string="Customer", domain="[('customer', '=', 1)]"),
        'project_id': fields.many2one('project.project', string="Project"),
        'visit_task_id': fields.many2one('project.task', string="Visit Task"),
        'task_ids': fields.many2many('project.task', 'bss_visit_report.visit_task_rel', 'visit_id', 'task_id', string='Tasks'),
        'state': fields.selection(STATE, string="State"),
        'date_from': fields.datetime("Date From"),
        'date_to': fields.datetime("Date To"),
        'time': fields.float("Time"),
    }

    _defaults = {

    }

bss_visit()
