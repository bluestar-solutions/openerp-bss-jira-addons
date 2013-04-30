# -*- coding: utf-8 -*-
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
from openerp.netsvc import logging
import json
from bss_webservice_handler.webservice import webservice
from datetime import datetime, date

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

    def ws_decode_write(self, cr, uid, model, content, datetime_format):
        decoded_list = json.loads(content)
        field_list = model.fields_get(cr,uid)
        self._logger.debug("List is : %s, length is %d",str(decoded_list),len(decoded_list))
        self._logger.debug("Field list is : %s, length is %d",str(field_list),len(field_list))
        if not decoded_list:
            return True
        elif len(decoded_list)==0:
            self._logger.debug("List is empty")
            return True

        for decoded in decoded_list:
            oid = model.search(cr, uid, [('jira_id', '=', decoded['id'])])
            if oid:
                jira_project = self.browse(cr, uid, oid)[0]
                if jira_project.name!=decoded['name']:
                    self._logger.debug('Update name for project %s from %s to %s',decoded['key'],jira_project.name,decoded['name'])
                    self.write(cr, uid, jira_project.id, {'name': decoded['name']})
            else:   
                data = {'jira_id': decoded['id'],
                        'key': decoded['key'],
                        'name': decoded['name']
                        }
                self._logger.debug('Create project %s',str(data))
                oid = model.create(cr, uid, data)
        return True   
    
    def ws_decode_write_worklog(self, cr, uid, model, content, datetime_format):
        decoded_list = json.loads(content)
