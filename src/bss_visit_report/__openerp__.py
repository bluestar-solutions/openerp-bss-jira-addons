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

{
    'name': 'Visit Reports',
    'version': '1.1-1',
    "category" : 'Bluestar/Generic module',
    'complexity': "easy",
    'description': """A module for visit reports.""",
    'author': 'bluestar solutions sàrl',
    'website': 'http://www.blues2.ch',
    'depends': ['base',
                'account',
#                'procurement',
                'project',
                'project_timesheet',
                'report_webkit',
                ],
    'data': ['bss_visit_account_invoice_data.xml',
             'bss_prepaid_hours_data.xml'],
    'init_xml': ['bss_visit_account_invoice_data.xml',
                 'bss_prepaid_hours_data.xml'],
    'update_xml': ['security/ir_security.xml',
                   'bss_task_view.xml',
                   'bss_visit_report_view.xml',
                   'bss_visit_sequence.xml',
                   
                   'wizard/bss_visit_task_wizard.xml',
                   'bss_visit_travel_zone_view.xml',
                   'bss_visit_view.xml',
                   'bss_prepaid_hours_view.xml',
                   'bss_visit_account_invoice_view.xml',
                   
                   'report/visit_report.xml',
                   'report/invoice_report.xml',
                   'report/prepaid_hours_report.xml',
                   
                   'security/ir.model.access.csv',
                   'security/visit_report_security.xml'],
    'css': [],
    'js': [],
    'qweb': [], 
    'demo_xml': [],
    'test': ['test/test_bss_prepaid_hours.yml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
