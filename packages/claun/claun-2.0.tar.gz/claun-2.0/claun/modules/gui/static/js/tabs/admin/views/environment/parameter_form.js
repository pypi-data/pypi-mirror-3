define([
	'core/claun',
	'text!tabs/admin/templates/common/parameter.html',
	'form2js',
	],
	function (Claun, ParameterTable) {
		var ParameterFormAttributes = {
			id: 'parameter-0',
			cellid: 'parameter[0]',
			parameterTable: _.template(ParameterTable),

			clean: function (result) {
				var id = undefined;
				if (result.pid !== undefined) {
					id = result.pid;
				}
				result = result.parameter[0];
				if (id) {
					result.id = id;
				}

				if (result.type == 'dropdown') {
					if (result['default'] !== undefined) {
						var input = $('#' + result['default'] + ' input:text');
						result['default'] = input.length > 0 ? input.val() : undefined;
					}
				}

				return result;
			},

			validate: function (result) {
				var self = this;
				
				if (result.name === undefined) {
					Claun.messages.formError('Missing parameter\'s name!', this.$('#' + this.formAttributes.id + '-name'));
					return false;
				}

				if (result.human_name === undefined) {
					Claun.messages.formError('Missing human name!', this.$('#' + this.formAttributes.id + '-human_name'));
					return false;
				}

				if (result.type === undefined) {
					Claun.messages.formError('Missing parameter\'s type!', this.$('#' + this.formAttributes.id + '-type'));
					return false;
				}

				if (result.user_editable === undefined) {
					Claun.messages.formError('Missing parameter\'s editability!', this.$('#' + this.formAttributes.id + '-user_editable'));
					return false;
				}
				
				if (result.type === 'dropdown' && $.inArray(result['default'], result.values) === -1) {
					Claun.messages.formError('The parameter\'s default value looks weird!', this.$('#' + this.formAttributes.id + '-settings'));
					return false;
				}

				if (result.type === 'boolean' && $.inArray(result['default'], [true, false]) === -1) {
					Claun.messages.formError('The parameter\'s default value looks weird!', this.$('#' + this.formAttributes.id + '-settings'));
					return false;
				}

				if (result.type === 'slider') {
					var stop = false,
					ctx = result;
					$.each(['min', 'max'], function () {
						if (ctx[this] === undefined) {
							Claun.messages.formError('The parameter\'s ' + this + ' value is missing!', self.$('#' + this.formAttributes.id + '-settings'));
							stop = true;
							return false;
						}

						if (isNaN(parseFloat(ctx[this]))) {
							Claun.messages.formError('The parameter\'s ' + this + 'value is not a number!', self.$('#' + this.formAttributes.id + '-settings'));
							stop = true;
							return false;
						}
						result[this] = parseFloat(ctx[this]);
					})
					if (stop) {
						return false;
					}
					result['default'] = parseFloat(result['default'])
					if (isNaN(result['default'])) {
						Claun.messages.formError('The parameter\'s default value is not a number!', this.$('#' + this.formAttributes.id + '-settings'));
						return false;
					}

					if (result['default'] > result.max || result['default'] < result.min) {
						Claun.messages.formError('The parameter\'s default value is not within min and max bounds!', this.$('#' + this.formAttributes.id + '-settings'));
						return false;
					}
				}

				return result;
			},

			renderForm: function () {
				var tpl = this.template({
					action: this.action,
					parameter: this.formAttributes.parameterTable(
					{
						id: this.formAttributes.id,
						showProcessingType: false,
						showGroup: true,
						showDeleteButton: false,
						cellid: this.formAttributes.cellid,
						types: this.additionalData.type(),
						values: this.values
					}
					),
					values: this.values
				});
				return this.$formWrapper.html(tpl);
			},

			initForm: function () {
				var self = this,
				selected = this.$('#' + this.formAttributes.id + '-type select').val();
				this.formAttributes._fillParameterSettings.call(this, this.formAttributes.cellid, this.formAttributes.id, selected, this.values);
				this.$('#' + this.formAttributes.id + '-type select').change(function () {
					self.formAttributes._fillParameterSettings.call(self, self.formAttributes.cellid, self.formAttributes.id, this.value);
				});
				return this.$el;
			}

		};
		return ParameterFormAttributes;
	});