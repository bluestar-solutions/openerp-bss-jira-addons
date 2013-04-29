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
			  font-family: DejaVu, sans-serif;
			  font-size: 8pt;
			  line-height: 1.4;
			  margin: 0;
			  margin-left: 5mm;
			  padding: 0;
			  height: 100%;
			  width: 100%;
			}
			.page {
			  margin: 0;
			  padding: 0;
			  width: 200mm;
			  height: 282mm;
			  page-break-after: always;
			  page-break-inside: avoid;
			}
			#header {
			  margin-left: 3mm;
			  font-size: 7pt;
			}
			#content {
			  width: 100%;
			}
			#footer {
			  width: 100%;
			  position: relative;
			  top: 0;
			  left: 0;
			  font-size: 0.8em;
			}
			
			#corporate_text {
			  font-size: 0.8em;
			}
			#header img {
			  width: 55mm;
			  margin-left: -8.5mm;
			}
			.draft {
			  position: absolute;
			  top: 117.5mm;
			  left: 20mm;
			  color: #FCC;
			  z-index: -10;
			  font-size: 108pt;
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
			  font-weight: bold;
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
			  font-weight: bold;
			  border-top: thin solid black;
			  text-transform: uppercase;
			  font-size: 1.1em;
			}
			tr.total_decompte {
			  font-weight: bold;
			  border: thin solid black;
			  text-transform: uppercase;
			}
			
			#decompte tr {
			  border-bottom: thin solid gray;
			}
			#decompte tr:nth-child(even) {
			  background-color: #DDD;
			}
			.landscape {
			  -webkit-transform: rotate(-90deg);
			  position: relative;
			  width: 280mm;
			  top: 85mm;
			  left: -80mm;
     			}
		</style>
	</head>

	<body>
		% for invoice in objects:
		% if invoice.state == 'draft':
		<div class="draft">Brouillon</div>
		% endif
		<div class="page">
			<div id="header">
				${helper.embed_logo_by_name('bss_header_logo')|n}
				<div class="corporate_text">
					${invoice.company_id.name}<br/>
					${invoice.company_id.street}<br/>
					${invoice.company_id.zip} ${invoice.company_id.city}<br/>
					${invoice.company_id.phone}<br/>
					N° TVA ${invoice.company_id.vat}
				</div>
			</div>
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
							<td width="90%">${invoice.nref}</td>
						</tr>
						<tr>
							<td>V / Référence : </td>
							<td>${invoice.vref}</td>
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
							
								<div style="clear:both;">${invoice.payment_term.name}</div>
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
			<div id="footer">
				<table>
					<tr>
						<td>Numéro de compte :</td><td>${invoice.company_id.bank_ids[0].acc_number}</td>
						<td>Clearing :</td><td>766</td>
						<td>Bénéficiaire :</td><td rowspan="3">${invoice.company_id.name}<br/>${invoice.company_id.street}<br/>${invoice.company_id.zip} ${invoice.company_id.city}<br/>${invoice.company_id.phone}</td>
					</tr>
					<tr>
						<td rowspan="2">Banques :</td><td rowspan="2" style="white-space:normal;">${invoice.company_id.bank_ids[0].bank_name}<br/>${invoice.company_id.bank_ids[0].bank.zip} ${invoice.company_id.bank_ids[0].bank.city}</td>
						<td>SWIFT :</td><td>${invoice.company_id.bank_ids[0].bank_bic}</td>
					</tr>
					<tr>
						<td>IBAN :</td>
						<td>
						% for bank in invoice.company_id.bank_ids:
						% if bank.state == 'iban':
						${bank.acc_number}
						% endif
						% endfor
						</td>
					</tr>
				</table>
			</div>
		</div>
		% if invoice.print_details:
		<div class="page">
			<table class="landscape">
				<thead>
					<tr>
						<th>Client :</th>
						<td colspan="4">${invoice.partner_id.name}</td>
					</tr>
					<tr>
						<td colspan="5">&nbsp;</td>
					</tr>
					<tr>
						<th>Date</th>
						<th>Temps</th>
						<th>%</th>
						<th width="100%">Travail effectué</th>
						<th>Réalisé par</th>
					</tr>
				</thead>
				<tbody id="decompte">
					<%
						related_lines_ids = invoice._get_related_lines()
						htot = 0
					%>
					% for rel_line in related_lines_ids:
					<% htot += (1.0-rel_line.to_invoice.factor)*rel_line.unit_amount %>
					<tr>
						<td>${datetime.strptime(rel_line.date,'%Y-%m-%d').strftime('%d.%m.%Y')}</td>
						<td class="number">${"%.2f" % rel_line.unit_amount}</td>
						<td>${rel_line.to_invoice.customer_name}</td>
						<td style="white-space:normal;">${rel_line.name}</td>
						<td>${rel_line.user_id.name}</td>
					</tr>
					% endfor
				</tbody>
				<tfoot>
					<tr>
						<td colspan="5">&nbsp;</td>
					</tr>
					<tr>
						<td colspan="2">
							<table width="100%">
								<tr class="total_decompte">
									<td>Total</td>
									<td class="number">${htot}</td>
								</tr>
							</table>
						</td>
						<td colspan="3">&nbsp;</td>
					</tr>
				</tfoot>
			</table>
		</div>
		% endif
		% endfor
	</body>
</html>
