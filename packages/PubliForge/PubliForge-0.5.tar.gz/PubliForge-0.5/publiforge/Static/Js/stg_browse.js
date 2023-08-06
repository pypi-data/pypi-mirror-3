// $Id: stg_browse.js 4a0f5530bf3c 2012/01/25 23:01:47 patrick $

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
            url: window.location.pathname.replace("browse", "browse_ajax"),
            onComplete: function(response) {
                if (!response.working) {
                    window.location = window.location.href;
                    return;
                }
            },
        });
        
        // Send request periodically
        refresh = 1000 * refresh.getProperty('class');
        var update = function(){ request.send(); }
        update.periodical(refresh);
    }
});