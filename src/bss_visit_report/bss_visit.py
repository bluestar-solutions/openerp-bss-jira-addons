# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import timedelta
from bss_utils.dateutils import orm_date
from openerp.netsvc import logging

STATE = (('draft', 'Draft'),
         ('pending', 'Pending'),
         ('terminated', 'Terminated'))

class bss_visit(osv.osv):

    _name = 'bss_visit_report.visit'
    _description = "Visit"
    _rec_name = 'ref'
    _logger = logging.getLogger(_name)
    
    def _todo_task_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for visit in self.browse(cr, uid, ids, context):
            res[visit.id] = []
            for vtask in visit.visit_task_ids:
                if vtask.state == 'todo':
                    res[visit.id].append(vtask.task_id.id)
        return res

    def _closed_task_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for visit in self.browse(cr, uid, ids, context):
            res[visit.id] = []
            for vtask in visit.visit_task_ids:
                if vtask.state not in ['new', 'todo']:
                    res[visit.id].append(vtask.task_id.id)
        return res

    _columns = {
        'ref': fields.char('Reference', size=64, select=1, readonly=True),    
        'project_id': fields.many2one('project.project', string="Project", readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'customer_id': fields.related('project_id',
                                      'partner_id',
                                      type="many2one",
                                      relation="res.partner",
                                      string="Customer",
                                      store=False,
                                      readonly=True),
        'customer_contact_id' : fields.many2one('res.partner', string="Customer Contact", readonly=False, states={'terminated': [('readonly', True)]}),
        'signer' : fields.char('Signer', size=128, readonly=False, states={'terminated': [('readonly', True)]}),
        'project_members': fields.related('project_id',
                                          'members',
                                          type="many2many",
                                          relation="res.users",
                                          string="Project Members",
                                          store=False,
                                          readonly=True),
        'user_id': fields.many2one('res.users', string="Visitor", readonly=False, required=True, states={'terminated': [('readonly', True)]}),
        'text' : fields.text('Text', readonly=False, states={'terminated': [('readonly', True)]}),
        'remarks' : fields.text('Remarks', readonly=False, states={'terminated': [('readonly', True)]}),
        'linked_task_id': fields.many2one('project.task', string="Visit Task", readonly=True),
        'visit_task_ids': fields.one2many('bss_visit_report.visit_task', 'visit_id', string='Tasks',
                                     readonly=False, states={'terminated': [('readonly', True)]}),
        'todo_task_ids': fields.function(_todo_task_ids, type='many2many', obj="project.task"),
        'closed_task_ids': fields.function(_closed_task_ids, type='many2many', obj="project.task"),
        'state': fields.selection(STATE, string="State"),
        'date': fields.date("Date", readonly=False, required=True, states={'terminated': [('readonly', True)]}),
        'hour_from': fields.float("Arrival", readonly=False, states={'terminated': [('readonly', True)]}),
        'hour_to': fields.float("Departure", readonly=False, states={'terminated': [('readonly', True)]}),
        'time': fields.float("Visit Time", readonly=False, states={'terminated': [('readonly', True)]}),
        'travel_time': fields.float("Travel Time", readonly=False, states={'terminated': [('readonly', True)]}),
        'travel_zone': fields.many2one('bss_visit_report.travel_zone', string="Travel Zone",
                                       readonly=False, states={'terminated': [('readonly', True)]}),
        'customer_ref': fields.char('Customer Reference', size=64, readonly=False, states={'terminated': [('readonly', True)]}),
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
                if visit.linked_task_id:
                    self.pool.get('project.task').write(cr, uid, [visit.linked_task_id.id], 
                                                        {'name': 'Intervention du %s' % orm_date(visit.date).strftime('%d.%m.%Y')}, context)
        if 'user_id' in vals:
            for visit in self.browse(cr, uid, ids, context):
                if visit.linked_task_id:
                    self.pool.get('project.task').write(cr, uid, [visit.linked_task_id.id], 
                                                        {'user_id': visit.user_id.id}, context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        vtask_pool = self.pool.get('bss_visit_report.visit_task')
        work_pool = self.pool.get('project.task.work')
        
        for visit in self.browse(cr, uid, ids, context):
            if visit.state == 'terminated':
                work_pool.unlink(cr, uid, [work.id for work in work_pool.browse(cr, uid, work_pool.search(cr, uid, [('task_id','=',visit.linked_task_id.id)]))])

            if visit.state in ['pending', 'terminated']:
                for vtask in vtask_pool.browse(cr, uid, vtask_pool.search(cr, uid, [('visit_id','=',visit.id)])):
                    self.pool.get('project.task').do_reopen(cr, uid, [vtask.task_id.id], context)
                    vtask_pool.unlink(cr, uid, [vtask.id], context=context)
                if visit.linked_task_id:
                    self.pool.get('project.task').unlink(cr, uid, [visit.linked_task_id.id], context=context)

        return super(bss_visit, self).unlink(cr, uid, ids, context=context)
    
    def action_validate(self, cr, uid, ids, context=None):
        for visit in self.browse(cr, uid, ids, context):
            for task in visit.project_id.tasks:
                if task.available_for_visit:
                    self.pool.get('bss_visit_report.visit_task').create(cr, uid, {
                        'visit_id': visit.id,        
                        'task_id': task.id,
                        'state': 'new',   
                    }, context)
            task_id = self.pool.get('project.task').create(cr, uid, {
                'name': 'Intervention du %s' % orm_date(visit.date).strftime('%d.%m.%Y'),
                'description': '',
                'project_id': visit.project_id.id,
                'user_id': visit.user_id.id,
                'partner_id': visit.customer_id.id,
            }, context)
            self.pool.get('project.task').do_open(cr, uid, [task_id], context)
            self.write(cr, uid, visit.id, {'state': 'pending', 'linked_task_id': task_id}, context)

    def action_terminate(self, cr, uid, ids, context=None):
        for visit in self.browse(cr, uid, ids, context):
            if visit.hour_to - visit.hour_from <= 0.0:
                raise osv.except_osv(_('Error'), _('Attendance difference must be greater than 00:00 !'))
            if not visit.time:
                raise osv.except_osv(_('Error'), _('Visit time must be greater than 00:00 !'))
            if not visit.travel_zone:
                raise osv.except_osv(_('Error'), _('Travel zone must be setted !'))
            if not visit.signer and not visit.customer_contact_id:
                raise osv.except_osv(_('Error'), _('Signer or customer contact must be setted !'))
            if not all(vtask.state != 'new' for vtask in visit.visit_task_ids):
                raise osv.except_osv(_('Error'), _('All tasks must be treated !'))
            
            self.pool.get('project.task.work').create(cr, uid, {
                'name': 'Intervention',
                'date': '%s %s' % (visit.date, str(timedelta(hours=visit.hour_from))),
                'task_id': visit.linked_task_id.id,
                'hours': visit.time,
                'user_id': visit.user_id.id,
            }, context)
            self.pool.get('project.task.work').create(cr, uid, {
                'name': 'Déplacement',
                'date': '%s %s' % (visit.date, str(timedelta(hours=visit.hour_from))),
                'task_id': visit.linked_task_id.id,
                'hours': visit.travel_time,
                'user_id': visit.user_id.id,
            }, context)
            self.pool.get('project.task').do_close(cr, uid, [visit.linked_task_id.id], context)
        self.write(cr, uid, ids, {'state': 'terminated'}, context)

    def action_reopen(self, cr, uid, ids, context=None):
        for visit in self.browse(cr, uid, ids, context):
            self.pool.get('project.task').do_reopen(cr, uid, [visit.linked_task_id.id], context)
            self.pool.get('project.task.work').unlink(cr, uid, 
                                                      [work.id for work in visit.linked_task_id.work_ids], 
                                                      context)
        self.write(cr, uid, ids, {'state': 'pending'}, context)
    
    def onchange_project_id(self, cr, uid, ids, project_id): 
        v={}
        
        if project_id:
            project = self.pool.get('project.project').browse(cr, uid, project_id)
            v['customer_id'] = project.partner_id.id

        return {'value': v} 
    
bss_visit()
