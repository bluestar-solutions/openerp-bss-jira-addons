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

from openerp.osv import osv

class bss_project_task_work(osv.osv):
    _inherit = 'project.task.work'
    
    def write(self, cr, uid, ids, vals, context=None):
        # just update the record with admin if it's called by task form on unmodified entries
        if len(vals) == 1 and 'task_id' in vals:
            return super(bss_project_task_work, self).write(cr, 1, ids, vals, context)
        
        return super(bss_project_task_work, self).write(cr, uid, ids, vals, context)
    
    
bss_project_task_work()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
