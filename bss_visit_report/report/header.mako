<!--    Settings:
        Paper Size : A4
        Top margin : 40.00
        Bottom margin : 20.00
        Left margin : 10.00
        Right margin : 10.00
-->

<!doctype html>
<html>
    <head>
        <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>

        <style>
         
          @page { 
            size: auto;
            margin: 0mm;
          }
          html, body {
            font-family: "UniversLT", "Comic Sans MS", serif;
            font-size: 9pt;
            line-height: 1.4;
            margin: 0;
            padding: 0;
          }
          
          #logo img {
            width: 4cm;
            position: absolute;
            top: 1cm;
            left: 0.36cm; /* 2-0.64 (visual margin) */
          }
          #address {
            position: absolute;
            top: 1.2cm;
            left: 13.5cm;
            font-size: 7.5pt;
          }
          body, html {
            height: 40mm;
          }
        </style>
    </head>
    <body>
      <span id="logo">${helper.embed_logo_by_name('bss_header_logo')|n}</span>
      <p id="address">
        Bluestar Solutions Sàrl<br>
        Av. J.-J. Rousseau 7<br>
        2000 Neuchâtel<br>
        +41 32 720 08 90<br>
        info@blues2.ch
      </p>
    </body>
</html>

