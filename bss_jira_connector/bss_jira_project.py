# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Bluestar Solutions Sàrl (<http://www.blues2.ch>).
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
import json
from datetime import datetime, timedelta
import re
from bss_jira_config import JIRA_DISABLE_TZ

JIRA_DATE_PATTERN = re.compile('(\\d{4})-(\\d{2})-(\\d{2})T(\\d{2}):(\\d{2}):(\\d{2})\.(\\d{3})([\+-])(\\d{2})(\\d{2})')

class bss_jira_project(osv.osv):
    _name = 'bss_jira_connector.jira_project'
    _logger = logging.getLogger(_name)
    
    _columns = {
        'jira_id': fields.integer('JIRA id', readonly=True),
        'key': fields.char('JIRA key', size=256, readonly=True),
        'name': fields.char('JIRA project name', size=256, readonly=True),
        'project_id': fields.many2one('project.project', string="Project"),
    }

    _sql_constraints = [
        ('jira_id_uniq', 'unique (jira_id)', 'The JIRA id must be unique !'),
        ('key_uniq', 'unique (key)', 'The JIRA key must be unique !'),
    ]
    
    def _save_error(self, cr, uid, worklog, message="Unknown error"):
        error_obj = self.pool.get('bss_jira_connector.jira_worklog_errors')
        
        err_data = {}
        err_data['user_id']= worklog.user_id
        err_data['project_id'] = self.browse(cr, uid, self.search(cr, uid, [('jira_id','=',worklog.jira_id)]))[0].project_id
        err_data['jira_issue_id'] = worklog.jira_issue_id
        err_data['jira_worklog_id'] = worklog.jira_id
        err_data['synchro_date_time'] = str(datetime.now())
        err_data['update_date'] = str(worklog.date)
        err_data['error_message'] = message
        err_data['key'] = self.browse(cr, uid, self.search(cr, uid, [('jira_id','=',worklog.jira_id)]))[0].key
        error_obj.create(cr, uid, err_data)
        self._logger.error(message)
        
    def _check_constraint(self, cr, uid, task_id, data):
        if data.has_key('name') or data.has_key('project_id'):
            task = self.pool.get('project.task').browse(cr, uid, task_id)[0]
            if task and len(task.work_ids):
                for task_work in task.work_ids:
                    if not task_work.hr_analytic_timesheet_id:
                        continue
                    if task_work.hr_analytic_timesheet_id.line_id.invoice_id:
                        return False
        return True

    def ws_decode_write(self, cr, uid, model, content, datetime_format):
        decoded_list = json.loads(content)
        field_list = model.fields_get(cr,uid)
        self._logger.info("List is : %s, length is %d",str(decoded_list),len(decoded_list))
        self._logger.info("Field list is : %s, length is %d",str(field_list),len(field_list))
        if not decoded_list:
            return True
        elif len(decoded_list)==0:
            self._logger.info("List is empty")
            return True

        for decoded in decoded_list:
            oid = model.search(cr, uid, [('jira_id', '=', decoded['id'])])
            if oid:
                jira_project = self.browse(cr, uid, oid)[0]
                if jira_project.name!=decoded['name']:
                    self._logger.info('Update name for project %s from %s to %s',decoded['key'],jira_project.name,decoded['name'])
                    self.write(cr, uid, jira_project.id, {'name': decoded['name']})
            else:   
                data = {'jira_id': decoded['id'],
                        'key': decoded['key'],
                        'name': decoded['name']
                        }
                self._logger.info('Create project %s',str(data))
                oid = model.create(cr, uid, data)
        return True   
    
    def decode_jira_time(self, cr, uid, string):
        with_timezone = self.pool.get('ir.config_parameter').get_param(cr, uid, JIRA_DISABLE_TZ, default=str(False)) == str(False)
        #"2013-04-16T13:23:42.000+0200"
        m = JIRA_DATE_PATTERN.search(string)
        d = datetime(int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)),int(m.group(6)),int(m.group(7)))
        t = timedelta(hours=int(m.group(9)), minutes=int(m.group(10)))
        if with_timezone:
            if m.group(8) == '+':
                return d-t
            else:
                return d+t
        else:
            return d
        
    def ws_decode_write_worklog(self, cr, uid, model, content, datetime_format):
        decoded_list = json.loads(content)
