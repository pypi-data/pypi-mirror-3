    $.fn.raysmethod = function (method) {
        validation_method = getMethod.call(this, method);
    };
    $.rays = {
        createErrorlist: function () {
            return $('<ul class="errorlist" />');
        },
        /**
         * ``this`` is the input field which gets validated.
         */
        findErrorlist: function () {
            return $(this).parent().find('.errorlist');
        },
        /**
         * ``this`` is the input field which gets validated.
         */
        insertErrorlist: function (errorlist) {
            return $(this).parent().prepend(errorlist).find('.errorlist');
        },
        hideErrorlist: function () {
            $(this).remove();
        },
        /**
         * ``this`` is the errorlist tag.
         */
        resetErrorlist: function () {
            $(this).empty();
        },
        /**
         * ``this`` is the errorlist tag.
         * ``error``: Is a string containing the error message.
         */
        insertError: function (error) {
            $(this).append($('<li/>').text(error));
        }
    };
/* Autocomplete */
(function ($) {
    $(function () {
        $('input[data-rays-autocomplete-url]').each(function() {
            $(this).autocomplete({
                source: $(this).attr('data-rays-autocomplete-url')
            });
        });
        $('input[data-rays-autocomplete-choices]').each(function() {
            var options = {source: []};
            var choices = $(this).attr('data-rays-autocomplete-choices');
            $('#' + choices + ' dt').each(function () {
                options.source.push({
                    value: $(this).text(),
                    label: $(this).next().text()
                });
            });
            $(this).autocomplete(options);
        });
    });
})(jQuery);

/* Datepicker */
(function($) {
    $(function () {
        if (!Modernizr.inputtypes.date) {
            $("input[type=date]").each(function(){
                var options = {
                    dateFormat: $(this).attr('data-rays-datepicker-format')
                };
                $(this).datepicker(options);
            });
        }
    });
})(jQuery);

/* Slider */
(function($) {
    $(function () {
        if (!Modernizr.inputtypes.range) {
            $("input[type=range]").each(function(){
                var that = $(this).hide();
                var value = parseInt(that.val());
                var min = parseInt(that.attr('min'));
                var max = parseInt(that.attr('max'));
                var step = parseInt(that.attr('step'));
                var options = {
                    value: isNaN(value) ? undefined : value,
                    min: isNaN(min) ? undefined : min,
                    max: isNaN(max) ? undefined : max,
                    step: isNaN(step) ? undefined : step,
                    change: function (event, ui) {
                        that.val(ui.value).trigger('change');
                    }
                };
                var slider = $('<div id="' + that.attr('id') + '_slider" />').insertAfter(that).slider(options);
                that.val(slider.value);
            });
        }
    });
})(jQuery);

/* Validation */
(function($, undefined) {
    $(function () {
        /**
         * Searches the following parts of the dom tree for a suitable
         * function. First match will be returned:
         *
         *  Data object of given input tag:
         *      ``$(input).data('rays.' + method_name);``
         *
         *  Data object of current form:
         *      ``$(input).parents('form').data('rays.' + method_name);``
         *
         *  Rays object in global jQuery namespace:
         *      ``$.rays[method_name];``
         */
        function getMethod(method_name, input) {
            var method;
            /* Get method from input tag */
            method = $(input).data('rays.' + method_name);
            if (method) {
                return method;
            }
            method = $(input).parents('form').data('rays.' + method_name);
            if (method) {
                return method;
            }
            return $.rays[method_name];
        }

        /**
         * Provides python-like string interpolation.
         * It supports value interpolation either by keys of a dictionary or
         * by index of an array.
         *
         * Examples::
         *
         *      $.rays.interpolate("Hello %s.", ["World"]) == "Hello World."
         *      $.rays.interpolate("Hello %(name)s.", {name: "World"}) == "Hello World."
         *      $.rays.interpolate("Hello %%.", ["World"]) == "Hello %."
         *
         * This version doesn't do any type checks and doesn't provide
         * formating support.
         */
        $.rays.interpolate = function (s, args) {
            var i = 0;
            return s.replace(/%(?:\(([^)]+)\))?([%diouxXeEfFgGcrs])/g, function (match, v, t) {
                if (t == "%") return "%";
                var value = args[v || i++];
                return value !== undefined ? value : "";
            });
        };

        $.rays.getValue = function (input) {
            if ($(input).attr('type') == 'checkbox') {
                return $(input).attr('checked');
            } else {
                return $(input).val();
            }
        };
        $.rays.defaultValidator = {
            stopOnError: false
        };
        $.rays.validate = function () {
            var validators = $(this).data('rays.validators');
            if (!$.isArray(validators) || validators.length == 0) {
                return;
            }
            var value = $.rays.getValue(this),
                errors = [];
            $.each(validators, function (i, validator) {
                error = validator.validate.call(this, value);
                if (error) {
                    errors.push(error);
                    if (validator.stopOnError) {
                        return false;
                    }
                }
            });
            handleErrors.call(this, errors);
        };

        /**
         * ``errors`` is an array of validation errors. If this array is
         * empty, the validation was passed successfully.
         */
        function handleErrors(errors) {
            var errorlist = getMethod('findErrorlist', this).call(this);
            if (!errorlist || errorlist.length == 0) {
                var errorlist_markup = getMethod('createErrorlist', this).call(this);
                getMethod('insertErrorlist', this).call(this, errorlist_markup);
                errorlist = getMethod('findErrorlist', this).call(this);
            }
            if (errors.length == 0) {
                getMethod('hideErrorlist', this).call(errorlist);
            } else {
                getMethod('resetErrorlist', this).call(errorlist);
                var insertError = getMethod('insertError', this);
                for (var i = 0; i < errors.length; i++) {
                    insertError.call(errorlist, errors[i]);
                }
            }
        };

        $.fn.addValidator = function (validator) {
            var validators = $(this).data('rays.validators') || [];
            if ($.isFunction(validator)) {
                validator = $.extend({},
                    $.rays.defaultValidator,
                    {validate: validator});
            }
            validators.push(validator);
            $(this).data('rays.validators', validators);
        };

        $(".rays-validation").each(function () {
            var that = this;
            var url = $(this).raysattr('validate', 'url');
            if (url) {
                $(this).blur(function () {
                    var value = $(this).val();
                    if ($(this).attr('type') == 'checkbox') {
                        value = $(this).attr('checked') ? '1' : '0';
                    }
                    $.getJSON(url, {value: value}, function (data) { handleErrors.call(that, data); });
                });
            }
        });

        $(':input').keyup($.rays.validate);
        $(':input').change($.rays.validate);
    });
})(jQuery);
