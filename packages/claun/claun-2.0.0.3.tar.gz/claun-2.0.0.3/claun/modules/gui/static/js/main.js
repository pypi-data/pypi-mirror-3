require.config({
	paths: {
		json: 'vendor/json2/json2.min',
		utf8: 'vendor/utf8/utf8_encode.min',
		base64: 'vendor/base64/base64_encode.min',
		//jquery: 'vendor/jquery/jquery-1.7.1.min',
		//underscore: 'vendor/underscore/underscore-min',
		jqueryui: 'vendor/jquery-ui/jquery-ui-1.8.16.custom.min',
		jquery_cycle: 'vendor/jquery-plugins/jquery.cycle.lite',
		text: 'vendor/require/text',
		order: 'vendor/require/order',
		//backbone: 'vendor/backbone/backbone-min',
		form2js: 'vendor/form2js/form2js',
		jquery_ajaxfileupload: 'vendor/jquery-plugins/jquery.ajaxfileupload',
		jqueryui_selectmenu: 'vendor/jquery-ui/jquery.ui.selectmenu',
		crypto_sha256: 'vendor/crypto/sha256-2.5.3',
		codemirror: 'vendor/codemirror/codemirror-compressed'
	}

});

require([
	'application',
	], function(Application) {
		Application.initialize();
	}
)
