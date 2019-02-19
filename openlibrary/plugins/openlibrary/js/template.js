// Simple Javascript Templating
//
// Inspired by http://ejohn.org/blog/javascript-micro-templating/

/* eslint-disable no-unused-vars */
// used in plugins/openlibrary/js/jquery.repeat.js
function Template(tmpl_text) {
    var s = [];
    var js = ["var _p=[];", "with(env) {"];

    function addCode(text) {
        js.push(text);
    }
    function addExpr(text) {
        js.push("_p.push(htmlquote(" + text + "));");
    }
    function addText(text) {
        js.push("_p.push(__s[" + s.length + "]);");
        s.push(text);
    }

    var tokens = tmpl_text.split("<%");

    addText(tokens[0]);
    for (var i=1; i < tokens.length; i++) {
        var t = tokens[i].split('%>');

        if (t[0][0] == "=") {
            addExpr(t[0].substr(1));
        }
        else {
            addCode(t[0]);
        }
        addText(t[1]);
    }
    js.push("}", "return _p.join('');");

    var f = new Function(["__s", "env"], js.join("\n"));
    var g = function(env) {
        return f(s, env);
    };
    g.toString = function() { return tmpl_text; };
    g.toCode = function() { return f.toString(); };
    return g;
}
/* eslint-enable no-unused-vars */
