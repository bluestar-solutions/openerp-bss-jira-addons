openerp.bss_partner_phonenumbers = function(instance) {

    instance.bss_partner_phonenumbers.FieldPhoneNumber = instance.web.form.FieldChar.extend({
        template : "FieldPhoneNumber",
        initialize_content: function() {
            this._super();
            var $button = this.$el.find('button');
            $button.click(this.on_button_clicked);
            this.setupFocus($button);
        },
        render_value: function() {
        	var field = this;
        	if (!field.get("effective_readonly")) {
        		field.$el.find('input').val(this.get('value') || '');
        	} else {
            	var conv = new instance.web.Model('bss.phonenumbers.converter');
            	conv.call('format', [this.get_value()]).then(function (result) {
                	field.$el.find('a')
                            .attr('href', result.rfc3966)
                            .text(result.international || '');
            	});
        	}
        },
        get_value: function() {
        	val = this.get('value');
        	if (!val) {
        		return '';
        	}
        	
		return val + ',' + this.session.user_context.lang.substring(3,5);
        },
        on_button_clicked: function() {
            location.href = 'tel:' + this.get('value');
        }
    });
    
    instance.web.form.widgets.add('phonenumber', 'instance.bss_partner_phonenumbers.FieldPhoneNumber');
    
}

