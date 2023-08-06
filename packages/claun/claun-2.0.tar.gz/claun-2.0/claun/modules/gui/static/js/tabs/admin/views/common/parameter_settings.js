define([
	'core/claun',
	'text!tabs/admin/templates/common/parameter_settings/boolean.html',
	'text!tabs/admin/templates/common/parameter_settings/dropdown.html',
	'text!tabs/admin/templates/common/parameter_settings/dropdown-row.html',
	'text!tabs/admin/templates/common/parameter_settings/slider.html',
	],
	function(Claun, Boolean, Dropdown, DropdownRow, Slider) {

		return {
			'boolean': Backbone.View.extend({
				tagName: 'div',
				initialize: function () {
					this.parameterCellId = this.options.parameterCellId;
					this.parameterId = this.options.parameterId;
					this.template = _.template(Boolean);
					this.values = this.options.values;
				},

				render: function () {
					this.$el.html(this.template({
						cellid: this.parameterCellId,
						id: this.parameterId,
						value: this.values['default'] === undefined ? undefined : this.values['default']
					}));
					this.$('#' + this.parameterId + '-boolean').css({
						direction: 'rtl',
						textAlign: 'left'
					}).buttonset();
					return this.$el;
				}
			}),

			dropdown: Backbone.View.extend({
				tagName: 'div',
				initialize: function () {
					this.parameterCellId = this.options.parameterCellId;
					this.parameterId = this.options.parameterId;
					this.template = _.template(Dropdown);
					this.dropdownRowTemplate = _.template(DropdownRow);
					this.values = this.options.values;
				},

				_appendValueRow: function (value) {
					var self = this,
					table = this.$('#' + this.parameterId + '-dropdown');
					if (table.attr('data-nextid') === undefined) {
						table.attr('data-nextid', 0);
					}
					var nextid =  table.attr('data-nextid'),
					ncellid	= this.parameterCellId + '-values' + '[' + nextid + ']',
					nid = this.parameterId + '-values-' + nextid;
					table.attr('data-nextid', parseInt(nextid) + 1);

					table.append(this.dropdownRowTemplate({
						id: nid,
						cellid: ncellid,
						value: value === undefined ? {} : value,
						groupName: self.parameterCellId + '-default'
					}));
					
					this.$('#' + nid + '-delete-row').click(function (event) {
						self.$('#' + $(event.srcElement || event.target).attr('data-id')).remove();
						if (self.$('tr').length == 1) {
							self._appendValueRow({
							value: '',
							'default': ''
						});
						}
					});
					this.$('input:radio').button().change(function () {
						$.each($('input:radio'), function () {
							if ($(this).is(':checked')) {
								$('label span', $(this).parent()).text('YES');
							} else {
								$('label span', $(this).parent()).text('NO');
							}
						})
					});
				},

				render: function () {
					this.$el.html(this.template({
						cellid: this.parameterCellId,
						id: this.parameterId,
						values: this.values
					}));
					var self = this;
					if (this.values.values !== undefined && this.values.values.length) {
						$.each(this.values.values, function () {
							self._appendValueRow({
								value: this,
								'default': self.values['default']
								})
						});
					} else {
						this._appendValueRow({
							value: '',
							'default': ''
						});
					}
					this.$('#add-dropdown-value-' + this.parameterId).click(function (event) {
						event.preventDefault();
						self._appendValueRow();
					});
					return this.$el;
				}
			}),

			slider: Backbone.View.extend({
				tagName: 'div',
				initialize: function () {
					this.parameterCellId = this.options.parameterCellId;
					this.parameterId = this.options.parameterId;
					this.template = _.template(Slider);
					this.values = this.options.values;
				},
				
				render: function () {
					this.$el.html(this.template({
						cellid: this.parameterCellId,
						id: this.parameterId,
						values: this.values
					}));
					return this.$el;
				}

			})
		}

	});