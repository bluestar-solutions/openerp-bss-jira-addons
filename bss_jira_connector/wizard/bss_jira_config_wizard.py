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

PROTOCOLS = [('http','Http'),('https','Https')]
HTTP_AUTH_TYPE = [('NONE', 'None'), ('BASIC', 'Basic')]

class bss_jira_config_wizard(osv.osv_memory):
    _name = 'bss_jira_connector.jira_config_wizard'
    _description = "Jira connector Configuration"
    _inherit = 'res.config'
    _logger = logging.getLogger(_name)
    
    _columns = {
        'protocol' : fields.selection(PROTOCOLS, 'Protocol'),
        'hostname' : fields.char('Hostname', required=True),
        'hostport' : fields.integer('Port', required=True),
        'pathtojira' : fields.char('Path to Jira (without leading \'/\')', required=True),
        'authtype' : fields.selection(HTTP_AUTH_TYPE, 'Authentication type'),
        'username' : fields.char('Username'),
        'password' : fields.char('Password'),
        'interval' : fields.integer('Time between synchronization (minutes)', required=True),
        'maxresults' : fields.integer('Max number of results', required=True),
        'startofday' : fields.integer('Number of days to collect logs before now', required=True)
        }
    
    _defaults = {
        'protocol' : 'http',
        'hostport' : 80,
        'interval' : 5,
        'maxresults' : 1500,
        'startofday' : 1,
        'pathtojira' : '/jira',
        'authtype' : 'BASIC',
        }
    
    def execute(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids, context)[0]
        
        ws = self.pool.get('bss.webservice')
        
        values = {
                'name' : 'Jira webservice',
                'active' : True,
                'wait_next_minutes' : config.interval,
                'service_type' : 'GET',
                'ws_protocol' : config.protocol,
                'ws_host' : config.hostname,
                'ws_port' : config.hostport,
                'ws_path' : config.pathtojira + "/rest/api/2/search?jql=updated%20%3E%20startOfDay(-" + str(config.startofday) + ")%20ORDER%20BY%20updated%20DESC&startAt=0&maxResults=" + str(config.maxresults) + "&fields=assignee,description,summary,created,updated,duedate,priority,status,worklog,key,id,project,timeestimate,timeoriginalestimate",
                'http_auth_type' : config.authtype,
                'http_auth_login' : '' if config.authtype == 'NONE' else config.username,
                'http_auth_password' : '' if config.authtype == 'NONE' else config.password,
                'model_name' : 'bss_jira_connector.jira_project',
                'decode_method_name' : 'ws_decode_write_worklog',
                'datetime_format' : 'ISO8601',
                'call_limit_in_error' : 0.0
                }
        
        ws_ids = ws.search(cr, uid, [('name','=','Jira webservice')])
        
        if len(ws_ids) == 0:
            ws.create(cr, uid, values)
        else:
            ws.write(cr, uid, ws_ids[0], values)
        
        return {'type' : 'ir.actions.act_window_close'}
    
bss_jira_config_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
