define([
	'core/claun',
	'text!tabs/applications/templates/runningbox.html',
	],
	function(Claun, RunningBoxTemplate) {
		var RunningApps = Backbone.View.extend({
			template: null,
			running: [],

			initialize: function () {
				Claun.dispatcher.on('applications:start', this.applicationStart, this);
				Claun.dispatcher.on('applications:started', this.showRunningBox, this);
				Claun.dispatcher.on('applications:stop', this.applicationStop, this);

				Claun.dispatcher.on('user:notoken', this.stopPolling, this);
				Claun.dispatcher.on('user:loggedOut', this.stopPolling, this);
				Claun.dispatcher.on('user:loggedIn', this.startPolling, this);

				this.startPolling();
			},

			startPolling: function () {
				var self = this;
				this.interval = setInterval(function () {
					self.checkStatus(self);
				}, 3000);
			},

			stopPolling: function () {
				if (this.interval !== undefined) {
					clearInterval(this.interval);
				}
			},
			
			applicationStart: function (application) {
				if (this.running.length > 0) { // remove if multiple apps allowed
					Claun.messages.error('Another application is already running!')
					return;
				}

				if ($.inArray(application.get('id'), this.running) != -1) {
					Claun.messages.info('Application is already running.')
					return;
				}
				var data = '{"action": "' + application.get('actions').start + '"}',
				running = this.running;
				Claun.ajax({
					url: application.url(),
					contentType: 'application/json',
					accepts: {script: 'application/json'},
					dataType: 'json',
					type: 'PUT',
					data: data,
					statusCode: {
						202: function() {
							Claun.dispatcher.trigger('applications:started', application);
							running.push(application.get('id'))
						}
					}
				});
			},

			showRunningBox: function (application) {
				var template = _.template(RunningBoxTemplate)({
					name: application.get('name')
				});
				$('body').append(template);
				var box = $('#running-box');
				box.addClass('ui-corner-all').addClass('ui-widget-content');
				$('button', box).button().click(function () {
					Claun.dispatcher.trigger('applications:stop', application);
				});
			},

			closeRunningBox: function () {
				$('#running-box').remove();
			},

			applicationCrashed: function (application) {
				Claun.messages.error(application.get('name') + ' ' + application.get('status'));
				this.applicationStop(application, function() {});
				this.closeRunningBox();
			},

			applicationStop: function (application, success_func) {
				if (success_func == undefined) {
					success_func = function() {
						self.closeRunningBox();
						Claun.messages.info('Application has successfully stopped.');
					}
				}

				var data = '{"action": "' + application.get('actions').stop + '"}';
				var self = this;
				if (application.collection === undefined) { // collection might have been re-fetched in the meantime
					application.collection = this.model;
				}
				Claun.ajax({
					url: application.url(),
					contentType: 'application/json',
					accepts: {script: 'application/json'},
					type: 'PUT',
					dataType: 'json',
					data: data,
					success: function () {
						var idx = self.running.indexOf(application.get('id'))
						if (idx != -1) {
							self.running.splice(idx, 1);
						}
						success_func();
					}
				});
			},

			checkStatus: function (runningApps) {
				runningApps.model.fetch({
					success: function() {
						runningApps.model.each(function(m) {
							var status = m.get('status');
							if (status !== null && status !== 'running') {  // crashed app
								runningApps.applicationCrashed(m);
							}
							if (status == 'running' && $.inArray(m.get('id'), runningApps.running)  === -1) {
								Claun.dispatcher.trigger('applications:started', m);
								runningApps.running.push(m.get('id'))
							}
							if (status == null && $.inArray(m.get('id'), runningApps.running) !== -1) {
								Claun.messages.info('Application was stopped by someone else.');
								runningApps.running.splice($.inArray(m.get('id'), runningApps.running), 1);
								runningApps.closeRunningBox();
							}

						});
					}
				});
			}
		});


		return RunningApps;

	});