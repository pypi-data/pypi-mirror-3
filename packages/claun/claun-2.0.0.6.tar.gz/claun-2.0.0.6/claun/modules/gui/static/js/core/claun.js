define([
    'core/batch',
    'text!core/templates/forms_inputs/slider.html',
    'text!core/templates/forms_inputs/dropdown.html',
    'vendor/utf8/utf8_encode.min',
    'vendor/base64/base64_encode.min',
    'vendor/jquery-ui/jquery-ui-1.8.16.custom.min',
    'vendor/codemirror/codemirror-compressed'
    ], function(BatchOperations, SliderTemplate, DropdownTemplate) {
        Claun.initialize = function(messageboxid, tabs) {
            // String customization
            String.prototype.firstUpper = function() {
                return this.charAt(0).toUpperCase() + this.slice(1);
            }

            String.prototype.endsWith = function(suffix) {
                return this.indexOf(suffix, this.length - suffix.length) !== -1;
            };

            String.prototype.startsWith = function(prefix) {
                return this.indexOf(prefix) == 0;
            };

            String.prototype.webalize = function () {
                return this.replace(/\ /g, '-').toLowerCase();
            };

            String.prototype.unwebalize = function () {
                return this.replace(/-/g, ' ').replace(/_/g, ' ').firstUpper();
            };

            String.prototype.isValidJSON = function () {
                try {
                    Claun.json.parse(this);
                } catch (e) {
                    return false;
                }
                return true;
            };

            // Backbone View common methods
            Backbone.View.prototype.checkboxChanged = function (event) {
                var target = event.srcElement || event.target;
                target.checked = !!target.checked;
                var src = $(target);
                if (!src.hasClass('notextchange')) {
                    if (src.is(':checked')) {
                        $('label span', src.parent()).text('YES');
                    } else {
                        $('label span', src.parent()).text('NO');
                    }
                }
            };

            Backbone.View.prototype.hideOverlay = function (event) {
                if (event !== undefined) {
                    event.preventDefault();
                }
                this.$el.dialog('close');
            };

            Backbone.View.prototype.preRenderDialog = function() {
                this.$el.html('<div class="loader">@</div>');
                this.$el.dialog('option', 'title', 'Loading...');
                this.$el.dialog('open');
            };

            Backbone.View.prototype.preRenderTab = function() {
                this.$el.html('<div class="loader">@</div>');
            };

            Backbone.View.prototype.close = function () {
                this.$el.empty();
            };

            Backbone.View.prototype.updateRow = function (event, collection, updateValueCallback, successCallback, errorCallback) {
                event.preventDefault();
                var id = $(event.srcElement || event.target).attr('data-id'),
                model = collection.get(id);
                model.save(updateValueCallback(model),
                {
                    success: function () {
                        if (successCallback) {
                            successCallback($(event.srcElement || event.target));
                        }
                    },
                    error: function (model, response) {
                        if (errorCallback) {
                            errorCallback(model, response)
                        } else {
                            Claun.messages.error(response);
                        }
                    }
                });
            },

            // Global event dispatcher
            Claun.dispatcher = _.clone(Backbone.Events);

            // Global shortcuts
            Claun.json = JSON;

            // Tabs that will be displayed
            Claun.tabs = tabs

            // Messages
            Claun.messages = {
                timeout: 3,
                messagesList: [],
                timeouts: [],
                displayed: false,
                box: $(messageboxid).dialog({
                    resizable: false,
                    draggable: false,
                    position: 'top',
                    width: '60%',
                    height: 0,
                    autoOpen: false
                }).css({
                    opacity: 0.7
                }),

                generic: function (message, type) {
                    this.messagesList.push({
                        message:message,
                        type: type
                    });
                    Claun.dispatcher.trigger('claun:message:added');
                },

                success: function (message) {
                    return this.generic(message, 'success');
                },

                info: function (message) {
                    return this.generic(message, 'info');
                },

                warning: function (message) {
                    return this.generic(message, 'warning');
                },

                error: function (message) {
                    var msg = message;
                    if (message.status !== undefined && message.responseText !== undefined) {
                        msg = message.status + ": " + Claun.json.parse(message.responseText).error_description;
                    }
                    return this.generic(msg, 'error');
                },

                formError: function (message, el) {
                    Claun.messages.error(message);
                    if (el) {
                        el.addClass('error');
                        el.bind('change', function (event) {
                            el.removeClass('error');
                        });
                    }
                }
            };

            Claun.dispatcher.on('claun:message:added', function () {
                var self = this;
                if (this.displayed) { // Hide the old one
                    self.box.dialog('close');
                    self.messagesList.shift();
                    self.displayed = false;
                    $.each(this.timeouts, function () {
                        clearTimeout(this);
                    });
                    this.timeouts = [];
                }

                this.box.dialog('option', 'title', _.escape(this.messagesList[0].message));
                this.box.dialog('option', 'dialogClass', this.messagesList[0].type);
                this.box.dialog('open');
                self.displayed = true;
                $(messageboxid).hide(); // Get rid of body of the dialog
                Claun.messages.timeouts.push( setTimeout(function () {
                    self.box.dialog('close');
                    self.messagesList.shift();
                    self.displayed = false;
                }, 1000 * this.timeout) );
            }, Claun.messages);

            // Form input generators
            Claun.forms = {

                enhance: function (root, keepSubmit) {
                    if (keepSubmit === undefined) {
                        root.$('form').submit(function(event) {
                            event.preventDefault();
                        });
                    }
                    root.$('input:submit, button, input:checkbox').button();
                    root.$('select').selectmenu({
                        format: _.escape
                    });
                    root.$('.form-configuration-help').button().click(Claun.tooltip);
                    root.$('.show-configuration-help').button().click(function (event) {
                        if ($(this).attr('target') != '_blank') {
                            console.log('You have to set the target attribute to _blank to activate this link.')
                            event.preventDefault();
                        }
                    });

                    $.each(root.$('textarea.codemirror'), function () {
                        var self = this,
                        mirror = CodeMirror.fromTextArea(self, {
                            mode: 'javascript',
                            json: true,
                            lineNumbers: true,
                            tabSize: 8,
                            onChange: function () {
                                mirror.save();
                            }
                        });
                    });

                    $.each(root.$('.slider'), function () {
                        var $this = $(this);
                        var $input = $('input#' + $this.attr('data-id'));
                        $input.change(function () {
                            $this.slider({
                                value: $input.val()
                            });
                        });
                        $this.slider({
                            range: 'min',
                            step: $this.attr('data-type') === 'float' ? 0.1 : 1,
                            value: parseFloat($this.attr('data-default')),
                            min: parseFloat($this.attr('data-min')),
                            max: parseFloat($this.attr('data-max')),
                            slide: function (event, ui) {
                                $input.val( $this.attr('data-type') === 'float' && ui.value % 1 === 0 ? ui.value + '.0' : ui.value );
                            }
                        });
                    });
                },

                _generic: function (data, template) {
                    var value = data['value'] === undefined ? data['default'] : data['value'];
                    return {
                        input: template({
                            data: data,
                            value: value
                        }),
                        label: "<label for=\"" + _.escape(data.id) + "\">" + _.escape(data.human_name) + "</label>",
                        help: "<span class=\"form-configuration-help\" title=\"" + (data.help === undefined ? 'No help' : _.escape(data.help)) + "\">?</span>"
                    };
                },

                renderBoolean: function(data) {
                    var value = data['value'] === undefined ? data['default'] : data['value'];
                    return {
                        input: "<label for=\"" + _.escape(data.id) + "\">" + (value ? "YES" : "NO") + "</label>" + _.template('<input id="<%- data.id %>" name="<%- data.id %>" type="checkbox" <%- value ? "checked" : "" %> />', {
                            data: data,
                            value: value
                        }),
                        label: _.escape(data.human_name),
                        help: "<span class=\"form-configuration-help\" title=\"" + (data.help === undefined ? 'No help' : _.escape(data.help)) + "\">?</span>"
                    };
                },

                renderSlider: function(data) {
                    return this._generic(data, _.template(SliderTemplate));
                },

                renderDropdown: function(data) {
                    var template = _.template(DropdownTemplate);
                    return this._generic(data, template);
                }
            };

            // Tooltips, useful almost everywhere
            Claun._tooltips = [];

            Claun.tooltip = function(event, timeout) {
                var content = this.title === undefined ? 'No help' : this.title;
                if (timeout === undefined) {
                    timeout = 3000;
                }

                $.each(Claun._tooltips, function () {
                    this.hide();
                    this.remove();
                    clearTimeout(this.timeout);
                })

                var p = $('<p>').html(_.escape(content));
                p.addClass('tooltip').addClass('ui-corner-all').css({
                    opacity: 0.7,
                    zIndex: 150000
                }).css({
                    top: event.clientY - 100,
                    left: event.clientX - 40
                }).click(function () {
                    $(this).hide();
                });
                $('body').append(p);
                p.show();
                p.timeout = setTimeout(function () {
                    p.hide();
                    p.remove();
                }, timeout);
                Claun._tooltips.push(p);
            };

            // Security
            Claun.componentSignature = function () {
                return base64_encode(Claun.configuration.client_id + ':' + Claun.configuration.client_password)
            };

            Claun.sign = function (uri) {
                return uri + '?claun_authentication=' + Claun.componentSignature();
            };

            // AJAX
            // Because we use OAuth, we have to send an access token with every request. That is
            // why we set up a general ajax settings that will handle the tokens.
            // We will use jQuery's beforeSend callback.
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    var user = Claun.user.get('user');
                    // If there is a user...
                    if (user) {
                        var now = new Date();
                        var success = true;
                        // ...check the refresh time. If is time to refresh tokens, try to do so.
                        if (user.refresh_time - 10000 < now.getTime()) {
                            Claun.messages.info('Access token expired, please wait...');
                            $.ajax({
                                url: Claun.configuration.baseurl + 'users/auth/token',
                                async: false,
                                data: {
                                    grant_type: 'refresh_token',
                                    refresh_token: user.refresh_token
                                },
                                beforeSend: function (xhr) {
                                    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8');
                                    if (Claun.configuration.client_authentication) {
                                        xhr.setRequestHeader('X-Claun-Authentication', 'Basic ' + Claun.componentSignature());
                                    }
                                },
                                cache: false,
                                error: function (xhr, status, error) {
                                    try {
                                        error = Claun.json.parse(xhr.responseText).error_description;
                                    } catch (SyntaxError) {
                                        error = xhr.responseText;
                                    }
                                    Claun.dispatcher.trigger('user:notoken');
                                    Claun.messages.error("Cannot refresh token. (" + xhr.status + ": " + error + ")");
                                    success = false;
                                },
                                success: function (data) {
                                    Claun.dispatcher.trigger('user:changed', data);
                                    Claun.messages.info('Access token was successfully refreshed. Please, continue.');
                                }
                            });
                        }
                        if (success) {
                            // Add OAuth header to our request and Auth Basic for the client
                            if (Claun.configuration.client_authentication) {
                                xhr.setRequestHeader('X-Claun-Authentication', 'Basic ' + Claun.componentSignature());
                            }
                            xhr.setRequestHeader('X-Claun-User-Token', 'OAuth ' + user.access_token);
                        } else {
                            return false;
                        }
                    }
                }
            });

            $(document).ajaxError(function(e, xhr, options) {
                var error;
                try {
                    error = Claun.json.parse(xhr.responseText).error_description;
                } catch (SyntaxError) {
                    if (xhr.status == 0) {
                        error = 'Server probably broke down.';
                    } else {
                        error = xhr.responseText;
                    }
                }
                Claun.messages.error(error);
            });

            $('#loading').ajaxStart(function() {
                $(this).show();
            }).ajaxStop(function() {
                $(this).hide();
            });

            // Shortcuts
            Claun.ajax = $.ajax;
            Claun.batchOperations = BatchOperations;
        };

        return Claun;
    });