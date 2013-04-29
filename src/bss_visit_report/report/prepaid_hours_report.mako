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
			
			#content {
			  width: 100%;
			}
			#header {
			  margin-left: 3mm;
			  font-size: 7pt;
			}
			#header img {
			  width: 55mm;
			  margin-left: -8.5mm;
			}
			#customer_address {
			  float: right;
			  margin-right: 10mm;
			}
			
			#report_head {
			  width: 40%;
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
			td.number, th.head_num {
			  text-align: right;
			  border-left: thin solid gray;
			}
			tr.date {
			  border-bottom: thin solid black;
			}
			
			tr#solde_before {
			  border-bottom: thin solid gray;
			}
			tr#solde_after {
			  border-top: thin solid gray;
			}
			tr#solde_before, tr#solde_after {
			  font-weight: bold;
			}
			#solde_before td, #solde_after td {
			  text-align: right;
			}
			#report_content {
			  table-layout: fixed;
			}
			#report_content tbody tr:nth-child(even) {
			  background-color: #DDD;
			}
		</style>
	</head>

	<body>
		% for prepaid_hours in objects:
		<%
			date_from = datetime.strptime(prepaid_hours._context['date_from'], '%Y-%m-%d')
			date_to = datetime.strptime(prepaid_hours._context['date_to'], '%Y-%m-%d')
			tot_bef = 0.0
			tot_add = 0.0
			tot_val = 0.0
			for ppt in reversed(prepaid_hours.related_hours):
				if datetime.strptime(ppt.processed_date, '%Y-%m-%d') < date_from:
					if ppt.type == 'validated':
						tot_bef -= ppt.amount / 60.0
					elif ppt.type == 'add':
						tot_bef += ppt.amount / 60.0
		%>
		<div class="page">
			<div id="header">
				${helper.embed_logo_by_name('bss_header_logo')|n}
				<div class="corporate_text">
					${prepaid_hours.contract_id.company_id.name}<br/>
					${prepaid_hours.contract_id.company_id.street}<br/>
					${prepaid_hours.contract_id.company_id.zip} ${prepaid_hours.contract_id.company_id.city}<br/>
					${prepaid_hours.contract_id.company_id.phone}<br/>
					N° TVA ${prepaid_hours.contract_id.company_id.vat}
				</div>
			</div>
			<div id="content">
				<div id="customer_address">
					${prepaid_hours.contract_id.partner_id.name}<br/>
					${prepaid_hours.contract_id.partner_id.street}<br/>
					${prepaid_hours.contract_id.partner_id.country_id.code} - ${prepaid_hours.contract_id.partner_id.zip} ${prepaid_hours.contract_id.partner_id.city}
				</div>
				<div style="clear:both;">&nbsp;</div>
				
				<table id="report_head">
					<thead>
						<tr>
							<th colspan="2">État du carnet d'heures</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>Contrat :</td>
							<td>${prepaid_hours.contract_id.name}</td>
						</tr>
						<tr class="date">
							<td>Date :</td>
							<td>${date.today().strftime('%d.%m.%Y')}</td>
						</tr>
						<tr>
							<td>Du :</td>
							<td>${date_from.strftime('%d.%m.%Y')}</td>
						</tr>
						<tr>
							<td>Au :</td>
							<td>${date_to.strftime('%d.%m.%Y')}</td>
						</tr>
					</tbody>
				</table>
				<table id="report_content">
					<thead>
						<tr>
							<th width="10%">Date</th>
							<th width="7%">Code</th>
							<th width="53%">Description</th>
							<th width="10%">Débit</th>
							<th width="10%">Crédit</th>
							<th width="10%">Solde</th>
						</tr>
						<tr id="solde_before">
							<td colspan="3">&nbsp;</td>
							<td colspan="2">Solde au ${date_from.strftime('%d.%m.%Y')}</td>
							<td>${"%.2f" % tot_bef}</td>
						</tr>
					</thead>
					<tbody>
						% for ppt in reversed(prepaid_hours.related_hours):
						<% ppt_pd = datetime.strptime(ppt.processed_date, '%Y-%m-%d') %>
						% if ppt.type != 'pending' and ppt_pd >= date_from and ppt_pd <= date_to:
						<tr>
							<td>${ppt.processed_date}</td>
							<td>
								% if ppt.type == 'validated':
								${ppt.related_timesheet.user_id.employee_ids[0].initials}
								% else:
								&nbsp;
								% endif
							</td>
							<td>
								% if ppt.type == 'add':
								Achat de ${"%.2f" % (ppt.amount / 60.0)} heure(s)
								% else:
								${ppt.description}
								% endif
							</td>
							<td class="number">
								% if ppt.type == 'validated':
								<% tot_val += ppt.amount/60.0 %>
								${"%.2f" % (ppt.amount / 60.0)}
								% else:
								&nbsp;
								% endif
							</td>
							<td class="number">
								% if ppt.type == 'add':
								<% tot_add += ppt.amount/60.0 %>
								${"%.2f" % (ppt.amount / 60.0)}
								% else:
								&nbsp;
								% endif
							</td>
							<td class="number">${"%.2f" % (tot_bef + tot_add - tot_val)}</td>
						</tr>
						% endif
						% endfor
					</tbody>
					<tfooter>
						<tr id="solde_after">
							<td colspan="3">&nbsp;</td>
							<td colspan="2">Solde au ${date_to.strftime('%d.%m.%Y')}</td>
							<td>${"%.2f" % (tot_bef + tot_add - tot_val)}</td>
						</tr>
					</tfooter>
				</table>
			</div>
		</div>
		% endfor
	</body>
</html>
