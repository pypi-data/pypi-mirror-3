// $Id: bld_progress.js 51af43175819 2012/01/24 17:23:19 patrick $

window.addEvent("domready", function() {
    // Stop refresh and use AJAX
    if (window.location.search.indexOf("ajax") == -1) {
        var redirect = function() {
            var qs = window.location.search;
            window.location = qs ? qs + "&ajax" : "?ajax";
        };
        redirect.delay(1000);
        return;
    }

    // Request for progress
    var gauge = $("progressGauge");
    var step = $("progressStep");
    var playing = $("playing");
    var request = new Request.JSON({
        url: window.location.pathname.replace("progress", "progress_ajax"),
        onComplete: function(response) {
            if (!response.working) {
                window.location = window.location.pathname.replace("progress", "view");
                return;
            }
            playing.set('text', response.playing);
            gauge.getElement("div").tween("width", [
                gauge.getElement("div").getSize().x, response.percent * gauge.getSize().x / 100]);
            step.set('text', "["+response.percent+"%] "+response.message);
        },
    });

    // Send request periodically
    var refresh = 1000 * $("progress").getProperty('class');
    var update = function(){ request.send(); }
    update.periodical(refresh);
});