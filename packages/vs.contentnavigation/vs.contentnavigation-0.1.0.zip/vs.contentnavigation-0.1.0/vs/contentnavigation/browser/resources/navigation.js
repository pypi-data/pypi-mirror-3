window.vs = window.vs || {};

(function($) {
vs.Collapsible = function(options) {
    var settings = $.extend({}, vs.Collapsible.defaults, options);
    
    /* --- private helpers -------------------------------------------------- */
    var bind = function(thisReplacement, targetFunction) {
        return function() {
                return targetFunction.apply(thisReplacement, arguments);
        };
    };

    /* --- public API ------------------------------------------------------- */
    
    this.init = bind(this, function() {
        this.registerTriggers();
        this.establishInitialState();
    });
    
    this.hide = bind(this, function($item) {
        $item.removeClass(settings.cssOpen);
        $item.addClass(settings.cssClosed);
        $children = $item.find('.collapsible-children:first');
        settings.closingAnimation($children);
    });
    
    this.show = bind(this, function($item, additionalCSSClass) {
        $item.removeClass(settings.cssClosed);
        $item.addClass(settings.cssOpen).addClass(additionalCSSClass);
        $children = $item.find('.collapsible-children:first');
        settings.openingAnimation($children);
    });
    
    this.reveal = bind(this, function($item) {
        var $parents = $item.parents(settings.collapsibleItems);
        for (var i=0; i<$parents.length; i++) {
            var $parent = $($parents[i]);
            this.show($parent, 'collapsible-initially-open');
        }
        this.show($item, 'collapsible-initially-open');
    });
    
    /* --- internal implementation ------------------------------------------ */
    
    this.establishInitialState = bind(this, function() {
        var $collapsibleItems = $(settings.collapsibleItems);
        var previousClosingAnimation = settings.closingAnimation;
        settings.closingAnimation = function($item) { $item.hide(); };
        for (var i=0; i<$collapsibleItems.length; i++) {
            var $item = $($collapsibleItems[i]);
            this.hide($item);    
        }
        settings.closingAnimation = previousClosingAnimation;
        
        var previousOpeningAnimation = settings.openingAnimation;
        settings.openingAnimation = function($item) { $item.show(); };
        for (var i=0; i<settings.initiallyOpenItems.length; i++) {
            var $elementToOpen = $(settings.initiallyOpenItems[i]);
            this.reveal($elementToOpen);
        }
        settings.openingAnimation = previousOpeningAnimation;
    });
    
    this.registerTriggers = bind(this, function() {
        var $collapsibleItems = $(settings.collapsibleItems);
        $collapsibleItems.find('h3 > span').click(this.handleCollapsibleToggle);
    });
    
    this.handleCollapsibleToggle = bind(this, function(event) {
        var $clickedItem = $(event.target);
        var $container = $clickedItem.parents(settings.collapsibleItems).first();
        if ($container.hasClass(settings.cssOpen))
            this.hide($container);
        else
            this.show($container);
    });
    
};

vs.Collapsible.defaults = {
    collapsibleItems: undefined,
    initiallyOpenItems: [],
    
    cssOpen: 'collapsible-open',
    cssClosed: 'collapsible-closed',
    
    openingAnimation: function($item) { $item.show('slow'); },
    closingAnimation: function($item) { $item.hide('slow'); }
};


$(document).ready(function() {
    if (vs.testHelpers)
        return;
    
    var collapsible = new vs.Collapsible({
        collapsibleItems: '.collapsible-item',
        initiallyOpenItems: ['.initiallyOpen']
    });
    collapsible.init();
});

}(jQuery));


