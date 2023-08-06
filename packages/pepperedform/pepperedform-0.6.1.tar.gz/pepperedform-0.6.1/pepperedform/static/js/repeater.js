/*
Handle repeaters for sequences.

Usually you will create one manager for an entire page unless you have widgets
nested inside templates and then you will need to pass in callbacks to be
called when a new repetition is created.
*/
var repeater = {
    init: function (imports) {
        /* Initialize this module. */
    },
    RepeaterManager: new Class({
        Implements: [Events, Options],
        options: {
            cssClasses: {
                repeater: 'repeater',
                adder: 'adder',
                remover: 'remover',
                repetition: 'repetition',
                repetitions: 'repetitions'
            },
            randomCharSet: 'abcdefghijklmnopqrstuvwxyz0123456789',
            randomLength: 8,
            randomIdPrefix: 'randomid-',
            rewriteIdRe: new RegExp('^.*__REPEATER__.*$')
        },
        init: function (options) {
            /* Setup css classes and events for this manager to use. */
            this.setOptions(options);
        },
        attach: function (containerEl) {
            /* Attach all repeaters in the given container element. */
            var repeaterEls = containerEl.getElements(
                    '.' + this.options.cssClasses.repeater);
            Array.each(repeaterEls, function (repeaterEl) {
                // Make sure we don't activate sub-repeaters twice.
                var isSubrepeater = repeaterEl.getParent(
                    '.' + this.options.cssClasses.repeater) !== null;
                if (!isSubrepeater) {
                    this.attachEvents(repeaterEl);
                }
            }, this);
        },
        attachEvents: function (containerEl) {
            var adderEls, removerEls;
            adderEls = containerEl.getElements(
                '.' + this.options.cssClasses.adder);
            removerEls = containerEl.getElements(
                '.' + this.options.cssClasses.remover);
            Array.each(adderEls, this.activateAdder, this);
            Array.each(removerEls, this.activateRemover, this);
        },
        addRepetition: function (e) {
            /* Add a repetition to the repeater using its template. */
            var repEl, templateStr, idEls, forEls, repeaterEl,
                    repetitionsEl, forMap;
            repeaterEl = document.id(e.target).getParent(
                    '.' + this.options.cssClasses.repeater);
            repetitionsEl = repeaterEl.getElement(
                    '.' + this.options.cssClasses.repetitions);
            // Get template string from attribute set on repeater
            // container element.
            templateStr = repeaterEl.get('data-template');
            // Inject the template str into a dummy element and get
            // first repetition element out.
            repEl = (new Element('div', {
                'html': templateStr
            })).getElement('.' + this.options.cssClasses.repetition);
            // Rewrite id and for attributes.
            idEls = repEl.getElements('[id]');
            forEls = repEl.getElements('[for]');
            forMap = {};
            Array.each(forEls, function (forEl) {
                forMap[forEl.get('for')] = forEl;
            });
            Array.each(idEls, function (idEl) {
                var id, matchInfo, forEl, newId;
                id = idEl.get('id');
                if (this.options.rewriteIdRe.test(id)) {
                    if (forMap.hasOwnProperty(id)) {
                        forEl = forMap[id];
                    } else {
                        forEl = null;
                    }
                    newId = this.generateRandomId();
                    idEl.set('id', newId);
                    if (forEl !== null) {
                        forEl.set('for', newId);
                        delete forMap[id];
                    }
                }
            }, this);
            Array.each(forEls, function (forEl) {
                var forAttr = forEl.get('for');
                if (forMap.hasOwnProperty(forAttr)) {                    
                    forEl.set('for', this.generateRandomId());
                    delete forMap[forAttr];
                }
            }, this);
            // Setup any repeaters that were in template.
            this.attachEvents(repEl);
            this.fireEvent('repetitionCreated', [repEl]);
            repetitionsEl.grab(repEl);
            this.fireEvent('repetitionInjected', [repEl]);
        },
        removeRepetition: function (e) {
            /* Remove a repetition from the repeater. */
            var el, parentEl;
            el = document.id(e.target);
            parentEl = el.getParent('.' + this.options.cssClasses.repetition);
            parentEl.destroy();
        },
        activateAdder: function (adderEl) {
            adderEl.addEvent('click', this.addRepetition.bind(this));
        },
        activateRemover: function (removerEl) {
            removerEl.addEvent('click', this.removeRepetition.bind(this));
        },
        generateRandomId: function () {
            /* Generate a random dom element id. */
            var charSet, i, id, charSetLength, randomId;
            charSet = this.options.randomCharSet;
            randomId = this.options.randomIdPrefix;
            charSetLength = charSet.length;
            for (i = 0; i < this.options.randomLength; i += 1) {
                randomId += charSet.charAt(
                    Math.floor(Math.random() * (charSetLength + 1)));
            }
            return randomId;
        }
    })
};