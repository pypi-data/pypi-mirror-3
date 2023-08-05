function togglebox() {
    var boxhide = function(n_hide, n_show, n_cont, e) {
        dojo.style(n_hide, { display : "none" });
        dojo.style(n_show, { display : "inherit" });
        dojo.style(n_cont, { display : "none" });
    }

    var boxshow = function(n_hide, n_show, n_cont, e) {
        dojo.style(n_hide, { display : "inherit" });
        dojo.style(n_show, { display : "none" });
        dojo.style(n_cont, { display : "inherit" });
    }

    dojo.forEach(
        dojo.query("div.wikiblk div.boxext"),
        function(n) {
            var n_hide = dojo.query(".boxhide", n)[0];
            var n_show = dojo.query(".boxshow", n)[0];
            var n_cont = dojo.query(".boxcont", n)[0];
            dojo.connect( n_hide, "onclick",
                          dojo.partial(boxhide, n_hide, n_show, n_cont) );
            dojo.connect( n_show, "onclick",
                          dojo.partial(boxshow, n_hide, n_show, n_cont) );
        }
    );
}
dojo.addOnLoad(togglebox);
