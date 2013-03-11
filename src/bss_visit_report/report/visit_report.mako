<%
	import datetime
	import locale
	locale.setlocale(locale.LC_ALL, '')
%>

% for visit in objects:
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">

  <title>Rapport d'intervention ${visit.ref}${' - BROUILLON' if visit.state != 'terminated' else ''}</title>

  <meta name="viewport" content="width=device-width">
  <style>

  @page { 
    size: auto;
    margin: 0mm;
  }
  
  .clearfix:after {
    content: ".";
    display: block;
    clear: both;
    visibility: hidden;
    line-height: 0;
    height: 0;
  }
 
  .clearfix {
      display: inline-block;
  }

  html[xmlns] .clearfix {
      display: block;
  }

  * html .clearfix {
      height: 1%;
  }
  
  html, body {
    height: 100%;
  }
  body {
    margin: 0;
    width: 17cm;
    padding: 0 1cm;
    font-family: "UniversLT", "Comic Sans MS", serif;
    font-size: 9pt;
    line-height: 1.4;
  }
  dl {
    font-size: 0;
    border-top: 0.5pt solid #ccc;
    border-left: 0.5pt solid #ccc;
  }
  dt, dd {
    font-size: 9pt;
    display: inline-block;
    width: 25%;
    -webkit-box-sizing: border-box;
    box-sizing: border-box;
    padding: 1mm 3mm;
    margin: 0;
    border-right: 0.5pt solid #ccc;
    border-bottom: 0.5pt solid #ccc;
  }
  dt {
    color: #666;
    background-color: #e0e0e0;
  }
  h1 {
    font-size: 2.5em;
    line-height: 1.2;
    text-transform: uppercase;
    color: #003b96;
    font-weight: 200;
  }
  h3 {
    margin: 0.5cm 0 0.2cm 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #003b96;
    font-weight: normal;
    page-break-after: avoid;
  }
  h4 {
    margin: 0;
  }
  ul, li {
    list-style-image: none;
    list-style-type: none;
  }
  li p {
    color: #666;
    margin: 0;
  }
  ul {
    padding: 0;
  }
  li {
    margin: 0;
    padding: 0.3em 0 0.4em;
    page-break-inside: avoid;
  }
  ul.tasks li {
    width: 100%;
    margin-top: 2mm;
  }
  ul.tasks .task-content {
    float: left;
    width: 12cm;
  }
  ul.tasks p.desc {
    padding-top: 0.7em;
    font-size: 8pt;
    clear: both;
    width: 12cm;
  }
  span.status {
    display: block;
    float: left;
    width: 2.5cm;
    text-align: center;
    border-radius: 1mm;
    background-color: #003b96;
    padding: 1mm 2mm;
    margin-right: 4mm;
    margin-top: 1mm;
    color: white;
  }
  span.status.failed {
    background-color: #e0e0e0;
    color: #666;
  }
  span.status.todo {
    background-color: #e0e0e0;
    color: #003b96;
  }
  #signatures table {
    page-break-inside: avoid;
    width: 100%;
  }
  #signatures td {
    width: 50%;
  }
  #signatures p {
    margin: 0.4em 0;
  }
  #signatures input {
    margin: 0.8em 0;
    border-width: 0 0 1px 0;
    border-bottom: 1px solid #ccc;
    width: 5cm;
  }
  #draft {
    position: absolute;
    z-index: 0;
    left: 1cm;
    right: 1cm;
    top: 5.5cm;
    -webkit-transform: rotateZ(-23deg);
    text-align: center;
    color: rgba(178,196,224,0.7);
    font-size: 8em;
    font-weight: bold;
  }
  #all {
    position: relative;
    z-index: 100;
  }
  </style>
</head>
<body>
  % if visit.state != 'terminated':
  <div id="draft">
    [&nbsp;BROUILLON&nbsp;]
  </div>
  % endif
  <div id="all">
	  <h1>Rapport d'intervention ${visit.ref}</h1>
	  <h2>${visit.customer_id.name}</h2>
	  <dl>
	    <dt>Référence client</dt>
	    <dd>${visit.customer_ref}</dd>
	    <dt>Date</dt>
	    <dd>${visit.date}</dd>
	    <dt>Intervenant</dt>
        <dd>${visit.user_id.name}</dd>
        <dt>Contact client</dt>
        <dd>${visit.customer_contact_id.name or visit.signer}</dd>
	    <dt>Arrivée</dt>
	    <dd>${str(datetime.timedelta(hours=visit.hour_from))[:-3]}</dd>
	    <dt>Départ</dt>
	    <dd>${str(datetime.timedelta(hours=visit.hour_to))[:-3]}</dd>
	    <dt>Temps d'intervention</dt>
        <dd>${str(datetime.timedelta(hours=visit.time))[:-3]}</dd>
	    <dt>Zone de déplacement</dt>
	    <dd>${visit.travel_zone.name or ''}</dd>
	  </dl>
	
	  <h3>Tâches demandées</h3>
	  <ul>
	    % for visit_task in visit.visit_task_ids:   
	      <li>
	        <h4>${visit_task.task_id.name}</h4>
	      </li>
	    % endfor
	  </ul>
	
	  <h3>Tâches fermées</h3>
	  <ul class="tasks">
        % if visit.text:
            <li class="clearfix">
              <span class="status success">réalisé</span>
              <div class="task-content">
                <h4>Tâches demandées en cours de visite</h4>
              </div>
              % if visit_task.task_id.description:
                  <p class="desc">${visit.text.replace('\n', '<br>')}</p>
              % endif
            </li>
        % endif
	    % for visit_task in visit.visit_task_ids:
	      % if visit_task.state in ['done', 'cancelled']:
		    <li class="clearfix">
		      % if visit_task.state == 'done':
		        <span class="status success">réalisé</span>
		      % else:
		        <span class="status failed">annulé</span>
		      % endif
		      <div class="task-content">
		        <h4>${visit_task.task_id.name}</h4>
		        <p class="comm">${visit_task.comment}</p>
		      </div>
		      % if visit_task.task_id.description:
                  <p class="desc">${visit_task.task_id.description.replace('\n', '<br>')}</p>
              % endif
		    </li>
	      % endif
	    % endfor
	  </ul>
	
	  <h3>Tâches en suspens</h3>
	  <ul class="tasks">
	    % for visit_task in visit.visit_task_ids:
	      % if visit_task.state == 'todo':
		    <li class="clearfix">
		      <span class="status todo">à faire</span>
		      <div class="task-content">
		        <h4>${visit_task.task_id.name}</h4>
		        <p class="comm">${visit_task.comment}</p>
		      </div>
		      % if visit_task.task_id.description:
		          <p class="desc">${visit_task.task_id.description.replace('\n', '<br>')}</p>
		      % endif
		    </li>
	      % endif
	    % endfor
	  </ul>
	  
	  % if visit.remarks:
		  <h3>Remarques</h3>
		  <p class="task-comment">${visit.remarks.replace('\n', '<br>')}</p>
	  % endif
	  
	  <div id="signatures">
	    <table>
	      <tr>
	        <td>
	          <h4>Intervenant</h4>
	          <p>${visit.user_id.name}</p>
	          <input type="text">
	        </td>
	        <td>
	          <h4>Client</h4>
	            <p>${visit.signer or visit.customer_contact_id.name}</p>
	          <input type="text">
	        </td>
	      </tr>
	    </table>
	  </div>
	</div>
</body>
</html>
% endfor