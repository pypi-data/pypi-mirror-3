/*
 * views/applications/detail
 *
 * Displays details about one application - description, images and parameters.
 *
 */
define([
	'core/claun',
	'text!tabs/applications/templates/detail.html',
	'vendor/jquery-plugins/jquery.cycle.lite',
	'vendor/jquery-ui/jquery.ui.selectmenu',
	],
	function (Claun, ApplicationDetailTemplate) {
		var ApplicationDetail = Backbone.View.extend({
			initialize: function () {
				this.template = _.template(ApplicationDetailTemplate);
				Claun.dispatcher.on("applications:show:detail", this.render, this);
			},

			events: {
				"change input[type=checkbox]": "checkboxChanged",
				"click #appdetail-close": "hideOverlay",
				"click #applist-form-discard" : "appconfDiscarded",
				"click #applist-form-save": "appconfSaved",
				"click #applist-form-launch": "appLaunched"
			},

			appconfDiscarded: function (event) {
				var inputs = this.$('input[type!=hidden], select'),
				self = this,
				app = this.model,
				batchId = Claun.batchOperations.register(inputs.length);
				this.preRenderDialog();
				inputs.each(function(num, i) {
					var model = app.params.get(i.id);
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
							Claun.messages.info('Application parameters discarded.');
						} else {
							Claun.messages.error('Some parameters were not discarded (' + result.join(', ') + ').');
						}
						clearInterval(interval);
						self.render();
					}
				}, 500);
			},

			appconfSaved: function (event, finishedCallback) {
				var inputs = this.$('input[type!=hidden], select'),
				app = this.model,
				self = this,
				batchId = Claun.batchOperations.register(inputs.length);
				finishedCallback = finishedCallback === undefined ? function () {
					self.render();
				} : finishedCallback;
				this.preRenderDialog();
				inputs.each(function(num, i) {
					var model = app.params.get(i.id);
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
							Claun.messages.success('Application parameters saved.');
						} else {
							Claun.messages.error('Some parameters were not saved (' + result.join(', ') + ').');
						}
						clearInterval(interval);
						finishedCallback();
					}
				}, 500);
			},

			appLaunched: function (event) {
				var self = this;
				this.appconfSaved(event, function () {
					Claun.dispatcher.trigger('applications:start', self.model);
				})
				this.$el.dialog('close');
			},

			setApplication: function(application) {
				this.model = application;
			},

			render: function () {
				this.preRenderDialog();
				var appdetailTemplate = this.template,
				application = this.model,
				el = this.$el;
				this.model.params.fetch({
					success: function (collection, response) {
						el.html(
							appdetailTemplate({
								application: application
							}));
						Claun.forms.enhance(this);
						el.dialog('option', 'title', 'Application detail');
						var cycle = this.$('#application-images .cycle');
						cycle.cycle({
							fx: 'fade' 
						});
						var images = this.$('#application-images .cycle img');

						$.each(images, function () {
							this.width = this.naturalWidth / (this.naturalHeight / 300);
						});

						var sortedByHeight = _.sortBy(images, function(i) {
							return i.clientHeight
						}),
						sortedByWidth = _.sortBy(images, function(i) {
							return i.clientWidth
						});
						this.$('#application-images').css({
							height: sortedByHeight[sortedByHeight.length-1].height + 30
						})
						cycle.css({
							marginLeft: (cycle.width() - sortedByWidth[sortedByWidth.length - 1].width) / 2
						});

						

					}
				});
			}
		});
		return ApplicationDetail;
	});