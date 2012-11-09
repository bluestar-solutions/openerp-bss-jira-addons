# -*- coding: utf-8 -*-
# #############################################################################
# 
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
# #############################################################################

from openerp.osv import osv, fields
from openerp.netsvc import logging
from datetime import datetime, timedelta

class webservice_handler(osv.osv_memory):
    _name = 'bss.webservice_handler'
    _description = 'Webservice Handler'
    _logger = logging.getLogger(_name)
            
    _columns= {
        'name': fields.char('Name', size=64),
        'last_run': fields.datetime('Last Run'),
        'active': fields.boolean('Active'),
    }
    
    _defaults= {
        'name': 'Service Handler',
        'last_run': lambda *x: fields.datetime.now,
        'active': True,
    }

    #default cron (the one created if missing)
    cron = {'active': True,
            'priority': 2,
            'interval_number': 1,
            'interval_type': 'minutes',
            'nextcall': time.strftime("%Y-%m-%d %H:%M:%S",
                                      (datetime.now()
                                       + timedelta(minutes=1)).timetuple()),  # in one minute
            'numbercall': -1,
            'doall': True,
            'model': 'bss.webservice_handler',
            'function': 'run_all',
            'args': '()',
            }

    def get_cron_id(self, cr, uid, context):
        """return the webservice cron's id. Create one if the cron does not exists """
        cron_obj = self.pool.get('ir.cron')
        # find the cron that send messages
        cron_id = cron_obj.search(cr, uid,  [('function', 'ilike', self.cron['function']),
                                             ('model', 'ilike', self.cron['model'])],
                                  context={'active_test': False})
        if cron_id:
            cron_id = cron_id[0]

        # the cron does not exists
        if not cron_id:
            self.cron['name'] = _('Webservice Handler')
            cron_id = cron_obj.create(cr, uid, self.cron, context)

        return cron_id

    def run_all(self, cr, uid, context=None):
        webservice_obj = self.pool.get('bss.webservice')
        service_ids = webservice_obj.search(cr, uid, [('active','=',True),('wait_next_minutes','>',0)], order='priority,last_run')
        for service_id in service_ids:
            service = webservice_obj.browse(cr,uid,service_id,context)
            if service.last_success == service.last_run:
                next_run =  service.last_run + timedelta(minutes=service.wait_next_minutes)
            else:
                next_run =  service.last_run + timedelta(minutes=service.wait_retry_minutes)
                
            if next_run < datetime.now():
                service.do_run(cr,uid,service_id,context)
                
        
webservice_handler()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    