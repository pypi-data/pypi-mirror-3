/*
 * models/applications.js
 *
 * Model for the applications module.
 *
 */
define([
	'core/models/parameter'
	], function(Parameter) {
		var ApplicationParameters = Backbone.Collection.extend({
			model: Parameter
		});

		var Application = Backbone.Model.extend({
			initialize: function () {
				this.params = new ApplicationParameters();
				this.params.url = '/applications/list/' + this.id + '/parameters';
			},
			url: function () {
				return '/applications/list/' + this.id;
			}

		});
		var ApplicationList = Backbone.Collection.extend({
			model: Application,
			url: '/applications/list'
		});

		return ApplicationList;

	});