(function() {
var body = $(‘body’);
var backgrounds = new Array(
url('../images/block1o.jpg'),
url('../images/block1p.jpg'),
url('../images/block1e.jpg'),
url('../images/block1n.jpg'),
url('../images/block1s.jpg'),
url('../images/block1a.jpg'),
url('../images/block1l.jpg'),
url('../images/blocke.jpg'),
);
var current = 0;

function nextBackground() {
body.css(
‘background’,
backgrounds[current = ++current % backgrounds.length]
);

setTimeout(nextBackground, 10000);
}
setTimeout(nextBackground, 10000);
body.css(‘background’, backgrounds[0]);
});
