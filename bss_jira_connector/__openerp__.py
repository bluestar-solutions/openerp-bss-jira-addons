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

{
    'name': 'JIRA connector',
    'version': 'master',
    "category" : 'Bluestar/Generic module',
    'complexity': "easy",
    'description': """
A connector to fetch worklogs from Atlassian JIRA into OpenERP projects tasks
=============================================================================

This module uses bss_webservice_handler (https://launchpad.net/bss-webservice-addons) to fetch worklogs from Atlassian JIRA using its REST interface. 
Once a JIRA project (new object) is matched to an OpenERP project, all JIRA issues are copied as tasks on OpenERP 
side and all JIRA worklogs become analytic lines in OpenERP if a corresponding employee has been defined in the HR module.

Configure the JIRA webservice
-----------------------------

Create a webservice in Settings/Webservices with these settings :

* Name : jira worklog
* Type : (depend of your service)
* Webservice Protocol : (http/https)
* Webservice Host : your.jira.host
* Webservice Port : (your jira webservices port)
* Webservice Path : /jira/rest/api/2/search?jql=updated%20%3E%20startOfDay(-1)%20ORDER%20BY%20updated%20DESC&startAt=0&maxResults=1500&fields=assignee,description,summary,created,updated,duedate,priority,status,worklog,key,id,project,timeestimate,timeoriginalestimate
* Push Filter : (leave it empty)
* Get DB Key : (leave it empty)
* Date & Time Format : ISO 8601
* Soft log limit : 0
* Error log limit : 0.00

* HTTP Authentication : Basic
* HTTP Login : a-jira-user
* HTTP Password : a-jira-password

* Active : True

* Model Name : bss_jira_connector.jira_project
* Before Method Name : (leave it empty)
* After Method Name : (leave it empty)
* Encode Method Name : (leave it empty)
* Decode Method Name : ws_decode_write_worklog

You can manually execute webservice once with startOfMonth(-x) with x the number of month (in Webservice Path field) to collect before now. 
This will collect all JIRA projects with worklogs in this period.

Import worklogs into OpenERP projects
-------------------------------------

* Check the REST plugin is enabled in JIRA settings.
* Link JIRA projects with OpenERP projects in the Project > JIRA Projects menu.
* Fill in contract infos and project start date (no worklog before this date will be collected).
* Manually execute webservice once with startOfMonth(-x) to collect worklogs.
* Update webservice to start automatically with startOfDay(-1) and update waiting time.
    """,
    'author': 'Bluestar Solutions Sàrl',
    'website': 'http://www.blues2.ch',
    'depends': ['base',
                'project',
                'project_timesheet',
                'bss_webservice_handler',
                'procurement',
                ],
    'data': [],
    'init_xml': [],
    'update_xml': ['security/ir_security.xml',
                   
                   'security/ir.model.access.csv',
                   'bss_jira_project_view.xml',
                   
                   'wizard/bss_jira_config_wizard_view.xml',
                   
                   'bss_jira_config_view.xml',
                   ],
    'css': [],
    'js': [],
    'qweb': [], 
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images' : ['images/jira_project_edit.png',],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
