/* KSS plugins for plonetabs */

kukit.actionsGlobalRegistry.register('plonetabs-redirectTo', function(oper) {
;;; oper.componentName = '[plonetabs-redirectTo] action';
    var wl = window.location;
    oper.evaluateParameters([], {'protocol'     : wl.protocol,
                                 'host'         : wl.host,
                                 'pathname'     : wl.pathname,
                                 'search'       : wl.search,
                                 'searchparams' : '',
                                 'searchvalues' : '',
                                 'hash'         : wl.hash});

    // normalize parameters
    var protocol = oper.parms.protocol + (oper.parms.protocol[oper.parms.protocol.length - 1] == ':') ?  '' : ':';
    var host = oper.parms.host;
    var pathname = oper.parms.pathname;
    if ((params = oper.parms.searchparams) && (values = oper.parms.searchvalues)) {
        search = '?';
        params = params.split(',');
        values = values.split(',');
        for (var i = 0; i < params.length; i++) {
            search += params[i] + '=' + values[i] + '&';
        }
        search = (search.slice(search.length - 1) == '&') ? search.slice(0, search.length - 1) : search;
    } else {
        search = oper.parms.search;
        search = (search && search.substr(0, 1) == '?') ? search : (search ? '?' + search : '');
    }
    var hash = (oper.parms.hash.length > 1) ? ((oper.parms.hash.substr(0, 1) == '#' ? '' : '#') + oper.parms.hash) : '';

    url = protocol + '//' + host + pathname + search + hash;
    window.location.replace(url);

});

kukit.commandsGlobalRegistry.registerFromAction('plonetabs-redirectTo', kukit.cr.makeSelectorCommand);


kukit.actionsGlobalRegistry.register('plonetabs-toggleCollapsible', function(oper) {
;;; oper.componentName = '[plonetabs-toggleCollapsible] action';
    oper.evaluateParameters([], {'collapsed' : 'collapsedBlock',
                                 'expanded' : 'expandedBlock',
                                 'collapse': 'none'});

    var node = oper.node.parentNode;  // collapsible section

    if (oper.parms.collapse != 'none') {
        if (oper.parms.collapse == 'true') {
            removeClassName(node, oper.parms.expanded);
            addClassName(node, oper.parms.collapsed);
        } else {
            removeClassName(node, oper.parms.collapsed);
            addClassName(node, oper.parms.expanded);
        }
    } else {
        if (hasClassName(node, oper.parms.collapsed)) {
            removeClassName(node, oper.parms.collapsed);
            addClassName(node, oper.parms.expanded);
        } else {
            removeClassName(node, oper.parms.expanded);
            addClassName(node, oper.parms.collapsed);
        }
    }

});

kukit.commandsGlobalRegistry.registerFromAction('plonetabs-toggleCollapsible', kukit.cr.makeSelectorCommand);


kukit.actionsGlobalRegistry.register('plonetabs-resetForm', function(oper) {
;;; oper.componentName = '[plonetabs-resetForm] action';
    oper.evaluateParameters([], {});
    if (typeof(oper.node.reset) == 'function' || typeof(oper.node.reset) == 'object') {
        oper.node.reset();
    } else {
        kukit.logWarning('plonetabs-resetForm: reset could only be executed on form element');
    }

});

kukit.commandsGlobalRegistry.registerFromAction('plonetabs-resetForm', kukit.cr.makeSelectorCommand);

function blur(node) {
    tagName = node.tagName.toLowerCase();
    if ((tagName == 'input') || (tagName == 'select')
       || (tagName == 'textarea')) {
        node.blur();
;;;} else {
;;;    kukit.logWarning('Blur on node that cannot be blured!');
    };
};

kukit.actionsGlobalRegistry.register('plonetabs-blur', function(oper) {
;;; oper.componentName = '[plonetabs-blur] action';
    // TODO get rid of none
    oper.evaluateParameters([], {'none': false});
    blur(oper.node);

});

