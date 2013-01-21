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
    
    instance.bss_attendance_sheet.ListFieldDeviceType = instance.web.list.Column.extend({
        _format: function (row_data, options) {
        	if (row_data[this.id].value) {
        		return _.template('<span class="bss_device_type_phone"></span>', {});
        	} else {
        		return _.template('<span class="bss_device_type_computer"></span>', {});
        	}
        }
    });
    
    instance.web.list.columns.add('field.device_type', 'instance.bss_attendance_sheet.ListFieldDeviceType');
    
}

