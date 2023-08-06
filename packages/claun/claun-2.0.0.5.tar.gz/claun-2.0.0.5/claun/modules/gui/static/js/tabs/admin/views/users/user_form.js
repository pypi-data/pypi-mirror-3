define([
	'core/claun',
	'text!tabs/admin/templates/users/permission_row.html',
	'form2js',
	'crypto_sha256'
	],
	function (Claun, PermissionRow) {
		var UserFormSettings = {
			permissionRow: _.template(PermissionRow),

			clean: function (result) {
				if (result.password) {
					result.passwordhash = Crypto.SHA256(result.password);
					delete result['password']
				}
				result.permissions = _.uniq(result.permissions); //squash permissions
				if (result.uid !== undefined) {
					result.id = result.uid;
					delete result.uid;
				}

				return result;
			},

			validate: function (result) {
				if (result.name === undefined) {
					Claun.messages.formError('Missing username!', this.$('#name'));
					return false;
				}

				if (result.passwordhash === undefined && this.action !== 'edit') {
					Claun.messages.formError('Missing password!', this.$('#password'));
					return false;
				}

				if (result.permissions === undefined) {
					Claun.messages.formError('Missing permission groups!', this.$('#permissions'));
					return false;
				}

				if (result.allowed !== true && result.allowed !== false) {
					Claun.messages.formError('Missing allowed flag!', this.$('#allowed'));
					return false;
				}
				
				return result;
			},

			renderForm: function () {
				return this.$formWrapper.html(
					this.template({
						action: this.action,
						values: this.values
					})
					);
			},

			initForm: function () {
				var self = this;

				// permissions
				this.$("#add-permissions").click(function (event) {
					event.preventDefault();
					self.formAttributes._appendPermissionsRow.call(self);
				});

				if (this.values.permissions === undefined || this.values.permissions.length == 0) {
					this.formAttributes._appendPermissionsRow.call(self, 'all');
				} else {
					$.each(this.values.permissions, function () {
						self.formAttributes._appendPermissionsRow.call(self, this);
					});
				}

				return this.$el;
			},

			_appendPermissionsRow: function (selected) {
				var $permissions = this.$('#permissions'),
				self = this;
				if ($permissions.attr('data-nextid') === undefined) {
					$permissions.attr('data-nextid', 0);
				}
				var nextid =  $permissions.attr('data-nextid'),
				cellid = 'permissions[' + nextid + ']',
				id = 'permissions-' + nextid;
				$permissions.attr('data-nextid', parseInt(nextid) + 1);
				$permissions.append(this.formAttributes.permissionRow({
					id: id,
					cellid: cellid,
					groupModel: this.options.groupModel,
					selected: selected
				}));
				this.$('#' + id + '-delete-row', $permissions).click(function (event) {
					$('#' + $(event.srcElement || event.target).attr('data-id'), $permissions).remove();
					if ($('tr', $permissions).length == 1) {
						self.formAttributes._appendPermissionsRow.call(self);
					}
				});
				Claun.forms.enhance(this);
			}

		};
		return UserFormSettings;
	});