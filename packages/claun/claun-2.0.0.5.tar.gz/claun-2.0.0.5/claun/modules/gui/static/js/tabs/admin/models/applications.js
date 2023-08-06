define([
	], function() {
		var Frameworks = Backbone.Model.extend({
			url: '/applications/admin/additional-data/frameworks'
		});

		var Controllers = Backbone.Model.extend({
			url: '/applications/admin/additional-data/controllers'
		});

		var Platforms = Backbone.Model.extend({
			url: '/applications/admin/additional-data/platforms'
		});

		var Types = Backbone.Model.extend({
			url: '/applications/admin/additional-data/type'
		});

		var ProcessingTypes = Backbone.Model.extend({
			url: '/applications/admin/additional-data/processing_type'
		});

		var AdditionalData = Backbone.Collection.extend({
			url: '/applications/admin/additional-data',
			frameworks_model: new Frameworks,
			controllers_model: new Controllers,
			platforms_model: new Platforms,
			types_model: new Types,
			processing_types_model: new ProcessingTypes,

			initialize: function (options) {
				this.allowedGroups = options && options.allowedGroups ? options.allowedGroups : [];
				Claun.dispatcher.on('admin:node:added', this.fetchAll, this);
				Claun.dispatcher.on('admin:node:updated', this.fetchAll, this);
				Claun.dispatcher.on('admin:node:deleted', this.fetchAll, this);
				Claun.dispatcher.on('admin:frameworkConfiguration:added', this.fetchAll, this);
				Claun.dispatcher.on('admin:frameworkConfiguration:updated', this.fetchAll, this);
				Claun.dispatcher.on('admin:frameworkConfiguration:deleted', this.fetchAll, this);
				Claun.dispatcher.on('admin:controllerConfiguration:added', this.fetchAll, this);
				Claun.dispatcher.on('admin:controllerConfiguration:updated', this.fetchAll, this);
				Claun.dispatcher.on('admin:controllerConfiguration:deleted', this.fetchAll, this);
				this.fetchAll();
			},

			fetchAll: function () {
				this.frameworks_model.clear().fetch();
				this.types_model.fetch();
				this.controllers_model.clear().fetch();
				this.platforms_model.clear().fetch();
				this.processing_types_model.clear().fetch();
			},

			stopPolling: function () {
				if (this.timer) {
					clearInterval(this.timer)
					this.timer = '';
				}
			},

			startPolling: function () {
				if (this.timer) {
					return;
				}
				if (this.allowedGroups.length > 0) {
					var start = false;
					$.each(this.allowedGroups, function(idx, group) {
						if ($.inArray(group, Claun.user.getPermissions()) != -1) {
							start = true;
							return;
						}
					});
					if (!start) {
						return;
					}
				}
				var self = this;
				this.timer = setInterval(function () {
					self.fetchAll();
				}, 10000);
			},

			framework: function () {
				return this.frameworks_model.toJSON();
			},

			controller: function () {
				return this.controllers_model.toJSON();
			},

			platform: function () {
				return this.platforms_model.toJSON();
			},

			type: function () {
				return this.types_model.toJSON();
			},

			processingType: function () {
				return this.processing_types_model.toJSON();
			}

		});


		var ApplicationImage = Backbone.Model.extend({});

		var ApplicationImages = Backbone.Collection.extend({
			model: ApplicationImage
		});

		var AdminApplication = Backbone.Model.extend({

			initialize: function () {
				this.images = new ApplicationImages;
				this.images.url = '/applications/admin/list/' + this.id + '/images';
				if (this.id) {
					this.images.fetch();
				}
			},
			url: function () {
				return this.id ? '/applications/admin/list/' + this.id : '/applications/admin/list';
			}
		});
		var ApplicationList = Backbone.Collection.extend({
			model: AdminApplication,
			url: '/applications/admin/list'
		});

		return {
			ApplicationList: ApplicationList,
			AdditionalData: AdditionalData
		}

	});