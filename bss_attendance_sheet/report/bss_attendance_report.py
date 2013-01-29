# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
from openerp import tools

class bss_attendance_report(osv.osv):
    _name = "bss_attendance.attendance_report"
    _auto = False
    _rec_name = 'date'
    
    _columns = {
        'date': fields.date('Date')
    } 
    _order = 'date desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'bss_attendance_report')
        cr.execute("""create or replace view bss_attendance_report as (
            select
                sum(1) over (order by ds.date asc) id,
                ds.date date
            from
                (select current_date + s.a as date from generate_series(0,(select min(entry_date) - current_date from alfenimmo_account_entry),-1) as s(a)) ds
                left join alfenimmo_account_entry ae ON ae.entry_date = ds.date
            group by
                ds.date
            order by
                ds.date desc
            )""")
        
bss_attendance_report()
