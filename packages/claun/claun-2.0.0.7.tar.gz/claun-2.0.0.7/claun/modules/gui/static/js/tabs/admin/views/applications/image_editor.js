define([
	'core/claun',
	'text!tabs/admin/templates/applications/image_editor.html',
	'vendor/jquery-plugins/jquery.ajaxfileupload',
	],
	function (Claun, EditorTemplate) {
		var ImageEditor = Backbone.View.extend({
			initialize: function () {
				this.applications = this.options.model;
				this.template = _.template(EditorTemplate);
				Claun.dispatcher.on("admin:application:images:show", this.render, this);
				Claun.dispatcher.on("admin:application:image:deleted", this.refresh, this);
				Claun.dispatcher.on("admin:application:image:uploaded", this.refresh, this);
			},

			setApplication: function(application) {
				this.currentApp = application;
			},

			events: {
				'click #overlay-close': 'hideOverlay',
				'click .delete-image': 'delete'
			},

			refresh: function (app) {
				this.preRenderDialog();
				var self = this;
				app.images.fetch({
					success: function () {
						self.setApplication(app);
						self.render();
					}
				});
			},

			'delete': function (event) {
				event.preventDefault();
				var id = $(event.srcElement || event.target).attr('data-id'),
				self = this;
				$('<div>Really delete ' + id + '? You can\'t take it back.</div>').dialog({
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
							self.invokeDelete(id);
						}
					}
				});
			},

			invokeDelete: function (id) {
				var self = this;
				this.currentApp.images.get(id).destroy({
					success: function () {
						Claun.messages.info('Image ' + id + ' was deleted.');
						Claun.dispatcher.trigger("admin:application:image:deleted", self.currentApp);
					},
					error: function (model, response) {
						Claun.messages.error(response);
					}
				});
			},

			render: function () {
				this.preRenderDialog();
				this.$el.dialog('option', 'title', "Image management").html(this.template({
					application: this.currentApp
				}));

				var submitter = this.$('#submit-files'),
				self = this,
                params = {};
				submitter.button();
				submitter.click(function (event) {
					event.preventDefault();
				})

                params['access_token'] = Claun.user.get('user').access_token;
                if (Claun.configuration.client_authentication) {
                    params['claun_authentication'] = Claun.componentSignature();
                }
				this.$('input[type="file"]').ajaxfileupload({
					action: this.currentApp.images.url,
					params: params,
					submit_button: submitter,
					'onComplete': function(response) {
						self.$('#variable-status').html('Idle');
						if (response === '') {
							Claun.messages.success('Image was uploaded.')
							Claun.dispatcher.trigger("admin:application:image:uploaded", self.currentApp);
						} else {
							if (response.status !== undefined) { // internal error
								Claun.messages.error(response.message);
							} else { // error from server
								var contents = $(response).text(),
								text = contents ? Claun.json.parse(contents).error_description : response;
								Claun.messages.error(text);
							}
						}
					},
					'onStart': function() {
						self.$('#variable-status').html('Working');
					},
					'onCancel': function() {
						Claun.messages.error('Image can not be uploaded:' + this)
					}
				});
			}

		});
		return ImageEditor;
	});