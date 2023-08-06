define([
	'core/claun',
	'text!tabs/admin/templates/common/parameter.html',
	],
	function (Claun, ParameterTable) {

		var ApplicationFormSettings = {
			parameterTable: _.template(ParameterTable),
			clean: function (result) {

				if (result.controller.is === false) {
					delete result.controller;
				} else if (result.controller.is === true) {
					delete result.controller.is;
				}

				if (result.runtime && result.runtime.is !== undefined) {
					$.each(result.runtime.is, function (k, v) {
						if (!v) {
							delete result.runtime[k];
						}
					});
					delete result.runtime.is;
				} else {
					result.runtime = {};
				}

				if (result.aid !== undefined) {
					result.id = result.aid;
					delete result.aid;
				}

				// Re-map key: value
				$.each(['framework_configuration', 'controller_configuration'].concat(Object.keys(result.runtime).map(function (a) {
					return 'runtime.' + a
				})), function () {
					var target = null,
					repaired = {};
					if (this.startsWith('runtime.')) {
						target = result['runtime'][this.split('runtime.')[1]];
					} else {
						target = result[this];
					}
					if (target === undefined) {
						return;
					}

					$.each(target, function() {
						if (this.key !== undefined && this.value !== undefined) {
							repaired[this.key] = this.value;
						}
					})
					if (Object.keys(repaired).length > 0) {
						if (this.startsWith('runtime.')) {
							result['runtime'][this.split('runtime.')[1]] = repaired;
						} else {
							result[this] = repaired;
						}
					}
				});

				// Clean parameters
				if (result.parameters !== undefined) {
					$.each(result.parameters, function (idx) {
						if (this.type == 'dropdown') {
							if (this['default'] !== undefined) {
								var input = $('#' + this['default'] + ' input:text');
								result.parameters[idx]['default'] = input.length > 0 ? input.val() : undefined;
							}
						}
					});
				}

				if (Object.keys(result.runtime).length == 0) {
					delete result.runtime;
				}

				return result;
			},

			validate: function (result) {
				var self = this;

				// Application name
				if (result.name === undefined) {
					Claun.messages.formError('Missing application name!', this.$('#name'));
					return false;
				}

				// Framework
				if (result.framework === undefined) {
					Claun.messages.formError('Missing framework!', this.$('#framework-name'));
					return false;
				}

				// Platform
				if (result.runtime === undefined) {
					Claun.messages.formError('Missing at least one platform!', this.$('#runtime'));
					return false;
				}

				// If some, check parameters
				if (result.parameters !== undefined) {
					var parametersok = true;
					$.each(result.parameters, function (idx) {
						if (this.name === undefined) {
							Claun.messages.formError('Missing parameter\'s name!', self.$('#parameters>table:eq(' + idx + ')'));
							parametersok = false;
							return false;
						}

						if (this.human_name === undefined) {
							Claun.messages.formError('Missing parameter\'s human name!', self.$('#parameters>table:eq(' + idx + ')'));
							parametersok = false;
							return false;
						}

						if (this['default'] === undefined) {
							Claun.messages.formError('Missing parameter\'s default value!', self.$('#parameters>table:eq(' + idx + ')'));
							parametersok = false;
							return false;
						}

						if (this.type === 'dropdown' && $.inArray(this['default'], this.values) === -1) {
							Claun.messages.formError('The parameter\'s default value looks weird!', self.$('#parameters>table:eq(' + idx + ')'));
							parametersok = false;
							return false;
						}

						if (this.type === 'boolean' && $.inArray(this['default'], [true, false]) === -1) {
							Claun.messages.formError('The parameter\'s default value looks weird!', self.$('#parameters>table:eq(' + idx + ')'));
							parametersok = false;
							return false;
						}

						if (this.type === 'slider') {
							var stop = false,
							ctx = this;
							$.each(['min', 'max'], function () {
								if (ctx[this] === undefined) {
									Claun.messages.formError('The parameter\'s ' + this + ' value is missing!', self.$('#parameters>table:eq(' + idx + ')'));
									stop = true;
									return false;
								}

								if (isNaN(parseFloat(ctx[this]))) {
									Claun.messages.formError('The parameter\'s ' + this + 'value is not a number!', self.$('#parameters>table:eq(' + idx + ')'));
									stop = true;
									return false;
								}
								result.parameters[idx][this] = parseFloat(ctx[this]);
							});
							if (stop) {
								parametersok = false;
								return false;
							}
							this['default'] = parseFloat(this['default'])
							result.parameters[idx]['default'] = this['default'];
							if (isNaN(result.parameters[idx]['default'])) {
								Claun.messages.formError('The parameter\'s default value is not a number!', self.$('#parameters>table:eq(' + idx + ')'));
								parametersok = false;
								return false;
							}

							if (this['default'] > this.max || this['default'] < this.min) {
								Claun.messages.formError('The parameter\'s default value is not within min and max bounds!', self.$('#parameters>table:eq(' + idx + ')'));
								parametersok = false;
								return false;
							}
						}
					});
					if (!parametersok) {
						return false;
					}
				}

				return result;
			},

			renderForm: function () {
				var platforms = this.additionalData.platform();
				if (this.values.runtime) {
					platforms = _.uniq(Object.keys(this.values.runtime).concat(_.values(platforms)));
				}
				return this.$formWrapper.html(
					this.template({
						action: this.action,
						frameworks: this.additionalData.framework(),
						controllers: this.additionalData.controller(),
						platforms: platforms,
						values: this.values
					})
					);
			},

			initForm: function () {
				var self = this;
				// Toggle elements
				if (!this.values.controller) {
					this.$('.controller-details').toggle();
				}

				this.$('#controller-is').change(function () {
					var details = $('.controller-details');
					details.toggle();
					if (details.is(':visible')) {
						$.each(self.$('.controller-details select'), function () {
							var $this = $(this);
							$this.selectmenu({
								width: $this.width() * 2
							});
						});
					}
				});

				// Platforms
				$.each(this.$('.runtime-is'), function () {
					var platformName = this.id.split('-').reverse()[0];
					var platform = $('#runtime-configuration-details-' + platformName);
					self.$('#add-runtime-' + platformName).click(function () {
						self.formAttributes._appendKeyValueRow.call(self, 'runtime-' + platformName);
					});
					if (self.values.runtime === undefined || self.values.runtime[platformName] === undefined) {
						self.formAttributes._fillKeyValueRows.call(self, 'runtime-' + platformName); //empty row
						platform.toggle(); // hide
					} else {
						self.formAttributes._fillKeyValueRows.call(self, 'runtime-' + platformName, self.values.runtime[platformName]); // all previous values
					}
					$(this).change(function () {
						platform.toggle();
					});
				});

				// Dynamic selects

				this.formAttributes._fillConfigurations.call(this, 'framework', this.$('#framework-name').val(), true);
				this.formAttributes._fillConfigurations.call(this, 'controller', this.$('#controller-name').val(), true);

				this.$('#framework-name').change(function () {
					self.formAttributes._fillConfigurations.call(self, 'framework', this.value);
				});
				this.$('#controller-name').change(function () {
					self.formAttributes._fillConfigurations.call(self, 'controller', this.value);
				});

				// Key-value tables
				this.formAttributes._fillKeyValueRows.call(this, 'framework_configuration', this.values.framework_configuration);
				this.$('#add-framework_configuration').click(function (event) {
					event.preventDefault();
					self.formAttributes._appendKeyValueRow.call(self, 'framework_configuration');
				});

				this.formAttributes._fillKeyValueRows.call(this, 'controller_configuration', this.values.controller_configuration);
				this.$('#add-controller_configuration').click(function (event) {
					event.preventDefault();
					self.formAttributes._appendKeyValueRow.call(self, 'controller_configuration');
				});

				// Parameters
				this.formAttributes._fillParameters.call(this, 'parameters', this.values.parameters);
				this.$('#add-parameters').click(function (event) {
					event.preventDefault();
					self.formAttributes._prependParameter.call(self, 'parameters');
				});

				return this.$el;
			},

			_prependParameter: function (where, values) {
				var self = this,
				el = this.$('#' + where);
				if (el.attr('data-nextid') === undefined) {
					el.attr('data-nextid', 0);
				}
				var nextid =  el.attr('data-nextid'),
				cellid = where + '[' + nextid + ']',
				id = where + '-' + nextid;
				el.attr('data-nextid', parseInt(nextid) + 1);

				el.prepend(this.formAttributes.parameterTable({
					id: id,
					cellid: cellid,
					showProcessingType: true,
					showGroup: false,
					showDeleteButton: true,
					types: this.additionalData.type(),
					processingTypes: this.additionalData.processingType(),
					values: values === undefined ? {} : values
				}));
				var selected = this.$('#' + id + '-type select').val();
				this.formAttributes._fillParameterSettings.call(self, cellid, id, selected, values === undefined ? {} : values);

				this.$('#' + id + '-delete-row', el).click(function (event) {
					$('#' + $(event.srcElement || event.target).attr('data-id'), el).remove();
				});
				this.$('#' + id + '-type select').change(function () {
					self.formAttributes._fillParameterSettings.call(self, cellid, id, this.value);
				});
				Claun.forms.enhance(this);

			},

			_fillParameters: function (where, data) {
				if (data === undefined || Object.keys(data).length === 0) {
					return;
				}
				var self = this;
				$.each(data, function () {
					self.formAttributes._prependParameter.call(self, where, this);
				})
			},

			_fillConfigurations: function (type, name, initial) {
				var configsselect = this.$('#' + type + '-configuration'),
				value = this.values[type] !== undefined ? this.values[type]['configuration'] : false;
				configsselect.empty();
				if (this.additionalData[type]()[name]) {
					$.each(this.additionalData[type]()[name], function (idx, configname) {
						configsselect.append('<option value="' + _.escape(configname) + '" ' + (initial && value === configname ? 'selected="selected"' : '') + '>' + _.escape(configname) + '</option>')
					});
				}
				configsselect.selectmenu({
					width: configsselect.width() * 2
				});
			}

		};


		return ApplicationFormSettings;
	});