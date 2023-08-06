/*
 * models/environment.js
 *
 * Model for the environment module.
 */
define([
	'core/models/parameter'
	], function (Parameter) {
		// // This represents one computer in the cluster and is filled directly from our REST API.
		// To work this like magic, our API has to provide an id parameter for each computer and must return a list of computers.
		var Computer = Backbone.Model.extend({
			});

		// Single computer has then to be accessible by calling Collections's url + its id.
		var Cluster = Backbone.Collection.extend({
			model: Computer,
			url: '/environment/cluster',
			// Collection can be sorted by masterpriority parameter.
			byPriority: function () {
				return this.sortBy(function (c) {
					return c.get('masterpriority');
				});
			}
		});

		/*
		 * Configuration contains lots of parameters.
		 */
		var Configuration = Backbone.Collection.extend({
			model: Parameter,
			url: '/environment/configuration'
		});

		return {
			Configuration: Configuration,
			Cluster: Cluster
		};


	});