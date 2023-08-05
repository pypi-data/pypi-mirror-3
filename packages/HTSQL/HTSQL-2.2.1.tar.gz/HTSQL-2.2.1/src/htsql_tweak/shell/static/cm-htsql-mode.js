
CodeMirror.defineMode("htsql", function(conf) {
    return {
        token: function(stream, state) {
            if (stream.eatSpace()) {
                return null;
            }
            if (stream.match(/^:\s*[a-zA-Z_][0-9a-zA-Z_]*/)) {
                return 'htsql-function';
            }
            if (stream.match(/^[a-zA-Z_][0-9a-zA-Z_]*/)) {
                if (stream.match(/^\s*\(/, false)) {
                    return 'htsql-function';
                }
                return 'htsql-attribute';
            }
            if (stream.match(/^((\d*\.)?\d+[eE][+-]?\d+|\d*\.\d+|\d+\.?)/)) {
                return 'htsql-number';
            }
            if (stream.match(/^\'([^\']|\'\')*\'/)) {
                return 'htsql-string';
            }
            if (stream.match(/~|!~|<=|<|>=|>|==|=|!==|!=|!|&|\||->|\?|\^|\/|\*|\+|-/)) {
                return 'htsql-operator';
            }
            if (stream.match(/\.|,|\(|\)|\{|\}|\[|\]|:=|:|\$|@/)) {
                return 'htsql-punctuation';
            }
            stream.next();
            return null;
        }
    };
});

CodeMirror.defineMIME("text/x-htsql", "htsql");

