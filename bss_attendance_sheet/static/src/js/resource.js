openerp.bss_attendance_sheet = function(instance) {
    
    instance.bss_attendance_sheet.FieldDeviceType = instance.web.form.AbstractField.extend({
        template: 'FieldDeviceType',
        render_value: function() {
        	if (this.get('value')) {
        		this.$('span').addClass('bss_device_type_phone');
        	} else {
        		this.$('span').addClass('bss_device_type_computer');
        	}
        }
    });

    instance.web.form.widgets.add('device_type', 'instance.bss_attendance_sheet.FieldDeviceType');
    
}