kukit.commandsGlobalRegistry.registerFromAction('plonetabs-blur', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('plonetabs-handleServerError', function(oper) {
    oper.componentName = '[plonetabs-handleServerError] action';
    oper.evaluateParameters([], {'message' : ''});
    var message = oper.parms.message;
    if (message == '') {
        var server_reason = (/^.*(server_reason="(.*?)").*$/i).exec(kukit.E);
        if (server_reason && server_reason[2]) {
            message = server_reason[2];
        } else {
            var client_reason = (/^.*(client_reason="(.*?)").*$/i).exec(kukit.E);
            if (client_reason && client_reason[2]) {
                message = client_reason[2];
                if (message.indexOf('invalid KSS response') != -1) {
                    message = 'Error occured. ' +
                              'It seems like you are not logged in anymore ' +
                              'or have no privileges to perform this action. ' +
                              'In another case there might be an internal ' +
                              'server error while executing your last action.' +
                              ' Check your portal error log.' +
                              ' Eventually your server may be not available.';
                }
            }
        }
    }
    if (message) {
        alert(message);
    }
});


var PLONETABS_ADD_PATTERN = new RegExp('[^a-zA-Z0-9-_~,.\\$\\(\\)# ]','g');

kukit.actionsGlobalRegistry.register('plonetabs-generateId', function(oper) {
    oper.componentName = '[plonetabs-generateId] action';
    oper.evaluateParameters(['target', 'var_name'], {});

    var source = oper.node;
    var var_name = oper.parms.var_name;
    var initialValue = typeof(kukit.engine.stateVariables[var_name]) != 'undefined' ? kukit.engine.stateVariables[var_name] : '';
    var target = document.getElementById(oper.parms.target);

    if (target == null) {
        kukit.logWarning('plonetabs-generateId: target element ("' + oper.parms.target + '") not found');
        return ;
    }

    if (target.value == initialValue.replace(PLONETABS_ADD_PATTERN, '')) {
        target.value = source.value.replace(PLONETABS_ADD_PATTERN, '');
    }
    kukit.engine.stateVariables[var_name] = source.value;

});

function plonetabs_notifySortableUpdate(element, oper) {
    var draggables = element.getElementsByTagName('LI');
    var ids = [];
    for (var i = 0, o; o = draggables[i]; i++) {
        ids.push(o.id);
    }
    oper.parms = {'actions': ids.join('&'), 'cat_name': kukit.engine.stateVariables['plonetabs-category']};
    oper.executeServerAction('plonetabs-orderActions');
}

kukit.actionsGlobalRegistry.register('plonetabs-createSortable', function(oper) {
    oper.componentName = '[plonetabs-createSortable] action';
    oper.evaluateParameters([], {}, '', true);
    var parms = oper.clone().parms;

    var new_oper = oper.clone();
    parms['onUpdate'] = function(element){plonetabs_notifySortableUpdate(element, new_oper);};
    Sortable.create(oper.node, parms);
});

kukit.actionsGlobalRegistry.register('plonetabs-updateSortable', function(oper) {
    oper.componentName = '[plonetabs-updateSortable] action';
    oper.evaluateParameters([], {}, '', true);
    var parms = oper.clone().parms;
    var node = oper.node;
    var sort_list = node.parentNode;
    var options_ = Sortable.sortables[sort_list.id];

    if (typeof(options_) != 'undefined') {
        // check whether node element isn't already registered as draggables
        for (var i = 0, drag; drag = options_.draggables[i]; i++) {
            if (node == drag.element) {
                return false;
            }
        }
        // destroy sortable list
        Sortable.destroy(sort_list.id);
    }

    var new_oper = oper.clone();
    parms['onUpdate'] = function(element){plonetabs_notifySortableUpdate(element, new_oper);};
    Sortable.create(sort_list, parms);
});

kukit.commandsGlobalRegistry.registerFromAction('plonetabs-updateSortable', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('plonetabs-replaceOrInsert', function(oper) {
    oper.componentName = '[plonetabs-replaceOrInsert] action';
    var defaultSelectorType = kukit.selectorTypesGlobalRegistry.defaultSelectorType
    oper.evaluateParameters(['selector', 'html'], {'alternativeHTML': '',
                                                   'selectorType': defaultSelectorType,
                                                   'position': 'last', // can be one of the following: first, last, after, before
                                                   'positionSelector': '', // work together with position=after|before
                                                   'positionSelectorType': defaultSelectorType,
                                                   'withKssSetup': true});
    oper.evalBool('withKssSetup');
    var parentNode = oper.node;
    var nodes = kukit.selectorTypesGlobalRegistry.get(oper.parms.selectorType)(oper.parms.selector, parentNode);
    if (nodes.length > 0) {
        var content = oper.parms.html;
        var new_node = nodes[0];
        var action_ = 'replaceHTML';
    } else {
        var content = oper.parms.alternativeHTML ? oper.parms.alternativeHTML : oper.parms.html;
        var action_ = 'insertHTMLAsLastChild';
        var new_node = parentNode;
        var position = oper.parms.position;
        if (position == 'first') {
            action_ = 'insertHTMLAsFirstChild';
        } else if (position == 'after' || position == 'before') {
            var posSelector = kukit.selectorTypesGlobalRegistry.get(oper.parms.positionSelectorType);
            nodes = posSelector(oper.parms.positionSelector, new_node);
            if (nodes.length > 0) {
                new_node = nodes[0];
                action_ = (position == 'after') ? 'insertHTMLAfter' : 'insertHTMLBefore';
            }
        }
    }
    var new_oper = new kukit.op.Oper({'node': new_node,
                                      'parms': {'html': content,
                                                'withKssSetup': oper.parms.withKssSetup}});
    kukit.actionsGlobalRegistry.get(action_)(new_oper);
});

kukit.commandsGlobalRegistry.registerFromAction('plonetabs-replaceOrInsert', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('plonetabs-timeout', function(oper) {
    oper.componentName = '[plonetabs-timeout] action';
    oper.evaluateParameters(['cmd_name', 'delay',], {'repeat': 'true'}, '', true);
    oper.evalBool('repeat');
    var parms = oper.parms;

    // marshall it, the rest of the parms will be passed
    var actionParameters = {};
    for (var key in parms) {
        if (key != 'cmd_name' && key != 'delay' && key != 'repeat') {
            actionParameters[key] = parms[key];
        }
    }

    // clear previously set timeout if such exists
    var node = oper.node;
    if (typeof(node.plonetabs_counter) != 'undefined') {
        node.plonetabs_counter.clear();
    }

    // function to bind
    var new_oper = new kukit.op.Oper({'node': node, 'parms': actionParameters});
    var f = function() {
        // check if the node has been deleted
        // and weed it out if so
        if (oper.node != null && !oper.node.parentNode) {
;;;         var msg = 'Timeout action with ' + parms.cmd_name;
;;;         msg += ' client action stopped';
;;;         kukit.logDebug(msg);
            this.clear();
        } else {
;;;         var msg = 'TIMEOUT: Timer action with ' + parms.cmd_name;
;;;         msg += ' client action executed';
;;;         kukit.logDebug(msg);
            kukit.actionsGlobalRegistry.get(parms.cmd_name)(new_oper);
        }
    };
    var counter = new kukit.ut.TimerCounter(parms.delay, f, parms.repeat);
    node.plonetabs_counter = counter;
    counter.start();
});

kukit.commandsGlobalRegistry.registerFromAction('plonetabs-timeout', kukit.cr.makeSelectorCommand);
