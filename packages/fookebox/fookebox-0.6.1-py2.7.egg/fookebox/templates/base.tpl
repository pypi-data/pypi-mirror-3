<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<%def name="headers()">
</%def>

<html xml:lang="en">
	<head>
		<title>fookebox</title>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
		<link rel="stylesheet" href="css/style.css" type="text/css" media="screen" />
% if mobile:
		<link rel="stylesheet" href="css/style-mobile.css" type="text/css" media="screen" />
% endif
		<script type="text/javascript" src="js/prototype/prototype.js"></script>
		<script type="text/javascript" src="js/scriptaculous/scriptaculous.js?load=effects"></script>
% if config.get('lang'):
		<script type="text/javascript" src="js/fookebox/i18n/${config.get('lang')}.js"></script>
% endif
		<script type="text/javascript" src="js/fookebox/i18n/i18n.js"></script>
		<script type="text/javascript" src="js/fookebox/core.js"></script>
		${self.headers()}
	</head>
	<body id="body">
		${next.body()}
	</body>
</html>
