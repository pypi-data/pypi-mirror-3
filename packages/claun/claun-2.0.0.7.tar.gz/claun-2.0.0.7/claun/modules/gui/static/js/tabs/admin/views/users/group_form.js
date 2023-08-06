define([
	'core/claun',
	],
	function (Claun) {
		var GroupFormSettings = {
			clean: function (result) {
				if (result.gid !== undefined) {
					result.id = result.gid;
					delete result.gid;
				}
				return result;
			},

			validate: function (result) {
				if (result.name === undefined) {
					Claun.messages.formError('Missing group name!', this.$('#name'));
					return false;
				}

				return result;
			},

			renderForm: function () {
				return this.$formWrapper.html(
					this.template({
						action: this.action,
						values: this.values
					})
					);
			},

			initForm: function () {
				return this.$el;
			}

		};
		return GroupFormSettings;
	});