#/jira/rest/api/2/search?jql=timeSpent%20%3E%200%20and%20updated%20%3E%20startOfDay(-1)%20ORDER%20BY%20updated%20DESC&startAt=0&maxResults=500&fields=assignee,description,summary,created,updated,duedate,priority,status,worklog,key,id,project,timeestimate,timeoriginalestimate
#        field_list = model.fields_get(cr,uid)
#        self._logger.debug("List is : %s, length is %d",str(decoded_list),len(decoded_list))
#        self._logger.debug("Field list is : %s, length is %d",str(field_list),len(field_list))
        if not decoded_list:
            return True
        elif len(decoded_list)==0:
            self._logger.debug("List is empty")
            return True
        issue_list = decoded_list['issues']
        self._logger.debug('Issue list contains %d issues (len = %d)',decoded_list['total'],len(issue_list))
        found_projects = []
        active_projects = {}
        issue_obj = self.pool.get('project.task')
        worklog_obj = self.pool.get('project.task.work')
        user_obj = self.pool.get('res.users')
        for issue_fields in issue_list:
            issue = issue_fields['fields']
            self._logger.debug('Processing issue %s',issue_fields['key'])
            project = issue['project']
            if project['key'] not in found_projects:
                oid = model.search(cr, uid, [('jira_id', '=', project['id'])])
                if oid:
                    jira_project = self.browse(cr, uid, oid)[0]
                    if jira_project.name!=project['name']:
                        self._logger.debug('Update name for project %s from %s to %s',project['key'],jira_project.name,project['name'])
                    self.write(cr, uid, jira_project.id, {'name': project['name']})
                    found_projects.append(project['key'])
                    if jira_project.project_id:
                        active_projects[project['key']] = oid
                    else:
                        self._logger.debug('Project %s is not active',project['key'])
                        continue
                else:   
                    data = {'jira_id': project['id'],
                        'key': project['key'],
                        'name': project['name']
                        }
                    self._logger.debug('Create project %s',str(data))
                    oid = model.create(cr, uid, data)
            elif project['key'] in active_projects:
                jira_project = self.browse(cr, uid, active_projects[project['key']])[0]        
            else:
                self._logger.debug('Project %s is not active',project['key'])
                continue    

            if jira_project and jira_project.project_id:
                issue_jira_id = issue_fields['id']
                ioid = issue_obj.search(cr, uid, [('jira_id', '=', issue_jira_id)])
                issue_key = issue_fields['key']
                last_update = datetime.strptime(issue['updated'].split('.')[0],'%Y-%m-%dT%H:%M:%S')
                if ioid:
                    jira_issue = issue_obj.browse(cr, uid, ioid)[0]
                    data = {}
                    if jira_issue.key != issue_key:
                        data['key'] = issue_key
                    if jira_issue.name != issue['summary']:
                        data['name'] = issue['summary']
                    prio = str(int(issue['priority']['id']) - 1)
                    if jira_issue.priority != prio:
                        data['priority'] = prio
                    if jira_issue.project_id.id != jira_project.project_id.id:
                        data['project_id'] = jira_project.project_id.id
                    oe_assignee = jira_issue.user_id.login if jira_issue.user_id else None
                    if issue['assignee'] and issue['assignee']['name'] != oe_assignee:
                        assignee_id = user_obj.search(cr, uid, [('login','=',issue['assignee']['name'])])
                        if assignee_id and len(assignee_id):
                            data['user_id'] = assignee_id[0]                        
                    elif oe_assignee:
                        data['user_id']=None
                    if issue['description'] != jira_issue.description: 
                        data['description'] = issue['description']
                    if issue['timeoriginalestimate']:
                        toe = float(issue['timeoriginalestimate']) / 3600.0
                        if toe != jira_issue.planned_hours:
                            data['planned_hours'] = toe
                    if issue['timeestimate']:
                        te = float(issue['timeestimate']) / 3600.0
                        if te != jira_issue.planned_hours:
                            data['remaining_hours'] = te
                    if issue['duedate']:
                        duedate = datetime.strptime(issue['duedate'],'%Y-%m-%d')
                        if duedate != jira_issue.date_deadline:
                            data['date_deadline'] = duedate
                    if issue['status']['id'] != jira_issue.jira_status:
                        if issue['status']['id'] in ['1','4','10000']:
                            state = 'pending'
                        elif issue['status']['id'] in ['3','10001']:
                            state = 'open'
                        elif issue['status']['id'] in ['5','6']:
                            state = 'done'
                        if state:
                            data['stage_id'] = issue_obj.stage_find(cr, uid, [], jira_project.project_id.id, [('state', '=', state)])
                            data['jira_status'] = issue['status']['id']
                    
                    if jira_issue.last_update_datetime != last_update:
                        data['last_update_datetime'] = last_update
                    if data:
                        self._logger.debug('Update issue %s with %s',issue_key,str(data))
                        issue_obj.write(cr, uid, jira_issue.id, data)                             
                else:
                    data = {
                        'jira_id':issue_jira_id,
                        'key': issue_key,
                        'name': issue['summary'],
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
                    if issue['status']['id'] in ['1','4','10000']:
                        state = 'pending'
                    elif issue['status']['id'] in ['3','10001']:
                        state = 'open'
                    elif issue['status']['id'] in ['5','6']:
                        state = 'done'
                    if state:
                        data['stage_id'] = issue_obj.stage_find(cr, uid, [], jira_project.project_id.id, [('state', '=', state)])
                    data['last_update_datetime'] = last_update
                    self._logger.debug('Create issue %s',str(data))
                    ioid = issue_obj.create(cr, uid, data)
                    jira_issue = issue_obj.browse(cr, uid, ioid)[0]
                if issue['worklog']:
                    if issue['worklogs']:
                        pass
#        for decoded in decoded_list:
#            oid = model.search(cr, uid, [('jira_id', '=', decoded['id'])])
#            if oid:
#                jira_project = self.browse(cr, uid, oid)[0]
#                if jira_project.name!=decoded['name']:
#                    self._logger.debug('Update name for project %s from %s to %s',decoded['key'],jira_project.name,decoded['name'])
#                    self.write(cr, uid, jira_project.id, {'name': decoded['name']})
#            else:   
#                data = {'jira_id': decoded['id'],
#                        'key': decoded['key'],
#                        'name': decoded['name']
#                        }
#                self._logger.debug('Create project %s',str(data))
#                oid = model.create(cr, uid, data)
        return True    
 
bss_jira_project()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
