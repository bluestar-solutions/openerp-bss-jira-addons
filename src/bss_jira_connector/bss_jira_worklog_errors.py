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

class bss_jira_worklog_errors(osv.osv):
    _name = 'bss_jira_connector.jira_worklog_errors'
    _logger = logging.getLogger(_name)
    
    _columns = {
        'user_id': fields.many2one('res.users', 'User'),
        'project_id': fields.many2one('project.project', 'Project'),
        'jira_issue_id': fields.integer('JIRA issue id'),
        'key': fields.char('JIRA key', size=256),
        'jira_worklog_id': fields.integer('JIRA worklog id'),
        'synchro_date_time': fields.datetime('Error date'),
        'update_date': fields.datetime('Update date'),
        'error_message': fields.text('Error message'),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True, 
                 }
    _order = "synchro_date_time desc"
bss_jira_worklog_errors()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: