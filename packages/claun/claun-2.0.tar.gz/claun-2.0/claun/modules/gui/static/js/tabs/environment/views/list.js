/*
 * views/environment/list.js
 *
 * Main view for the environment module.
 *
 * It displays information about computers in the cluster, uses
 * the claun.modules.environment module on claun server.
 *
 * This tab can call HW control and display monitoring stats of
 * all nodes in the cluster.
 *
 * The template contains a table with information about nodes
 * and a giant button that displays the configuration window.
 *
 */
define([
	'core/claun',
	'tabs/environment/models/environment',
	'tabs/environment/views/configuration',
	'text!tabs/environment/templates/list.html',
	], function(Claun, Cluster, EnvConfiguration, EnvironmentTemplate) {
		var EnvironmentView = Backbone.View.extend({
			model: new Cluster.Cluster,
			template: null,
			overlay: null,
			events: {
				"click #env-configuration-button": "showConfiguration", // big button
				"click .hw-control": "hwControlHandle" // generates ajax calls to control HW of the nodes
			},

			/*
			 * when creating, pass `el` and `overlay` options
			 * @param overlay - modal dialog where the configuration will be displayed
			 * @param el - element where contents of this module will be displayed
			 */
			initialize: function () {
				this.template = _.template(EnvironmentTemplate);
				this.overlay = this.options.overlay;
				this.configDetail = new EnvConfiguration({
					el: this.overlay
				});
				Claun.dispatcher.on('user:notoken', this.stopPolling, this);
				Claun.dispatcher.on('user:loggedOut', this.stopPolling, this);

				Claun.dispatcher.on('admin:node:added', this.reloadComputers, this);
				Claun.dispatcher.on('admin:node:updated', this.reloadComputers, this);
				Claun.dispatcher.on('admin:node:deleted', this.reloadComputers, this);

				var self = this;
				Claun.dispatcher.trigger('buttons:add', 'Reload computers', function () {
					self.reloadComputers();
				});
			},
			showConfiguration: function (event) {
				event.preventDefault();
				Claun.dispatcher.trigger('environment:show:configuration');
			},

			invokeHwControlHandle: function (href) {
				$.ajax({
					url: href,
					success: function (data) {
						Claun.messages.info("Request was accepted, wait a few moments, please...");
					},
					error: function (xhr, status, error) {
						try {
							Claun.messages.error('Bad news: ' + Claun.json.parse(xhr.responseText).error_description);
						} catch (err) {
							Claun.messages.error('Bad news: ' + error);
						}
					}
				});
			},

			hwControlHandle: function (event) {
				event.preventDefault();
				var self = this,
				$src = $(event.srcElement || event.target),
				node = ($($src.parent().parent().siblings()[0]).children()[$src.parent().parent().children().index($src.parent())].innerHTML);

				$('<div>Really do "' + (event.srcElement || event.target).text + '" on "' + node + '"?</div>').dialog({
					resizable: false,
					movable: false,
					height: 300,
					width: 400,
					title: 'Are you sure?',
					modal: true,
					buttons: {
						"No": function() {
							$( this ).dialog( "close" );
						},
						"Go ahead": function() {
							$( this ).dialog( "close" );
							self.invokeHwControlHandle((event.srcElement || event.target).href);
						}
					}
				});
			},

			reloadComputers: function () {
				var self = this;
				Claun.ajax({
					url: this.model.url,
					contentType: 'application/json',
					type: 'PUT',
					data: '{"action": "reload"}',
					success: function () {
						Claun.messages.info('Nodes were reloaded on the server.');
						if ((self.$el.is(':visible'))) {
							self.render();
						}
					}
				});
			},

			/*
			 * Displays all nodes ordered by priority.
			 * jQuery-UI init is also here.
			 */
			render: function () {
				this.preRenderTab();
				var self = this;
				this.model.fetch({
					success: function() {
						self.monitorInterval = setInterval(function() { //monitors
							self.model.fetch({
								success: function() {
									$.each(self.$('.monitor'), function(id, monitor) {
										var identification = monitor.id.split('-'),
										monitors = self.model.get(identification[0]).get('monitors');
										if (monitors[identification[1]] != undefined) {
											$(monitor).html(monitors[identification[1]].value);
										}
									});
								}
							});

						}, 5000);

						self.$el.html(self.template({
							cluster: self.model.byPriority()
						}));
						Claun.forms.enhance(self);
					}
				});
			},

			/*
			 * On tab close, unregisters the monitorInterval.
			 */
			close: function () {
				this.stopPolling();
				this.$el.empty();
			},

			stopPolling: function () {
				if (this.monitorInterval != undefined) {
					clearInterval(this.monitorInterval);
				}
			}
		});
		return {
			main: EnvironmentView
		}

	})