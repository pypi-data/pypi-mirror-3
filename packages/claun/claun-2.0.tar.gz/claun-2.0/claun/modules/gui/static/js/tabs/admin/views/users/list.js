define([
	'core/claun',
	'tabs/admin/models/users',
	'tabs/admin/views/common/form_handler',
	'tabs/admin/views/common/delete_handler',
	'tabs/admin/views/users/user_form',
	'tabs/admin/views/users/group_form',
	'text!tabs/admin/templates/users/list.html',
	'text!tabs/admin/templates/users/user_form.html',
	'text!tabs/admin/templates/users/group_form.html',
	],
	function(Claun, model, FormHandler, DeleteHandler, UserFormAttributes, GroupFormAttributes, ListTemplate, UserFormTemplate, GroupFormTemplate) {
		var AdminApplicationsView = Backbone.View.extend({
			groupModel: new model.GroupList(),
			userModel: new model.UserList(),
			template: null,
			overlay: null,
			events: {
				"click .edit-group": "editGroup",
				"click #add-group": 'addGroup',
				"click .delete-group": function (event) {
					return this.groupDeleteHandler.showDialog(event);
				},
				"click .edit-user": "editUser",
				"click #add-user": 'addUser',
				"click .delete-user": function (event) {
					return this.userDeleteHandler.showDialog(event);
				},
				"click .allow": "allowUser",
				"click .disallow": "disallowUser"
			},

			initialize: function () {
				this.model =  this.userModel;
				this.template = _.template(ListTemplate);
				this.overlay = this.options.overlay;
				this.userForm = new FormHandler({
					el: this.overlay,
					collection: this.userModel,
					template: UserFormTemplate,
					onEventRender: 'admin:user:form:show',
					formAttributes: UserFormAttributes,
					groupModel: this.groupModel,
					actionHandlers: {
						add: {
							successMessage: 'User created.',
							successEvent: 'admin:user:added',
							titleMessage: 'Add user'
						},
						edit: {
							successMessage: 'User updated.',
							successEvent: 'admin:user:updated',
							titleMessage: 'Edit user'
						}
					}
				});

				this.userDeleteHandler = new DeleteHandler({
					model: this.userModel,
					name: 'user',
					securityCallback: function (id) {
						if (id == Claun.user.get('user').name.webalize()) {
							Claun.messages.error('You can not delete yourself!');
							return false;
						}
						return true;
					}
				});

				this.groupDeleteHandler = new DeleteHandler({
					model: this.groupModel,
					name: 'group',
					securityCallback: function (id) {
						if ($.inArray(id, Claun.user.get('user').permissions) !== -1) {
							Claun.messages.error('You are a member of that group, you can not delete it.');
							return false;
						}
						return true;
					}
				});

				this.groupForm = new FormHandler({
					el: this.overlay,
					collection: this.groupModel,
					template: GroupFormTemplate,
					onEventRender: 'admin:group:form:show',
					formAttributes: GroupFormAttributes,
					actionHandlers: {
						add: {
							successMessage: 'Group created.',
							successEvent: 'admin:group:added',
							titleMessage: 'Add group'
						},
						edit: {
							successMessage: 'Group updated.',
							successEvent: 'admin:group:updated',
							titleMessage: 'Edit group'
						}
					}
				});

				Claun.dispatcher.on('admin:group:deleted', this.render, this);
				Claun.dispatcher.on('admin:group:updated', this.render, this);
				Claun.dispatcher.on('admin:group:added', this.render, this);
				Claun.dispatcher.on('admin:user:deleted', this.render, this);
				Claun.dispatcher.on('admin:user:updated', this.render, this);
				Claun.dispatcher.on('admin:user:added', this.render, this);
			},

			addUser: function (event) {
				event.preventDefault();
				Claun.dispatcher.trigger('admin:user:form:show', 'add');
			},

			editUser: function (event) {
				event.preventDefault();
				var id = $(event.srcElement || event.target).attr('data-id');
				this.userForm.setActionAttribute('edit', 'values', this.userModel.get(id).attributes);
				Claun.dispatcher.trigger('admin:user:form:show', 'edit');
				if (id == Claun.user.get('user').name.webalize()) {
					Claun.messages.warning('You are editing yourself!');
				}
			},

			allowUser: function (event) {
				var id = $(event.srcElement || event.target).attr('data-id');
				if (id == Claun.user.get('user').name.webalize()) {
					Claun.messages.warning('You are editing yourself!');
				}
				this.updateRow(event, this.model, function (model) {
					return {
						allowed: true
					}
				}, function (el) {
					el.html("&#x2713;").removeClass('allow').addClass('disallow');
				});
			},

			disallowUser: function (event) {
				var id = $(event.srcElement || event.target).attr('data-id');
				if (id == Claun.user.get('user').name.webalize()) {
					Claun.messages.warning('You are editing yourself!');
				}
				this.updateRow(event, this.model, function (model) {
					return {
						allowed: false
					}
				}, function (el) {
					el.html("&#x2717;").removeClass('disallow').addClass('allow');
				});
			},

			addGroup: function (event) {
				event.preventDefault();
				Claun.dispatcher.trigger('admin:group:form:show', 'add');
			},

			editGroup: function (event) {
				event.preventDefault();
				var id = $(event.srcElement || event.target).attr('data-id');
				if ($.inArray(id, Claun.user.get('user').permissions) !== -1) {
					Claun.messages.error('You are a member of that group, you can not edit it!')
				} else {
					this.groupForm.setActionAttribute('edit', 'values', this.groupModel.get(id).attributes);
					Claun.dispatcher.trigger('admin:group:form:show', 'edit');
				}
			},

			render: function () {
				this.preRenderTab();
				var self = this,
				batchId = Claun.batchOperations.register(2);
				this.groupModel.fetch({
					success: function () {
						Claun.batchOperations.success(batchId, 'groups');
					},
					error: function () {
						Claun.batchOperations.fail(batchId, 'groups');
					}
				});
				this.userModel.fetch({
					success: function () {
						Claun.batchOperations.success(batchId, 'users');
					},
					error: function () {
						Claun.batchOperations.fail(batchId, 'users');
					}
				});
				var interval = setInterval(function () {
					var result = Claun.batchOperations.result(batchId);
					if (result === true || typeof result === 'object') {
						if (result === true) {
							self.$el.html(self.template({
								users: self.userModel.toJSON(),
								groups: self.groupModel.toJSON()
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
			main: AdminApplicationsView,
			groups: ['admin']
		}

	});