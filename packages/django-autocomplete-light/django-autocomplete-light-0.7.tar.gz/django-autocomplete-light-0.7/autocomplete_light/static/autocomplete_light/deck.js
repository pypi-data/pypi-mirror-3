function AutocompleteDeck(el) {
    this.wrapper = el;

    this.input = this.wrapper.find('input[type=text].autocomplete')
    this.valueSelect = this.wrapper.find('select.valueSelect');
    this.payload = $.parseJSON(this.wrapper.find('.json_payload').html());
    this.deck = this.wrapper.find('.deck');
    this.addTemplate = this.wrapper.find('.add_template .result');

    this.getValue = function(result) {
        return result.data('value');
    };
    this.initializeAutocomplete = function() {
        this.autocomplete = this.input.yourlabs_autocomplete(this.autocompleteOptions);
    };
    this.bindSelectOption = function() {
        this.input.bind('selectOption', function(e, option) {
            if (!option.length)
                return // placeholder: create option here

            var wrapper = $(this).parents('.autocomplete_light_widget');
            var deck = wrapper.yourlabs_deck();

            deck.selectOption(option);
        });
    };
    this.freeDeck = function() {
        // Remove an item if the deck is already full
        if (this.payload.max_items && this.deck.children().length >= this.payload.max_items) {
            var remove = $(this.deck.children()[0]);
            this.valueSelect.find('option[data-value='+remove.attr('data-value')+']').attr(
                'selected', '').remove();
            remove.remove();
        }
    }
    this.updateDisplay = function() {
        this.input.val('');

        if (this.payload.max_items && this.valueSelect.find('option').length == this.payload.max_items) {
            this.input.hide();
        } else {
            this.input.show();
        }

        this.deck.show();
    }
    this.addToDeck = function(result, value) {
        var item = this.deck.find('[data-value='+value+']');
        if (!item.length) {
            var result = result.clone();

            // Might be necessary for created values.
            if (!result.attr('data-value')) {
                result.attr('data-value', value);
            }

            this.deck.append(result);
            result.append('<span class="remove">' + this.wrapper.find('.remove').html() + '</span>');
        }
    }
    this.addToSelect = function(result, value) {
        var option = this.valueSelect.find('option[value='+value+']');
        if (! option.length) {
            this.valueSelect.append(
                '<option selected="selected" value="'+ value +'"></option>');
            option = this.valueSelect.find('option[value='+value+']');
        }
        option.attr('selected', 'selected');
        this.valueSelect.trigger('change');
    }
    this.selectOption = function(result) {
        // Get the value for this result.
        var value = this.getValue(result);

        this.freeDeck();
        this.addToDeck(result, value);
        this.addToSelect(result, value);
        this.updateDisplay();
    }
    this.deselectOption = function(result) {
        var value = this.getValue(result);

        this.valueSelect.find('option[value='+value+']').remove();
        this.valueSelect.trigger('change');
        result.remove();

        if (this.deck.find('*').length == 0) {
            this.deck.hide();
        }

        if (this.payload.max_items && this.valueSelect.find('option').length < this.payload.max_items) {
            this.input.show();
        }
    };
    this.autocompletId = this.input.attr('id');
    this.autocompleteOptions = {
        url: this.payload.channel.url,
        id: this.autocompletId,
        iterablesSelector: '.result',
        minCharacters: this.payload.min_characters,
        outerContainerClasses: 'autocomplete_light_widget',
        defaultValue: this.payload.placeholder,
    }
    this.initialize = function() {
        var results = this.deck.find('.result');

        results.append(this.wrapper.find('.remove:last').clone().show());
        if (this.payload.max_items > 0 && results.length == this.payload.max_items) {
            this.input.hide();
        }

        this.initializeAutocomplete();
        this.bindSelectOption();
    }
}

$.fn.yourlabs_deck = function(overrides) {
    var id;
    overrides = overrides ? overrides : {};
    id = overrides.id || this.attr('id');

    if (!(id && this)) {
        alert('failure: the element needs an id attribute, or an id option must be passed');
        return false;
    }

    if ($.fn.yourlabs_deck.registry == undefined) {
        $.fn.yourlabs_deck.registry = {};
    }

    if ($.fn.yourlabs_deck.registry[id] == undefined) {
        $.fn.yourlabs_deck.registry[id] = new AutocompleteDeck(this);
        $.fn.yourlabs_deck.registry[id] = $.extend($.fn.yourlabs_deck.registry[id], overrides);
        $.fn.yourlabs_deck.registry[id].initialize();
        $.fn.yourlabs_deck.registry[id].wrapper.attr('data-deckready', 1);
        $.fn.yourlabs_deck.registry[id].wrapper.trigger('deckready');
    }

    return $.fn.yourlabs_deck.registry[id];
}

$(document).ready(function() {
    $('.autocomplete_light_widget[data-bootstrap=normal]').each(function() {
        var deck = $(this).yourlabs_deck();
    });

    $('.autocomplete_light_widget .deck .remove').live('click', function() {
        var wrapper = $(this).parents('.autocomplete_light_widget');
        if (!wrapper.length) return;
        var deck = wrapper.yourlabs_deck();
        var selector = deck.input.yourlabs_autocomplete().iterablesSelector;
        var result = $(this).parents(selector);
        deck.deselectOption(result);
    });

    // support values added directly in the select via js (ie. admin + sign)
    // for this, we make one timer that regularely checks for values in the select
    // that are not in the deck. The reason for that is that change is not triggered
    // when options are added like this:
    // $('select#id_dependencies').append(
    //      '<option value="9999" selected="selected">blabla</option>')
    function updateDecks() {
        $('.autocomplete_light_widget[data-deckready=1]').each(function() {
            var deck = $(this).yourlabs_deck();
            var value = deck.valueSelect.val();

            function updateValueDisplay(value) {
                if (!value) return;

                var result = deck.deck.find('[data-value='+value+']');
                if (!result.length) {
                    var result = deck.addTemplate.clone();
                    var html = deck.valueSelect.find('option[value='+value+']').html();
                    result.html(html);
                    result.attr('data-value', value);
                    deck.selectOption(result);
                }
            }

            if (value instanceof Array) {
                for(var i=0; i<value.length; i++) {
                    updateValueDisplay(value[i]);
                }
            } else {
                updateValueDisplay(value);
            }
        });
        setTimeout(updateDecks, 2000);
    }
    setTimeout(updateDecks, 1000);
});
