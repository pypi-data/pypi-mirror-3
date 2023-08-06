define([
	'core/claun',
	'text!tabs/admin/templates/common/keyvaluerow.html',
	'tabs/admin/views/common/parameter_settings',
	'form2js',
	],
	function(Claun, KeyValueRow, ParameterSettings) {

		var DefaultFormAttributes = function () {
			return {
				keyValueRow: _.template(KeyValueRow),
				init: function () {
					var self = this;
					this.$('form').submit(function (event) {
						self.submit(event);
					}).bind('reset', function (event) {
						self.discard(event);
					});

					$.each(this.$('.closable'), function () {
						var self = this;
						$('>th *', self).css({
							cursor: 'pointer'
						}).click(function () {
							$('>td>*', self).toggle();
							$(self).toggleClass('closed');
						});
					});

					$.each(this.$('.closed'), function () {
						$('>td>*', this).toggle();
					});
					this.formAttributes.initForm.call(this);
					Claun.forms.enhance(this);
				},

				render: function () {
					this.preRenderDialog.call(this);
					this.$el.dialog('option', 'title', this.actionHandlers[this.action].titleMessage).html(this.formAttributes.renderForm.call(this));
					this.formAttributes.init.call(this);
				},

				renderForm: function () {
					return this.$formWrapper.html(
						this.template({
							context: this,
							values: this.values
						})
						);
				},
				
				clean: function (result) {
					return result;
				},

				validate: function (result) {
					return result;
				},

				initForm: function () {
				},

				_appendKeyValueRow: function (where, key, value) {
					var self = this,
					table = this.$('#' + where);
					if (table.attr('data-nextid') === undefined) {
						table.attr('data-nextid', 0);
					}
					var nextid =  table.attr('data-nextid'),
					cellid = where + '[' + nextid + ']',
					id = where + '-' + nextid;
					table.attr('data-nextid', parseInt(nextid) + 1);
					table.append(this.formAttributes.keyValueRow({
						id: id,
						cellid: cellid,
						key: key,
						value: value
					}));
					this.$('#' + id + '-delete-row', table).click(function (event) {
						$('#' + $(event.srcElement || event.target).attr('data-id'), table).remove();
						if ($('tr', table).length == 1) {
							self.formAttributes._appendKeyValueRow.call(self, where);
						}
					});
				},

				_fillKeyValueRows: function (where, data) {
					var self = this;
					if (data === undefined || Object.keys(data).length == 0) {
						this.formAttributes._appendKeyValueRow.call(self, where);
						return;
					}
					$.each(data, function(key, value) {
						self.formAttributes._appendKeyValueRow.call(self, where, key, value);
					})
				},

				_fillParameterSettings: function (cellId, id, name, values) {
					var el = this.$('#' + id + '-settings');
					if (ParameterSettings[name] !== undefined) {
						var renderer = new ParameterSettings[name]({
							parameterCellId: cellId,
							parameterId: id,
							values: values === undefined ? {} : values
						});
						el.html(renderer.render());
					} else {
						el.html('-');
					}
				}
			}
		};

		var DefaultActionHandlers = function () {
			return {
				add: {
					submitCallback: function (result, event) {
						var self = this;
						this.collection.create(result, {
							success: function () {
								Claun.messages.success(self.actionHandlers['add'].successMessage);
								self.$el.dialog('close');
								Claun.dispatcher.trigger(self.actionHandlers['add'].successEvent);
							},
							error: function (response) {
								Claun.messages.error(response.responseText);
							}
						});
					},
					successMessage: 'Object created.',
					successEvent: 'admin:object:added',
					titleMessage: 'Add object'
				},
				edit: {
					submitCallback: function (result, event) {
						if (result.id === undefined) {
							Claun.messages.error('Unknown id!');
							return false;
						}
						var self = this;
						this.collection.get(result.id).clear().save(result, {
							success: function () {
								Claun.messages.success(self.actionHandlers['edit'].successMessage);
								self.$el.dialog('close');
								Claun.dispatcher.trigger(self.actionHandlers['edit'].successEvent);
							},
							error: function (response) {
								Claun.messages.error(response.responseText);
							}
						});
					},
					successMessage: 'Object updated.',
					successEvent: 'admin:object:updated',
					titleMessage: 'Edit object'
				}
			}
		};

		var FormHandler = Backbone.View.extend({
			values: {},

			initialize: function () {
				this.template = _.template(this.options.template);
				this.$formWrapper = $('<div></div>');
				this.additionalData = this.options.additionalData;
				this.callbackContext = this.options.callbackContext === undefined ? this : this.options.callbackContext;
				this.collection = this.options.collection;
				this.formAttributes = $.extend(true, new DefaultFormAttributes, this.options.formAttributes);
				this.actionHandlers = $.extend(true, new DefaultActionHandlers, this.options.actionHandlers);
				this.action = this.options.action ? this.options.action : 'add';
				Claun.dispatcher.on(this.options.onEventRender, this.onEventRender, this);
			},

			onEventRender: function (action) {
				this.setAction(action);
				this.render();
			},

			setAction: function (action) {
				if (!(action in this.actionHandlers)) {
					return;
				}
				this.action = action;
			},

			setActionAttribute: function (action, attrname, value) {
				if (action in this.actionHandlers) {
					this.actionHandlers[action][attrname] = value;
				}
			},

			events: {
				"change input[type=checkbox]": "checkboxChanged",
				'click #overlay-close': 'hideOverlay'
			},

			discard: function (event) {
				event.preventDefault();
				this.render();
				if (this.actionHandlers[this.action].discardCallback) {
					this.actionHandlers[this.action].discardCallback.call(this.callbackContext, event);
				}
			},

			submit: function (event) {
				event.preventDefault();
				var result = this.validateResult(form2js(event.target.id, '-'));
				if (result === false) {
					return;
				}
				if (this.actionHandlers[this.action].submitCallback) {
					this.actionHandlers[this.action].submitCallback.call(this.callbackContext, result, event);
				}
			},

			validateResult: function (result) {
				result = this.cleanResult(result);
				return this.formAttributes.validate.call(this.callbackContext, result);
			},

			cleanResult: function (result) {
				return this.formAttributes.clean.call(this.callbackContext, result);
			},

			render: function () {
				this.values = this.actionHandlers[this.action].values === undefined ? {} : this.actionHandlers[this.action].values;
				return this.formAttributes.render.call(this.callbackContext);
			}

		})
		return FormHandler;
	});