/* 
 * bdajax v1.3
 * 
 * Requires:
 * - jQuery 1.6.4
 * - jQuery Tools 1.2.6
 */

(function($) {

    $(document).ready(function() {
        bdajax.spinner.hide();
        $(document).bdajax();
    });
    
    $.fn.bdajax = function() {
        var context = $(this);
        $('*', context).each(function() {
            for (var i in this.attributes) {
                var attr = this.attributes[i];
                if (attr && attr.nodeName) {
                    var name = attr.nodeName;
                    if (name.indexOf('ajax:bind') > -1) {
                        var events = attr.nodeValue;
                        var ajax = $(this);
                        ajax.unbind(events);
                        if (ajax.attr('ajax:action')
                         || ajax.attr('ajax:event')
                         || ajax.attr('ajax:overlay')) {
                            ajax.bind(events, bdajax._dispatching_handler);
                        }
                    }
                }
            }
        });
        for (var binder in bdajax.binders) {
            bdajax.binders[binder](context);
        }
        return context;
    }
    
    bdajax = {
        
        // By default, we redirect to the login page on 403 error.
        // That we assume at '/login'.
        default_403: '/login',
        
        // object for 3rd party binders
        binders: {},
        
        // ajax spinner handling
        spinner: {
            
            _elem: null,
            _request_count: 0,
            
            elem: function() {
                if (bdajax.spinner._elem == null) {
                    bdajax.spinner._elem = $('#ajax-spinner');
                }
                return bdajax.spinner._elem;
            },
            
            show: function() {
                bdajax.spinner._request_count++;
                if (bdajax.spinner._request_count > 1) {
                    return;
                }
                bdajax.spinner.elem().show();
            },
            
            hide: function(force) {
                bdajax.spinner._request_count--;
                if (force) {
                    bdajax.spinner._request_count = 0;
                    bdajax.spinner.elem().hide();
                    return;
                } else if (bdajax.spinner._request_count <= 0) {
                    bdajax.spinner._request_count = 0;
                    bdajax.spinner.elem().hide();
                }
            }
        },
        
        parseurl: function(url) {
            var idx = url.indexOf('?');
            if (idx != -1) {
                url = url.substring(0, idx);
            }
            if (url.charAt(url.length - 1) == '/') {
                url = url.substring(0, url.length - 1);
            }
            return url;
        },
        
        parsequery: function(url) {
            var params = {};
            var idx = url.indexOf('?');
            if (idx != -1) {
                var parameters = url.slice(idx + 1).split('&');
                for (var i = 0;  i < parameters.length; i++) {
                    var param = parameters[i].split('=');
                    params[param[0]] = param[1];
                }
            }
            return params;
        },
        
        parsetarget: function(target) {
            var url = bdajax.parseurl(target);
            var params = bdajax.parsequery(target);
            if (!params) { params = {}; }
            return {
                url: url,
                params: params
            };
        },
        
        request: function(options) {
            if (options.url.indexOf('?') != -1) {
                var addparams = options.params;
                options.params = bdajax.parsequery(options.url);
                options.url = bdajax.parseurl(options.url);
                for (var key in addparams) {
                    options.params[key] = addparams[key];
                }
            } else {
                if (!options.params) { options.params = {}; }
            }
            if (!options.type) { options.type = 'html'; }
            if (!options.error) {
                options.error = function(req, status, exception) {
                    if (parseInt(status, 10) === 403) {
                        window.location.pathname = bdajax.default_403;
                    } else {
                        var message = '<strong>' + status + '</strong> ';
                        message += exception;
                        bdajax.error(message);
                    }
                };
            }
            if (!options.cache) { options.cache = false; }
            var wrapped_success = function(data, status, request) {
                options.success(data, status, request);
                bdajax.spinner.hide();
            }
            var wrapped_error = function(request, status, error) {
                options.error(request,
                              request.status || status,
                              request.statusText || error);
                bdajax.spinner.hide(true);
            }
            bdajax.spinner.show();
            $.ajax({
                url: options.url,
                dataType: options.type,
                data: options.params,
                success: wrapped_success,
                error: wrapped_error,
                cache: options.cache
            });
        },
        
        action: function(options) {
            options.success = bdajax._ajax_action_success;
            bdajax._perform_ajax_action(options);
        },
        
        fiddle: function(payload, selector, mode) {
            if (mode == 'replace') {
                $(selector).replaceWith(payload);
                var context = $(selector);
                if (context.length) {
                    context.parent().bdajax();
                } else {
                    $(document).bdajax();
                }
            } else if (mode == 'inner') {
                $(selector).html(payload);
                $(selector).bdajax();
            }
        },
        
        continuation: function(definitions) {
            if (!definitions) {
                return;
            }
            bdajax.spinner.hide();
            var definition, target;
            for (var idx in definitions) {
                definition = definitions[idx];
                if (definition.type == 'action') {
                    target = bdajax.parsetarget(definition.target);
                    bdajax.action({
                        url: target.url,
                        params: target.params,
                        name: definition.name,
                        mode: definition.mode,
                        selector: definition.selector
                    });
                } else if (definition.type == 'event') {
                    bdajax.trigger(definition.name,
                                   definition.selector,
                                   definition.target);
                } else if (definition.type == 'message') {
                    if (definition.flavor) {
                        var flavors = ['message', 'info', 'warning', 'error'];
                        if (flavors.indexOf(definition.flavor) == -1) {
                            throw "Continuation definition.flavor unknown";
                        }
                        switch (definition.flavor) {
                            case 'message':
                                bdajax.message(definition.payload);
                                break;
                            case 'info':
                                bdajax.info(definition.payload);
                                break;
                            case 'warning':
                                bdajax.warning(definition.payload);
                                break;
                            case 'error':
                                bdajax.error(definition.payload);
                                break;
                        }
                    } else {
                        if (!definition.selector) {
                            throw "Continuation definition.selector expected";
                        }
                        $(definition.selector).html(definition.payload);
                    }
                }
            }
        },
        
        trigger: function(name, selector, target) {
            var evt = $.Event(name);
            evt.ajaxtarget = bdajax.parsetarget(target);
            $(selector).trigger(evt);
        },
        
        overlay: function(options) {
            var elem = $('#ajax-overlay');
            elem.removeData('overlay');
            var url, params;
            if (options.target) {
                var target = bdajax.parsetarget(options.target);
                url = target.url;
                params = target.params;
            } else {
                url = options.url;
                params = options.params;
            }
            bdajax._perform_ajax_action({
                name: options.action,
                selector: '#ajax-overlay-content',
                mode: 'inner',
                url: url,
                params: params,
                success: function(data) {
                    bdajax._ajax_action_success(data);
                    // overlays are not displayed if no payload is received.
                    if (!data.payload) {
                        return;
                    }
                    elem.overlay({
                        mask: {
                            color: '#fff',
                            loadSpeed: 200
                        },
                        onClose: function() {
                            var overlay = this.getOverlay();
                            $('#ajax-overlay-content', overlay).html('');
                        },
                        oneInstance: false,
                        closeOnClick: true,
                        fixed: false
                    });
                    var overlay = elem.data('overlay');
                    overlay.load();
                }
            });
        },
        
        message: function(message) {
            var elem = $('#ajax-message');
            elem.removeData('overlay');
            elem.overlay({
                mask: {
                    color: '#fff',
                    loadSpeed: 200
                },
                onBeforeLoad: function() {
                    var overlay = this.getOverlay();
                    $('.message', overlay).html(message);
                },
                onLoad: function() {
                    elem.find('button:first').focus();
                },
                onBeforeClose: function() {
                    var overlay = this.getOverlay();
                    $('.message', overlay).empty();
                },
                oneInstance: false,
                closeOnClick: false,
                fixed: false,
                top:'20%'
            });
            elem.data('overlay').load();
        },
        
        error: function(message) {
            $("#ajax-message .message").removeClass('error warning info')
                                       .addClass('error');
            bdajax.message(message);
        },
        
        info: function(message) {
            $("#ajax-message .message").removeClass('error warning info')
                                       .addClass('info');
            bdajax.message(message);
        },
        
        warning: function(message) {
            $("#ajax-message .message").removeClass('error warning info')
                                       .addClass('warning');
            bdajax.message(message);
        },
        
        dialog: function(options, callback) {
            var elem = $('#ajax-dialog');
            elem.removeData('overlay');
            elem.overlay({
                mask: {
                    color: '#fff',
                    loadSpeed: 200
                },
                onBeforeLoad: function() {
                    var overlay = this.getOverlay();
                    var closefunc = this.close;
                    $('.text', overlay).html(options.message);
                    $('button', overlay).unbind();
                    $('button.submit', overlay).bind('click', function() {
                        closefunc();
                        callback(options);
                    });
                    $('button.cancel', overlay).bind('click', function() {
                        closefunc();
                    });
                },
                oneInstance: false,
                closeOnClick: false,
                fixed: false,
                top:'20%'
            });
            elem.data('overlay').load();
        },
        
        _dispatching_handler: function(event) {
            event.preventDefault();
            event.stopPropagation();
            var elem = $(this);
            var options = {
                elem: elem,
                event: event
            };
            if (elem.attr('ajax:confirm')) {
                options.message = elem.attr('ajax:confirm');
                bdajax.dialog(options, bdajax._do_dispatching);
            } else {
                bdajax._do_dispatching(options);
            }
        },
        
        _do_dispatching: function(options) {
            var elem = options.elem;
            var event = options.event;
            if (elem.attr('ajax:action')) {
                bdajax._handle_ajax_action(elem, event);
            }
            if (elem.attr('ajax:event')) {
                bdajax._handle_ajax_event(elem);
            }
            if (elem.attr('ajax:overlay')) {
                bdajax._handle_ajax_overlay(elem, event);
            }
        },
        
        _handle_ajax_event: function(elem) {
            var target = elem.attr('ajax:target');
            var defs = bdajax._defs_to_array(elem.attr('ajax:event'));
            for (var i = 0; i < defs.length; i++) {
                var def = defs[i];
                def = def.split(':');
                bdajax.trigger(def[0], def[1], target);
            }
        },
        
        _ajax_action_success: function(data) {
            if (!data) {
                bdajax.error('Empty response');
                bdajax.spinner.hide();
            } else {
                bdajax.fiddle(data.payload, data.selector, data.mode);
                bdajax.continuation(data.continuation);
            }
        },
        
        _perform_ajax_action: function(options) {
            options.params['bdajax.action'] = options.name;
            options.params['bdajax.mode'] = options.mode;
            options.params['bdajax.selector'] = options.selector;
            bdajax.request({
                url: bdajax.parseurl(options.url) + '/ajaxaction',
                type: 'json',
                params: options.params,
                success: options.success
            });
        },
        
        _handle_ajax_action: function(elem, event) {
            var target;
            if (event.ajaxtarget) {
                target = event.ajaxtarget;
            } else {
                target = bdajax.parsetarget(elem.attr('ajax:target'));
            }
            var actions = bdajax._defs_to_array(elem.attr('ajax:action'));
            for (var i = 0; i < actions.length; i++) {
                var defs = actions[i].split(':');
                bdajax.action({
                    name: defs[0],
                    selector: defs[1],
                    mode: defs[2],
                    url: target.url,
                    params: target.params
                });
            }
        },
        
        _handle_ajax_overlay: function(elem, event) {
            var target;
            if (event.ajaxtarget) {
                target = event.ajaxtarget;
            } else {
                target = bdajax.parsetarget(elem.attr('ajax:target'));
            }
            var actionname = elem.attr('ajax:overlay');
            bdajax.overlay({
                action: actionname,
                url: target.url,
                params: target.params
            });
        },
        
        _defs_to_array: function(str) {
            // XXX: if space in selector when receiving def str, this will fail
            var arr;
            if (str.indexOf(' ') != -1) {
                arr = str.split(' ');
            } else {
                arr = new Array(str);
            }
            return arr;
        }
    };

})(jQuery);