# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

STATE = (('draft', 'Draft'), 
         ('terminated', 'Terminated'))

class bss_visit(osv.osv):

    _name = 'bss_visit_report.visit'
    _description = "Visit"
    _rec_name = 'ref'

    _columns = {
        'ref': fields.char('Reference', size=64, select=1, readonly=True),    
        'project_id': fields.many2one('project.project', string="Project"),
        'customer_id': fields.related('project_id',
                                      'partner_id',
                                      type="many2one",
                                      relation="res.partner",
                                      string="Customer",
                                      store=False,
                                      readonly=True),
        'project_members': fields.related('project_id',
                                          'members',
                                          type="many2many",
                                          relation="res.users",
                                          string="Project Members",
                                          store=False,
                                          readonly=True),
        'user_id': fields.many2one('res.users', string="Visitor"),
        'visit_task_id': fields.many2one('project.task', string="Visit Task"),
        'initial_task_ids': fields.many2many('project.task', 'bss_visit_report_visit_initial_task_rel', 'visit_id', 'task_id', string='Initial Tasks'),
        'done_task_ids': fields.many2many('project.task', 'bss_visit_report_visit_done_task_rel', 'visit_id', 'task_id', string='Done Tasks'),
        'undone_task_ids': fields.many2many('project.task', 'bss_visit_report_visit_undone_task_rel', 'visit_id', 'task_id', string='Undone Tasks'),
        'state': fields.selection(STATE, string="State"),
        'date_from': fields.datetime("Date From"),
        'date_to': fields.datetime("Date To"),
        'time': fields.float("Time"),
        'travel_time': fields.float("Time"),
        'travel_zone': fields.many2one('bss_visit_report.travel_zone', string="Travel Zone", required=True),
    }

    _defaults = {
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def create(self, cr, uid, vals, context=None):
        if not 'ref' in vals:
            vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, 'bss_visit_report.visit.ref')
        return super(bss_visit, self).create(cr, uid, vals, context=context)

bss_visit()
