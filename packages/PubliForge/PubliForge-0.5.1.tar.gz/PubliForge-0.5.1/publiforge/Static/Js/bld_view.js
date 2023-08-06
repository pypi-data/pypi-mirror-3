// $Id: bld_view.js dee5b2f98448 2012/01/18 09:10:50 patrick $

window.addEvent("domready", function() {
    // Log
    var log = $("log");
    if (log) {
        var logSlide = new Fx.Slide($("logLines"));
        var logA = log.getElement("a.toggle")

        if (log.hasClass("end")) {
            logSlide.hide();
            var src = logA.getElement("img").src;
            logA.getElement("img").src = src.substring(0, src.lastIndexOf("/"))+"/open_false.png";
        }

        logA.addEvent("click", function(e){ e.stop(); logSlide.toggle(); });

        logSlide.addEvent("complete", function() {
            var src = logA.getElement("img").src;
            logA.getElement("img").src = src.substring(0, src.lastIndexOf("/"))+"/open_"+this.open+".png";
        });
    }
});