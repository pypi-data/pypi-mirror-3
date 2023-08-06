/*
 * views/applications/list
 *
 * Handles list of all applications.
 * Uses the claun.modules.applications module from the server part.
 */
define([
	'core/claun',
	'tabs/applications/models/applications',
	'tabs/applications/views/detail',
	'tabs/applications/views/running',
	'text!tabs/applications/templates/list.html',
	'vendor/jquery-plugins/jquery.cycle.lite',
	],
	function(Claun, ApplicationList, ApplicationDetail, RunningApps, ApplicationListTemplate) {
		var ApplicationsView = Backbone.View.extend({
			model: new ApplicationList,
			template: null,
			overlay: null,
			events: {
				"click .application": "showAppDetail" // displays applciation detail
			},

			/*
			 * when creating, pass `el` and `overlay` options
			 * @param overlay - modal dialog where the configuration will be displayed
			 * @param el - element where contents of this module will be displayed
			 */
			initialize: function () {
				this.template = _.template(ApplicationListTemplate);
				this.overlay = this.options.overlay;
				this.appDetail = new ApplicationDetail({
					el: this.overlay
				});
				this.runningApps = new RunningApps({
					model: this.model
					});
			},

			showAppDetail: function (event) {
				event.preventDefault();
				this.appDetail.setApplication(this.model.get(event.currentTarget.id));
				Claun.dispatcher.trigger('applications:show:detail');
			},

			render: function () {
				this.preRenderTab();
				var self = this;
				this.model.fetch({
					success: function() {
						self.$el.html(self.template({
							apps: self.model.toJSON()
						}));
						this.$('.cycle').cycle({
							fx: 'fade'
						});
					}
				});
			}
		});
		return {
			main: ApplicationsView
		}

	});