<%
	import datetime
	import locale
	locale.setlocale(locale.LC_ALL, '')
%>

% for visit in objects:
<html>

<head>
	<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
	<style type="text/css">
		${css}
	</style>
</head>

<body>
	<h1>Rapport d'intervention ${visit.ref}</h1>
	<h2>${visit.customer_id.name}</h2>
	<p>Date : ${visit.date}</p>
	<p>Intervenant : ${visit.user_id.name}</p>
	<p>Présence : ${str(datetime.timedelta(hours=visit.hour_from))[:-3]} - ${str(datetime.timedelta(hours=visit.hour_to))[:-3]}</p>
	<p>Temps d'intervention : ${str(datetime.timedelta(hours=visit.time))[:-3]}</p>
	<p>Déplacement : ${visit.travel_zone.name}</p>
	
	<h2>Tâches initiales</h2>
	% for task in visit.task_ids:	
		<p>${task.name}</p>
	% endfor
	
	<h2>Tâches fermées</h2>
	% for task in visit.task_ids:
		% if task.state in ['terminated', 'cancelled']:
			<p>${task.name} / ${task.state}</p>
		% endif
	% endfor
	
	<h2>Tâches ouvertes</h2>
	% for task in visit.task_ids:
		% if task.state not in ['terminated', 'cancelled']:
			<p>${task.name} / ${task.state}</p>
		% endif
	% endfor
	
</body>

</html>
% endfor