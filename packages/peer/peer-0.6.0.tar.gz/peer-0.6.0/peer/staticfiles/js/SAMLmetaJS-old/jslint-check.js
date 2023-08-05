var JSLINT = require("/home/lgs/proyectos/jslint").JSLINT,
    print = require("sys").print,
    readFileSync = require("fs").readFileSync,
    error = null, i = 0, j = 0, src = null;

for (i = 2; i < process.argv.length; i++) {
    print("Analyzing file " + process.argv[i] + "\n");
    src = readFileSync(process.argv[i], "utf8");
    JSLINT(src, {
        strict: false, //true,
        white: false, //true,
        onevar: false, //true,
        undef: true,
        newcap: true,
        nomem: true,
        regexp: true,
        plusplus: false, //true,
        bitwise: true,
        maxerr: 100,
        indent: 4,
        predef: ['console', 'window', 'DOMParser', 'ActiveXObject', 'XMLHttpRequest', 'jQuery', 'google', 'SAMLmetaJS']
    });

    for (j = 0; j < JSLINT.errors.length; j++ ) {
        error = JSLINT.errors[j];
        if (error !== null) {
            if (typeof error.evidence !== "undefined") {
		        print("\n" + error.evidence + "\n");
            } else {
                print("\n");
            }
		    print("    Problem at line " + error.line + " character " + error.character + ": " + error.reason);
        }
    }

    if (JSLINT.errors.length > 0) {
	    print("\n" + JSLINT.errors.length + " Error(s) found.\n");
        break;
    }
}
