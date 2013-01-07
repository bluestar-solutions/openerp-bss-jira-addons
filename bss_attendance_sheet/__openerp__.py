# -*- encoding: utf-8 -*-
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
    'name': 'Timesheet',
    'version': '1.0-1',
    "category" : 'Bluestar/Generic module',
    'complexity': "easy",
    'description': """A module for Bluestar Timesheet.""",
    'author': 'bluestar solutions sàrl',
    'website': 'http://www.blues2.ch',
    'depends': ['hr_attendance',
                'hr_timesheet_sheet',
                'hr_contract',
                'hr_holidays',
                'bss_webservice_handler'],
    'init_xml': [],
    'update_xml': ['security/ir.model.access.csv',
                   
                   'data/bss.webservice.csv',
                   
                   'bss_employee_view.xml',
                   'bss_company_view.xml',
                   'bss_holidays_view.xml',
                   'bss_contract_view.xml',
                   'bss_attendance_view.xml',
                   
                   'bss_attendance_sheet_view.xml'],
    'css': ['static/src/css/style.css'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
