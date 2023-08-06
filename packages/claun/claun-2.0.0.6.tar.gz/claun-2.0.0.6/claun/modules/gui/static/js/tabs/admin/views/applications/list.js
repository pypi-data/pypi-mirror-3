define([
    'core/claun',
    'tabs/admin/models/applications',
    'tabs/admin/views/common/form_handler',
    'tabs/admin/views/common/delete_handler',
    'tabs/admin/views/applications/application_form',
    'tabs/admin/views/applications/image_editor',
    'text!tabs/admin/templates/applications/list.html',
    'text!tabs/admin/templates/applications/application_form.html',
    ],
    function(Claun, model, FormHandler, DeleteHandler, ApplicationFormAttributes, ImageEditor, AllAppsListTemplate, AppFormTemplate) {
        var groups = ['admin', 'admin_applications'];
        var AdminApplicationsView = Backbone.View.extend({
            model: new model.ApplicationList(),
            template: null,
            overlay: null,
            events: {
                "click .makeVisible": "makeVisible",
                "click .makeInvisible": "makeInvisible",
                "click .images": "manageImages",
                "click .edit": "edit",
                "click #add-application": 'add',
                "click .delete": function (event) {
                    return this.deleteHandler.showDialog(event);
                }
            },

            initialize: function () {
                this.template = _.template(AllAppsListTemplate);
                this.overlay = this.options.overlay;

                this.additionalData = new model.AdditionalData({
                    allowedGroups: groups
                });
                this.additionalData.startPolling();
                Claun.dispatcher.on('user:notoken', this.additionalData.stopPolling, this.additionalData);
                Claun.dispatcher.on('user:loggedOut', this.additionalData.stopPolling, this.additionalData);

                this.appForm = new FormHandler({
                    el: this.overlay,
                    additionalData: this.additionalData,
                    collection: this.model,
                    template: AppFormTemplate,
                    onEventRender: 'admin:application:form:show',
                    formAttributes: ApplicationFormAttributes,
                    actionHandlers: {
                        add: {
                            successMessage: 'Application created.',
                            successEvent: 'admin:application:added',
                            titleMessage: 'Add application'
                        },
                        edit: {
                            successMessage: 'Application updated.',
                            successEvent: 'admin:application:updated',
                            titleMessage: 'Edit application'
                        }
                    }
                });

                this.deleteHandler = new DeleteHandler({
                    model: this.model,
                    name: 'application'
                });

                this.imageEditor = new ImageEditor({
                    el: this.overlay,
                    model: this.model
                });
                Claun.dispatcher.on('admin:application:added', this.render, this);
                Claun.dispatcher.on('admin:application:updated', this.render, this);
                Claun.dispatcher.on('admin:application:deleted', this.render, this);
                Claun.dispatcher.on("admin:application:image:deleted", this.render, this);
                Claun.dispatcher.on("admin:application:image:uploaded", this.render, this);
            },

            makeVisible: function (event) {
                this.updateRow(event, this.model, function (model) {
                    return {
                        visible: true
                    }
                }, function (el) {
                    el.html("&#x2713;").removeClass('makeVisible').addClass('makeInvisible');
                });
            },

            makeInvisible: function (event) {
                this.updateRow(event, this.model, function (model) {
                    return {
                        visible: false
                    }
                }, function (el) {
                    el.html("&#x2717;").addClass('makeVisible').removeClass('makeInvisible');
                });
            },

            edit: function (event) {
                event.preventDefault();
                this.appForm.setActionAttribute('edit', 'values', this.model.get($(event.srcElement || event.target).attr('data-id')).attributes);
                Claun.dispatcher.trigger('admin:application:form:show', 'edit');
            },

            manageImages: function (event) {
                event.preventDefault();
                this.imageEditor.setApplication(this.model.get($(event.srcElement || event.target).attr('data-id')));
                Claun.dispatcher.trigger('admin:application:images:show');
            },

            _displayModalDialog: function (message) {
                $('<div>' + message + '</div>').dialog({
                        resizable: false,
                        movable: false,
                        height: 300,
                        width: 400,
                        title: 'Hmm...',
                        modal: true,
                        buttons: {
                            "OK": function() {
                                $( this ).dialog( "close" );
                            }
                        }
                    });
            },

            add: function (event) {
                event.preventDefault();
                if (!Object.keys(this.additionalData.framework()).length) {
                    this._displayModalDialog('No framework configurations are available. Create some, please.');
                    return;
                }

                if (!Object.keys(this.additionalData.controller()).length) {
                    this._displayModalDialog('No controller configurations are available. Create some, please.');
                    return;
                }

                if (!Object.keys(this.additionalData.platform()).length) {
                    this._displayModalDialog('No platforms are available. Create some nodes, please.');
                    return;
                }

                Claun.dispatcher.trigger('admin:application:form:show', 'add');
            },

            render: function () {
                this.preRenderTab();
                var self = this;
                this.model.fetch({
                    success: function () {
                        self.$el.html(self.template({
                            apps: self.model.toJSON()
                        }));
                        Claun.forms.enhance(self);
                    }
                });
            }
        });
        return {
            main: AdminApplicationsView,
            groups: groups
        }

    });