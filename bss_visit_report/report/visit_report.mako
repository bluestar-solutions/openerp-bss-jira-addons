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
	<h1>Rapport d'intervention ${visit.ref}${' - BROUILLON' if visit.state != 'terminated' else ''}</h1>
	<h2>${visit.customer_id.name}</h2>
	<p>Date : ${visit.date}</p>
	<p>Intervenant : ${visit.user_id.name}</p>
	<p>Présence : ${str(datetime.timedelta(hours=visit.hour_from))[:-3]} - ${str(datetime.timedelta(hours=visit.hour_to))[:-3]}</p>
	<p>Temps d'intervention : ${str(datetime.timedelta(hours=visit.time))[:-3]}</p>
	<p>Déplacement : ${visit.travel_zone.name}</p>
	
	<h2>Tâches initiales</h2>
	% for visit_task in visit.visit_task_ids:	
		<p>${visit_task.task_id.name}</p>
	% endfor
	
	<h2>Tâches fermées</h2>
	% for visit_task in visit.visit_task_ids:
		% if visit_task.state in ['done', 'cancelled']:
			<p>${visit_task.task_id.name} / ${'Réalisé' if visit_task.state == 'done' else 'Annulé'}</p>
		% endif
	% endfor
	
	<h2>Tâches ouvertes</h2>
	% for visit_task in visit.visit_task_ids:
		% if visit_task.state == 'todo':
			<p>${visit_task.task_id.name}</p>
		% endif
	% endfor
	
</body>

</html>
% endfor