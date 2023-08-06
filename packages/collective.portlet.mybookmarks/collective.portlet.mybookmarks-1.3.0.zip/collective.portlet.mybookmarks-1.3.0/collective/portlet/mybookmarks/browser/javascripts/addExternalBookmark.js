function setFormClass(event){
	event.preventDefault();
	var form=jq('#addExternalBlock #externalBookmarkForm');
	form.toggleClass('bookmarkHiddenStructure');
}


jq(document).ready(function() {
	var dd=jq('#addExternalBlock');
	if (dd.length === 1) {
		var portal_url=dd.children('span#hiddenAbsoluteUrl').html();
		var translated_label=dd.children('span#hiddenJsLabel').html();
		var href_title=jq('#externalBookmarkFieldset legend').html()
		var form=dd.children('#externalBookmarkForm');
		html='<a id="addExternalLink"';
		html+='title="'+href_title+'"';
		html+='href="#">';
		html+='<img class="bookmarkIcon" src="'+portal_url+'/++resource++collective.portlet.mybookmarks.images/add.png" alt="[ADD]"/>';
		html+=translated_label;
		html+='</a>';
		form.before(html);
		jq('a#addExternalLink').bind('click', setFormClass);
	}
});

