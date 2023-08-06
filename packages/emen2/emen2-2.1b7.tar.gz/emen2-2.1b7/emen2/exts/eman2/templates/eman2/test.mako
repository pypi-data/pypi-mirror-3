<%! 
	import jsonrpc.jsonutil 
	import pprint
%>
<%inherit file="/page" />
<%namespace name="buttons" file="/buttons"  />


<%block name="js_ready">
	${parent.js_ready()}
	var bdo = "bdo:2012032700000";

	function p1d(d, apix) {
		// Convert to query format...
		var recs = [];
		var dx = 1.0 / (2.0 * apix * (d.length+1));
		for (var i=0;i<d.length;i++) {
			var rec = {'x':dx*(i+1), y:d[i]}
			recs.push(rec);
		}

		// Plot.
		$("#test").PlotScatter({
			q: {
				recs:recs,
				x: {key: 'x'},
				y:  {key: 'y'}
			}
		});
	}


	$.ajax({
		type: 'POST',
		url: EMEN2WEBROOT+'/preview/'+bdo+'/pspec1d/',
		dataType: 'json',
		success: function(d) {
			p1d(d, 1.33);
		}
	});
</%block>



<h1>Test 1D Plot</h1>

<div id="test">
	<div class="e2-plot"></div>
</div>
