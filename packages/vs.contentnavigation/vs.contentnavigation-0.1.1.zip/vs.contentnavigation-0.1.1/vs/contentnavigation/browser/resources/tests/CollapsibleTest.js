
window.vs = window.vs || {};
window.vs.testHelpers = window.vs.testHelpers || {};

(function($) {

describe("Collapsible", function() {
    var collapsible = null;
    
    beforeEach(function() {
        vs.testHelpers.testContainer().innerHTML = '';
        
        var Item = vs.testHelpers.collapsibleItem;
        var folder1_tree = new Item('Folder 1', [
            new Item('Folder 1.1', [
                new Item('Folder 1.1.1'),
                new Item('Folder 1.1.2')
            ]),
            new Item('Folder 1.2', [
                new Item('Folder 1.2.1'),
                new Item('Folder 1.2.2')
            ])
        ]);
        this.suite.renderTree(folder1_tree);
        var folder2_tree = new Item('Folder 2', [
            new Item('Folder 2.1', [
                new Item('Folder 2.1.1'),
                new Item('Folder 2.1.2')
            ]),
            new Item('Folder 2.2', [
                new Item('Folder 2.2.1'),
                new Item('Folder 2.2.2')
            ])
        ]);
        this.suite.renderTree(folder2_tree);
        collapsible = this.suite.collapsible();
    });

/* --- working on a single-element ------------------------------------------ */

    it('can hide a single element', function() {
        expect($('.collapsible-item.collapsible-closed').length).toBe(0);
        expect($('.collapsible-item .collapsible-children:visible').length).toBe((1+2)+(1+2));
        
        collapsible.hide($('#Folder-1-1'));
        expect($('.collapsible-item.collapsible-closed').length).toBe(1);
        expect($('.collapsible-item .collapsible-children:visible').length).toBe((1+1)+(1+2));
    });

    it('can make a single element (and its parents) visible', function() {
        collapsible.establishInitialState();
        expect($('.collapsible-item .collapsible-children:visible').length).toBe(0);
                
        collapsible.reveal($('#Folder-1-2-1'));
        expect($('#Folder-1').hasClass('collapsible-open')).toBe(true);
        expect($('#Folder-1-2').hasClass('collapsible-open')).toBe(true);
        expect($('#Folder-1-2-1').hasClass('collapsible-open')).toBe(true);
        expect($('.collapsible-item .collapsible-children:visible').length).toBe(2);
    });

/* --- initialization ------------------------------------------------------- */

    it('hides all elements below the root level by default', function() {
        expect($('.collapsible-item .collapsible-children:visible').length).toBe(2*3);
        expect($('.collapsible-item.collapsible-closed').length).toBe(0);
        
        collapsible.establishInitialState();
        expect($('.collapsible-item .collapsible-children:visible').length).toBe(0);
        expect($('.collapsible-item.collapsible-closed').length).toBe(2*7);
    });

    it('can configure items displayed by default', function() {
        $(vs.testHelpers.testContainer()).find('#Folder-1-2-1').addClass('initiallyOpen');
        collapsible = this.suite.collapsible({
            initiallyOpenItems: ['.initiallyOpen']
        });
        
        collapsible.establishInitialState();
        expect($('#Folder-1-2-1').hasClass('collapsible-open')).toBe(true);
        expect($('.collapsible-item .collapsible-children:visible').length).toBe(2);
        
        expect($('#Folder-1').hasClass('collapsible-initially-open')).toBe(true);
        expect($('#Folder-1-2').hasClass('collapsible-initially-open')).toBe(true);
        expect($('#Folder-1-2-1').hasClass('collapsible-initially-open')).toBe(true);
    });
    
    
    /* --- internal helpers ------------------------------------------------- */

    this.renderTree = function(tree) {
        $([
        '<div id="subnavigation-sitemap">',
            tree.toHTML(),
        '</div>'].join('\n')).appendTo(vs.testHelpers.testContainer());
    };

    this.collapsible = function(options) {
        defaults = {
            collapsibleItems: '.collapsible-item', 
            openingAnimation: function($item) { $item.show(); },
            closingAnimation: function($item) { $item.hide(); }
        };
        return new vs.Collapsible(
            $.extend({}, defaults, options)
        );
    };
});

}(jQuery));

