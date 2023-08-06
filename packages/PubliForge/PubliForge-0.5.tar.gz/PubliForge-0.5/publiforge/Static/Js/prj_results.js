// $Id: prj_results.js b1ffa5a75b89 2012/02/19 23:23:01 patrick $

window.addEvent("domready", function() {
    // Stop refresh and use AJAX
    var refresh = $("refresh");
    if (refresh && window.location.search.indexOf("ajax") == -1) {
        var redirect = function() {
            var qs = window.location.search;
            window.location = qs ? qs + "&ajax" : "?ajax";
        };
        redirect.delay(1000);
        return;
    }

    // Request for progress
    if (refresh) {
        var request = new Request.JSON({
            url: window.location.pathname.replace("results", "results_ajax"),
            onComplete: function(response) {
                if (!response.working) {
                    window.location = window.location.href;
                    return;
                }
                $$("div.progressGauge").each(function(item, index) {
                    if (response[item.get("id").substring(6)])
                        item.getElement("div").setStyle(
                            "width", response[item.get("id").substring(6)] + "%");
                    else
                        item.getElement("div").setStyle("width", "100%");
                        
                });
            },
        });
        
        // Send request periodically
        refresh = 1000 * refresh.getProperty('class');
        var update = function(){ request.send(); }
        update.periodical(refresh);
    }
});