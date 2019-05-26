/*
 * Javascript code that performs symbol replacement. insert_symbols.py adds this script to 
 * each Anki editor's WebView after setting the symbol list. 
 *
 * Anki 2.0 uses jQuery version 1.5.
 */

var insert_symbols = new function() {

    var matchList = JSON.parse('%s');
    var shouldCheckOnKeyup = false;

    this.setMatchList = function(str) {
        matchList = JSON.parse(str);
    }

    // Keypress Handling:
    //----------------------------------

    /*
     * Note: keydown() events are fired whenever a key is pressed, including multiple times for
     * long presses, but keyup() events are only fired ONCE when a key is released. Furthermore,
     * window.getSelection().focusNode does not update with the new characters until the keyup()
     * event. 
     *
     * 
     */

    function onKeyDown(evt) {
        if (evt.which == 13 || evt.which == 32) {
            checkForReplacement(true);
        } else {
            shouldCheckOnKeyup = true;
        }
    }

    function onKeyUp(evt) {
        if (shouldCheckOnKeyup) {
            checkForReplacement();
            shouldCheckOnKeyup = false;
        }
    }

    $(".field").keydown(onKeyDown);
    $(".field").keyup(onKeyUp);

    // Pattern Matching:
    //----------------------------------

    /**
     * Checks whether the current text should be replaced by a symbol from the symbol list.
     * For simplicity, this function only looks at text within the current Node.
     */
    function checkForReplacement(isWhitespacePressed) {
        var sel = window.getSelection();
        if (sel.isCollapsed) {
            var text = sel.focusNode.textContent;
            var cursorPos = sel.focusOffset;
            //debugErr(sel.focusNode.textContent + '\n' + sel.focusOffset);

            var result = matchesKeyword(text, cursorPos, isWhitespacePressed);
            if (result.val !== null) {
                performReplacement(sel.focusNode, cursorPos - result.keylen, cursorPos, result.val);
            }
        }
    }

    /**
     * Checks whether TEXT.substring(0, LEN) ends with any keys in the symbol list, and if so, returns the match.
     *
     * @param text A string containing the substring to check.
     * @param len The length of the substring.
     * @return An object where VAL is value of the matched key-value pair (or null if no match), and KEYLEN is the 
     *   length of the key in the matched key-value pair.
     */
    function matchesKeyword(text, len, isWhitespacePressed) {
        //debugErr("In MK, text:" + text + " substring len: " + len);

        for (var i = 0, k; i < matchList.length; i++) {
            if (!matchList[i].spe && !isWhitespacePressed) {
                continue;
            }

            key = matchList[i].key;
            var startIndex = len - key.length;

            //debugErr("In MK, text:" + text + " key:" + key + " lenChk:" + (len >= key.length) + "" + );

            if (startIndex >= 0 && text.substring(startIndex, len) === key) {
                //debugErr("In MK, text:" + matchList[i].val + " len: " + key.length);
                return {"val":matchList[i].val, "keylen":key.length};
            }
        }

        return {"val":null, "keylen":0};
    }

    /**
     * Replaces the text in the given node with new text.
     * 
     * @param node The node to perform replacement on.
     * @param rangeStart The start index of the range.
     * @param rangeEnd The end index of the range (should be 1 + the index of the last character to be deleted). 
     * @param newText Replacement text.
     */
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

    // $("body").append('<div class="debug"></div>');
    // $(".debug").html("Hi, this is a test.");

    // function debugDiv(str) {
    //     py.run("debug_div:"+ str);
    // }

    // function debugErr(str) {
    //     py.run("debug_err:"+ str);
    // }
}
