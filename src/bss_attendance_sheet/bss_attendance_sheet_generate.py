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

from openerp.osv import osv, fields
from datetime import datetime, timedelta
from bss_utils.dateutils import orm_date

class bss_attendance_sheet_generate(osv.osv_memory):
    
    _name = 'bss.attendance_sheet.generate'
    _inherit = 'res.config'
    _description = 'Attendance Sheet Generation'
    
    
    def default_get(self, cr, uid, fields, context=None):            
        res = dict()
        
        today = datetime.today().date()
        res['date_start'] = today.replace(day=1, month=1).isoformat()
        res['date_end'] = today.isoformat()

        return res    

    _columns = {
        'date_start': fields.date('Date Start', required=True),
        'date_end': fields.date('Date End', required=True),
    }   
    
    def execute(self, cr, uid, ids, context=None):
        sheet_ojb = self.pool.get('bss_attendance_sheet.sheet')
        
        params = self.browse(cr, uid, ids, context)[0]
        
        date_start = orm_date(params.date_start)
        date_end = orm_date(params.date_end)
        nb_days = (date_end - date_start).days
        for i in range(nb_days+1):
            sheet_ojb._check_all_sheet(cr, uid, (date_start + timedelta(days=i)).isoformat(), context)

        
bss_attendance_sheet_generate()





