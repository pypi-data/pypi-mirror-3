/*
 * views/environment/configuration.js
 *
 * Configuration of the environment.
 * Uses element as a modal dialog
 *
 */
define([
	'core/claun',
	'tabs/environment/models/environment',
	'text!tabs/environment/templates/configuration.html',
	'jqueryui_selectmenu'
	], function (Claun, Cluster, ConfigurationTemplate) {
		var EnvConfiguration = Backbone.View.extend({
			initialize: function () {
				this.template = _.template(ConfigurationTemplate);
				this.model = new Cluster.Configuration;

				Claun.dispatcher.on('environment:show:configuration', this.render, this);
			},

			events: {
				"change input[type=checkbox]": "checkboxChanged",
				"click #configuration-close": "hideOverlay",
				"click #configuration-form-discard" : "configDiscarded",
				"click #configuration-form-save" : "configSaved",
				"click #configuration-form-save-close" : "configSavedClosed"
			},

			/*
			 * Resets all inputs to theirs default values.
			 * Commits changes to the server.
			 */
			configDiscarded: function () {
				var inputs = this.$('input[type!=hidden], select'),
				config = this.model,
				self = this,
				batchId = Claun.batchOperations.register(inputs.length);
				this.preRenderDialog();
				inputs.each(function(num, i) {
					var model = config.get(i.id);
					model.save({
						value: model['default']
					}, {
						success: function () {
							Claun.batchOperations.success(batchId, i.id);
						},
						error: function () {
							Claun.batchOperations.fail(batchId, i.id);
						}
					});
				});
				var interval = setInterval(function () {
					var result = Claun.batchOperations.result(batchId);
					if (result === true || typeof result === 'object') {
						if (result === true) {
							Claun.messages.info('Environment configuration discarded.');
						} else {
							Claun.messages.error('Some parameters were not discarded (' + result.join(', ') + ').');
						}
						clearInterval(interval);
						self.render();
					}
				}, 500);
			},

			/*
			 * Commits current values of all inputs to server.
			 */
			configSaved: function (event, finishedCallback) {
				var inputs = this.$('input[type!=hidden], select'),
				config = this.model,
				self = this,
				batchId = Claun.batchOperations.register(inputs.length);
				finishedCallback = finishedCallback === undefined ? function () {
					self.render();
				} : finishedCallback;
				this.preRenderDialog();
				inputs.each(function(num, i) {
					var model = config.get(i.id);
					if (i.type === 'checkbox') {
						i.value = i.checked;
					}
					model.save({
						value: i.value
					}, {
						success: function () {
							Claun.batchOperations.success(batchId, i.id);
						},
						error: function () {
							Claun.batchOperations.fail(batchId, i.id);
						}
					});
				});
				var interval = setInterval(function () {
					var result = Claun.batchOperations.result(batchId);
					if (result === true || typeof result === 'object') {
						if (result === true) {
							Claun.messages.success('Environment configuration saved.');
						} else {
							Claun.messages.error('Some parameters were not saved (' + result.join(', ') + ').');
						}
						clearInterval(interval);
						finishedCallback();
					}
				}, 500);
			},

			configSavedClosed: function(event) {
				this.configSaved(event, function() {});
				this.hideOverlay();
			},

			/*
			 * Renders all inputs, al jquery-ui decoration should be done
			 * here. Sets-up tooltips and fetches the model from server.
			 */
			render: function () {
				this.preRenderDialog();
				var	el = this.$el,
				template = this.template;
				this.model.fetch({
					success: function (collection, response) {
						el.html(template({
							parameters: collection.toJSON()
						}));
						Claun.forms.enhance(this);
						el.dialog('option', 'title', 'Configuration');
					}
				});
			}
		});

		return EnvConfiguration;
	});