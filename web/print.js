/* Print the deck — Cavendish Cards.
 *
 * The page is already the artifact: fifteen sheets of nine cards, inline, at
 * exactly 7.5 x 10.5 in. So this file does almost nothing. It sets the page
 * box, decides whether the backs come along, and calls print().
 *
 * `size: auto` is deliberate. One sheet geometry fits both US Letter and A4
 * inside a quarter-inch margin, so the paper the reader has selected is the
 * paper that works -- there is no paper control on this page and there does
 * not need to be. The rule goes in through the CSSOM rather than an inline
 * <style>, which the site's CSP refuses.
 */
(function () {
  "use strict";

  var pageRule = -1;

  function setPageBox() {
    try {
      var sheet = null, i;
      for (i = 0; i < document.styleSheets.length; i++) {
        var ss = document.styleSheets[i];
        if (ss.href && ss.href.indexOf("styles.css") !== -1) { sheet = ss; break; }
      }
      if (!sheet) return;
      if (pageRule >= 0) {
        try { sheet.deleteRule(pageRule); } catch (e) { /* already gone */ }
        pageRule = -1;
      }
      pageRule = sheet.insertRule("@page{size:auto;margin:0.25in}", sheet.cssRules.length);
    } catch (e) {
      /* A locked or cross-origin stylesheet. The sheets are still the right
       * size on paper; the reader just has to set the margins themselves,
       * which the instructions on the page tell them to do anyway. */
    }
  }

  function go(withBacks) {
    var backs = document.getElementById("print-backs-details");
    /* A closed <details> prints nothing, so the backs have to be open before
     * the dialog opens. Reopening state afterwards is deliberate: somebody who
     * printed faces only should not come back to a page that has silently
     * unfolded a second copy of the deck. */
    var wasOpen = backs ? backs.open : false;
    if (backs && withBacks) backs.open = true;
    document.body.classList.add("printing-deck");
    if (withBacks) document.body.classList.add("printing-backs");
    setPageBox();
    window.print();
    window.addEventListener("afterprint", function restore() {
      window.removeEventListener("afterprint", restore);
      document.body.classList.remove("printing-deck", "printing-backs");
      if (backs) backs.open = wasOpen;
    });
  }

  function init() {
    var f = document.getElementById("print-faces");
    if (f) f.addEventListener("click", function () { go(false); });
    var b = document.getElementById("print-both");
    if (b) b.addEventListener("click", function () { go(true); });
    var note = document.getElementById("print-note");
    if (note) {
      note.textContent = "These buttons set the page size and margins for you. " +
        "Check that the print dialog says 100% and not “fit to page” before " +
        "you send it.";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
