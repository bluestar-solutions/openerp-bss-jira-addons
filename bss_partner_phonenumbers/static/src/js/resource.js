openerp.bss_partner_phonenumbers = function(instance) {
	var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.bss_partner_phonenumbers.FieldPhoneNumber = instance.web.form.FieldChar.extend({
        template : "FieldPhoneNumber",
        initialize_content: function() {
            this._super();
            var $button = this.$el.find('button');
            $button.click(this.on_button_clicked);
            this.setupFocus($button);
        },.
        render_value: function() {
            if (!this.get("effective_readonly")) {
                this._super();
            } else {
                this.$el.find('a')
                        .attr('href', 'tel:' + this.get('value'))
                        .text(this.get('value') || '');
            }
        },
        on_button_clicked: function() {
            location.href = 'tel:' + this.get('value');
        }
    });
    
    instance.web.form.widgets.add('phonenumber', 'instance.bss_partner_phonenumbers.FieldPhoneNumber');
}

