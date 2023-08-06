define([
	'core/claun',
	],
	function(Claun) {
		var DeleteHandler = Backbone.View.extend({

			initialize: function () {
				this.name = this.options.name;
				this.securityCallback = this.options.securityCallback;
				this.triggerName = this.options.triggerName ? this.options.triggerName : this.name;
			},
			showDialog: function (event) {
				event.preventDefault();
				var id = $(event.srcElement || event.target).attr('data-id'),
				self = this;
				$('<div>Really delete "' + _.escape(id) + '"? You can\'t take it back.</div>').dialog({
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
				if (this.securityCallback && !this.securityCallback(id)) {
					return;
				}
				var self = this;
				this.model.get(id).destroy({
					success: function () {
						Claun.messages.info(self.name.firstUpper() + ' ' + id + ' was deleted.');
						Claun.dispatcher.trigger('admin:' + self.triggerName + ':deleted');
					},
					error: function (model, response) {
						Claun.messages.error(response);
					}
				});
			}

		})
		return DeleteHandler;
	});