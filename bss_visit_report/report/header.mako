<html>

	<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
		<script>
			function subst() {
				var vars = {};
				var x = document.location.search.substring(1).split('&');
				for ( var i in x) {
					var z = x[i].split('=', 2);
					vars[z[0]] = unescape(z[1]);
				}
				var x = [ 'frompage', 'topage', 'page', 'webpage', 'section',
						'subsection', 'subsubsection' ];
				for ( var i in x) {
					var y = document.getElementsByClassName(x[i]);
					for ( var j = 0; j < y.length; ++j)
						y[j].textContent = vars[x[i]];
				}
				
	            if(vars['page'] > 1){
	                document.getElementById("logo").style.display = 'none';
	            }
			}
		</script>
		<style type="text/css">
			${css}
		</style>
	</head>
	
	<body onload="subst()">
		${_debug or ''|n}
	
		<div id="logo">${helper.embed_logo_by_name('endago_logo')|n}</div>
	</body>

</html>