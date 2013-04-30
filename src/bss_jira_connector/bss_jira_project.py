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
        if jira_project:
            issue_jira_id = issue_fields['id']
            ioid = issue_obj.search(cr, uid, [('jira_id', '=', issue_jira_id)])
            issue_key = issue_fields['key']
            if ioid:
                jira_issue = issue_obj.browse(cr, uid, ioid)[0]
                
            else:
                data = {
                        
                        }
                
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
