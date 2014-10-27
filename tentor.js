var system = require('system');

if (system.args.length < 3) {
	console.log("Usage: tentor.js program_id grade");
	phantom.exit(1);
}

var url = "https://www.student.chalmers.se/sp/programplan?program_id=" + system.args[1] + "&grade=" + system.args[2];
var page = require('webpage').create();

page.open(url, function(status) {
	var results = page.evaluate(function() {
		var list = document.querySelectorAll("#contentpage > table:nth-child(4) > tbody > tr"), codes = [];
		for (var i = 0; i < list.length; i++) {
			var cells = list[i].cells;
			// column 1 = course code, 5 = course name, 7 = date of tentamen
			if (cells.length == 10 && cells[5].innerText.indexOf('Tentamen') != -1) {
				var c = [ cells[1].innerText, cells[5].innerText.replace(', Tentamen', ''), cells[7].innerText || '-'];
				codes.push(c.join("\t"));
			}
		}
		return codes;
	});
	console.log(results.join("\n"));
	phantom.exit();
});