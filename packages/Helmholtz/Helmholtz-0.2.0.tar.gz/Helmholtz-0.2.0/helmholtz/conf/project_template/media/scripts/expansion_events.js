function open_close_container(e){  
	var index = buttons.indexOf(e.target.getAttribute('id'));
	target = dojo.byId(ids[index]);
	if (cookies_enabled) var cookie_name = cookies[index];
    if (dojo.style(target,'height') < 1) {
        state = "opened";
        var anim = dojo.fx.wipeIn({node:target,duration:500})
    }
    else {
   	 state = "closed";
   	 var anim = dojo.fx.wipeOut({node:target,duration:500})
    }
    if (cookies_enabled) setCookie(cookie_name,state,1);
    anim.play();  
}

function open_close_row(e){
	 var index = expanders.indexOf(e.target);
	 row = rows[index];
	 if (dojo.style(row,'height') > 1) {
		 var anim = dojo.fx.wipeOut({'node':row,'duration':0});
		 state = "closed";
	 }
	 else {
		 var anim = dojo.fx.wipeIn({'node':row,'duration':0});
		 state = "opened";
	 }
	 if (cookies_enabled) setCookie("tableExpander_" + index,state,1);
	 anim.play();
}