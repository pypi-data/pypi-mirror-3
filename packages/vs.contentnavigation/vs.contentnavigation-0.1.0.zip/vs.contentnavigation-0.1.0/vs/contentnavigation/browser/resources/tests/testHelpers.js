window.vs = window.vs || {};
window.vs.testHelpers = window.vs.testHelpers || {};


(function($) {

vs.testHelpers.testContainer = function() {
    var container = document.getElementById('testcontainer');
    if (! container) {
        container = document.createElement('div');
        container.setAttribute('id', 'testcontainer');
        document.getElementsByTagName('body')[0].appendChild(container);
    }
    return container;
};

vs.testHelpers.collapsibleItem = function(title, children) {
    children = children || [];
    
    this.toHTML = function() {
        var id = title.replace(/[^a-zA-Z0-9]/g, '-');
        var htmlLines = [
            '<div class="collapsible-item " id="' + id + '">',
                '<h3>' + title + '<span/></h3>'
        ];
        if (children.length > 0) {
            htmlLines.push(
                '<div class="collapsible-children ">'
            );
            htmlLines = htmlLines.concat($.map(children, function(item) { return item.toHTML(); } ));
            htmlLines.push(
                '</div>'
            );
        }
        htmlLines.push(
            '</div>'
        );
        return htmlLines.join('\n');
    };
};

}(jQuery));

