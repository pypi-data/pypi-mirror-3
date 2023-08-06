(function($) {

	/**
	 * Forms managements
	 */
	$.ZBlog.form = {

		check: function(callback) {
			$.ZBlog.ajax.check($.fn.ajaxSubmit, '/--static--/ztfy.jqueryui/js/jquery-form.min.js', callback);
		},

		hideStatus: function() {
			$('DIV.form DIV.status').animate({
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
			var dataType = $.browser.msie ? 'text' : 'json';
			$.ZBlog.ajax.submit(form, $(form).attr('action') + '/@@ajax/ajaxCreate', data, callback || $.ZBlog.form._addCallback, null, dataType);
		},

		_addCallback: function(result, status) {
			if (status == 'success') {
				if ($.browser.msie) {
					result = $.parseJSON($(result).text());
				}
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
				} else if (output == 'OK') {
					$.ZBlog.dialog.close();
					$('DIV.status').remove();
					$('DIV.required-info').after('<div class="status"><div class="summary">' + $.ZBlog.I18n.DATA_UPDATED + '</div></div>');
				} else if (output == 'RELOAD') {
					window.location.reload();
				} else if (output == 'CALLBACK') {
					eval(result.callback);
				} else if (output && output.startsWith('<!-- OK -->')) {
					$.ZBlog.dialog.close();
					$('DIV.form').replaceWith(output);
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
				if (output != 'ERRORS') {
					setTimeout('$.ZBlog.form.hideStatus();', 2000);
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
			var action = $(form).attr('action').replace(/\?X-Progress-ID=.*/, '');
			$($.ZBlog.form).data('edit_action', action);
			var dataType = $.browser.msie ? 'text' : 'json';
			$.ZBlog.ajax.submit(form, action + '/@@ajax/ajaxEdit', {}, callback || $.ZBlog.form._editCallback, null, dataType);
		},

		_editCallback: function(result, status, response) {
			if (status == 'success') {
				if ($.browser.msie) {
					result = $.parseJSON($(result).text());
				}
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
				} else if (output == 'CALLBACK') {
					eval(result.callback);
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
				} else {
					var dialog = $.ZBlog.dialog.getCurrent();
					$('DIV.dialog', dialog).replaceWith(output);
					var form = $('FORM', dialog);
					form.attr('action', $($.ZBlog.form).data('edit_action'));
					$('#'+form.attr('id')+'-buttons-dialog_submit', dialog).bind('click', function(event) {
						$.ZBlog.form.edit(this.form);
					});
					$('#'+form.attr('id')+'form-buttons-dialog_cancel', dialog).bind('click', function(event) {
						$.ZBlog.dialog.close();
					});
					$('#tabforms UL.tabs', dialog).tabs($(dialog).selector + ' DIV.panes > DIV');
				}
				if (output != 'ERRORS') {
					setTimeout('$.ZBlog.form.hideStatus();', 2000);
				}
			}
		},

		remove: function(oid, source, callback) {
			jConfirm($.ZBlog.I18n.CONFIRM_REMOVE, $.ZBlog.I18n.CONFIRM, function(confirmed) {
				if (confirmed) {
					var data = {
						id: oid
					}
					$.ZBlog.form.ajax_source = source;
					$.ZBlog.ajax.post(window.location.href + '/@@ajax/ajaxRemove', data, callback || $.ZBlog.form._removeCallback, null, 'text');
				}
			});
		},

		_removeCallback: function(result, status) {
			if ((status == 'success') && (result == 'OK')) {
				$($.ZBlog.form.ajax_source).parents('TR').remove();
			}
		},

		update: function(form, callback) {
			$.ZBlog.form.check(function() {
				$.ZBlog.form._update(form, callback);
			});
			return false;
		},

		_update: function(form, callback) {
			if (typeof(tinyMCE) != 'undefined') {
				tinyMCE.triggerSave();
			}
			var data = $(form).formToArray(true);
			$.ZBlog.ajax.post($(form).attr('action') + '/@@ajax/ajaxUpdate', data, callback || $.ZBlog.form._updateCallback, null, 'text');
		},

		_updateCallback: function(result, status) {
			if ((status == 'success') && (result == 'OK')) {
				$('DIV.status').remove();
				$('LEGEND').after('<div class="status"><div class="summary">Data successfully updated.</div></div>');
			}
		}

	}  /** $.ZBlog.form */

	/**
	 * Container management
	 */
	$.ZBlog.container = {

		remove: function(oid, source) {
			var options = {
				_source: source,
				url: $.ZBlog.json.getAddr(),
				type: 'POST',
				method: 'remove',
				params: {
					id: oid
				},
				success: function(data, status) {
					$(this._source).parents('TR').remove();
				},
				error: function(request, status, error) {
					jAlert(request.responseText, $.ZBlog.I18n.ERROR_OCCURED, window.location.reload);
				}
			}
			jConfirm($.ZBlog.I18n.CONFIRM_REMOVE, $.ZBlog.I18n.CONFIRM, function(confirmed) {
				if (confirmed) {
					$.jsonRpc(options);
				}
			});
		}

	}  /** $.ZBlog.container */

	/**
	 * Sortables management
	 */
	$.ZBlog.sortable = {

		options: {
			handle: 'IMG.handler',
			axis: 'y',
			containment: 'parent',
			placeholder: 'sorting-holder',
			stop: function(event, ui) {
				var ids = new Array();
				$('TABLE.orderable TD.id').each(function (i) {
					ids[ids.length] = $(this).text();
				});
				var data = {
					ids: ids
				}
				$.ZBlog.ajax.post(window.location.href + '/@@ajax/ajaxUpdateOrder', data, null, function(request, status, error) {
					jAlert(request.responseText, $.ZBlog.I18n.ERROR_OCCURED, window.location.reload);
				});
			}
		}

	}  /** $.ZBlog.sortable */

	/**
	 * Treeviews management
	 */
	$.ZBlog.treeview = {

		changeParent: function(event,ui) {
			var $dragged = $(ui.draggable.parents('TR'));
			if ($dragged.appendBranchTo(this)) {
				var source = $dragged.attr('id').substr('node-'.length);
				var target = $(this).attr('id').substr('node-'.length);
				var options = {
					url: $.ZBlog.json.getAddr(),
					type: 'POST',
					method: 'changeParent',
					params: {
						source: parseInt(source),
						target: parseInt(target)
					},
					error: function(request, status, error) {
						jAlert(request.responseText, $.ZBlog.I18n.ERROR_OCCURED, window.location.reload);
					}
				}
				$.jsonRpc(options);
			}
		}

	}  /** $.ZBlog.treeview */

	/**
	 * Internal references management
	 */
	$.ZBlog.reference = {

		activate: function(selector) {
			$('INPUT[name='+selector+']').attr('readonly','')
										 .val('')
										 .focus();
			$('INPUT[name='+selector+']').prev().val('');
		},

		keyPressed: function(event) {
			if (event.which == 13) {
				$.ZBlog.reference.search(this);
				return false;
			}
		},

		search: function(query) {
			var result;
			var options = {
				url: $.ZBlog.json.getAddr(),
				type: 'POST',
				method: 'search',
				async: false,
				params: {
					query: query
				},
				success: function(data, status) {
					result = data.result;
				},
				error: function(request, status, error) {
					jAlert(request.responseText, "Error !", window.location.reload);
				}
			}
			$.jsonRpc(options);
			return result;
		},

		select: function(oid, title) {
			var source = $.ZBlog.reference.source;
			$(source).prev().val(oid);
			$(source).val(title + ' (OID: ' + oid + ')')
					 .attr('readonly', 'readonly');
			$('#selector').overlay().close();
			$('#selector').remove();
			return false;
		}

	}  /** $.ZBlog.reference */

	/**
	 * Topics management
	 */
	$.ZBlog.topic = {

		remove: function(form) {
			$.ZBlog.ajax.post($(form).attr('action') + '/@@ajax/ajaxDelete', {}, $.ZBlog.topic.removeCallback, null, 'json');
			return false;
		},

		removeCallback: function(result, status) {
			if (status == 'success') {
				window.location = result.url;
			}
		}

	}  /** $.ZBlog.topic */

	var lang = $('HTML').attr('lang') || $('HTML').attr('xml:lang');
	$.getScript('/--static--/ztfy.blog/js/i18n/' + lang + '.js');

	/**
	 * Override Chromium opacity bug on Linux !
	 */
	if ($.browser.safari) {
		$.support.opacity = true;
	}

	/**
	 * Automatically handle images properties download links
	 */
	if ($.fn.fancybox) {
		$(document).ready(function() {
			$('DIV.download-link IMG').parents('A').fancybox({
				type: 'image',
				titleShow: false,
				hideOnContentClick: true
			});
		});
	}

})(jQuery);