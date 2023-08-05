jq(document).ready(function() {
    var reveal_url = 'jq_reveal_email'
    if (typeof(portal_url) != 'undefined') {
	reveal_url = portal_url + '/' + reveal_url;
    }
    jq('a.hidden-email').each(function() {
        jq.pyproxy_call(reveal_url, {'uid': jq(this).attr('rel')});
    });
});