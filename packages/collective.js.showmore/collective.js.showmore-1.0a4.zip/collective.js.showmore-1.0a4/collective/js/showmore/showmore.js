(function($) {
 
    var LINK_TEXT = 'Show more...';
    var LINK_TEXT_LESS = 'Show fewer...';
    var LINK_CLASS = 'showMoreLink';
    var LINK_CLASS_LESS = 'showLessLink';
    var HIDDEN_CLASS = 'showMoreHidden';
    var VISIBLE_CLASS = 'showMoreVisible';
    var DISPLAY_LESS = true;
    var GRACE_COUNT = 1;
    
    $.fn.showMore = function(options) {
        // use custom link for more text if provided
        var more_text = options.link_text || LINK_TEXT;
        // use custom link for less text if provided
        var less_text = options.link_text_less || LINK_TEXT_LESS;
        // use custom link class if provided
        var link_class = options.link_class || LINK_CLASS;
        // use custom link class if provided
        var link_class_less = options.link_class_less || LINK_CLASS_LESS;
        // use custom hidden class if provided
        var hidden_class = options.hidden_class || HIDDEN_CLASS;
        // use custom hidden class if provided
        var visible_class = options.visible_class || VISIBLE_CLASS;
        // use custom display less link if provided
        var display_less = options.display_less || DISPLAY_LESS;
        // use custom grace count if provided
        var grace_count = options.grace_count || GRACE_COUNT;
        var nodesToHide = this.find(options.expression);
        // hide nodes only if there are enough to hide
        if (nodesToHide.length > grace_count) {
            nodesToHide.addClass(hidden_class).hide();
        }
        var moreClickHandler = function(e) {
            var parent = $(this).parent()
            // show hidden nodes
            parent.find('.' + hidden_class).removeClass(hidden_class).
                   addClass(visible_class).show();
            // hide more link
            parent.find('.' + link_class).hide();
            // show less link
            parent.find('.' + link_class_less).show();
        };
        // create the more link
        var moreTextNode = document.createTextNode(more_text);
        var moreLink = $('<a />').addClass(link_class).append(moreTextNode).
            css({cursor:'pointer'}).click(moreClickHandler);
        // add more links only if there are hidden nodes
        var hasHiddenNodes = function(index) {
            var count = $(this).find('.' + hidden_class).length;
            return (count > 0);
        };
        this.filter(hasHiddenNodes).append(moreLink);
        // create the (hidden) less link, if necessary
        if (display_less) {
            var lessClickHandler = function(e) {
                    var parent = $(this).parent()
                    // hide visible nodes
                    parent.find('.' + visible_class).removeClass(visible_class).
                           addClass(hidden_class).hide();
                    // show more link
                    parent.find('.' + link_class).show();
                    // hide less link
                    parent.find('.' + link_class_less).hide();
            };
            var lessTextNode = document.createTextNode(less_text);
            var lessLink = $('<a />').addClass(link_class_less).append(lessTextNode).
                css({cursor:'pointer', display:'none'}).click(lessClickHandler);
            this.filter(hasHiddenNodes).append(lessLink);
        };
        return this;
    };

})(jQuery);
