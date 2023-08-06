define([
	'core/claun',
	'core/models/user',
	'core/views/main',
	'tabs/applications/views/list',
	'tabs/environment/views/list',
	'tabs/admin/views/applications/list',
	'tabs/admin/views/users/list',
	'tabs/admin/views/environment/list',
	'tabs/admin/views/distribappcontrol/list',
	], function(ClaunWrapper, User, AppView, AppList, EnvList, AdminApps, AdminUsers, AdminEnvironment, AdminDistribAppControl) {
		return {
			initialize: function() {
				// We can define a mock console when we don't want any output.
				if (! Claun.configuration.console) {
					window.console = {
						log: function (msg) {
						}
					};
				}
				// When DOM is ready, do some magic
				$(function () {
					ClaunWrapper.initialize('#message', {
						'applications': AppList,
						'environment': EnvList,
						'admin_applications': AdminApps,
						'admin_users': AdminUsers,
						'admin_environment': AdminEnvironment,
						'frameworks_and_controllers': AdminDistribAppControl
					});
					ClaunWrapper.user = new User;
					
					var appview = new AppView({
						el: '#container',
						overlayElement: '#overlay',
						loginElement: '#login'
					});

				});
			}
		}
	});
