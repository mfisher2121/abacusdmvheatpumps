/* Neighbors page: fill the visitor's link into scripts, copy buttons, QR flyer. */
(function () {
  var link = window.mbShareUrl('/check/', 'copy');
  document.querySelectorAll('[data-script]').forEach(function (box) {
    box.textContent = box.textContent.replace('{link}', link);
  });
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var text = btn.parentNode.querySelector('[data-script]').textContent;
      window.mbTrack('share_click', { channel: 'copy_script', where: 'neighbors' });
      (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(
        function () { btn.textContent = 'Copied'; setTimeout(function () { btn.textContent = 'Copy'; }, 1800); },
        function () { btn.textContent = 'Select the text above to copy'; }
      );
    });
  });

  var qrBox = document.getElementById('qr');
  if (qrBox && window.qrcode) {
    var qr = window.qrcode(0, 'M');
    qr.addData(window.mbShareUrl('/check/', 'flyer'));
    qr.make();
    qrBox.innerHTML = qr.createSvgTag({ cellSize: 4, margin: 0, scalable: true });
  }
  var pf = document.getElementById('print-flyer');
  if (pf) pf.addEventListener('click', function () {
    window.mbTrack('share_click', { channel: 'flyer', where: 'neighbors' });
    var w = window.open('', '_blank');
    if (!w) { window.print(); return; }
    w.document.write('<!doctype html><title>Flyer</title><link rel="stylesheet" href="/assets/site.css"><body style="background:#fff;padding:2rem">' +
      document.getElementById('flyer').outerHTML + '<script>setTimeout(function(){print()},400)<\/script></body>');
    w.document.close();
  });
})();
