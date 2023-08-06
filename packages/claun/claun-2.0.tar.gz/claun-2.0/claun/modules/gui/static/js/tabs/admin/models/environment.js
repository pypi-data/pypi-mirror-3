define([
	], function() {
		var Node = Backbone.Model.extend({});
		var NodeList = Backbone.Collection.extend({
			model: Node,
			url: '/environment/admin/nodes',
			byPriority: function () {
				return this.sortBy(function (c) {
					return c.get('masterpriority');
				});
			}
		});

		var Parameter = Backbone.Model.extend({});
		var ParameterList = Backbone.Collection.extend({
			model: Parameter,
			url: '/environment/admin/parameters'
		});

		var Projections = Backbone.Model.extend({
			url: '/environment/admin/additional-data/projections'
		});

		var Types = Backbone.Model.extend({
			url: '/environment/admin/additional-data/type'
		});

		var AdditionalData = Backbone.Collection.extend({
			url: '/environment/admin/additional-data',
			projections_model: new Projections,
			types_model: new Types,

			initialize: function (options) {
				this.allowedGroups = options && options.allowedGroups ? options.allowedGroups : [];
				Claun.dispatcher.on('admin:param:added', this.fetchAll, this);
				Claun.dispatcher.on('admin:param:updated', this.fetchAll, this);
				Claun.dispatcher.on('admin:param:deleted', this.fetchAll, this);
				this.fetchAll();
			},

			fetchAll: function () {
				this.types_model.clear().fetch();
				this.projections_model.clear().fetch();
			},

			stopPolling: function () {
				if (this.timer) {
					clearInterval(this.timer);
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

			projection: function () {
				return this.projections_model.toJSON();
			},

			type: function () {
				return this.types_model.toJSON();
			}

		});

		return {
			NodeList:NodeList,
			ParameterList: ParameterList,
			AdditionalData: AdditionalData
		
		};
	});