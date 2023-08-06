// $Id: base.js bc236c725df4 2012/01/24 22:50:00 patrick $

// State
var idx = {"closed": 0, "tabUser": 1, "tabGroup": 2, "tabStorage": 3,
           "tabProject": 4, "tabProcessing": 5, "tabPack": 6}
var state = Cookie.read("PF_STATE");
if (!state) { state = "false|0|0|0|0|0|0"; }
state = state.split('|');


// showTab function
var showTab = function() {
    $$("ul.tabToc li").removeProperty("class");
    $$(".tabContent").setStyle("display", "none");
    $(this.get("id").replace("Content", "Link"))
        .getParent().setProperty("class", "tabCurrent");
    this.setStyle("display", "block");
    state[idx[this.getParent().getElement(".tabToc").get("id")]] =
        this.get('id').replace("tabContent", "");
    Cookie.write("PF_STATE", state.join("|"), {path: "/"});
}


window.addEvent("domready", function() {
    // Left panel
    var leftSlide = $("leftSlide");
    if (leftSlide) {
        var fxSlide = new Fx.Slide(leftSlide, {mode: "horizontal"});
        var fxTween = new Fx.Tween(leftSlide.getParent(), {duration: "short"});
        state[idx["closed"]] = (state[idx["closed"]] == "true")
        
        if (state[idx["closed"]] ) {
            fxSlide.hide();
            $("content2").setStyle("right", "98%");
            $("leftPanel").setStyles({width:"2%", left:"98%"});
            $("mainPanel").setStyles({width:"98%", left:"98.09%"});
            $("leftClose").getElement("a").set("text", "»");
            $("left").setStyle("visibility", "hidden");
            fxTween.set("width", $("leftPanel").getSize().x);
        }

        $("leftClose").addEvent("click", function(e) {
            e.stop();
            if (state[idx["closed"]])
                fxTween.start("width", "0").chain(function(){
                    $("content2").setStyle("right", "78%");
                    $("leftPanel").setStyles({width:"22%", left:"78%"});
                    $("mainPanel").setStyles({width:"78%", left:"78%"});
                    $("left").setStyle("visibility", "visible");
                    $("leftClose").getElement("a").set("text", "«");
                    fxSlide.slideIn().chain(function(){
                        leftSlide.getParent().setStyle("width", "");});
                });
            else
                fxSlide.slideOut().chain(function(){
                    $("content2").setStyle("right", "98%");
                    $("leftPanel").setStyles({width:"2%", left:"98%"});
                    $("mainPanel").setStyles({width:"98%", left:"98.09%"});
                    $("leftClose").getElement("a").set("text", "»");
                    $("left").setStyle("visibility", "hidden");
                    fxTween.start("width", $("leftPanel").getSize().x);
                });
            state[idx["closed"]] = !state[idx["closed"]];
            Cookie.write("PF_STATE", state.join("|"), {path: "/"});
        });
    }

    // Tab set
    var tabSet = $("tabSet");
    if (tabSet) {
        $$(".tabContent").each(function(item, index) {
            item.setProperty("id", item.get("id").replace("tab", "tabContent"));  
        });
        var tab = new String(window.location);
        tab = $("tabContent" + tab.split("#tab")[1]);
        if (!tab) tab = $("tabContent" + state[idx[tabSet.getElement(".tabToc").get("id")]]);
        if (!tab) tab = $("tabContent0");
       
        showTab.bind(tab)();
        $$(".tabLink").each(function(item, index) {
            item.addEvent("click", showTab.bind($(item.get("id").replace("Link", "Content"))));
        });
    }

    // Flash
    var flash = $("flash");
    if (!flash) flash = $("flashAlert");
    if (flash) {
        flash = new Fx.Slide(flash);
        flash.hide().slideIn();
        (function(){flash.slideOut();}).delay(10000);
    }

    // Action parameters
    var actionParams = $("actionParams");
    if (actionParams) { (new Fx.Slide(actionParams)).hide().slideIn(); }

    // ToolTip
    var toolTip = $("toolTip");
    if (toolTip) {
        toolTip = new Fx.Slide(toolTip);
        toolTip.hide().slideIn();
        (function(){toolTip.slideOut();}).delay(20000);
    }

    // Check all buttons
    var checkAll = $('check_all');
    if (checkAll) {
        checkAll.addEvent("click", function(e) {
            $$("input.listCheck").setProperty("checked", checkAll.getProperty("checked"));
        });
    }

    // Slow button
    var slowImg = new Element("img", {"src": "/Static/Images/wait_slow.gif", "alt": "slow"});
    $$("a.slow").addEvent("click", function() {
      if (this.getElement("img"))
        { this.getElement("img").src = "/Static/Images/wait_slow.gif"; }
      else
        { this.appendText(' '); slowImg.inject(this); }
    });
    $$("input.slow").addEvent("click", function() {
        if (this.src) this.src = "/Static/Images/wait_slow.gif";
        else slowImg.inject(this.getParent());
    });

  // VCS parameters
  var vcsParams = $("vcsParams");
  if (vcsParams) {
    var vcsEngine = $("vcs_engine");
    var vcsParamsDiv = new Fx.Slide(vcsParams);
    var stgURI = new Fx.Slide($("stgURL"));
    if (vcsEngine.value == "none" || vcsEngine.value == "local") {
        vcsParamsDiv.hide();
        stgURI.show();
    } else {
        vcsParamsDiv.show();
        stgURI.hide();
    }

    vcsEngine.addEvent("change", function(e){
      e.stop();
      if (vcsEngine.value == "none" || vcsEngine.value == "local") {
        stgURI.slideIn(); 
        vcsParamsDiv.slideOut();
      } else {
        vcsParamsDiv.slideIn();
        stgURI.slideOut(); 
      }
    });
  }
});
