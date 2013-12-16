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

class bss_jira_issue(osv.osv):
    _inherit = 'project.task'
    _logger = logging.getLogger('bss_jira_connector.jira_issue')
    
    _columns = {
        'jira_id': fields.integer('JIRA id', readonly=True),
        'key': fields.char('JIRA key', size=256, readonly=True),
        'last_update_datetime': fields.datetime('Last update', readonly=True),
        'jira_status': fields.selection([('1','Open'),('3','In progress'),('4','Reopened'),('5','Resolved'),('6','Closed'),('10000','In test'),('10001','Need info')],'JIRA status', readonly=True),
    }
    
    def init(self, cr):
        cr.execute("SELECT * FROM pg_constraint WHERE conname = 'project_task_jira_id_uniq';")
        if len(cr.fetchall()):
            cr.execute("ALTER TABLE project_task DROP CONSTRAINT project_task_jira_id_uniq;")
            
        cr.execute("SELECT * FROM pg_constraint WHERE conname = 'project_task_key_uniq';")
        if len(cr.fetchall()):
            cr.execute("ALTER TABLE project_task DROP CONSTRAINT project_task_key_uniq;")
  
bss_jira_issue()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
