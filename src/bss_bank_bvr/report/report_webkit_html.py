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

from openerp.addons.l10n_ch_payment_slip.report import report_webkit_html
from openerp.report import report_sxw

report_sxw.report_sxw('report.invoice_bank_bvr_webkit',
                      'account.invoice',
                      'bss_bank_bvr/report/bank_bvr.mako',
                      parser=report_webkit_html.L10nCHReportWebkitHtml)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
