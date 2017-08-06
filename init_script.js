// Javascript code to load into insert_symbols.py

$("body").append('<div class="debug"></div>');

var myDiv = $(".debug");
var myText = "This is my text.";

$(".debug").html("Hi, this is a test.");

function onKeyPress(evt) {
	if (String.fromCharCode(evt.charCode) == '1') {
		//is_DebugDiv("Button '1' was pressed.");
		//$(".debug").html("Button '1' was pressed.");
		myDiv.html("Button '1' was pressed.");
	} else if (String.fromCharCode(evt.charCode) == '2') {
		is_DebugDiv("Button '2' was pressed.");
	} else if (String.fromCharCode(evt.charCode) == '`') {
		is_DebugErr($("body").html());
	} else if (String.fromCharCode(evt.charCode) == '3') {
		myText = "Modified to text 1";
	} else if (String.fromCharCode(evt.charCode) == '4') {
		myText = "Modified to text 2";
	} else if (String.fromCharCode(evt.charCode) == '5') {
		is_DebugDiv(myText);
	}
}

$(".field").keypress(onKeyPress);

function is_DebugDiv(str) {
	py.run("debug_div:"+ str);
}

function is_DebugErr(str) {
	py.run("debug_err:"+ str);
}