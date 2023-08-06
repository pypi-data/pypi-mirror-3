define([
	'core/claun',
	'core/views/keyboard',
	'text!core/templates/loginform.html',
	'text!core/templates/changepasswordform.html',
	'vendor/utf8/utf8_encode.min',
    'vendor/base64/base64_encode.min',
	], function(Claun, Keyboard, LoginTemplate, ChangePasswordTemplate) {
		var UserView = Backbone.View.extend({

			initialize: function () {
				this.loginTemplate = _.template(LoginTemplate);
				this.changePasswordTemplate = _.template(ChangePasswordTemplate);
				this.$el.dialog({
					title: "Login to claun",
					modal: true,
					width: '70%',
					height: $(document).height() * 0.7,
					draggable: false,
					resizable: false,
					autoOpen: false
				});

				this.keyboard = new Keyboard({
					el: '#keyboard',
					disabledKeys: ['tab', 'return']
				});

				Claun.dispatcher.on('user:loggedIn', this.render, this);
				Claun.dispatcher.on('user:notoken', this.renderLoginForm, this);
				Claun.dispatcher.on('user:changepwd', this.changePassword, this);
			},

			events: {
				'click a.focus': 'changeFocus',
				'click a.erase': 'eraseField'
			},

			logoutUser: function () {
				Claun.user.logout();
			},

			registerButtons: function () {
				var self = this;
				Claun.dispatcher.trigger('buttons:add', 'Logout user', function () {
					self.logoutUser();
				});

				Claun.dispatcher.trigger('buttons:add', 'Change password', function () {
					self.renderChangePasswordForm();
				});
			},

			onChangePassword: function (event) {
				var user = Claun.user.get('user'),
				old_password = this.$('#old_password').val(),
				new_password = this.$('#new_password').val(),
				new_password_2 = this.$('#new_password_2').val();

				if (old_password == '') {
					Claun.messages.formError('Old password is required!', $('#old_password'));
					return;
				}
				if (new_password == '') {
					Claun.messages.formError('New password is required!', $('#new_password'));
					return;
				}
				if (new_password_2 == '') {
					Claun.messages.formError('New password again is required!', $('#new_password_2'));
					return;
				}

				if (new_password !== new_password_2) {
					Claun.messages.error('New passwords are not equal.');
					return;
				}

				var self = this;
				Claun.ajax({
					contentType: 'application/json',
					data: '{"oldpassword": "' + old_password + '","newpassword": "' + new_password + '"}',
					url: Claun.configuration.baseurl + 'users/' + user.id.webalize(),
					type: 'PUT',
					success: function () {
						Claun.messages.success('Password changed.');
						self.$el.dialog('close');
					}
				});
				
			},

			renderChangePasswordForm: function () {
				this.$el.html(this.changePasswordTemplate({
					user: Claun.user.get('user')
				})).dialog({
					title: "Change password",
					closeOnEscape: true,
					open: function(event, ui) {
						$(".ui-dialog-titlebar-close", $(this).parent()).show();
					}
				});
				var self = this;
				this.$('input:submit, button, input:checkbox', this.$el).button();
				this.$('#changepasswordform', this.$el).submit(function(event) {
					event.preventDefault();
					self.onChangePassword();
				});

				this.$('input[type=text], input[type=password]').blur(function (event) {
					event.preventDefault();
					if (self.keyboard.target !== '#' + this.id) {
						$(this).removeClass('focus');
					}
				}).focus(function (event) {
					event.preventDefault();
					$(this).addClass('focus');
					self.keyboard.setTarget('#' + this.id);
				});

				this.keyboard.setTarget('#username');
				this.keyboard.render();
				this.$el.dialog('open');
				return this;
			},

			renderLoginForm: function () {
				this.$el.html(this.loginTemplate({
					user: Claun.user.get('user')
				})).dialog({
					title: "Login to claun",
					closeOnEscape: false,
					open: function(event, ui) {
						$(".ui-dialog-titlebar-close", $(this).parent()).hide();
					}
				});
				var self = this;
				this.$('input:submit, button, input:checkbox', this.$el).button();
				this.$('#loginform', this.$el).submit(function(event) {
					event.preventDefault();
					self.onLogin();
				});

				this.$('input[type=text], input[type=password]').blur(function (event) {
					event.preventDefault();
					if (self.keyboard.target !== '#' + this.id) {
						$(this).removeClass('focus');
					}
				}).focus(function (event) {
					event.preventDefault();
					$(this).addClass('focus');
					self.keyboard.setTarget('#' + this.id);
				});

				this.keyboard.setTarget('#username');
				this.keyboard.render();
				this.$el.dialog('open');
				return this;
			},

			changeFocus: function (event) {
				event.preventDefault();
				var id = $(event.srcElement || event.target).attr('data-target');
				this.keyboard.setTarget(id);
			},

			eraseField: function (event) {
				event.preventDefault();
				var id = $(event.srcElement || event.target).attr('data-target');
				this.$(id).val('');
			},

			// After submitting the login form, an AJAX request is sent to the OAuth server to obtain the access token, refresh token and expiration time.
			// Form is not sent in the traditional way, it is only processed here.
			onLogin: function (event) {
				var uname = $('#username');
				var pwd = $('#password');
				// If username or password field is empty, an error is displayed.
				if (pwd.val() === '' || uname.val() === '') {
					Claun.messages.formError("Fill in username and password!", uname.val() === '' ? uname : pwd);
					return;
				}
				var self = this;
				// If the fields are OK, an AJAX request is issued.
				Claun.ajax({
					url: Claun.configuration.baseurl + 'users/auth/token',
					data: {
						grant_type: 'password',
						username: uname.val(),
						password: pwd.val()
					},
					// We set the appropriate headers for an OAuth request. We have to set client_id and client_password outside.
					// Having it in plain text in the code is not the best way, but there is no other one.
					beforeSend: function (xhr) {
						xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8');
						xhr.setRequestHeader('X-Claun-Authentication', 'Basic ' + base64_encode(Claun.configuration.client_id + ':' + Claun.configuration.client_password));
					},
					// Do not cache!
					cache: false,
					// In case of error, display some fancy error message. The error message relies on the nice format of the error message and awaits JSON
					// with an 'error_description' key.
					error: function (xhr, status, error) {
						try {
							error = Claun.json.parse(xhr.responseText).error_description;
						} catch (SyntaxError) {
							error = xhr.responseText;
						}
						Claun.messages.error("Cannot verify on server, check and try again, please. (" + xhr.status + ": " + error + ")");
					},
					// When the user is verified on the server, we set user data to the model
					// and show some nice message.
					success: function (data) {
						self.$el.dialog('close');
						Claun.dispatcher.trigger('user:changed', data, true);
						Claun.messages.info("You are logged in!");
						Claun.dispatcher.trigger('user:loggedIn');
					}
				});
			}
		});
		return UserView;
	});
