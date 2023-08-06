<%! 
	import jsonrpc.jsonutil 
	import pprint
%>
<%inherit file="/page" />
<%namespace name="buttons" file="/buttons"  />

<h1>Test Upload Handler</h1>

<form method="post" action="" enctype="multipart/form-data">
	<input type="file" name="file_binary" />
	<input type="submit" value="Submit" />
</form>

<h1>Header output:</h1>

<pre>
${pprint.pprint(header)}
</pre>