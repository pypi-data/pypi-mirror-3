define([
	'core/claun',
	'text!tabs/admin/templates/environment/platform_row.html',
	],
	function (Claun, PlatformRow) {
		var NodeFormAttributes = {
			platformRow: _.template(PlatformRow),
			clean: function (result) {
				if (result.projections && result.projections.is) {
					$.each(result.projections.is, function (k, v) {
						if (!v) {
							delete result.projections[k];
						}
					});
					delete result.projections.is;
				} else {
					result.projections = {};
				}

				if (result.nid) {
					result.id = result.nid;
					delete result.nid;
				}

				if (result.port) {
					result.port = parseInt(result.port);
				}

				$.each(Object.keys(result.projections), function () {
					var target = null,
					repaired = {};
					target = result['projections'][this];
					if (target === undefined) {
						return;
					}

					$.each(target, function() {
						if (this.key !== undefined && this.value !== undefined) {
							repaired[this.key] = this.value;
						}
					})
					if (Object.keys(repaired).length > 0) {
						result['projections'][this] = repaired;
					}
				});

				return result;
			},

			validate: function (result) {
				if (result.hostname === undefined) {
					Claun.messages.formError('Missing hostname!', this.$('#hostname'));
					return false;
				}

				if (result.ip === undefined || result.ip.match(/^\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}$/) === null) {
					Claun.messages.formError('Missing or bad IP address!', this.$('#ip'));
					return false;
				}
				if (result.port === undefined || isNaN(result.port)) {
					Claun.messages.formError('Missing or bad port!', this.$('#port'));
					return false;
				}

				if (result.fqdn === undefined) {
					Claun.messages.formError('Missing FQDN!', this.$('#fqdn'));
					return false;
				}

				if (result.platforms === undefined || result.platforms.length == 0) {
					Claun.messages.formError('Missing at least one platform!', this.$('#platforms'));
					return false;
				}

				if (result.connected === undefined) {
					Claun.messages.formError('Missing connected attribute!', this.$('#connected'));
					return false;
				}

				return result;
			},

			renderForm: function () {
				var projections = this.additionalData.projection();
				if (this.values.projections) {
					projections = _.uniq(Object.keys(this.values.projections).concat(_.values(projections)));
				}

				return this.$formWrapper.html(
					this.template({
						action: this.action,
						projections: projections,
						values: this.values
					})
					);
			},

			initForm: function () {
				var self = this;

				// watch out for changes, see application_form
				$.each(this.$('.projections-is'), function () {
					var projectionName = this.id.split('-').reverse()[0];
					var projection = $('#projections-configuration-details-' + projectionName);
					self.$('#add-projections-' + projectionName).click(function () {
						self.formAttributes._appendKeyValueRow.call(self, 'projections-' + projectionName);
					});
					if (self.values.projections === undefined || self.values.projections[projectionName] === undefined) {
						self.formAttributes._fillKeyValueRows.call(self, 'projections-' + projectionName);
						projection.toggle();
					} else {
						self.formAttributes._fillKeyValueRows.call(self, 'projections-' + projectionName, self.values.projections[projectionName]);
					}
					$(this).change(function () {
						projection.toggle();
					});
				});

				// Key-value tables

				this.$('#add-platform').click(function () {
					self.formAttributes._appendPlatformRow.call(self, 'platforms');
				});

				if (self.values.platforms === undefined) {
					this.formAttributes._appendPlatformRow.call(this, 'platforms');
				} else {
					$.each(self.values.platforms, function () {
						self.formAttributes._appendPlatformRow.call(self, 'platforms', this);
					});
				}
				return this.$el;
			},

			_appendPlatformRow: function (where, value) {
				var self = this,
				table = this.$('#' + where);
				if (table.attr('data-nextid') === undefined) {
					table.attr('data-nextid', 0);
				}
				var nextid =  table.attr('data-nextid'),
				cellid = where + '[' + nextid + ']',
				id = where + '-' + nextid;
				table.attr('data-nextid', parseInt(nextid) + 1);
				table.append(this.formAttributes.platformRow({
					id: id,
					cellid: cellid,
					value: value
				}));
				this.$('#' + id + '-delete-row', table).click(function (event) {
					$('#' + $(event.srcElement || event.target).attr('data-id'), table).remove();
					if ($('tr', table).length == 0) {
						self.formAttributes._appendPlatformRow.call(self, where);
					}
				});
			}

		};
		return NodeFormAttributes;
	});