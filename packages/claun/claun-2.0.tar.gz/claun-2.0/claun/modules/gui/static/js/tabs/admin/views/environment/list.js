define([
    'core/claun',
    'tabs/admin/models/environment',
    'tabs/admin/views/common/form_handler',
    'tabs/admin/views/common/delete_handler',
    'tabs/admin/views/environment/node_form',
    'tabs/admin/views/environment/parameter_form',
    'text!tabs/admin/templates/environment/list.html',
    'text!tabs/admin/templates/environment/node_form.html',
    'text!tabs/admin/templates/environment/parameter_form.html',
    ],
    function(Claun, model, FormHandler, DeleteHandler, NodeFormAttributes, ParameterFormAttributes, ListTemplate, NodeFormTemplate, ParameterFormTemplate) {
        var groups = ['admin', 'admin_environment'];
        var AdminEnvironmentView = Backbone.View.extend({
            nodeModel: new model.NodeList,
            parametersModel: new model.ParameterList,
            template: null,
            overlay: null,
            events: {
                "click .makeUserEditable": "makeUserEditable",
                "click .makeUserNotEditable": "makeUserNotEditable",
                "click #add-parameter": 'addParameter',
                "click .edit-parameter": "editParameter",
                "click .delete-parameter": function (event) {
                    return this.parameterDeleteHandler.showDialog(event);
                },
                "click .makeConnected": "makeConnected",
                "click .makeDisconnected": "makeDisconnected",
                "click .priorityUp": "priorityUp",
                "click .priorityDown": "priorityDown",
                "click #add-node": 'addNode',
                "click .edit-node": "editNode",
                "click .delete-node": function (event) {
                    return this.nodeDeleteHandler.showDialog(event);
                }
            },

            initialize: function () {
                this.template = _.template(ListTemplate);
                this.overlay = this.options.overlay;
                this.additionalData = new model.AdditionalData({
                    allowedGroups: groups
                });
                this.additionalData.startPolling();
                Claun.dispatcher.on('user:notoken', this.additionalData.stopPolling, this.additionalData);
                Claun.dispatcher.on('user:loggedOut', this.additionalData.stopPolling, this.additionalData);

                this.nodeDeleteHandler = new DeleteHandler({
                    model: this.nodeModel,
                    name: 'node'
                });

                this.parameterDeleteHandler = new DeleteHandler({
                    model: this.parametersModel,
                    name: 'param'
                });

                this.nodeForm = new FormHandler({
                    el: this.overlay,
                    additionalData: this.additionalData,
                    collection: this.nodeModel,
                    template: NodeFormTemplate,
                    onEventRender: 'admin:node:form:show',
                    formAttributes: NodeFormAttributes,
                    actionHandlers: {
                        add: {
                            successMessage: 'Node created.',
                            successEvent: 'admin:node:added',
                            titleMessage: 'Add node'
                        },
                        edit: {
                            successMessage: 'Node updated.',
                            successEvent: 'admin:node:updated',
                            titleMessage: 'Edit node'
                        }
                    }
                });
                this.parameterForm = new FormHandler({
                    el: this.overlay,
                    additionalData: this.additionalData,
                    collection: this.parametersModel,
                    template: ParameterFormTemplate,
                    onEventRender: 'admin:param:form:show',
                    formAttributes: ParameterFormAttributes,
                    actionHandlers: {
                        add: {
                            successMessage: 'Parameter created.',
                            successEvent: 'admin:param:added',
                            titleMessage: 'Add parameter'
                        },
                        edit: {
                            successMessage: 'Parameter updated.',
                            successEvent: 'admin:param:updated',
                            titleMessage: 'Edit parameter'
                        }
                    }
                });

                Claun.dispatcher.on('admin:node:added', this.render, this);
                Claun.dispatcher.on('admin:node:updated', this.render, this);
                Claun.dispatcher.on('admin:node:deleted', this.render, this);
                Claun.dispatcher.on('admin:param:added', this.render, this);
                Claun.dispatcher.on('admin:param:updated', this.render, this);
                Claun.dispatcher.on('admin:param:deleted', this.render, this);
            },

            makeConnected: function (event) {
                this.updateRow(event, this.nodeModel, function (model) {
                    return {
                        connected: true
                    }
                }, function (el) {
                    el.html("&#x2713;").removeClass('makeConnected').addClass('makeDisconnected');
                });
            },

            makeDisconnected: function (event) {
                this.updateRow(event, this.nodeModel, function (model) {
                    return {
                        connected: false
                    }
                }, function (el) {
                    el.html("&#x2717;").removeClass('makeDisconnected').addClass('makeConnected');
                });
            },

            priorityUp: function (event) {
                this.updateRow(event, this.nodeModel, function (model) {
                    return {
                        masterpriority: model.get('masterpriority') + 1
                    }
                }, function (el) {
                    Claun.dispatcher.trigger('admin:node:updated');
                });
            },

            priorityDown: function (event) {
                this.updateRow(event, this.nodeModel, function (model) {
                    return {
                        masterpriority: model.get('masterpriority') - 1
                    }
                }, function (el) {
                    Claun.dispatcher.trigger('admin:node:updated');
                });
            },

            addNode: function (event) {
                event.preventDefault();

                if (!Object.keys(this.additionalData.projection()).length) {
                    this._displayModalDialog('No projections are available. Create some projection parameters, please.');
                    return;
                }
                Claun.dispatcher.trigger('admin:node:form:show', 'add');
            },
			
            editNode: function (event) {
                event.preventDefault();
                this.nodeForm.setActionAttribute('edit', 'values', this.nodeModel.get($(event.srcElement || event.target).attr('data-id')).attributes);
                Claun.dispatcher.trigger('admin:node:form:show', 'edit');
            },

            addParameter: function (event) {
                event.preventDefault();
                Claun.dispatcher.trigger('admin:param:form:show', 'add');
            },

            editParameter: function (event) {
                event.preventDefault();
                this.parameterForm.setActionAttribute('edit', 'values', this.parametersModel.get($(event.srcElement || event.target).attr('data-id')).attributes);
                Claun.dispatcher.trigger('admin:param:form:show', 'edit');
            },

            makeUserEditable: function (event) {
                this.updateRow(event, this.parametersModel, function (model) {
                    return {
                        user_editable: true
                    }
                }, function (el) {
                    el.html("&#x2713;").removeClass('makeUserEditable').addClass('makeUserNotEditable');
                });
            },

            makeUserNotEditable: function (event) {
                this.updateRow(event, this.parametersModel, function (model) {
                    return {
                        user_editable: false
                    }
                }, function (el) {
                    el.html("&#x2717;").removeClass('makeUserNotEditable').addClass('makeUserEditable');
                });
            },

            render: function () {
                this.preRenderTab();
                var self = this,
                batchId = Claun.batchOperations.register(2);
                this.nodeModel.fetch({
                    success: function () {
                        Claun.batchOperations.success(batchId, 'nodes');
                    },
                    error: function () {
                        Claun.batchOperations.fail(batchId, 'nodes');
                    }
                });
                this.parametersModel.fetch({
                    success: function () {
                        Claun.batchOperations.success(batchId, 'parameters');
                    },
                    error: function () {
                        Claun.batchOperations.fail(batchId, 'parameters');
                    }
                });
                var interval = setInterval(function () {
                    var result = Claun.batchOperations.result(batchId);
                    if (result === true || typeof result === 'object') {
                        if (result === true) {
                            self.$el.html(self.template({
                                nodes: self.nodeModel.byPriority(),
                                parameters: self.parametersModel.toJSON()
                            }));
                            Claun.forms.enhance(self);
                        } else {
                            Claun.messages.error('Can\'t fetch models.');
                        }
                        clearInterval(interval);

                    }
                }, 300);

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
            }
        });
        return {
            main: AdminEnvironmentView,
            groups: groups
        }

    });