define([
	'core/claun',
	], function(Claun) {
		// Keeps information if a user is logged in and if yes, who is that user.
		var User = Backbone.Model.extend({
			// Default values
			defaults: {
				loggedIn: false,
				user: null
			},
			// Binds events and fills user from localStorage. If some user is found in the browser, a loggedIn property is set.
			initialize: function () {
				Claun.dispatcher.bind('user:changed', this.onUserChange, this);
				// set template for convenience
				var localUser = localStorage.getItem('user');
				if (localUser) {
					this.set({
						'user': Claun.json.parse(localUser),
						'loggedIn': !!localUser
					});
				}
			},

			getPermissions: function () {
				return this.get('user').permissions;
			},

			logout: function () {
				localStorage.removeItem('user');
				this.clear();
				Claun.dispatcher.trigger('user:loggedOut');
			},

			// When a user is changed (new access token, first login etc.),
			onUserChange: function (data, login) {
				// we compute the expiration time of the new token...
				var refresh_time = new Date(new Date().getTime() + parseInt(data.expires_in, 10) * 1000).getTime();
				// ...and save the data to both local storage and this model
				var user = {
					access_token: data.access_token,
					refresh_token: data.refresh_token,
					refresh_time:  refresh_time,
					permissions: data.permissions,
					name: data.name,
                    id: data.id
				};
				localStorage.setItem('user', Claun.json.stringify(user));
				this.set({
					'user': user
				});
				
				// By setting the login parameter we might prevent triggering the event.
				if (login) {
					this.set({
						'loggedIn': !!this.get('user')
					});
				}
			}
		});
		return User;
	});