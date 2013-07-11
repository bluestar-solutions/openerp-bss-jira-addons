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

class bss_jira_worklog(osv.osv):
    _inherit = 'project.task.work'
    _logger = logging.getLogger('bss_jira_connector.jira_worklog')
    
    _columns = {
        'jira_id': fields.integer('JIRA id', readonly=True),
        'jira_issue_id': fields.integer('JIRA issue id', readonly=True),
    }

    _sql_constraints = [
        ('jira_id_uniq', 'unique (jira_id)', 'The JIRA id must be unique !'),
    ]

bss_jira_worklog()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: