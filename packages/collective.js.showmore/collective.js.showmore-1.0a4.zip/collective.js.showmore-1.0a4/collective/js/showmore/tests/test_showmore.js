module('showMore', {
    setup: function() {
        $('#main').append($(
            '<div class="showMoreSection">' + 
            '<p>First paragraph</p>' +
            '<p>Second paragraph</p>' +
            '<p>Third paragraph</p>' +
            '</div>'
        ));
    },
    teardown: function() {
    }
});

test('jQuery chaining', function() {
    expect(1);
    
    var main = $('#main');
    same(main.showMore({}), main, 
         'showMore returns original jQuery object');
});

test('hide all', function() {
    expect(5);
    
    $('#main').showMore({expression:'p'});
    var hidden = $('p.showMoreHidden');
    same(hidden.length, 3, 'showMore adds class to three nodes');
    var hidden = $('p:hidden');
    same(hidden.length, 3, 'showMore hides three nodes');
    var link = $('a.showMoreLink')
    same(link.length, 1, 
         'showMore adds a link');
    same(link.text(), 'Show more...',
         'link has default text');
    link.click();
    var link = $('a.showMoreLink')
    same(link.length, 0, 
         'handler removes the link');
});

test('click link handler', function() {
    expect(3);
    
    var section = $('#main').showMore({expression:'p'})
    var link = $('a.showMoreLink')
    link.click();
    var visible = $('p:visible');
    same(visible.length, 3, 'handler shows all hidden nodes');
    var hidden = $('p:not(.showMoreHidden)');
    same(hidden.length, 3, 'handler removes class from all hidden nodes');
    var link = $('a.showMoreLink')
    same(link.length, 0, 
         'handler removes the link');
});

test('hide none', function() {
    expect(3);
    
    $('#main').showMore({expression:'p:gt(2)'});
    var hidden = $('p.showMoreHidden');
    same(hidden.length, 0, 'showMore adds class to 0 nodes');
    var hidden = $('p:hidden');
    same(hidden.length, 0, 'showMore hides no nodes');
    var link = $('a.showMoreLink')
    same(link.length, 0, 
         'showMore adds no link because it does not hide any node');
});

test('hide some', function() {
    expect(3);
    
    $('#main').showMore({expression:'p:gt(0)'});
    var hidden = $('p.showMoreHidden');
    same(hidden.length, 2, 'showMore adds class to 2 nodes');
    var hidden = $('p:hidden');
    same(hidden.length, 2, 'showMore hides 2 nodes');
    var link = $('a.showMoreLink')
    same(link.length, 1, 
         'showMore adds the link because some nodes were hidden');
});

test('hide none because of grace', function() {
    expect(3);
    
    $('#main').showMore({expression:'p:gt(1)'});
    var hidden = $('p.showMoreHidden');
    same(hidden.length, 0, 'showMore adds class to 0 nodes');
    var hidden = $('p:hidden');
    same(hidden.length, 0, 'showMore hides 0 nodes');
    var link = $('a.showMoreLink')
    same(link.length, 0, 
         'showMore adds no link because it does not hide any node');
});

test('custom link text', function() {
    expect(2);
    
    var CUSTOM = 'More...'
    $('#main').showMore({expression:'p', link_text:CUSTOM});
    var link = $('a.showMoreLink')
    same(link.length, 1, 
         'showMore adds a link');
    same(link.text(), CUSTOM,
         'link has custom text');
});

test('custom link class', function() {
    expect(1);
    
    var CUSTOM = 'linkClass'
    $('#main').showMore({expression:'p', link_class:CUSTOM});
    var link = $('a.' + CUSTOM)
    same(link.length, 1, 
         'showMore adds a link with custom class');
});

test('custom hidden class', function() {
    expect(1);
    
    var CUSTOM = 'hiddenClass'
    $('#main').showMore({expression:'p', hidden_class:CUSTOM});
    var hidden = $('p.' + CUSTOM);
    same(hidden.length, 3, 'showMore adds custom class to three nodes');
});

test('custom grace count', function() {
    expect(2);
    
    var CUSTOM = 3
    $('#main').showMore({expression:'p', grace_count:CUSTOM});
    var hidden = $('p.showMoreHidden');
    same(hidden.length, 0, 'showMore adds custom class to 0 nodes');
    var hidden = $('p:hidden');
    same(hidden.length, 0, 'showMore hides 0 nodes');
});

