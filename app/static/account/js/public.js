(function (window) {
    var public = {
        post: function (url, data, callback, error) {
			return this._jqAjax(url, data, callback, error, 'post');
        },
        get: function (url, data, callback, error) {
			return this._jqAjax(url, data, callback, error, 'get');
		},
        _jqAjax: function (url, data, succCallback, error, type, dataType) {
			var type = type || "post";
			var dataType = dataType || "json";
			var asyn;
			var load = {};
			$.ajax({
				type: type,
				url: url,
				data: data,
				async: asyn,
				dataType: dataType,
				beforeSend: function () {
					load = $(document).dialog({
						type: 'toast',
						infoIcon: '/static/account/img/loading.gif',
						infoText: 'Please wait...'
					});
				},
				success: function (response) {

					load.close();
					var res;
					if (typeof res == 'string') {
						res = JSON.parse(response);
					} else {
						res = response;
					}
					Pub.catchCommonError(res);
					if (succCallback) {
						succCallback(res);
					}
				},
				complete: function () {
					load.close();
				},
				error: error
			});
        },
        msg: function (text, positon, time) {
			$(document).dialog({
				type: 'notice',
				infoText: text,
				autoClose: time || 3000,
				position: positon || 'middle' 
			});
        },
        toast: function (text, type, time) {
			var img = '';
			switch (type) {
				case 'success':
					img = '/static/account/img/success.png';
					break;
				case 'fail':
					img = '/static/account/img/fail.png';
					break;
				default:
					img = '/static/account/img/loading.gif';
			}
			$(document).dialog({
				type: 'toast',
				infoIcon: img,
				infoText: text || '',
				autoClose: time || 1500
			});
		},
        catchCommonError: function (data) {
			var _this = this;
			if (data.code != 0) {
				this.msg(data.message || '');
			}
		},
		dialogConfirm: {},
		confirm: function (title, content, callback, cancel) {
			var _this = this;
			this.dialogConfirm = $(document).dialog({
				type: 'confirm',
				closeBtnShow: true,
				titleText: title || 'prompt',
				content: content,
				onClickConfirmBtn: function () {
					callback();
				},
				onClickCancelBtn: function () {
					if (cancel && typeof cancel == 'function') {
						cancel();
					}
					_this.dialogConfirm.close();
				},
				onClickCloseBtn: function () {
					if (cancel && typeof cancel == 'function') {
						cancel();
					}
					_this.dialogConfirm.close();
				}
			});
		},
    }
    window.Pub = public;
})(window);