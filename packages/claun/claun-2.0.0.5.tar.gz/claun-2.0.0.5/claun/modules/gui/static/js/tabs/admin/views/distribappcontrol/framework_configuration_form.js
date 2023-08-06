define([
	'core/claun',
	'form2js',
	],
	function (Claun) {
		var FrameworkConfigurationAttributes = {
			clean: function (result) {
				if (result.fcid !== undefined) {
					result.id = result.fcid;
					delete result.fcid;
				}
				return result;
			},
			validate: function (result) {
				if (result.framework_name === undefined) {
					Claun.messages.formError('Missing framework name!', this.$('#framework_name'));
					return false;
				}

				if (result.configuration_name === undefined) {
					Claun.messages.formError('Missing configuration name!', this.$('#configuration_name'));
					return false;
				}

				if (result.parameters === undefined) {
					Claun.messages.formError('Missing parameters!', this.$('#parameters'));
					return false;
				}

				if (!result.parameters.isValidJSON()) {
					Claun.messages.formError('Parameters field is not a valid JSON!', this.$('#parameters'));
					return false;
				}

				return result;
			},

			renderForm: function () {
				var vals = _.clone(this.values);
				vals['parameters'] = Claun.json.stringify(this.values.parameters, null, 4);

				return this.$formWrapper.html(
					this.template({
						action: this.action,
						values: vals
					})
					);
			}
		};
		return FrameworkConfigurationAttributes;
	});