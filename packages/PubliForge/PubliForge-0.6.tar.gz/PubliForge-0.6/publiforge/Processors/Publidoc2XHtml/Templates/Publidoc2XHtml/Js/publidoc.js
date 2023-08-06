// $Id: publidoc.js c24008cf2ab8 2012/06/02 16:20:06 patrick $ 

var text = null;
var spot = null;
var box = null;
var boxProperty = '';

window.addEvent('domready', function(){
    // Tooltips
    $$(".pdocImageTooltip").setStyles({"opacity": 0, "display": "block"});
    $$(".pdocImagePulse").addEvent("click", function() {
        var pulse = this;
        var tooltip = $(this.get('id')+"t");
        pulse.setStyle("display", "none");
        tooltip.tween("opacity", 1);
        (function(){
            tooltip.tween("opacity", 0);
            pulse.setStyle("display", "block");
        }).delay(12000);
    });
   $$(".pdocImageTooltip").addEvent("click", function() {
       this.tween("opacity", 0);
       $(this.get('id').substr(0, this.get('id').length-1)).setStyle("display", "block");
   });
     
    // Effect: glow
    var effectGlow = $("effectGlow");
    if (effectGlow) {
        text = $("effectGlowText");
        spot = $("effectGlowSpot");
        box = $("effectGlowBox")
        if (typeof box.style.webkitBoxShadow == 'string') {
            boxProperty = 'webkitBoxShadow';
        } else if (typeof box.style.MozBoxShadow == 'string') {
            boxProperty = 'MozBoxShadow';
        } else if (typeof box.style.boxShadow == 'string') {
            boxProperty = 'boxShadow';
        }

        if (text && spot && box) {
            effectGlow.onmousemove = onMouseMove;
            effectGlow.ontouchmove = function (e) {
                e.preventDefault();
                e.stopPropagation();
                onMouseMove({clientX: e.touches[0].clientX, clientY: e.touches[0].clientY});
            }
        }
    }
});


function onMouseMove(e) {
    if (typeof e === 'undefined' || typeof e.clientX === 'undefined') {
        return;
    }
    
    var xm = (e.clientX - Math.floor(window.innerWidth / 2)) * 0.4;
    var ym = (e.clientY - Math.floor(window.innerHeight / 3)) * 0.4;
    var d = Math.round(Math.sqrt(xm*xm + ym*ym) / 5);
    text.style.textShadow = -xm + 'px ' + -ym + 'px ' + (d + 10) + 'px black';
    
    if (boxProperty) {
        box.style[boxProperty] = '0 ' + -ym + 'px ' + (d + 30) + 'px black';
    }
    
    xm = e.clientX - Math.floor(window.innerWidth / 2);
    ym = e.clientY - Math.floor(window.innerHeight / 2);
    spot.style.backgroundPosition = xm + 'px ' + ym + 'px';
}

