expanders = dojo.query(".expander");
rows = dojo.query(".detail_row, .expanded_row");

rows.forEach(
    function(item){
        var index = rows.indexOf(item);
        if (cookies_enabled) {var state = getCookie("tableExpander_"+index);} else {var state = "closed";}
        if (state!="opened") dojo.style(item,'display','none');
    }
);

expanders.forEach(
    function(item){           
        dojo.connect(item,'onclick',null,open_close_row);
    }
); 