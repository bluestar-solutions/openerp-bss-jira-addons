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

JIRA_DISABLE_TZ = 'bss_jira_disable_timezone'

class project_configuration(osv.osv_memory):
    _inherit = 'project.config.settings'

    _columns = {
        JIRA_DISABLE_TZ: fields.boolean('Disable timezone conversion',
            help ="""This setting disables the conversion between JIRA and OpenERP datetime with
            the timezone provided by the JIRA datetime."""),
    }
    
    def get_default_bss_jira_disable_timezone(self, cr, uid, ids, context=None):
        return {
            JIRA_DISABLE_TZ: 
                self.pool.get('ir.config_parameter').get_param(cr, uid, JIRA_DISABLE_TZ, default=str(False)) == str(True)
        }
   
    def set_bss_jira_disable_timezone(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids)
        config = config and config[0]
        val = '%s' % config.bss_jira_disable_timezone or False
        self.pool.get('ir.config_parameter').set_param(cr, uid, JIRA_DISABLE_TZ, val)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
