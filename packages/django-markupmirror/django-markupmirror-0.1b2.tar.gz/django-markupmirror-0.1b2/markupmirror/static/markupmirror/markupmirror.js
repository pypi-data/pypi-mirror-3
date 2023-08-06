var markupmirror = {
    "jQuery": jQuery
};

/* jQuery closure and document ready */
(function($) { $(function() {



/* make AJAX requests work with Django's CSRF protection */
$.ajaxSetup({
    crossDomain: false
});
$(document).ajaxSend(function(event, xhr, settings) {
    if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type))) {
        xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
    }
});


/* Plugin that handles the initialization of CodeMirror editors
   and preview iframes for each textarea.markupmirror-editor */
var MarkupMirrorEditor = function(element, options) {
    var _this = this,
        _public = {

            /* to configure the wrapper */
            configure: function(obj) {
                var key;
                for (key in obj) {
                    _private.options[key] = obj[key];
                }

                return _this;
            },

            /* add the Codemirror to a new element */
            add: function(el, options) {

                /* skip if no element passed */
                if(!el || el.length === 0) {
                    return _this;
                }

                var editor;
                $.each(el, function() {
                    if (this.nodeName.toLowerCase() !== 'textarea') {
                        return true;
                    }

                    if (options === undefined) {
                        if (_private.getOption('_init') === true &&
                            _private.getOption('inherit') === true) {
                            editor = CodeMirror.fromTextArea(
                                this,
                                _private.getOption('initOptions'));
                            _public.configure({'editor': editor});
                        } else {
                            editor = CodeMirror.fromTextArea(this);
                            _public.configure({'editor': editor});
                        }
                    } else {
                        /* so we are able to overwrite just a few of the
                         * options */
                        if(_private.getOption('_init') === true &&
                           _private.getOption('extend')) {
                            options = $.extend(
                                _private.getOption('initOptions'),
                                options);
                        }

                        editor = CodeMirror.fromTextArea(this, options);
                        _public.configure({'editor': editor});
                    }

                    if(typeof(_private.getOption('onInit')) === 'function') {
                        _private.getOption('onInit')(this);
                    }
                });

                return _this;
            }
        },

        /* this will not be exposed to the public */
        _private = {
            getOption: function(index) {
                return _private.options[index] || undefined;
            },

            /* store configuration options here */
            options: {
                /* initial options passed in */
                initOptions: undefined,

                /* new added elements inherit from the inital options */
                inherit: true,

                /* extends the original options object by passing
                   a new element in */
                extend: true,

                /* initial init was done */
                _init: false,

                /* callback */
                onInit: undefined,

                /* the original codemirror editor object */
                editor: undefined
            }
        };

    /* initialise the plugin here */
    _public.configure({
        _init: true,
        initOptions: options
    });

    /* add init element */
    _public.add(element, options);

    _this = _public;
    return _this;
};


/* Initialize plugin for all textarea.markupmirror-editor elements.
   Ignore the add-rows of model inlines because CM cannot be copied. */
var preview_delay,
    $textarea = $('.markupmirror-editor:not(.empty-form textarea)'),
    MME = new MarkupMirrorEditor(undefined,
            $.extend({
                'onChange': function(editor) {
                    clearTimeout(preview_delay);
                    preview_delay = setTimeout(function() {
                        update_preview(editor);
                    }, 500);
                }
            },
            $textarea.first().data('mmSettings')))
        .configure({
            'onInit': create_iframe
        });
$textarea.each(function() {
    var $this = $(this);
    MME.add($this, $this.data('mmSettings'));
});



/* refresh the iframe for a group of CodeMirrors */
function refresh_iframe($codemirror) {
    $codemirror.each(function() {
        var $this = $(this);
        $this.get(0).CodeMirror.refresh();
        $this.children('iframe').trigger('_resize');
    });
}

/* inserting new inlines (stacked or tabular) */
$('.add-row').children('a').on('click', function(event) {
    var $group = $(event.target)
        .closest('.inline-group'),
        is_tabular = $group.children('.inline-related:first').is('.tabular'),
        added_form;
    if (is_tabular) {
        added_form = $group.find('.form-row:not(.empty-form)').last();
    } else {
        added_form = $group.find('.inline-related:not(.empty-form)').last();
    }
    MME.add(added_form.find('.markupmirror-editor'));
});

/* opening collapsed fieldsets */
$('.collapse').find('.collapse-toggle').on('click', function(event) {
    var $codemirror = $(event.target)
        .closest('.module')
        .find('.CodeMirror');
    refresh_iframe($codemirror);
});

/* FeinCMS related handlers */
if (feincms !== undefined) {

    /* switching tabs in FeinCMS */
    $('.change-form').on('click', '.navi_tab', function(event) {
        var $tab = $(event.target),
            id = $tab.attr('id'),
            panel_id = id.substr(0, id.length - 4),  // _tab -> _body
            $codemirror = $('#' + panel_id + '_body').find('.CodeMirror');
        refresh_iframe($codemirror);
    });

    /* adding new content items in FeinCMS */
    contentblock_init_handlers.push(function() {
        var $textareas = $('.order-machine').find('.markupmirror-editor');
        $textareas.each(function() {
            var $this = $(this);
            /* continue if CodeMirror already initialized */
            if ($this.next('.CodeMirror').length !== 0) {
                return true;
            }

            MME.add($this, $this.data('mmSettings'));
            var $codemirror = $this.next('.CodeMirror'),
                resize_delay,
                initial_resize = function($codemirror) {
                    clearTimeout(resize_delay);
                    if ($codemirror.is(':visible')) {
                        refresh_iframe($codemirror);
                    } else {
                        resize_delay = setTimeout(function() {
                            initial_resize($codemirror);
                        }, 50);
                    }
                };
            initial_resize($codemirror);
        });
    });

}


/* when changing the textarea we replace the iframe content with the
   new coming from the server */
function update_preview(editor) {
    var $textarea = $(editor.getTextArea()),
        $codemirror = $textarea.next('.CodeMirror'),
        $iframe = $codemirror.children('iframe'),
        mm_settings = $textarea.data('mmSettings'),
        url = mm_settings['preview_url'],
        markup_type = mm_settings['markup_type'];

    $.post(url, {
            /* csrfmiddlewaretoken: '{{ csrf_token }}', */
            markup_type: markup_type,
            text: editor.getValue()
        },
        function(data, textStatus, jqXHR) {
            $iframe.trigger('_resize');

            if( $iframe.data('load') === true ) {
                $iframe.trigger('_update', {html: data});
            } else {
                $iframe.data('replace', data);
            }
        }
    );
}


/* when init a textarea with codemirror we also create an iframe */
function create_iframe(textarea) {
    var $textarea = $(textarea),
        $iframe = $('<iframe />').attr(
            'src', $textarea.data('mmSettings')['base_url']),
        $codemirror = $textarea.next('.CodeMirror');

    $iframe
        .addClass('CodeMirror-preview')
        .on({
            'load': function() {
                var $this = $(this);
                $this.data('load', true);

                if( $this.data('replace') !== undefined ) {
                    $this.trigger('_update', {html: $this.data('replace')});
                }
            },
            '_resize': function() {
                $(this).css({
                    'height': $(this).prev().outerHeight()
                });
            },
            '_update': function(e, data) {
                $(this)
                    .contents()
                    .find('body')
                    .html(data.html);
            }
        })
        .trigger('_resize')
        .appendTo($codemirror);

    /* update iframe contents for the first time */
    update_preview($codemirror.get(0).CodeMirror);
}



/* end jQuery closure and document ready */
}); })(markupmirror.jQuery);
