/**
 * 
 */

jq(document).ready(function() {
	
    /**
     * Context URL to be used for all AJAX call
     */
    var call_context = jq("head base").attr('href');
    if (call_context.charAt(call_context.length-1)!='/') call_context=call_context+'/';

    /*
     * Don't want to call the context when is in the portal factory. See the Ale's blog post:
     * http://blog.redturtle.it/redturtle-blog/2010/03/11/careful-with-that-ajax-eugene
     */
    if (call_context.indexOf('/portal_factory')>-1) {
        call_context=call_context.substring(0,call_context.indexOf('/portal_factory')+1);
    };
	
	var kupu = jq("#kupu-editor-annotations");
	if (kupu.length>0) {
		kupu.hide();
		var label = jq("#archetypes-fieldname-annotations label.formQuestion");
		var toggle = jq('&nbsp;<a href="javascript:;"><img alt="Mostra" src="'+call_context+'/++resource++monet.calendar.location.images/show_control.gif" /></a>')
				.data("opened", false).click(function() {
					var img = toggle.children("img");
					if (toggle.data('opened')) {
						toggle.data('opened', false);
						img.attr("alt", "Mostra").attr("src", call_context+'/++resource++monet.calendar.location.images/show_control.gif');
						kupu.hide();
					}
					else {
						toggle.data('opened', true);
						img.attr("alt", "Nascondi").attr("src", call_context+'/++resource++monet.calendar.location.images/hide_control.gif');
						kupu.show();						
					}
				});
		label.after(toggle);
	}
});