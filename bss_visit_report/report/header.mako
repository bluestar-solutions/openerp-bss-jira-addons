<!--    Settings:
        Paper Size : A4
        Top margin : 55.00
        Bottom margin : 0.00
        Left margin : 0.00
        Right margin : 0.00
-->

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
    <body style="border:0; margin: 0;" onload="subst()">
        <table class="header" style="border-bottom: 0px solid black; width: 100%">
            <tr>
                <td>${helper.embed_logo_by_name('camptocamp_logo')|n}</td>
                <td style="text-align:right"> </td>
            </tr>
            <tr>
                <td><br/></td>
                <td style="text-align:right"> </td>
            </tr>
            <tr>
                <td>${company.partner_id.name |entity}</td>
                <td/>
            </tr>
            <tr>
                <td >${company.partner_id.street or ''|entity}</td>
                <td/>
            </tr>
            <tr>
                <td>Phone: ${company.partner_id.phone or ''|entity} </td>
                <td/>
            </tr>
            <tr>
                <td>Mail: ${company.partner_id.email or ''|entity}<br/></td>
            </tr>
        </table> ${_debug or ''|n} </body>
</html>

