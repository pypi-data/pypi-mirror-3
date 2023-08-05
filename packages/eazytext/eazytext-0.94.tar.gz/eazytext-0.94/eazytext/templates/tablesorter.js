function swap(cols, i, j) {
    var tmp = cols[j];
    cols[j] = cols[i];
    cols[i] = tmp;
}

function bubblesort(cols, desc) { // Bubble sort
    var swapped = true;
    var j = 0;
    var l = cols.length;
    while(swapped) {
        swapped = false;
        j++;
        for(i = 0; i < (l-j); i++) {
            // Note that this is the reverse comparision for
            // descending and ascending, since while placing the rows are
            // placed in the reverse order
            if( desc && cols[i].innerHTML > cols[i+1].innerHTML ) {
                swap(cols, i, i+1);
                swapped = true;
            } else if( cols[i].innerHTML < cols[i+1].innerHTML) {
                swap(cols, i, i+1);
                swapped = true;
            }
        };
    };
};

function tablesorter() {
    var parent_tr = function(n) {
        var n_parent = n;
        var n_tr = null;
        while(n_parent && (! n_tr)) {
            if( n_parent.tagName == "TR" ) {
                n_tr = n_parent;
            } else {
                n_parent = n_parent.parentNode;
            };
        }
        return n_tr;
    };

    var sortby = function(n_th, cols, e) {
        var zwikidesc = dojo.attr(n_th, "zwikidesc");
        var n_parent = n_th;
        var n_trth = null;
        var n_table = null;

        while(n_parent && (! n_table)) {
            if( n_parent.tagName == "TR" ) {
                n_table = n_parent.parentNode;
                n_trth = n_parent;
            } else {
                n_parent = n_parent.parentNode;
            };
        }

        if( n_table && cols.length) {
            var desc = dojo.attr(n_th, "zwikidesc") == "true";

            bubblesort(cols, desc);

            dojo.attr(n_th, "zwikidesc", desc ? "false" : "true");
            // Render
            for(i = 0; i < cols.length; i++ ) {
                var n_tr = parent_tr(cols[i]);
                dojo.destroy(n_tr);
                dojo.place( n_tr, n_trth, "after" );
            }
            dojo.query("div", n_th)[0].innerHTML = desc ? "&#9660;" : "&#9650;";
        };

    };

    var fortable = function(n_table) {
        var n_rows = dojo.query("tr", n_table);
        var n_trth = [];
        var n_trtd = [];
        for(i = 0; i < n_rows.length; i++) {
            var n_tr   = n_rows[i];
            var n_cols = dojo.query("td", n_tr);
            if( n_cols.length ) {
                n_trtd[n_trtd.length] = n_cols;
            } else {
                n_trth[n_trth.length] = dojo.query("th", n_tr);
            };
        };
        for(i = 0; i < n_trth.length; i++ ) {
            var l = n_trth[i].length;
            var cols = [];
            for(j = 0; j < l; j++) { cols[cols.length] = [] };
            dojo.map(
                dojo.filter( n_trtd, function(n) { return n.length == l }),
                function(nc) {
                    for(j = 0; j < l; j++) {
                        cols[j][cols[j].length] = nc[j]
                    };
                }
            );
            for(j = 0; j < l; j++) {
                var n_th = n_trth[i][j];
                dojo.style(n_th, { cursor : "pointer" });
                dojo.addClass(n_th, "hoverhighlight");
                dojo.attr(n_th, "zwikidesc", "none");
                dojo.connect( n_th, "onclick",
                              dojo.partial(sortby, n_th, cols[j]));
                dojo.create( "div",
                             { innerHTML: "&#9660;&#9650;",
                               style: { float: "right", fontSize: "xx-small" }
                             },
                             n_th, "last"
                          );
            };
        };
    };

    dojo.forEach(dojo.query("div.wikiblk table.sortable"), fortable);
};

dojo.addOnLoad(tablesorter);
