define([
	'core/claun',
	'tabs/admin/models/distribappcontrol',
	'tabs/admin/views/common/form_handler',
	'tabs/admin/views/common/delete_handler',
	'tabs/admin/views/distribappcontrol/framework_configuration_form',
	'tabs/admin/views/distribappcontrol/controller_configuration_form',
	'text!tabs/admin/templates/distribappcontrol/list.html',
	'text!tabs/admin/templates/distribappcontrol/framework_configuration_form.html',
	'text!tabs/admin/templates/distribappcontrol/controller_configuration_form.html',
	],
	function(Claun, model, FormHandler, DeleteHandler, FrameworkConfigurationFormAttributes, ControllerConfigurationFormAttributes, ListTemplate, FrameworkConfigurationFormTemplate, ControllerConfigurationFormTemplate) {
		var AdminDistribAppControlView = Backbone.View.extend({
			frameworkConfigurationsModel: new model.FrameworkConfigurationList,
			controllerConfigurationsModel: new model.ControllerConfigurationList,
			template: null,
			overlay: null,
			events: {
				"click #add-controller-configuration": 'addControllerConfiguration',
				"click .edit-controller-configuration": "editControllerConfiguration",
				"click .delete-controller-configuration": function (event) {
					return this.controllerConfigurationDeleteHandler.showDialog(event);
				},
				"click #add-framework-configuration": 'addFrameworkConfiguration',
				"click .edit-framework-configuration": "editFrameworkConfiguration",
				"click .delete-framework-configuration": function (event) {
					return this.frameworkConfigurationDeleteHandler.showDialog(event);
				}
			},

			initialize: function () {
				this.template = _.template(ListTemplate);
				this.overlay = this.options.overlay;

				this.frameworkConfigurationDeleteHandler = new DeleteHandler({
					model: this.frameworkConfigurationsModel,
					name: 'framework configuration',
					triggerName: 'frameworkConfiguration'
				});

				this.controllerConfigurationDeleteHandler = new DeleteHandler({
					model: this.controllerConfigurationsModel,
					name: 'controller configuration',
					triggerName: 'controllerConfiguration'
				});

				this.frameworkConfigurationForm = new FormHandler({
					el: this.overlay,
					collection: this.frameworkConfigurationsModel,
					template: FrameworkConfigurationFormTemplate,
					onEventRender: 'admin:frameworkConfiguration:form:show',
					formAttributes: FrameworkConfigurationFormAttributes,
					actionHandlers: {
						add: {
							successMessage: 'Framework configuration created.',
							successEvent: 'admin:frameworkConfiguration:added',
							titleMessage: 'Add framework configuration'
						},
						edit: {
							successMessage: 'Framework configuration updated.',
							successEvent: 'admin:frameworkConfiguration:updated',
							titleMessage: 'Edit framework configuration'
						}
					}
				});
				this.controllerConfigurationForm = new FormHandler({
					el: this.overlay,
					collection: this.controllerConfigurationsModel,
					template: ControllerConfigurationFormTemplate,
					onEventRender: 'admin:controllerConfiguration:form:show',
					formAttributes: ControllerConfigurationFormAttributes,
					actionHandlers: {
						add: {
							successMessage: 'Controller configuration created.',
							successEvent: 'admin:controllerConfiguration:added',
							titleMessage: 'Add controller configuration'
						},
						edit: {
							successMessage: 'Controller configuration updated.',
							successEvent: 'admin:controllerConfiguration:updated',
							titleMessage: 'Edit controller configuration'
						}
					}
				});

				Claun.dispatcher.on('admin:frameworkConfiguration:added', this.render, this);
				Claun.dispatcher.on('admin:frameworkConfiguration:updated', this.render, this);
				Claun.dispatcher.on('admin:frameworkConfiguration:deleted', this.render, this);
				Claun.dispatcher.on('admin:controllerConfiguration:added', this.render, this);
				Claun.dispatcher.on('admin:controllerConfiguration:updated', this.render, this);
				Claun.dispatcher.on('admin:controllerConfiguration:deleted', this.render, this);
			},

			addFrameworkConfiguration: function (event) {
				event.preventDefault();
				Claun.dispatcher.trigger('admin:frameworkConfiguration:form:show', 'add');
			},

			editFrameworkConfiguration: function (event) {
				event.preventDefault();
				this.frameworkConfigurationForm.setActionAttribute('edit', 'values', this.frameworkConfigurationsModel.get($(event.srcElement || event.target).attr('data-id')).attributes);
				Claun.dispatcher.trigger('admin:frameworkConfiguration:form:show', 'edit');
			},

			addControllerConfiguration: function (event) {
				event.preventDefault();
				Claun.dispatcher.trigger('admin:controllerConfiguration:form:show', 'add');
			},

			editControllerConfiguration: function (event) {
				event.preventDefault();
				this.controllerConfigurationForm.setActionAttribute('edit', 'values', this.controllerConfigurationsModel.get($(event.srcElement || event.target).attr('data-id')).attributes);
				Claun.dispatcher.trigger('admin:controllerConfiguration:form:show', 'edit');
			},

			render: function () {
				this.preRenderTab();
				var self = this,
				batchId = Claun.batchOperations.register(2);
				this.frameworkConfigurationsModel.fetch({
					success: function () {
						Claun.batchOperations.success(batchId, 'frameworkConfigurations');
					},
					error: function () {
						Claun.batchOperations.fail(batchId, 'frameworkConfigurations');
					}
				});
				this.controllerConfigurationsModel.fetch({
					success: function () {
						Claun.batchOperations.success(batchId, 'controllerConfigurations');
					},
					error: function () {
						Claun.batchOperations.fail(batchId, 'controllerConfigurations');
					}
				});
				var interval = setInterval(function () {
					var result = Claun.batchOperations.result(batchId);
					if (result === true || typeof result === 'object') {
						if (result === true) {
							self.$el.html(self.template({
								frameworkConfigurations: self.frameworkConfigurationsModel.toJSON(),
								controllerConfigurations: self.controllerConfigurationsModel.toJSON()
							}));
							Claun.forms.enhance(self);
						} else {
							Claun.messages.error('Can\'t fetch models.');
						}
						clearInterval(interval);

					}
				}, 300);

			}
		});
		return {
			main: AdminDistribAppControlView,
			groups: ['admin', 'admin_distribappcontrol']
		}

	});