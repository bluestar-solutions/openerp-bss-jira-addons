# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.tools.translate import _
from bss_utils.dateutils import orm_date

STATE = (('draft', 'Draft'),
         ('pending', 'Pending'),
         ('terminated', 'Terminated'))

class bss_visit(osv.osv):

    _name = 'bss_visit_report.visit'
    _description = "Visit"
    _rec_name = 'ref'

    _columns = {
        'ref': fields.char('Reference', size=64, select=1, readonly=True),    
        'project_id': fields.many2one('project.project', string="Project", readonly=True, states={'draft': [('readonly', False)]}),
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
        'user_id': fields.many2one('res.users', string="Visitor", readonly=False, states={'terminated': [('readonly', True)]}),
        'linked_task_id': fields.many2one('project.task', string="Visit Task", readonly=True),
        'task_ids': fields.many2many('project.task', 'bss_visit_report_visit_initial_task_rel', 'visit_id', 'task_id', string='Initial Tasks',
                                     readonly=False, states={'terminated': [('readonly', True)]}),
        'state': fields.selection(STATE, string="State"),
        'date': fields.date("Date", readonly=False, states={'terminated': [('readonly', True)]}),
        'hour_from': fields.float("From", readonly=False, states={'terminated': [('readonly', True)]}),
        'hour_to': fields.float("To", readonly=False, states={'terminated': [('readonly', True)]}),
        'time': fields.float("Time", readonly=False, states={'terminated': [('readonly', True)]}),
        'travel_time': fields.float("Travel Time", readonly=False, states={'terminated': [('readonly', True)]}),
        'travel_zone': fields.many2one('bss_visit_report.travel_zone', string="Travel Zone",
                                       readonly=False, states={'terminated': [('readonly', True)]}),
    }

    _defaults = {
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def create(self, cr, uid, vals, context=None):
        if not 'ref' in vals:
            vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, 'bss_visit_report.visit.ref')
        return super(bss_visit, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        res = super(bss_visit, self).write(cr, uid, ids, vals, context=context)
        if 'date' in vals:
            for visit in self.browse(cr, uid, ids, context):
                self.pool.get('project.task').write(cr, uid, [visit.linked_task_id.id], 
                                                    {'name': 'Visite du %s' % orm_date(visit.date).strftime('%d.%m.%Y')}, context)
        if 'user_id' in vals:
            for visit in self.browse(cr, uid, ids, context):
                self.pool.get('project.task').write(cr, uid, [visit.linked_task_id.id], 
                                                    {'user_id': visit.user_id.id}, context)
        return res
    
    def action_validate(self, cr, uid, ids, context=None):
        for visit in self.browse(cr, uid, ids, context):
            task_id = self.pool.get('project.task').create(cr, uid, {
                'name': 'Visite du %s' % orm_date(visit.date).strftime('%d.%m.%Y'),
                'description': '',
                'project_id': visit.project_id.id,
                'user_id': visit.user_id.id,
                'partner_id': visit.customer_id.id,
            }, context)
            self.write(cr, uid, visit.id, {'state': 'pending', 'linked_task_id': task_id}, context)

    def action_terminate(self, cr, uid, ids, context=None):
        for visit in self.browse(cr, uid, ids, context):
            if visit.hour_to - visit.hour_from <= 0.0:
                raise osv.except_osv(_('Error'), _('Attendance difference must be greater than 00:00 !'))
            if not visit.time:
                raise osv.except_osv(_('Error'), _('Visit time must be greater than 00:00 !'))
            if not visit.travel_zone:
                raise osv.except_osv(_('Error'), _('Travel zone must be set !'))
        self.write(cr, uid, ids, {'state': 'terminated'}, context)

    def action_reopen(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'pending'}, context)
    
    def onchange_project_id(self, cr, uid, ids, project_id): 
        v={}
        
        if project_id:
            project = self.pool.get('project.project').browse(cr, uid, project_id)
            v['task_ids'] = []
            for task in project.tasks:
                if task.state != 'done' and task.state != 'cancelled':
                    v['task_ids'].append(task.id)
            v['customer_id'] = project.partner_id.id

        return {'value': v} 

bss_visit()
