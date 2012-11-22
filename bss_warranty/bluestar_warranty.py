# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://www.openerp.com>).
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
"""
Module to handle publisher warranty contracts as well as notifications from
OpenERP.
"""

import logging
import smtplib
from tools.translate import _
from openerp.tools import ustr
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from osv import osv, fields

_logger = logging.getLogger(__name__)

class bluestar_warranty(osv.osv):
    _inherit = "publisher_warranty.contract"

    def send(self, cr, uid, tb, explanations, remarks=None, issue_name=None):
        """ Method called by the client to send a problem to the publisher warranty server. """
        
        if not explanations:
            explanations = ""
        if not remarks:
            remarks = ""
        if not issue_name:
            issue_name = ""

        valid_contracts = self._get_valid_contracts(cr, uid)
        valid_contract = valid_contracts[0]

        try:
            origin = 'client'
            config_pool = self.pool.get('ir.config_parameter')
            dbuuid = config_pool.get_param(cr, uid, 'database.uuid')
            db_create_date = config_pool.get_param(cr, uid, 'database.create_date')
            user = self.pool.get("res.users").browse(cr, uid, uid)
            user_name = user.name
            email = user.user_email

            s = smtplib.SMTP(config_pool.get_param(cr, uid, 'smtp.url'), int(config_pool.get_param(cr, uid, 'smtp.port')))
            s.set_debuglevel(1)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(config_pool.get_param(cr, uid, 'smtp.login'), config_pool.get_param(cr, uid, 'smtp.password'))
    
            mail = MIMEMultipart()
            mail['Subject'] = '[%s] OpenERP error report' % user.company_id.name
            mail['From'] = config_pool.get_param(cr, uid, 'error_report.mail_from')
            mail['To'] = config_pool.get_param(cr, uid, 'error_report.mail_to')
            
            body = u''
            body += ' * Contract :       ' + str(valid_contract.name) + '\n'
            body += ' * DB name :        ' + str(cr.dbname) + '\n'
            body += ' * DB uuid :        ' + str(dbuuid) + '\n'
            body += ' * DB create date : ' + str(db_create_date) + '\n'
            body += ' * User name :      ' + str(user_name) + '\n'
            body += ' * User email :     ' + str(email) + '\n'
            body += ' * Origin :         ' + str(origin) + '\n'
            body += ' * Issue name :\n' + issue_name + '\n'
            body += ' * Explanations :\n' + explanations + '\n'
            body += ' * Remarks :\n' + remarks + '\n'
            body += '\n'
            body += "############################################\n"
            body += "##### Type :    " + tb['type'] + "\n"
            body += "##### Message : " + tb['fault_code'] + "\n"
            body += "##### Debug :\n" + tb['debug'] + "\n"
                
            email_body_utf8 = ustr(body).encode('utf-8')
            text = MIMEText(email_body_utf8, _subtype='plain', _charset='utf-8')
            mail.attach(text)

            s.sendmail(mail['From'], mail['To'], mail.as_string())
        
            s.quit()

        except osv.except_osv:
            raise
        except Exception:
            _logger.warning("Error sending problem report", exc_info=1)
            raise osv.except_osv(_("Error"),
                                  _("Error during communication with the publisher warranty server."))

        return True

bluestar_warranty()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
