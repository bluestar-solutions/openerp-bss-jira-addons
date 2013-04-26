# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

class bss_visit_account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    _columns = {
        'test_field': fields.boolean('Test Field')
    }
    
    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        """finalize_invoice_move_lines(cr, uid, invoice, move_lines) -> move_lines
        Hook method to be overridden in additional modules to verify and possibly alter the
        move lines to be created by an invoice, for special cases.
        :param invoice_browse: browsable record of the invoice that is generating the move lines
        :param move_lines: list of dictionaries with the account.move.lines (as for create())
        :return: the (possibly updated) final move_lines to create for this invoice
        """
        
        print '------------ TEST OVERRIDE finalize_invoice_move_lines'
        
        return move_lines

bss_visit_account_invoice()
