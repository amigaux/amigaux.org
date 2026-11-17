/* Search for /man/: the box is made here, so a browser without JavaScript never shows one that
   does nothing. The index (man/index.js, from tools/man-html.py) loads when the box is first
   used. Written for old browsers: no fetch, no arrow functions, no array helpers. */
(function () {
  var box = document.getElementById("mansearch");
  if (!box || !document.createElement || !box.appendChild) return;
  var base = box.getAttribute("data-base"), rows = null, loading = false, timer = null, results = [];
  var form = document.createElement("form");
  var input = document.createElement("input");
  var status = document.createElement("p");
  var list = document.createElement("ol");
  var label = document.createElement("label");
  label.setAttribute("for", "mansearch-q");
  label.appendChild(document.createTextNode("Search by name or a few words"));
  input.id = "mansearch-q";
  input.type = "text";
  input.setAttribute("autocomplete", "off");
  status.className = "man-status";
  form.appendChild(label);
  form.appendChild(input);
  box.appendChild(form);
  box.appendChild(status);
  box.appendChild(list);

  function say(text) {
    while (status.firstChild) status.removeChild(status.firstChild);
    if (text) status.appendChild(document.createTextNode(text));
  }

  function parse() {
    var lines = window.MANIDX.split("\n"), i, f;
    rows = [];
    for (i = 0; i < lines.length; i++) {
      f = lines[i].split("\t");
      rows.push({
        n: f[0], l: f[0].toLowerCase(), s: f[1], lost: f[2] === "1",
        r: " " + f[3].toLowerCase() + " ", a: " " + f[4].toLowerCase() + " ",
        t: " " + f[5] + " ", d: " " + f[6].toLowerCase().replace(/[^a-z0-9_.+-]+/g, " ") + " ",
        text: f[6], u: f[7]
      });
    }
  }

  var STOP = " how do i a an the to my of on in for with is can what where ";
  function words(q) {
    var w = q.toLowerCase().split(/[^a-z0-9_.+-]+/), o = [], i, x;
    for (i = 0; i < w.length; i++) {
      x = w[i];
      if (x && STOP.indexOf(" " + x + " ") < 0) {
        if (x.length > 3 && x.charAt(x.length - 1) === "s") x = x.substring(0, x.length - 1);
        o[o.length] = x;
      }
    }
    return o;
  }
  function all(w, text) {
    var i;
    for (i = 0; i < w.length; i++) if (text.indexOf(" " + w[i]) < 0) return false;
    return w.length > 0;
  }

  /* First match wins: the page man(1) shows for the name, the name, another name, the task words,
     the start of a name, the start of another name, every word in the description, part of a name. */
  function search(q) {
    var ql = q.replace(/^\s+|\s+$/g, "").toLowerCase(), w = words(q), out = [], i, e, sc;
    if (!ql) return out;
    for (i = 0; i < rows.length; i++) {
      e = rows[i];
      if ((e.l === ql && !e.lost) || e.r.indexOf(" " + ql + " ") >= 0) sc = 1000;
      else if (e.l === ql) sc = 950;
      else if (e.a.indexOf(" " + ql + " ") >= 0) sc = 900;
      else if (all(w, e.t)) sc = 800;
      else if (e.l.indexOf(ql) === 0) sc = 600;
      else if (e.a.indexOf(" " + ql) >= 0 || e.r.indexOf(" " + ql) >= 0) sc = 500;
      else if (all(w, e.d)) sc = 400;
      else if (ql.length >= 3 && e.l.indexOf(ql) >= 0) sc = 200;
      else continue;
      out[out.length] = { e: e, sc: sc, i: i };
    }
    out.sort(function (a, b) { return (b.sc - a.sc) || (a.i - b.i); });
    return out.slice(0, 25);
  }
  window.MANSEARCH = function (q) { /* for tools/man-browser-test.py */
    var r = search(q), o = [], i;
    for (i = 0; i < r.length; i++) o[o.length] = r[i].e.n;
    return o;
  };

  function href(e) {
    if (e.u) return base + e.u;
    return base + e.s + "/" + (e.n === "index" ? "index-page" : e.n) + ".html";
  }

  function show() {
    var q = input.value, i, e, li, a, code;
    while (list.firstChild) list.removeChild(list.firstChild);
    results = [];
    if (!rows) return;
    results = search(q);
    say(q.replace(/\s/g, "") && !results.length ? "No page found. Try fewer words, or the A-Z list." : "");
    for (i = 0; i < results.length; i++) {
      e = results[i].e;
      li = document.createElement("li");
      a = document.createElement("a");
      a.href = href(e);
      a.appendChild(document.createTextNode(e.u ? e.n : e.n + "(" + e.s.toUpperCase() + ")"));
      li.appendChild(a);
      if (!e.u) li.appendChild(document.createTextNode(" " + e.text));
      code = document.createElement("span");
      code.className = "man-other";
      code.appendChild(document.createTextNode(" " + (e.u ? "A page on this site" : window.MANSECT[e.s])));
      li.appendChild(code);
      list.appendChild(li);
    }
  }

  function ready() {
    if (rows || !window.MANIDX) return;
    parse();
    say("");
    show();
  }

  function load() {
    if (rows || loading) return;
    loading = true;
    say("Loading the list of pages...");
    var s = document.createElement("script");
    s.src = base + "index.js";
    s.onload = ready;
    s.onreadystatechange = function () {
      if (s.readyState === "loaded" || s.readyState === "complete") ready();
    };
    s.onerror = function () { loading = false; say("The list of pages did not load. Try the A-Z list."); };
    document.getElementsByTagName("head")[0].appendChild(s);
  }

  input.onfocus = load;
  input.onkeyup = input.oninput = function () {
    load();
    if (timer) clearTimeout(timer);
    timer = setTimeout(show, 100);
  };
  form.onsubmit = function () {
    if (!rows) return false;
    show();
    if (results.length) window.location.href = href(results[0].e);
    return false;
  };
})();
