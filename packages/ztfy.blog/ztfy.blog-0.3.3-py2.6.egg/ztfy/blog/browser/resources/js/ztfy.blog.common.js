(function($) {

	/**
	 * String prototype extensions
	 */
	String.prototype.startsWith = function(str) {
		var slen = this.length;
		var dlen = str.length;
		if (slen < dlen) {
			return false;
		}
		return (this.substr(0,dlen) == str);
	}

	String.prototype.endsWith = function(str) {
		var slen = this.length;
		var dlen = str.length;
		if (slen < dlen) {
			return false;
		}
		return (this.substr(slen-dlen) == str);
	}

	/**
	 * Main $.ZBlog JavaScript package
	 */
	$.ZBlog = {

		/**
		 * JSON management
		 */
		json: {

			getAddr: function() {
				var href = window.location.href;
				return href.substr(0, href.lastIndexOf("/")+1);
			},

			post: function(method, params, onsuccess, onerror, base) {
				var addr = $.ZBlog.json.getAddr();
				if (base) {
					addr += '/' + base;
				}
				var options = {
					url: addr,
					type: 'POST',
					method: method,
					params: params,
					success: onsuccess,
					error: onerror
				};
				$.jsonRpc(options);
			}

		},  /** $.ZBlog.json */

		/**
		 * AJAX management
		 */
		ajax: {

			check: function(checker, source, callback) {
				if (typeof(checker) == 'undefined') {
					$.getScript(source, callback)
				} else {
					callback();
				}
			},

			getAddr: function() {
				var href = window.location.href;
				return href.substr(0, href.lastIndexOf("/")+1);
			},
	
			post: function(url, data, onsuccess, onerror, datatype) {
				if (url.startsWith('http://')) {
					var addr = url;
				} else {
					var addr = $.ZBlog.ajax.getAddr() + url;
				}
				var options = {
					url: addr,
					type: 'POST',
					data: $.param(data, true),  /* use traditional JQuery params decoding */
					dataType: datatype || 'json',
					success: onsuccess,
					error: onerror || $.ZBlog.ajax.error
				};
				$.ajax(options);
			},

			submit: function(form, url, data, onsuccess, onerror, datatype) {
				if (url.startsWith('http://')) {
					var addr = url;
				} else {
					var addr = $.ZBlog.ajax.getAddr() + url;
				}
				var options = {
					url: addr,
					type: 'POST',
					iframe: true,
					data: data,
					dataType: datatype || 'json',
					success: onsuccess,
					error: onerror || $.ZBlog.ajax.error
				};
				$(form).ajaxSubmit(options);
			},

			error: function(request, status, error) {
				$.ZBlog.ajax.check(jAlert, '/--static--/ztfy.jqueryui/js/jquery-alerts.min.js', function() {
					jAlert(status + ':\n\n' + error, $.ZBlog.I18n.ERROR_OCCURED, null);
				});
			}

		},  /** $.ZBlog.ajax */

		/**
		 * Loading management
		 */
		loader: {

			div: null,

			start: function(parent) {
				parent.empty();
				var $div = $('<div class="loader"></div>').appendTo(parent);
				var $img = $('<img class="loading" src="/--static--/ztfy.blog/img/loading.gif" />').appendTo($div);
				$.ZBlog.loader.div = $div;
			},

			stop: function() {
				if ($.ZBlog.loader.div != null) {
					$.ZBlog.loader.div.replaceWith('');
					$.ZBlog.loader.div = null;
				}
			}

		},  /** $.ZBlog.loader */

		/**
		 * Dialogs management
		 */
		dialog: {

			options: {
				expose: {
					maskId: 'mask',
					color: '#ccc',
					opacity: 0.6,
					zIndex: 9998
				},
				api: true,
				oneInstance: false,
				closeOnClick: false,
				onBeforeLoad: function() {
					$.ZBlog.loader.start(this.getContent());
					this.getContent().load($.ZBlog.dialog.dialogs[$.ZBlog.dialog.getCount()-1].src);
					if ($.browser.msie && ($.browser.version < '7')) {
						$('select').css('visibility', 'hidden');
					}
				},
				onClose: function() {
					$.ZBlog.dialog.onClose();
					if ($.browser.msie && ($.browser.version < '7')) {
						$('select').css('visibility', 'hidden');
					}
				}
			},

			dialogs: [],

			getCount: function() {
				return $.ZBlog.dialog.dialogs.length;
			},

			getCurrent: function() {
				var count = $.ZBlog.dialog.getCount();
				return $('#dialog_' + count);
			},

			open: function(src) {
				if (!$.ZBlog.dialog.dialogs) {
					$.ZBlog.dialog.dialogs = new Array();
				}
				var index = $.ZBlog.dialog.getCount() + 1;
				var id = 'dialog_' + index;
				var options = {}
				var expose_options = {
					maskId: 'mask',
					color: '#ccc',
					opacity: 0.6,
					zIndex: $.ZBlog.dialog.options.expose.zIndex + index
				};
				$.extend(options, $.ZBlog.dialog.options, { expose: expose_options });
				$.ZBlog.dialog.dialogs.push({
					src: src,
					body: $('<div class="overlay"></div>').attr('id', id)
														  .appendTo($('body'))
				});
				$('#' + id).empty()
						   .overlay(options)
						   .load();
			},

			close: function() {
				var count = $.ZBlog.dialog.getCount();
				var id = 'dialog_' + count;
				$('#' + id).overlay().close();
			},

			onClose: function() {
				if (typeof(tinyMCE) != 'undefined') {
					if (tinyMCE.activeEditor) {
						tinyMCE.execCommand('mceRemoveControl', false, tinyMCE.activeEditor.id);
					}
				}
				$('BODY DIV:last').remove();
				$.ZBlog.dialog.dialogs.pop();
			}

		},  /** $.ZBlog.dialog */

		/**
		 * Properties viewlet management
		 */
		properties: {

			switcher: function(div) {
				$('DIV.properties DIV.switch').toggle();
			}

		}  /** $.ZBlog.properties */

	}

})(jQuery);