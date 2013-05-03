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
		tr.total_decompte {
		  font-weight: bolder;
		  border: thin solid black;
		  text-transform: uppercase;
		}
		td.number, th.head_num {
		  text-align: right;
		}
		#decompte tr {
		  border-bottom: thin solid gray;
		}
		#decompte tr:nth-child(even) {
		  background-color: #DDD;
		}
		</style>
	</head>
	<body>
		% for invoice in objects:
		<div id="content">
			<table>
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
						<th>Int.</th>
						<th width="100%">Travail effectué</th>
						<th>%</th>
						<th>Temps</th>
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
						<td>${rel_line._get_employee_for_user().initials or ''}</td>
						<td style="white-space:normal;">${rel_line.name}</td>
						<td>${rel_line.to_invoice.customer_name}</td>
						<td class="number">${"%.2f" % rel_line.unit_amount}</td>
					</tr>
					% endfor
				</tbody>
				<tfoot>
					<tr>
						<td colspan="5">&nbsp;</td>
					</tr>
					<tr>
						<td colspan="3">&nbsp;</td>
						<td colspan="2">
							<table width="100%">
								<tr class="total_decompte">
									<td>Total</td>
									<td class="number">${"%.2f" % htot}</td>
								</tr>
							</table>
						</td>
					</tr>
				</tfoot>
			</table>
		</div>
		% endfor
	</body>
</html>
