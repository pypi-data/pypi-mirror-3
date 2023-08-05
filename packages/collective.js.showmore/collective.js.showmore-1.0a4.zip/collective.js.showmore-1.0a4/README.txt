collective.js.showmore
======================

Introduction
------------

`collective.js.showmore` provides a JQuery plugin.

The plugin hides a set of nodes and replaces them with a "Show more..." link.
When the link is clicked, the hidden nodes are made visible again.


API
---

The plugin defines a new `showMore` function.
It requires a dictionary as parameter.

The dictionary parameter has one required value:

`expression`
    The expression is a jQuery selector used to select which children nodes
    will be hidden.  In case no nodes are hidden, the link is not created.

The dictionary parameter can optionally define other values:

`grace_count`
    Defines how many items should not be hidden; default value is 1.
    In the default case, if there is only one item that would be
    hidden, do not hide and replace it with the link.

`link_text`
    Defines the text of the more link; default value is "Show more...".

`link_class`
    Defines the class added to the more link; default value is
    `showMoreLink`.

`hidden_class`
    Defines the class set on the hidden nodes; default value is
    `showMoreHidden`.

`display_less`
    Enable or disable the display of the less link; default value is 
    `true`.

`link_text_less`
    Defines the text of the less link; default value is "Show fewer...".

`link_class_less`
    Defines the class added to the less link; default value is
    `showLessLink`.

`visible_class`
    Defines the class set on the visible nodes; default value is
    `showMoreVisible`.


Example
-------

The function can be called like the following::

    jq(function() {
        jq('ul').showMore({expression:'li:gt(1)'});
    });

`li` children nodes of all `ul`'s of the document will be hidden (except the
two first `li`s of each `ul`). A "Show more..." link will be added at the end
of each `ul`. `ul`'s with two or less `li`'s will remain untouched. A "Show
less..." link will be displayed when you click in the "Show more..." link,
so that you can alternate the hidden/visible content.


Miscellaneous
-------------

The Javacript code is registered as a Z3 resource::

    ++resource++collective.showmore.js
