<%
import locale
locale.setlocale(locale.LC_ALL, 'fr_CH.utf-8')
%>

<html>
<head>
	<% 
		ref_start_left   = 1.5
		ref_coef_space   = 2.5
	%>
       <style type="text/css">
           @font-face {
               font-family: "bvrocrb";
               font-style: normal;
               font-weight: normal;
               src: url(${police_absolute_path('ocrbb.ttf')}) format("truetype");
           }

	#bvrfooter {
		position:relative;
		left:64mm;
		top:48mm;
		font-family:bvrocrb;
		font-size:12pt;
		text-align:left;
		height: 13mm;
		width: 119mm;
	}
	.digitref {
		position:absolute;
		top:7px;
		text-align:center;
		float:left;
		width:9px;
	}
	
	#info_block {
		position: absolute;
		top: 90mm;
		left: 30mm;
		font-size: 12;
	}
	
	th {
		text-align: left;
	}

           .ocrbb{
             text-align:right;
             font-family:bvrocrb;
             font-size:${str(company.bvr_scan_line_font_size or '0.0').replace(',','.')}pt;
             position:absolute;
             top:${str(company.bvr_scan_line_vert or '0.0').replace(',','.')}mm;
             left:${str(company.bvr_scan_line_horz or '0.0').replace(',','.')}mm;
             z-index:4;
             letter-spacing:${str(company.bvr_scan_line_letter_spacing or '0.0').replace(',','.')}
           }

           .slip_address_b {
            position:absolute;
            top:${str(213 + (company.bvr_delta_vert or 0.0)).replace(',','.')}mm;
            left:${str(4 + (company.bvr_delta_horz or 0.0)).replace(',','.')}mm;

           }

         .dest_address_bvr {
           position:absolute;
           top:${str(company.bvr_add_vert or '0.0').replace(',','.')}mm;
           left:${str(company.bvr_add_horz or '0.0').replace(',','.')}mm;
           font-size:12;
          }
          
         .slip_bank_acc {
           font-family:Helvetica;
           font-size:8pt;
           border-width:0px;
           padding-left:0mm;
           padding-top:0mm;
           position:absolute;
           top:${str(196 + (company.bvr_delta_vert or 0.0)).replace(',','.')}mm;
           left:${str(32 + (company.bvr_delta_horz or 0.0)).replace(',','.')}mm;
          }

         .slip_bank_add_acc {
           font-family:Helvetica;
           font-size:8pt;
           border-width:0px;
           padding-left:0mm;
           padding-top:0mm;
           position:absolute;
           top:${str(163 + (company.bvr_delta_vert or 0.0)).replace(',','.')}mm;
           left:${str(4 + (company.bvr_delta_horz or 0.0)).replace(',','.')}mm;
          }

          .slip_comp {
              font-family:Helvetica;
              font-size:8pt;
              border-width:0px;
              padding-left:0mm;
              padding-top:0mm;
              position:absolute;
              top:${str(175+ (company.bvr_delta_vert or 0.0)).replace(',','.')}mm;
              left:${str(4 + (company.bvr_delta_horz or 0.0)).replace(',','.')}mm;
           }

           .slip_add {
             font-family:Helvetica;
             font-size:8pt;
             border-width:0px;
             padding-left:0mm;
             padding-top:0mm;
           }

           .slip_amount {
             width:5cm;
             text-align:right;
             font-size:10pt;
             font-family:Helvetica;
             position:absolute;
             top:${str(204 + (company.bvr_delta_vert or 0.0)).replace(',','.')}mm;
             left:${str(2 + (company.bvr_delta_horz or 0.0)).replace(',','.')}mm;
           }

           /*
            Slip 2 element
           */

           .slip2_address_b {
             position:absolute;
             top:${str(205 + (company.bvr_delta_vert or 0.0)).replace(',','.')}mm;
             left:${str(122 + (company.bvr_delta_horz or 0.0)).replace(',','.')}mm;
           }


         .slip2_bank_acc {
           font-family:Helvetica;
           font-size:8pt;
           border-width:0px;
           padding-left:0mm;
           padding-top:0mm;
           position:absolute;
           top:${str(196 + (company.bvr_delta_vert or 0.0)).replace(',','.')}mm;
           left:${str(90 + (company.bvr_delta_horz or 0.0)).replace(',','.')}mm;
          }



         .slip2_bank_add_acc {
           font-family:Helvetica;
           font-size:8pt;
           border-width:0px;
           padding-left:0mm;
           padding-top:0mm;
           position:absolute;
           top:${str(163 + (company.bvr_delta_vert or 0.0)).replace(',','.')}mm;
           left:${str(62 + (company.bvr_delta_horz or 0.0)).replace(',','.')}mm;
          }


         .slip2_ref {
              text-align:right;
              font-size:11pt;
              font-family:Helvetica;
              position:absolute;
              top:${str(187 + (company.bvr_delta_vert or 0.0)).replace(',','.')}mm;
              left:${str(130 + (company.bvr_delta_horz or 0.0)).replace(',','.')}mm;
           }

           .slip2_comp {
             font-family:Helvetica;
             font-size:8pt;
             border-width:0px;
             padding-left:0mm;
             padding-top:0mm;
             position:absolute;
             top:${str(175+ (company.bvr_delta_vert or 0.0)).replace(',','.')}mm;
             left:${str(62 + (company.bvr_delta_horz or 0.0)).replace(',','.')}mm;
           }

           .bvr_background {
               width:210mm;
               height:106mm;
               border:0;
               margin:0;
               position:absolute;
               z-index:-10;
               top:${str(151.2+ (company.bvr_delta_vert or 0.0)).replace(',','.')}mm;
               left:${str(0 + (company.bvr_delta_horz or 0.0)).replace(',','.')}mm;
           }

           .slip2_amount {
             width:5cm;
             text-align:right;
             font-size:10pt;
             font-family:Helvetica;
             position:absolute;
             top:${str(204 + (company.bvr_delta_vert or 0.0)).replace(',','.')}mm;
             left:${str(61 + (company.bvr_delta_horz or 0.0)).replace(',','.')}mm;
           }

          ${css}
    </style>

   </head>
   <body topmargin="0px">

       %for inv in objects :
       <% setLang(inv.partner_id.lang) %>
       <!--adresses + info block -->
        <table class="dest_address_bvr"  style="position:absolute;width:230px;word-wrap:break-word">
               %if inv.partner_id.title:
               <tr><td>${inv.partner_id.title.name}</tr></td>
               %endif
               %if inv.partner_id.name:
               <tr><td>${inv.partner_id.name}</td></tr>
               %endif
               <tr><td>${inv.partner_id.street or ''|entity}</td></tr>
               % if inv.partner_id.street2:
               <tr><td>${inv.partner_id.street2 or ''|entity}</td></tr>
               % endif
               <tr><td>${inv.partner_id.zip or ''|entity} ${inv.partner_id.city or ''|entity}</td></tr>
               %if inv.partner_id.country_id :
               <tr><td>${inv.partner_id.country_id.name or ''|entity} </td></tr>
               %endif
	</table>
	<table id="info_block">
		<tr>
			<th>N° facture :</th>
			<td>${inv.number}</td>
		</tr>
		<tr>
			<th>Date :</th>
			<td>${inv.date_invoice}</td>
		</tr>
		<tr>
			<th>Conditions de paiement :</th>
			<td>${inv.payment_term.name or 'n/a'}</td>
		</tr>
	</table>

       <div id="cont_${inv.id}" style="padding-left:20mm;padding-top:0;padding-bottom:10;height:180mm">
        <!-- Your communication message here -->
       </div>
    %if company.bvr_background:
    <img name="bvr_background" id="bvr_background" class="bvr_background" alt="bvr" src="${bvr_absolute_path()}" />
    %endif
    <!-- slip 1 elements -->
       <div id="slip_address_b" class="slip_address_b">
		${_space(_get_ref(inv))}<br/><br/>
		%if title:
		${inv.partner_id.title.name or ''|entity}<br/>
		%endif
		${inv.partner_id.name |entity}<br/>
		${inv.partner_id.street or ''|entity}<br/>
		% if inv.partner_id.street2:
		${inv.partner_id.street2 or ''|entity}<br/>
		% endif
		${inv.partner_id.zip or ''|entity} ${inv.partner_id.city or ''|entity}
       </div>
       %if inv.partner_bank_id and inv.partner_bank_id.print_bank and inv.partner_bank_id.bank:
         <div id="slip_bank_add_acc" class="slip_bank_add_acc">
           ${inv.partner_bank_id.bank_name or ''} <br/>
           ${inv.partner_bank_id.bank and inv.partner_bank_id.bank.zip or ''}&nbsp;${inv.partner_bank_id.bank and inv.partner_bank_id.bank.city or ''}
         </div>
       %endif


       <div id="slip_bank_acc" class="slip_bank_acc">${inv.partner_bank_id.print_account and inv.partner_bank_id.acc_number or ''}</div>

       <div id="slip_amount" class="slip_amount"><span >${locale.format('%.2f',inv.amount_total, 1)[:-3]}</span>  <span style="padding-left:6mm">${('%.2f' % inv.amount_total)[-2:]}</span></div>

       %if  inv.partner_bank_id.print_partner:
       <div id="slip_comp" class="slip_comp">
		${user.company_id.partner_id.name}<br/>
		${user.company_id.partner_id.street}<br/>
		${user.company_id.partner_id.zip} ${user.company_id.partner_id.city}
      </div>
      %endif

    <!-- slip 2 elements -->
       <div id="slip2_ref" class="slip2_ref" >${_space(_get_ref(inv))}</div>
       <div id="slip2_amount" class="slip2_amount"><span>${locale.format('%.2f',inv.amount_total, 1)[:-3]}</span>  <span style="padding-left:6mm">${('%.2f' % inv.amount_total)[-2:]}</span></div>
       <div id="slip2_address_b" class="slip2_address_b">
		%if title:
		${inv.partner_id.title.name or ''|entity}<br/>
		%endif
		${inv.partner_id.name |entity}<br/>
		${inv.partner_id.street or ''|entity}<br/>
		% if inv.partner_id.street2:
		${inv.partner_id.street2 or ''|entity}<br/>
		% endif
		${inv.partner_id.zip or ''|entity} ${inv.partner_id.city or ''|entity}
       </div>

       %if inv.partner_bank_id.print_partner:
       <div id="slip2_comp" class="slip2_comp">
		${user.company_id.partner_id.name}<br/>
		${user.company_id.partner_id.street}<br/>
		${user.company_id.partner_id.zip} ${user.company_id.partner_id.city}
       </div>
       %endif

       %if inv.partner_bank_id and inv.partner_bank_id.print_bank and inv.partner_bank_id.bank:
         <div id="slip2_bank_add_acc" class="slip2_bank_add_acc">
           ${inv.partner_bank_id.bank_name or ''} <br/>
           ${inv.partner_bank_id.bank and inv.partner_bank_id.bank.zip or ''}&nbsp;${inv.partner_bank_id.bank and inv.partner_bank_id.bank.city or ''}
         </div>
       %endif

       <div id="slip2_bank_acc" class="slip2_bank_acc">${inv.partner_bank_id.print_account and inv.partner_bank_id.acc_number or ''}</div>
    <!--- scaner code bar -->
	<div id="bvrfooter">
		 <% 
			tt = [ v for v in mod10r('01'+str('%.2f' % inv.amount_total).replace('.','').rjust(10,'0')) ]
			tt.append('&gt;')
			tt += [v for v in _get_ref(inv)]
			tt.append('+')
			tt.append('&nbsp;')
			tt += [v for v in inv.partner_bank_id.acc_number.split('-')[0]+(str(inv.partner_bank_id.acc_number.split('-')[1])).rjust(6,'0')+inv.partner_bank_id.acc_number.split('-')[2]]
			tt.append('&gt;')
		 %>
		 
		%for ii,c in enumerate(tt) :
			<div class="digitref" style="left:${ref_start_left + (ii*ref_coef_space)}mm;">${c}</div>
		%endfor
	</div>
    %endfor
</body>
</html>
