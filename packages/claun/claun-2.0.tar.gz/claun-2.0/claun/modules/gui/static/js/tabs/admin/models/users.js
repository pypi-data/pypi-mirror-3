define([
	], function() {
		var User = Backbone.Model.extend({});
		var UserList = Backbone.Collection.extend({
			model: User,
			url: '/users/admin/users'
		});

		var Group = Backbone.Model.extend({});
		var GroupList = Backbone.Collection.extend({
			model: Group,
			url: '/users/admin/groups'
		});

		return {
			GroupList: GroupList,
			UserList: UserList
		}

	});