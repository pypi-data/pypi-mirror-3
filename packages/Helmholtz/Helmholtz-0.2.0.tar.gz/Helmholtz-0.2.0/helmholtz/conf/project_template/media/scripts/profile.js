dojo.require("dojo.parser");
dojo.require("dojox.charting.Chart2D");
dojo.require("dojox.charting.action2d.Highlight");
dojo.require("dojox.charting.action2d.Tooltip");
dojo.require("dijit.Dialog");
dojo.require("dijit.TitlePane");
dojo.require("dojox.charting.themes.PlotKit.green");
dojo.require("dojo.fx");

function open_close_container(e){  
    if (e.target.getAttribute('id') == 'open_members_button') {
        target = dojo.byId("members_container");
    }
    if (dojo.style(target,'height') < 1) {
        state = "opened";
        var anim = dojo.fx.wipeIn({node:target,duration:500})
    }
    else {
	    state = "closed";
	    var anim = dojo.fx.wipeOut({node:target,duration:500})
    }
    setCookie("memberExpander",state,1);
    anim.play();  
}

function open_close_row(e){
    var index = expanders.indexOf(e.target);
    var row = rows[index];
    if (dojo.style(row,'height') > 1) {
        var anim = dojo.fx.wipeOut({'node':row,'duration':0});
        var state = "closed";
    }
    else {
	    var anim = dojo.fx.wipeIn({'node':row,'duration':0});
        var state = "opened";
    }
    setCookie("positionExpander_" + index,state,1);
	anim.play();
}

/*member expanders*/
var node = dojo.byId("members_container");
var state = getCookie("memberExpander");
if (state != "opened") dojo.style(node,{'height':'0px','overflow':'hidden'});
dojo.connect(dojo.byId("open_members_button"),'onclick',null,open_close_container);
/*position expanders*/
expanders = dojo.query(".expander");
rows = dojo.query(".expanded_row");
rows.forEach(function(item){
    var index = rows.indexOf(item);
    var state = getCookie("positionExpander_"+index);
    if (state!="opened") dojo.style(item,'display','none');
}
);
expanders.forEach(
function(item){           
    dojo.connect(item,'onclick',null,open_close_row);
}
); 