# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2013 Bluestar Solutions Sàrl (<http://www.blues2.ch>).
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
    "name": "Webservice Handler",
    'version': 'master',
    "category" : "Bluestar/Addons/WS",
    "complexity": "easy",
    "description": """A module to synchronize datas with external webservices. """,
    "author": "Bluestar Solutions Sàrl",
    "website": "http://www.blues2.ch",
    'depends': [],
    'init_xml': [],
    'update_xml': ['module_data.xml',
                   
                   'security/ws_handler_security.xml',
                   'security/ir.model.access.csv',
                   
                   'webservice_handler.xml'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
