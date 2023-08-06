// $Id: tsk_index.js dd70bbd8d862 2012/07/14 14:02:51 patrick $

window.addEvent("domready", function() {
    // Slide task
    var task = $("newTask");
    if (task) {
        task = new Fx.Slide(task, {duration: 'long'});
        task.hide().slideIn();
    }
});