# -*- coding: utf-8 -*-
# #############################################################################
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
# #############################################################################
import time

from openerp.osv import osv, fields
from openerp.netsvc import logging
from openerp.tools.translate import _
from datetime import datetime, timedelta

class webservice_handler(osv.osv_memory):
    _name = 'bss.webservice_handler'
    _description = 'Webservice Handler'
    
    _is_init = False
            
    _columns= {
        'name': fields.char('Name', size=64),
        'service_id': fields.many2one('bss.webservice', 'Webservice'),
        'last_run': fields.datetime('Last Run'),
        'active': fields.boolean('Active'),
    }
    
    _defaults= {
        'name': 'Service Handler',
        'last_run': lambda *x: datetime.now(),
        'active': True,
    }

    #default cron (the one created if missing)
    cron = {'active': True,
            'priority': 2,
            'interval_number': 1,
            'interval_type': 'minutes',
            'nextcall': time.strftime("%Y-%m-%d %H:%M:%S",
                                      datetime.now().timetuple()),  # in one minute
            'numbercall': -1,
            'doall': False,
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
        _logger = logging.getLogger('bss.webservice_handler')
        _logger.info('Started webservice handler')
        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug('Webservices started at %s', datetime.now())
        webservice_obj = self.pool.get('bss.webservice')
        service_ids = webservice_obj.search(cr, uid, [('active','=',True),('wait_next_minutes','>',0)], order='priority,last_run')
        _logger.debug('service ids = %s ', str(service_ids))
        services = webservice_obj.browse(cr,uid,service_ids,context)

        for service in services:           
#            _logger.debug('Service is %s', str(service))
            if not self._is_init:
                webservice_obj.write(cr, uid, service.id, {'is_running': False}, context)
                cr.commit()
            
            if service.last_run:
                _logger.debug('last_run is %s', str(service.last_run))
                if service.last_success and service.last_success == service.last_run:
                    next_run =  datetime.strptime(service.last_run,"%Y-%m-%d %H:%M:%S.%f") + timedelta(minutes=service.wait_next_minutes)
                else:
                    next_run =  datetime.strptime(service.last_run,"%Y-%m-%d %H:%M:%S.%f") + timedelta(minutes=service.wait_retry_minutes)
            else:
                next_run = datetime(2000,1,1)
            _logger.info('Service %s next run at %s',service.name, next_run.strftime("%Y-%m-%d %H:%M:%S"))
            if next_run < datetime.now():
                _logger.debug('Context is %s', str(context))
                webservice_obj.do_run(cr, uid, service.id, context)
        self._is_init = True
        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug('Webservices ended at %s', datetime.now())
        _logger.info('Ended webservice handler')
                
        
webservice_handler()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
