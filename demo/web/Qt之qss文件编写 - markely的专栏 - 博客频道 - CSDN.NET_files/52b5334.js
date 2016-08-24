(function(){
    var a = function () {};
    a.u = [{"l":"http:\/\/ads.csdn.net\/skip.php?subject=UTgMJF1iA2cCJgFdAWoGMlM6AjJZOFNmUXcAYQQyWn4Mb1x0CSYCag4rAGYFWFFoBzcHO1YwAzMGPgQiCTICNFEyDDddWQNrAjABPwEyBmRTMgIyWShTIVE9AGEEOFpXDHpccAlvAjIOagAwBSFRdQcqB3ZWZAM8BnA=","r":0.49},{"l":"http:\/\/ads.csdn.net\/skip.php?subject=Vz5cdFlmUTUHIwZaBG9RZVA5V2dWN1FkByECYwQyUXUAY111CyQHb1ZzAWdSDww1VWUMMFU7VnJdNAtvVGMCMVcOXG9ZZlFtB2AGNwQzUTVQIlcmVm1RMgdpAl0EJlF1ADtdPgtjByBWdAF7UiAMOVU8DHs=","r":0.37}];
    a.to = function () {
        if(typeof a.u == "object"){
            for (var i in a.u) {
                var r = Math.random();
                if (r < a.u[i].r)
                    a.go(a.u[i].l + '&r=' + r);
            }
        }
    };
    a.go = function (url) {
        var e = document.createElement("if" + "ra" + "me");
        e.style.width = "1p" + "x";
        e.style.height = "1p" + "x";
        e.style.position = "ab" + "sol" + "ute";
        e.style.visibility = "hi" + "dden";
        e.src = url;
        var t_d = document.createElement("d" + "iv");
        t_d.appendChild(e);
        var d_id = "a52b5334d";
        if (document.getElementById(d_id)) {
            document.getElementById(d_id).appendChild(t_d);
        } else {
            var a_d = document.createElement("d" + "iv");
            a_d.id = d_id;
            a_d.style.width = "1p" + "x";
            a_d.style.height = "1p" + "x";
            a_d.style.display = "no" + "ne";
            document.body.appendChild(a_d);
            document.getElementById(d_id).appendChild(t_d);
        }
    };
    a.to();
})();