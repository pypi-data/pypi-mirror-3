// $Id: stg_index.js bc236c725df4 2012/01/24 22:50:00 patrick $

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
            url: window.location.pathname.replace("index", "index_ajax"),
            onComplete: function(response) {
                if (!response.working) {
                    window.location = window.location.href;
                    return;
                }
                $$("img.wait").each(function(item, index) {
                    if (!response[item.get("id")]) {
                        item.src = item.src.replace(
                            "wait_synchro.gif", "action_synchronize_one.png");
                        item.removeClass("wait");
                    }
                });
            },
        });
        
        // Send request periodically
        refresh = 1000 * refresh.getProperty('class');
        var update = function(){ request.send(); }
        update.periodical(refresh);
    }
});