for (i=0;i<n_containers;i++) {
	var node = dojo.byId(ids[i]);
	console.debug(ids[i])
	if (node) {
	    if (cookies_enabled) {var state = getCookie(cookies[i]);} else {var state = "closed";}
	    if (state != "opened") dojo.style(node,{'height':'0px','overflow':'hidden'});
	    dojo.connect(dojo.byId(buttons[i]),'onclick',null,open_close_container);
	}
}