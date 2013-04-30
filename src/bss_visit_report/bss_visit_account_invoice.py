# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import time
from datetime import timedelta
from openerp.netsvc import logging

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _logger = logging.getLogger()
    
    def _get_related_lines_ids(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        aal_object = self.pool.get('account.analytic.line')
        
        for invoice in self.browse(cr, uid, ids, context):
            res[invoice.id] = aal_object.search(cr, uid, [('invoice_id','=',invoice.id)], order='date')
            
        return res
    
    _columns = {
        'nref' : fields.char(u'N / Référence', size=64),
        'vref' : fields.char(u'V / Référence', size=64),
        'print_details' : fields.boolean(u'Imprimer le détail'),
        'related_lines' : fields.function(_get_related_lines_ids, u'Détails', obj="account.analytic.line", type="one2many", method=True, store=False)
    }
    
    def _get_related_lines(self, cr, uid, ids, context=None):
        aal_object = self.pool.get('account.analytic.line')
        invoice_id = self.browse(cr, uid, ids)[0].id
        aal_ids = aal_object.search(cr, uid, [('invoice_id','=',invoice_id)], order='date')
        return aal_object.browse(cr, uid, aal_ids)

account_invoice()

class account_analytic_line(osv.osv):
    _inherit = 'account.analytic.line'
    
    def _get_employee_for_user(self, cr, uid, ids, context=None):
        hre_pool = self.pool.get('hr.employee')
        user_id = self.browse(cr, uid, ids)[0].user_id
        employee_id = hre_pool.search(cr, uid, [('user_id','=',user_id.id)], context)
        return hre_pool.browse(cr, uid, employee_id)[0]
    
    def invoice_cost_create(self, cr, uid, ids, data=None, context=None):
        analytic_account_obj = self.pool.get('account.analytic.account')
        account_payment_term_obj = self.pool.get('account.payment.term')
        invoice_obj = self.pool.get('account.invoice')
        product_obj = self.pool.get('product.product')
        invoice_factor_obj = self.pool.get('hr_timesheet_invoice.factor')
        fiscal_pos_obj = self.pool.get('account.fiscal.position')
        product_uom_obj = self.pool.get('product.uom')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoices = []
        if context is None:
            context = {}
        if data is None:
            data = {}

        journal_types = {}
        for line in self.pool.get('account.analytic.line').browse(cr, uid, ids, context=context):
            if line.journal_id.type not in journal_types:
                journal_types[line.journal_id.type] = set()
            journal_types[line.journal_id.type].add(line.account_id.id)
        for journal_type, account_ids in journal_types.items():
            for account in analytic_account_obj.browse(cr, uid, list(account_ids), context=context):
                partner = account.partner_id
                if (not partner) or not (account.pricelist_id):
                    raise osv.except_osv(_('Analytic Account incomplete !'),
                            _('Contract incomplete. Please fill in the Customer and Pricelist fields.'))

                date_due = False
                if partner.property_payment_term:
                    pterm_list= account_payment_term_obj.compute(cr, uid,
                            partner.property_payment_term.id, value=1,
                            date_ref=time.strftime('%Y-%m-%d'))
                    if pterm_list:
                        pterm_list = [line[0] for line in pterm_list]
                        pterm_list.sort()
                        date_due = pterm_list[-1]

                curr_invoice = {
                    'name': time.strftime('%d/%m/%Y') + ' - '+account.name,
                    'partner_id': account.partner_id.id,
                    'company_id': account.company_id.id,
                    'payment_term': partner.property_payment_term.id or False,
                    'account_id': partner.property_account_receivable.id,
                    'currency_id': account.pricelist_id.currency_id.id,
                    'date_due': date_due,
                    'fiscal_position': account.partner_id.property_account_position.id,
                    'date_invoice' : time.strftime('%Y-%m-%d'),
                }

                context2 = context.copy()
                context2['lang'] = partner.lang
                # set company_id in context, so the correct default journal will be selected
                context2['force_company'] = curr_invoice['company_id']
                # set force_company in context so the correct product properties are selected (eg. income account)
                context2['company_id'] = curr_invoice['company_id']

                last_invoice = invoice_obj.create(cr, uid, curr_invoice, context=context2)
                invoices.append(last_invoice)
                
                cr.execute("""SELECT sum(unit_amount) as amount, to_invoice, product_id, product_uom_id
                                FROM account_analytic_line as line LEFT JOIN account_analytic_journal journal ON (line.journal_id = journal.id)
                                WHERE account_id = %s
                                    AND line.id IN %s AND journal.type = %s AND to_invoice IS NOT NULL
                                GROUP BY to_invoice, product_id, product_uom_id
                            """, (account.id, tuple(ids), journal_type))
                
                for invoice_details in cr.dictfetchall():
                    if data.get('product'):
                        invoice_details['product_id'] = data['product'][0]
                    factor = invoice_factor_obj.browse(cr, uid, invoice_details['to_invoice'], context=context2)
                    invoice = invoice_obj.browse(cr, uid, last_invoice, context)
                    details = []
                    details.append(u"Selon décompte du %s" % (time.strftime('%d.%m.%Y',time.strptime(invoice.date_invoice,'%Y-%m-%d'))))
                    
                    product = product_obj.browse(cr, uid, invoice_details['product_id'], context=context2)
                    if not product:
                        raise osv.except_osv(_('Error!'), _('There is no product defined. Please select one or force the product through the wizard.'))
                    
                    ctx =  context.copy()
                    ctx.update({'uom':invoice_details['product_uom_id']})
                    price = self._get_invoice_price(cr, uid, account, invoice_details['product_id'], None, invoice_details['amount'], ctx)
                    
                    general_account = product.property_account_income or product.categ_id.property_account_income_categ
                    if not general_account:
                        raise osv.except_osv(_("Configuration Error!"), _("Please define income account for product '%s'.") % product.name)
                    taxes = product.taxes_id or general_account.tax_ids
                    tax = fiscal_pos_obj.map_tax(cr, uid, account.partner_id.property_account_position, taxes)
                    
                    curr_line = {
                        'price_unit': price,
                        'quantity': invoice_details['amount'],
                        'discount': factor.factor,
                        'invoice_line_tax_id': [(6,0,tax )],
                        'invoice_id': last_invoice,
                        'name': "\n".join(details),
                        'product_id': invoice_details['product_id'],
                        'invoice_line_tax_id': [(6,0,tax)],
                        'uos_id': invoice_details['product_uom_id'],
                        'account_id': general_account.id,
                        'account_analytic_id': account.id,
                    }
                    
                    invoice_line_obj.create(cr, uid, curr_line, context=context)
                    cr.execute("update account_analytic_line set invoice_id=%s WHERE account_id = %s and id IN %s", (last_invoice, account.id, tuple(ids)))
                
                invoice_obj.button_reset_taxes(cr, uid, [last_invoice], context)
    
        return invoices
    
account_analytic_line()
