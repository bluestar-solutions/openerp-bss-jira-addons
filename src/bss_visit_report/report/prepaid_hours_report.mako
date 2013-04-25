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
			<div id="content">
				<table id="report_head">
					<thead>
						<tr>
							<th colspan="2">Rapport sur carnet d'heures</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>Client :</td>
							<td width="90%">${prepaid_hours.pph_name}</td>
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
							<th>Date</th>
							<th>Description</th>
							<th>Débit</th>
							<th>Crédit</th>
							<th>Solde</th>
						</tr>
						<tr id="solde_before">
							<td colspan="2">&nbsp;</td>
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
							<td colspan="2">&nbsp;</td>
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
