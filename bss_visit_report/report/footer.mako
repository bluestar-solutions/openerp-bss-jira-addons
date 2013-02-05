<html>
    <head>
        <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
        <script>
            function subst() {
	            var vars={};
	            var x=document.location.search.substring(1).split('&');
	            for(var i in x) {var z=x[i].split('=',2);vars[z[0]] = unescape(z[1]);}
	            var x=['frompage','topage','page','webpage','section','subsection','subsubsection'];
	            for(var i in x) {
		            var y = document.getElementsByClassName(x[i]);
		            for(var j=0; j<y.length; ++j) y[j].textContent = vars[x[i]];
	            }
            }
        </script>
        <style type="text/css">
		${css}
        </style>
    </head>
    <body onload="subst()">
        <div class="footer">
            <div>&nbsp;de <span class="topage"/></div>
            <div>Page <span class="page"/></div>
        </div>
    </body>
</html>