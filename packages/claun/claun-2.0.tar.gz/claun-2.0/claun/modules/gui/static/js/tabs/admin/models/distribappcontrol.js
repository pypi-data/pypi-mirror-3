define([
	], function() {

		var FrameworkConfiguration = Backbone.Model.extend({});
		var FrameworkConfigurationList = Backbone.Collection.extend({
			model: FrameworkConfiguration,
			url: '/distribappcontrol/admin/framework-configurations'
		});

		var ControllerConfiguration = Backbone.Model.extend({});
		var ControllerConfigurationList = Backbone.Collection.extend({
			model: ControllerConfiguration,
			url: '/distribappcontrol/admin/controller-configurations'
		});

		return {
			FrameworkConfigurationList: FrameworkConfigurationList,
			ControllerConfigurationList: ControllerConfigurationList
		}

	});