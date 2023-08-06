// $Id: publidoc.js 595ce8b0ad17 2012/06/21 16:01:57 patrick $ 

window.addEvent('domready', function() {
    // Tooltips
    (function initialize() {
        $$(".pdocImagePulse").each(function(pulse) {
            if (pulse.getParent().getElement("svg")) 
                var mainImg = pulse.getParent().getElement("svg");
            else
                var mainImg = pulse.getParent().getElement("img");
            var pulseImg = pulse.getElement("img");
            var tooltip  = $(pulse.get('id')+"t");
            mainImg.setStyle("max-width", "none");
            var pulseWidth  = 100 * pulseImg.getSize().x / mainImg.getSize().x;
            var pulseHeight = 100 * pulseImg.getSize().y / mainImg.getSize().y;
            var mainImgRealWidth = mainImg.getSize().x;

            pulse.setStyles({
                "width": pulseWidth + "%", "height": pulseHeight + "%",
                "left": (pulse.getStyle("left").toFloat() - pulseWidth/2) + "%",
                "top":  (pulse.getStyle("top").toFloat() - pulseHeight/2) + "%"
            });
            pulseImg.setStyle("width", "100%");
            mainImg.setStyle("max-width", "100%");
            mainImg.getParent().setStyle("max-width", "100%");

            var fontSize = tooltip.getStyle("font-size").toFloat();
            tooltip.setStyles({
                "opacity": 0, "display": "block",
                "font-size": (fontSize * mainImg.getSize().x / mainImgRealWidth)
                    + tooltip.getStyle("font-size").replace(fontSize, "")
            });
            
            var tooltipImg = tooltip.getElement("img");
            if (tooltipImg) {
                tooltip.setStyle(
                    "width", (100 * tooltipImg.getSize().x / mainImgRealWidth) + "%");
                tooltipImg.setStyle("width", "100%");
            }
        });

        $$(".pdocImagePulse").addEvent("click", function() {
            var pulse   = this;
            var tooltip = $(this.get('id')+"t");
            pulse.setStyle("display", "none");
            tooltip.tween("opacity", 1);
            (function() {
                tooltip.tween("opacity", 0);
                pulse.setStyle("display", "block");
            }).delay(12000);
        });
        
        $$(".pdocImageTooltip").addEvent("click", function() {
            this.tween("opacity", 0);
            $(this.get('id').substr(0, this.get('id').length-1))
                .setStyle("display", "block");
        });
    }).delay(100);
});
