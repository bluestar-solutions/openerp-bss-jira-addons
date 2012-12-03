openerp.bss_partner_phonenumbers = function(instance) {

    instance.bss_partner_phonenumbers.FieldPhoneNumber = instance.web.form.FieldChar.extend({
        template : "FieldPhoneNumber",
        initialize_content: function() {
        	console.log('initialize_content')
            this._super();
            var $button = this.$el.find('button');
            $button.click(this.on_button_clicked);
            this.setupFocus($button);
        },
        render_value: function() {
        	console.log('render_value')
        	console.log(this.dataset)
        	if (!this.get("effective_readonly")) {
        		if (this.name in this.view.datarecord) {
        			this.$el.find('input').val(this.view.datarecord[this.name]['e164'] || '');
        		}
            } else {
                this.$el.find('a')
                        .attr('href', this.view.datarecord[this.name]['rfc3966'])
                        .text(this.view.datarecord[this.name]['international'] || '');
            }
        },
        get_value: function() {
        	val = this.get('value')
        	if (!val) {
        		val = ''
        	}
            return val + ',' + this.session.user_context.lang.substring(3,5);
        },
        on_button_clicked: function() {
            location.href = 'tel:' + this.get('value');
        }
    });
    
    instance.web.form.widgets.add('phonenumber', 'instance.bss_partner_phonenumbers.FieldPhoneNumber');
    
}