#/jira/rest/api/2/search?jql=updated%20%3E%20startOfDay(-1)%20ORDER%20BY%20updated%20DESC&startAt=0&maxResults=500&fields=assignee,description,summary,created,updated,duedate,priority,status,worklog,key,id,project,timeestimate,timeoriginalestimate
#        field_list = model.fields_get(cr,uid)
#        self._logger.info("List is : %s, length is %d",str(decoded_list),len(decoded_list))
#        self._logger.info("Field list is : %s, length is %d",str(field_list),len(field_list))
        if not decoded_list:
            return True
        elif len(decoded_list)==0:
            self._logger.info("List is empty")
            return True
        issue_list = decoded_list['issues']
        self._logger.info('Issue list contains %d issues (len = %d)',decoded_list['total'],len(issue_list))
        found_projects = []
        active_projects = {}
        issue_obj = self.pool.get('project.task')
        worklog_obj = self.pool.get('project.task.work')
        user_obj = self.pool.get('res.users')
        ts_obj = self.pool.get('hr_timesheet_sheet.sheet')
        error_obj = self.pool.get('bss_jira_connector.jira_worklog_errors')
        jira_issue_oe_project = {}
        jira_issue_keys = {}
        issue_worklogs = {}
        for issue_fields in issue_list:
            is_issue_cause_error = False
            issue = issue_fields['fields']
            self._logger.info('Processing issue %s',issue_fields['key'])
            project = issue['project']
            if project['key'] not in found_projects:
                self._logger.info('Processing project %s',project['key'])
                oid = model.search(cr, uid, [('jira_id', '=', project['id'])])
                if oid:
                    jira_project = self.browse(cr, uid, oid)[0]
                    if jira_project.name!=project['name']:
                        self._logger.info('Update name for project %s from %s to %s',project['key'],jira_project.name,project['name'])
                    self.write(cr, uid, jira_project.id, {'name': project['name']})
                    found_projects.append(project['key'])
                    if jira_project.project_id:
                        active_projects[project['key']] = oid
                    else:
                        self._logger.info('Project %s is not active',project['key'])
                        continue
                else:   
                    data = {'jira_id': project['id'],
                        'key': project['key'],
                        'name': project['name']
                        }
                    self._logger.info('Create project %s',str(data))
                    oid = model.create(cr, uid, data)
                    jira_project = self.browse(cr, uid, [oid])[0]
            elif project['key'] in active_projects:
                jira_project = self.browse(cr, uid, active_projects[project['key']])[0]        
            else:
                self._logger.info('Project %s is not active',project['key'])
                continue    

            if jira_project and jira_project.project_id:
                issue_jira_id = issue_fields['id']
                jira_issue_oe_project[issue_jira_id] = jira_project.project_id.id
                ioid = issue_obj.search(cr, uid, [('jira_id', '=', issue_jira_id)])
                issue_key = issue_fields['key']
                jira_issue_keys[issue_jira_id]=issue_key
                last_update = self.decode_jira_time(cr, uid, issue['updated'])
                previous_update = None
                if ioid:
                    jira_issue = issue_obj.browse(cr, uid, ioid)[0]
                    previous_update = datetime.strptime(jira_issue.last_update_datetime,'%Y-%m-%d %H:%M:%S')
                    if last_update <= previous_update:
                        #update already done --> do nothing
                        self._logger.info('issue update already done --> do nothing %s %s',str(last_update),str(previous_update))
                        continue
                    data = {}
                    if jira_issue.key != issue_key:
                        data['key'] = issue_key
                    summary =  issue['summary']
                    summary = summary.replace('"','_').replace('\'','_')
                    if len(summary)>127:
                        summary = '%s...' % summary[:120]
                    if jira_issue.name != summary:
                        data['name'] = summary
                    prio = str(int(issue['priority']['id']) - 1)
                    if jira_issue.priority != prio:
                        data['priority'] = prio
                    if jira_issue.project_id.id != jira_project.project_id.id:
                        data['project_id'] = jira_project.project_id.id
                    oe_assignee = None
                    if jira_issue.user_id:
                        oe_assignee = jira_issue.user_id.login 
                    if issue['assignee'] and issue['assignee']['name'] != oe_assignee:
                        self._logger.info('assignee = %s user = %s',issue['assignee']['name'],oe_assignee)
                        assignee_id = user_obj.search(cr, uid, [('login','=',issue['assignee']['name'])])
                        self._logger.info('assignee_id = %s ',str(assignee_id))
                        if assignee_id and len(assignee_id):
                            data['user_id'] = assignee_id[0]                        
                    elif not issue['assignee'] and oe_assignee:
                        data['user_id']=None
                    if issue['description'] and jira_issue.description and issue['description'] != jira_issue.description:
                        self._logger.info('issue description = %s task description = %s',issue['description'],jira_issue.description)
                        data['description'] = issue['description']
                    elif not issue['description'] and jira_issue.description:
                        data['description'] = None
                    elif issue['description'] and not jira_issue.description:
                        data['description'] = issue['description']
                    if issue['timeoriginalestimate']:
                        toe = float(issue['timeoriginalestimate']) / 3600.0
                        if abs(toe - jira_issue.planned_hours) > 0.01:
                            self._logger.info('timeoriginalestimate %s jira_issue.planned_hours %s',str(toe),str(jira_issue.planned_hours))
                            data['planned_hours'] = toe
                    if issue['timeestimate']:
                        te = float(issue['timeestimate']) / 3600.0
                        if abs(te - jira_issue.remaining_hours) > 0.01:
                            self._logger.info('timeestimate %s jira_issue.remaining_hours %s',str(te),str(jira_issue.remaining_hours))
                            data['remaining_hours'] = te
                    if issue['duedate']:
                        duedate = datetime.strptime(issue['duedate'],'%Y-%m-%d')
                        if duedate != jira_issue.date_deadline:
                            data['date_deadline'] = duedate
                    if issue['status']['id'] != jira_issue.jira_status:
                        if issue['status']['id'] in ['1','4','10000']:
                            state = 'pending'
                        elif issue['status']['id'] in ['3']:
                            state = 'open'
                        elif issue['status']['id'] in ['5','6','10001']:
                            state = 'done'
                        if state:
                            data['stage_id'] = issue_obj.stage_find(cr, uid, [], jira_project.project_id.id, [('state', '=', state)])
                            data['jira_status'] = issue['status']['id']
                    
                    if jira_issue.last_update_datetime != str(last_update):
                        self._logger.info('jira_issue.last_update_datetime %s last_update %s',str(jira_issue.last_update_datetime),str(last_update))
                        data['last_update_datetime'] = str(last_update)
                    if data:
                        # Test if update breaks invoiced line constraint
                        if self._check_constraint(cr, uid, ioid, data):
                            self._logger.info('Update issue %s with %s',issue_key,str(data))
                            issue_obj.write(cr, uid, ioid, data)
                        else:
                            self._logger.error('Updating issue %s breaks invoiced line constraint',issue_key)
                            self._logger.info('Data : %s' % str(data))
                            is_issue_cause_error = True
                else:
                    summary =  issue['summary']
                    summary = summary.replace('"','_').replace('\'','_')
                    if len(summary)>127:
                        summary = '%s...' % summary[:120]
                    data = {
                        'jira_id':issue_jira_id,
                        'key': issue_key,
                        'name': summary,
                        'priority': str(int(issue['priority']['id']) - 1),
                        'project_id': jira_project.project_id.id,
                            }
                    if issue['assignee']:
                        assignee_id = user_obj.search(cr, uid, [('login','=',issue['assignee']['name'])])
                        if assignee_id and len(assignee_id):
                            data['user_id'] = assignee_id[0]
                    if issue['description']: 
                        data['description'] = issue['description']
                    if issue['timeoriginalestimate']:
                        data['planned_hours'] = float(issue['timeoriginalestimate']) / 3600.0
                    if issue['timeestimate']:
                        data['remaining_hours'] = float(issue['timeestimate']) / 3600.0 
                    if issue['duedate']:
                        data['date_deadline'] = datetime.strptime(issue['duedate'],'%Y-%m-%d')
                    
                    data['jira_status'] = issue['status']['id']
                    if issue['status']['id'] in ['1','4','10001']:
                        state = 'pending'
                    elif issue['status']['id'] in ['3']:
                        state = 'open'
                    elif issue['status']['id'] in ['5','6','10000']:
                        state = 'done'
                    if state:
                        data['stage_id'] = issue_obj.stage_find(cr, uid, [], jira_project.project_id.id, [('state', '=', state)])
                    data['last_update_datetime'] = str(last_update)
                    self._logger.info('Create issue %s',str(data))
                    ioid = issue_obj.create(cr, uid, data)
                    jira_issue = issue_obj.browse(cr, uid, ioid)
                issue_worklogs[jira_issue.jira_id] = []
                if issue['worklog']:
                    if issue['worklog']['worklogs']:
                        for worklog in issue['worklog']['worklogs']:
                            author_id = user_obj.search(cr, uid, [('login','=',worklog['author']['name'])])
                            if not author_id:
                                #author not in openerp --> do nothing
                                continue
                            started_date = self.decode_jira_time(cr, uid, worklog['started'])
                            tsid = ts_obj.search(cr, uid, [('user_id','=',author_id[0]),('date_from','<=', started_date),('date_to','>=', started_date),('state','not in',['new','draft'])])
                            worklog_jira_id = worklog['id']
                            woid = worklog_obj.search(cr, uid, [('jira_id', '=', worklog_jira_id)])
                            if is_issue_cause_error:
                                if woid:
                                    self._save_error(cr, uid, worklog_obj.browse(cr, uid, woid), 'You cannot modify an invoiced analytic line!')
                                continue
                            issue_worklogs[jira_issue.jira_id].append(worklog_jira_id)
                            if woid:
                                work_last_update = self.decode_jira_time(cr, uid, worklog['updated'])
                                jira_worklog = worklog_obj.browse(cr, uid, woid)[0]
                                if previous_update and work_last_update <= previous_update:
                                    #update already done --> do nothing
                                    self._logger.info('worklog update already done --> do nothing')
                                    continue
                                #Check if work log is editable
                                
                                data = {}
                                if jira_worklog.jira_issue_id != jira_issue.jira_id:
                                    data['jira_issue_id'] = jira_issue.jira_id
                                    data['task_id'] = jira_issue.id
                                comment = worklog['comment'] or '/'
                                comment = comment.replace('"','_').replace('\'','_')
                                if len(comment)>127:
                                    comment = "%s..." % comment[:120]
                                if comment != jira_worklog.name:
                                    data['name'] = comment
                                if jira_worklog.date != str(started_date):
                                    data['date'] = str(started_date)
                                hours = float(worklog['timeSpentSeconds']) / 3600.0    
                                if abs(jira_worklog.hours - hours) > 0.01:
                                    self._logger.info('hours %s jira_worklog.hours %s',str(hours),str(jira_worklog.hours))
                                    data['hours'] = hours            

                                if data:
                                    if tsid:
                                        weid = error_obj.search(cr, uid, [('jira_worklog_id','=',worklog_jira_id)])
                                        if not weid:
                                            err_data = {}
                                            err_data['user_id']= author_id[0]
                                            err_data['project_id'] = jira_project.project_id.id
                                            err_data['jira_issue_id'] = jira_issue.id
                                            err_data['jira_worklog_id'] = worklog_jira_id
                                            err_data['synchro_date_time'] = str(datetime.now())
                                            err_data['update_date'] = str(work_last_update)
                                            err_data['key'] = issue_fields['key']
                                            err_data['error_message'] = u'timesheet has been submitted : cannot change worklog !' 
                                            error_obj.create(cr, uid,err_data)                                           
                                            self._logger.error('timesheet has been submitted : cannot change worklog !')
                                        continue
                                    self._logger.info('Update worklog %s with %s',jira_worklog.id,str(data))
                                    worklog_obj.write(cr, uid, woid, data)                             
                            else:
                                if tsid:
                                    weid = error_obj.search(cr, uid, [('jira_worklog_id','=',worklog_jira_id)])
                                    if not weid:
                                        err_data = {}
                                        err_data['user_id']= author_id[0]
                                        err_data['project_id'] = jira_project.project_id.id
                                        err_data['jira_issue_id'] = jira_issue.id
                                        err_data['jira_worklog_id'] = worklog_jira_id
                                        err_data['synchro_date_time'] = str(datetime.now())
                                        err_data['update_date'] = str(work_last_update)
                                        err_data['key'] = issue_fields['key']
                                        err_data['error_message'] = u'timesheet has been submitted : cannot insert worklog !' 
                                        error_obj.create(cr, uid,err_data)                                           
                                        self._logger.error('timesheet has been submitted : cannot insert worklog !')
                                    continue

                                if started_date < datetime.strptime(jira_project.project_id.date_start,'%Y-%m-%d'):
                                    #Do not log work before start of project
                                    continue
                                data = {}
                                data['jira_id'] = worklog_jira_id
                                data['jira_issue_id'] = jira_issue.jira_id
                                comment = worklog['comment'] or '/'
                                comment = comment.replace('"','_').replace('\'','_')
                                if len(comment)>127:
                                    comment = "%s..." % comment[:120]
                                data['name'] = comment
                                data['user_id'] = author_id[0]
                                data['task_id'] = jira_issue.id
                                data['date'] = str(started_date)
                                data['hours'] = float(worklog['timeSpentSeconds']) / 3600.0

                                self._logger.info('Create worklog %s',str(data))
                                woid = worklog_obj.create(cr, uid, data)
        worklog_to_delete = []
        for issue_id in issue_worklogs:
            wids = worklog_obj.search(cr, uid, [('jira_issue_id', '=', issue_id),('jira_id','not in',issue_worklogs[issue_id])]) 
            if wids:
                for worklog in worklog_obj.browse(cr, uid, wids):
                    tsid = ts_obj.search(cr, uid, [('user_id','=',worklog.user_id.id),('date_from','<=', worklog.date),('date_to','>=', worklog.date),('state','not in',['new','draft'])])
                    if tsid:
                        weid = error_obj.search(cr, uid, [('jira_worklog_id','=',worklog.jira_id)])
                        if not weid:
                            self._save_error(cr, uid, worklog, u'timesheet has been submitted : delete refused !')
                    else:
                        worklog_to_delete.append(worklog.id)
                        self._logger.info('Delete worklogs for %s : %s',issue_id,str(worklog.id))
        if worklog_to_delete:
            worklog_obj.unlink(cr, uid, worklog_to_delete)
        self._logger.info('Synchronization finished')
        return True    
 
bss_jira_project()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
