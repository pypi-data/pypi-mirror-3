<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.0/jquery.min.js" type="text/javascript"></script>
    <script src="./jquery/jquery.query.js" type="text/javascript"></script>
    <link type="text/css" href="./css/main.css" rel="stylesheet" />
    <link type="text/css" href="./css/lucullus.css" rel="stylesheet" />

    % extjs = '/js/ext-3.3.1'
    <link rel="stylesheet" type="text/css" href="{{extjs}}/resources/css/ext-all.css" />
    <script type="text/javascript" src="{{extjs}}/adapter/ext/ext-base-debug.js"></script>
    <script type="text/javascript" src="{{extjs}}/ext-all-debug.js"></script>

    % lucjs = '/js/lucullus'
    % for pkg in ('base','maps','gui', 'level'):
        <script type="text/javascript" src="{{lucjs}}/{{pkg}}.js"></script>
    % end
    <script type="text/javascript" src="/js/mlayer.js"></script>
	<script type="text/javascript" src="https://github.com/flot/flot/raw/master/jquery.flot.js"></script>
    <title>Lucullus 3dSpec Viewer</title>
</head>
<body style='overflow: hidden'>
    <canvas />
</body>
</html>
<script type="text/javascript">


</script>