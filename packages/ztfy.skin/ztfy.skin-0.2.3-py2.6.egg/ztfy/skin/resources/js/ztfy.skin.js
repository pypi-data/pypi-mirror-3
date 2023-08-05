(function($) {

	if (typeof($.ZTFY) == 'undefined') {
		$.ZTFY = {};
	}

	$.ZTFY.skin = {

		check: function(checker, source, callback) {
			if (typeof(checker) == 'undefined') {
				$.getScript(source, callback)
			} else {
				callback();
			}
		},

		getCSS: function(resource, id, callback) {
			var head = $('HEAD');
			var check = $('style[ztfy_id='+id+']', head);
			if (check.length == 0) {
				$.get(resource, function(data) {
					var style = $('<style></style>').attr('type','text/css')
													.attr('ztfy_id', id)
													.text(data);
					head.prepend(style);
					if (callback) {
						callback();
					}
				});
			}
		}

	}

})(jQuery);