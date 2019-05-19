/* Javascript code that checks whether a symbol should be inserted on each keypress.
 * This is injected into the Anki editor's WebView by insert_symbols.py */

// Namespace insert_symbols
var insert_symbols = new function() {

    // Variables:
    //----------------------------------
    var matchList = JSON.parse('%s');
    var isValidKeypress = false;

    // Update matchList:
    //----------------------------------
    this.setMatchList = function(str) {
        matchList = JSON.parse(str);
    }

    // Keypress Handling:
    //----------------------------------
    function onKeyPress(evt) {
        if (evt.which == 13 || evt.which == 32) {
            checkForReplacement();
        } else {
            isValidKeypress = true;
        }
    }

    function onKeyUp(evt) {
        if (isValidKeypress) {
            checkForReplacement();
            isValidKeypress = false;
        }
    }

    $(".field").keypress(onKeyPress);
    $(".field").keyup(onKeyUp);

    // Pattern Matching:
    //----------------------------------

    // Checks if last
    function checkForReplacement() {
        var sel = window.getSelection();
        if (sel.isCollapsed) {
            var text = sel.focusNode.textContent;
            var cursorPos = sel.focusOffset;
            //debugErr(sel.focusNode.textContent + '\n' + sel.focusOffset);

            var result = matchesKeyword(text, cursorPos, matchList);
            if (result.text !== null) {
                performReplacement(sel.focusNode, cursorPos - result.keylen, cursorPos, result.text);
            }
        }
    }

    // Checks for matches
    function matchesKeyword(text, cursorPos, matchList) {
        //debugErr("In MK, text:" + substr + " cursorPos: " + cursorPos);

        for (var i = 0, k; i < matchList.length; i++) {
            key = matchList[i].key;
            var startPos = cursorPos - key.length;

            //debugErr("In MK, text:" + text + " key:" + key + " lenChk:" + (cursorPos >= key.length) + "" + );

            if (startPos >= 0 && text.substring(startPos, cursorPos) === key) {
                //debugErr("In MK, text:" + matchList[i].val + " len: " + key.length);
                return {"text":matchList[i].val, "keylen":key.length};
            }
        }

        return {"text":null, "len":0};
    }

    // Performs replacement
    function performReplacement(node, rangeStart, rangeEnd, newText) {
        var range = document.createRange();
        range.setStart(node, rangeStart);
        range.setEnd(node, rangeEnd);

        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        document.execCommand("insertHTML", false, newText);
    }

    // Debugging:
    //----------------------------------

    //$("body").append('<div class="debug"></div>');
    //$(".debug").html("Hi, this is a test.");

    // function debugDiv(str) {
    //  py.run("debug_div:"+ str);
    // }

    function debugErr(str) {
        py.run("debug_err:"+ str);
    }

}
