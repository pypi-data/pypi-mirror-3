(function($) {

	/**
	 * Loading management
	 */
	$.ZBlog.loader = {

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

	}  /** $.ZBlog.loader */

	/**
	 * Forms managements
	 */
	$.ZBlog.form = {

		check: function(callback) {
			$.ZBlog.ajax.check($.fn.ajaxSubmit, '/--static--/ztfy.jqueryui/js/jquery-form.min.js', callback);
		},

		hideStatus: function() {
			$('FORM DIV.status').animate({
				'opacity': 0,
				'height': 0,
				'margin-top': 0,
				'margin-bottom': 0,
				'padding-top': 0,
				'padding-bottom': 0
			}, 2000, function() {
				$(this).remove();
			});
		},

		reset: function(form) {
			form.reset();
			$('input:first', form).focus();
		},

		add: function(form, parent, callback) {
			$.ZBlog.form.check(function() {
				$.ZBlog.form._add(form, parent, callback);
			});
			return false;
		},

		_add: function(form, parent, callback) {
			if (typeof(tinyMCE) != 'undefined') {
				tinyMCE.triggerSave();
			}
			var data = {}
			if (parent) {
				data.parent = parent;
			}
			$($.ZBlog.form).data('add_action', $(form).attr('action'));
			$.ZBlog.ajax.submit(form, $(form).attr('action') + '/@@ajax/ajaxCreate', data, callback || $.ZBlog.form._addCallback, null, 'json');
		},

		_addCallback: function(result, status) {
			if (status == 'success') {
				output = result.output;
				if (output == 'ERRORS') {
					var dialog = $.ZBlog.dialog.getCurrent();
					$('DIV.status', dialog).remove();
					$('DIV.error', dialog).remove();
					var status = $('<div></div>').addClass('status');
					$('<div></div>').addClass('summary')
									.text(result.errors.status)
									.appendTo(status);
					var errors = $('<ul></ul>').appendTo(status);
					for (var i=0; i < result.errors.errors.length; i++) {
						var error = result.errors.errors[i];
						if (error.widget) {
							$('<li></li>').text(error.widget + ' : ' + error.message)
										  .appendTo(errors);
							var widget = $('[id=' + error.id + ']', dialog).parents('DIV.widget');
							var row = $(widget).parents('DIV.row');
							widget = widget.clone(true);
							$('DIV.widget', row).remove();
							$('DIV.error', row).remove();
							$('<div></div>').addClass('error')
											.append($('<div></div>').addClass('error')
													 				.text(error.message))
											.appendTo(row);
							widget.appendTo(row);
						} else {
							$('<li></li>').text(error.message)
										  .appendTo(errors);
						}
					}
					$('FORM', dialog).before(status);
				} else if (output == 'RELOAD') {
					window.location.reload();
				} else if (output && output.startsWith('<!-- OK -->')) {
					$.ZBlog.dialog.close();
					$('#content').replaceWith(output);
				} else {
					var dialog = $.ZBlog.dialog.getCurrent();
					$('DIV.dialog', dialog).replaceWith(output);
					$('FORM', dialog).attr('action', $($.ZBlog.form).data('add_action'));
					$('#form-buttons-add', dialog).bind('click', function(event) {
						$.ZBlog.form.add(this.form, result.parent);
					});
					$('#form-buttons-cancel', dialog).bind('click', function(event) {
						$.ZBlog.dialog.close();
					});
					$('#tabforms UL.tabs', dialog).tabs($(dialog).selector + ' DIV.panes > DIV');
				}
			}
		},

		edit: function(form, base, callback) {
			$.ZBlog.form.check(function() {
				$.ZBlog.form._edit(form, base, callback);
			});
			return false;
		},

		_edit: function(form, base, callback) {
			if (typeof(tinyMCE) != 'undefined') {
				tinyMCE.triggerSave();
			}
			$($.ZBlog.form).data('edit_action', $(form).attr('action'));
			$.ZBlog.ajax.submit(form, $(form).attr('action') + '/@@ajax/ajaxEdit', {}, callback || $.ZBlog.form._editCallback, null, 'json');
		},

		_editCallback: function(result, status) {
			if (status == 'success') {
				var output = result.output;
				if (output == 'RELOAD') {
					window.location.reload();
				} else if (output == 'REDIRECT') {
					$.ZBlog.dialog.close();
					window.location.href = result.target;
				} else if (output == 'OK') {
					$.ZBlog.dialog.close();
					$('DIV.status').remove();
					$('DIV.required-info').after('<div class="status"><div class="summary">' + $.ZBlog.I18n.DATA_UPDATED + '</div></div>');
				} else if (output == 'NONE') {
					$.ZBlog.dialog.close();
					$('DIV.status').remove();
					$('DIV.required-info').after('<div class="status"><div class="summary">' + $.ZBlog.I18n.NO_UPDATE + '</div></div>');
				} else if (output == 'ERRORS') {
					var dialog = $.ZBlog.dialog.getCurrent();
					$('DIV.status', dialog).remove();
					$('DIV.error', dialog).remove();
					var status = $('<div></div>').addClass('status');
					$('<div></div>').addClass('summary')
									.text(result.errors.status)
									.appendTo(status);
					var errors = $('<ul></ul>').appendTo(status);
					for (var i=0; i < result.errors.errors.length; i++) {
						var error = result.errors.errors[i];
						if (error.widget) {
							$('<li></li>').text(error.widget + ' : ' + error.message)
										  .appendTo(errors);
							var widget = $('[id=' + error.id + ']', dialog).parents('DIV.widget');
							var row = $(widget).parents('DIV.row');
							widget = widget.clone(true);
							$('DIV.widget', row).remove();
							$('DIV.error', row).remove();
							$('<div></div>').addClass('error')
											.append($('<div></div>').addClass('error')
													 				.text(error.message))
											.appendTo(row);
							widget.appendTo(row);
						} else {
							$('<li></li>').text(error.message)
										  .appendTo(errors);
						}
					}
					$('FORM', dialog).before(status);
				} else if (output && output.startsWith('<!-- OK -->')) {
					$.ZBlog.dialog.close();
					$('DIV.form').replaceWith(output);
					setTimeout('$.ZBlog.form.hideStatus();', 2000);
				} else {
					var dialog = $.ZBlog.dialog.getCurrent();
					$('DIV.dialog', dialog).replaceWith(output);
					var form = $('FORM', dialog);
					form.attr('action', $($.ZBlog.form).data('edit_action'));
					$('#'+form.attr('id')+'-buttons-dialog_submit', dialog).bind('click', function(event) {
						$.ZBlog.form.edit(this.form);
					});
					$('#'+form.attr('id')+'-buttons-dialog_cancel', dialog).bind('click', function(event) {
						$.ZBlog.dialog.close();
					});
					$('#tabforms UL.tabs', dialog).tabs($(dialog).selector + ' DIV.panes > DIV');
				}
			}
			setTimeout('$.ZBlog.form.hideStatus();', 2000);
		}

	}  /** $.ZBlog.form */

	/**
	 * Common actions
	 */
	$.ZBlog.actions = {

		showLoginForm: function(source) {
			var $inputs = $('SPAN.inputs', source);
			$inputs.parents('LI:first').addClass('selected');
			$inputs.show();
			$('INPUT', $inputs).get(0).focus();
		},

		login: function(form) {
			if (typeof(form) == 'undefined') {
				form = $('FORM[name="login_form"]');
			}
			$.ZBlog.form.check(function() {
				$.ZBlog.actions._login(form);
			});
			return false;
		},

		_login: function(form) {
			$.ZBlog.ajax.submit(form, $(form).attr('action') + '/@@ajax/login', {}, $.ZBlog.actions._loginCallback, $.ZBlog.actions._loginError, 'json');
		},

		_loginCallback: function(result, status) {
			if (status == 'success') {
				if (result == 'OK') {
					window.location.reload();
				} else {
					jAlert($.ZBlog.I18n.BAD_LOGIN_MESSAGE, $.ZBlog.I18n.BAD_LOGIN_TITLE, null);
				}
			}
		},

		_loginError: function(request, status) {
			jAlert(status, $.ZBlog.I18n.ERROR_OCCURED, null);
		},

		logout: function() {
			$.get(window.location.href + '/@@login.html/@@ajax/logout', $.ZBlog.actions._logoutCallback);
		},

		_logoutCallback: function(result, status) {
			window.location.reload();
		}

	}  /** $.ZBlog.actions */

	/**
	 * Codes samples handling
	 */
	$.ZBlog.code = {

		resizeFrame: function(frame) {
			$(frame).css('height', $('BODY', frame.contentDocument).height() + 20);
		}

	}  /** $.ZBlog.code */

	var lang = $('HTML').attr('lang') || $('HTML').attr('xml:lang');
	$.getScript('/--static--/ztfy.blog/js/i18n/' + lang + '.js');

	/**
	 * Override Chromium opacity bug on Linux !
	 */
	if ($.browser.safari) {
		$.support.opacity = true;
	}

})(jQuery);