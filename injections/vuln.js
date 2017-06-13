var icon = document.getElementById("list-icon");
var head = document.head || document.getElementsByTagName('head')[0];

var style = document.createElement('style');
var css = '#list-icon{cursor:pointer;transition:background-color 1s;}';
style.type = 'text/css';
if(style.styleSheet){style.styleSheet.cssText = css;}else{style.appendChild(document.createTextNode(css));}
head.appendChild(style);

window.onhashchange = function(){window.onhashchange=null;alert('Cancelling');};

icon.onclick = function(){window.onhashchange=null;alert('Activated');};