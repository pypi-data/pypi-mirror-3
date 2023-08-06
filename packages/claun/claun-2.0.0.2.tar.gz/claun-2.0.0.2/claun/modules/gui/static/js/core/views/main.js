define([
	'core/claun',
	'core/views/user',
	'text!core/templates/general.html',
	'utf8',
	'base64',
	], function(Claun, UserView, generalTemplate) {
		// Main application view.
		var AppView = Backbone.View.extend({
			// General template is the template used for normal content visible to a logged in user.
			generalTemplate: null,
			el: null,
			tabs: {},

			initialize: function () {
				Claun.dispatcher.on('user:loggedIn', this.render, this);
				Claun.dispatcher.on('user:loggedOut', this.render, this);
				Claun.dispatcher.on('tab:show', this.renderTab, this);
				Claun.dispatcher.on('buttons:add', this.addButton, this);
				Claun.dispatcher.on('buttons:remove', this.removeButton, this);

				this.buttons = {};
				this.generalTemplate = _.template(generalTemplate);
				this.overlay = this.options.overlayElement;
				this.$overlay = $(this.overlay);
				this.$overlay.dialog({
					modal: true,
					width: 1200,
					title: '',
					height: 920,
					draggable: false,
					resizable: false,
					autoOpen: false,
					open: function(){
						var self = this;
						$('.ui-widget-overlay').click(function () {
							$(self).dialog('close');
						})
					}
				});

				this.userView = new UserView({
					el: this.options.loginElement
				});

				this.render();
			},

			events: {
				'click #reload': 'reload'
			},

			reload: function () {
				window.location.reload();
			},

			addButton: function (name, callback) {
				var button = $('<li><button id="' + name.webalize() + '">' + name + '</button></li>')
				button.click(callback);
				this.buttons[name] = button;
			},

			removeButton: function (name) {
				delete this.buttons[name];
				this.$('#' + name, '.buttons').remove();
			},

			render: function () {
				if (!Claun.user.get('loggedIn')) {
					this.userView.renderLoginForm();
				} else {
					this.userView.registerButtons();
					this.$el.html(this.generalTemplate());
					this._prepareTabs();
					this.renderTab(Object.keys(this.tabs)[0]);
				}
				var buttonEl = this.$('.buttons');
				$.each(this.buttons, function (key, value) {
					buttonEl.append(value);
				});
				this.$('button', buttonEl).button();
				return this;
			},

			_prepareTabs: function () {
				var tabs = this.tabs;
				var overlayEl = this.overlay;
				var tabsel = $('#tabs');
				$.each(Claun.tabs, function (name, stuff) {
					var append = false;
					if (stuff.groups !== undefined) {
						$.each(stuff.groups, function(idx, group) {
							if ($.inArray(group, Claun.user.getPermissions()) != -1) {
								append = true;
								return;
							}
						});
					} else {
						append = true;
					}
					if (!append) {
						return;
					}


					$('ul', tabsel).append('<li><a href="#' + name.webalize() + '">' + name.unwebalize() + '</a></li>');
					tabsel.append('<div id="' + name.webalize() + '"></div>');

					tabs[name.webalize()] = new stuff.main({
						el: '#'+name.webalize(),
						overlay: overlayEl
					});

					$('#tabs a[href=#' + name.webalize() + ']').click(function () {
						Claun.dispatcher.trigger('tab:show', name.webalize());
					});
				});

				this.$('#tabs').tabs().addClass('ui-tabs-vertical ui-helper-clearfix');
				this.$('li', '#tabs').removeClass('ui-corner-top').addClass('ui-corner-left');
				this.$('.ui-tabs-vertical .ui-tabs-panel').addClass('ui-corner-top');
				this.$('.ui-tabs-nav').removeClass('ui-corner-all').removeClass('ui-widget-header');
				this.$('.ui-tabs-panel').height($(document).height() - 115); //ugly constant
			},

			renderTab: function(name) {
				var tabs = this.tabs;
				$.each(tabs, function(name, tab) {
					tab.close();
				});
				this.tabs[name].render();
				return this;
			}


		});
		return AppView;
	});
