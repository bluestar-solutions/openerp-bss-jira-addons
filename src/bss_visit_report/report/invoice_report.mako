<%
	import locale
	from datetime import date, datetime
	locale.setlocale(locale.LC_ALL, '')
%>
<!doctype html>
<html>
	<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
		<style type="text/css">
		html, body {
		  font-family: Arial, sans-serif;
		  font-size: 8pt;
		  line-height: 1.4;
		  margin: 0;
		  margin-left: 6mm;
		  padding: 0;
		  height: 100%;
		}
		#content {
		  width: 100%;
		  height: 200mm;
		  margin-left: -10px;
		  position: relative;
		}
		
		.draft {
		  position: absolute;
		  top: 72.5mm;
		  left: 25mm;
		  color: #FCC;
		  z-index: -10;
		  font-size: 108pt;
		  text-align: center;
		  -webkit-transform: rotate(-54deg) scalex(1.5);
		}
		
		#customer_address {
		  float: right;
		  margin-right: 10mm;
		}
		#invoice_head {
		  width: 40%;
		}
		#invoice_foot {
		  border-top: thin solid black;
		}
		#invoice_foot_total {
		  width: 35%;
		  float: right;
		}
		#invoice_foot_tva {
		  width: 60%;
		  float: left;
		}
		table {
		  width: 100%;
		  border-collapse: collapse;
		}
		th {
		  font-weight: bolder;
		  border: thin solid black;
		  white-space: nowrap;
		  text-align: left;
		  padding: 2px 10px 3px 10px;
		}
		td {
		  vertical-align: top;
		  padding: 2px 10px;
		  white-space: nowrap;
		}
		#invoice_foot_total td {
		  padding: 0px;
		}
		td.number, th.head_num {
		  text-align: right;
		}
		tr.total {
		  font-weight: bolder;
		  border-top: thin solid black;
		  text-transform: uppercase;
		  font-size: 1.1em;
		}
		</style>
	</head>
	<body>
		% for invoice in objects:
		% if invoice.state == 'draft':
		<div class="draft">Brouillon</div>
		% endif
		<div id="content">
			<!-- Address of recipient -->
			<div id="customer_address">
				${invoice.partner_id.name}<br/>
				${invoice.partner_id.street}<br/>
				${invoice.partner_id.country_id.code} - ${invoice.partner_id.zip} ${invoice.partner_id.city}
			</div>
			<div style="clear:both;">&nbsp;</div>
			
			<!-- Invoice infos -->
			<table id="invoice_head">
				<thead>
					<tr>
						<th colspan="2">Facture N° ${invoice.number}</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td>N / Référence : </td>
						<td width="90%">${invoice.nref or 'n/a'}</td>
					</tr>
					<tr>
						<td>V / Référence : </td>
						<td>${invoice.vref or 'n/a'}</td>
					</tr>
					<tr>
						<td>Date : </td>
						<td>${invoice.date_invoice}</td>
					</tr>
					<tr>
						<td colspan="2"></td>
					</tr>
				</tbody>
			</table>
			
			<!-- Invoice lines -->
			<table>
				<thead>
					<tr>
						<th width="40%">Description</th>
						<th>Quantité</th>
						<th class="head_num">Prix unitaire</th>
						<th>TVA</th>
						<th class="head_num">Montant</th>
					</tr>
				</thead>
				<tbody>
					% for line in invoice.invoice_line:
					<tr>
						<td>
							% if line.product_id.product_tmpl_id.type == "service":
								${line.product_id.name}<br/>
							% endif
							${line.name}
						</td>
						<td>${line.quantity} ${line.uos_id.name}</td>
						<td class="number">${locale.format('%.2f', line.price_unit, 1)}</td>
						<td>${"%.2f%%*" % (line.invoice_line_tax_id[0].amount*100)}</td>
						<td class="number">${locale.format('%.2f', line.price_subtotal, 1)}</td>
					</tr>
					% endfor
				
					<tr>
						<td colspan="5" id="invoice_foot">
							<div id="invoice_foot_tva">
								TVA exclue* 8.00% / CHF ${locale.format('%.2f', invoice.amount_untaxed, 1)}: CHF ${locale.format('%.2f', invoice.amount_tax, 1)}
							</div>

							<table id="invoice_foot_total">
								<tr>
									<td>Total net</td>
									<td class="number">${locale.format('%.2f', invoice.amount_untaxed, 1)}</td>
								</tr>
								<tr>
									<td>TVA</td>
									<td class="number">${locale.format('%.2f', invoice.amount_tax, 1)}</td>
								</tr>
								<tr class="total">
									<td>Total</td>
									<td class="number">${locale.format('%.2f', invoice.amount_total, 1)}</td>
								</tr>
							</table>
						
							<div style="clear:both;">Conditions de paiement : ${invoice.payment_term.name or ''}</div>
							<br/><br/>
							<div>
								<p>
									Nous vous remercions vivement de votre confiance.<br/><br/>
									Meilleures salutations,<br/><br/>
									votre team bluestar solutions
								</p>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>
		% endfor
	</body>
</html>
