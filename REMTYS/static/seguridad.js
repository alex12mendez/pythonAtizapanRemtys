(function () {
  let _0xdev = false;
  const _0xth = 160;

  function _0xabc() {
    document.body.innerHTML = `
      <h1 style="text-align:center; color:red;">ERROR 403 - ACCESO RESTRINGIDO</h1>
      <p style="text-align:center;">Intento de inspección detectado. Este sitio está protegido.</p>
      <pre style="background:#000; color:#0f0; padding:10px; font-size:14px; overflow:auto;">
        SYSTEM WARNING:
        memory@0x0000EF14 = NULL
        usuario_fake = "invitado"
        permisos = "ninguno"
        rastreo_habilitado = TRUE;
      </pre>
    `;
  }

  const _0xint1 = setInterval(() => {
    const w = window.outerWidth - window.innerWidth > _0xth;
    const h = window.outerHeight - window.innerHeight > _0xth;
    if (w || h) {
      if (!_0xdev) {
        _0xdev = true;
        _0xabc();
        clearInterval(_0xint1);
        clearInterval(_0xint2);
      }
    } else {
      _0xdev = false;
    }
  }, 1000);

  const _0xint2 = setInterval(() => {
    const el = new Image();
    Object.defineProperty(el, 'id', {
      get: function () {
        _0xabc();
        clearInterval(_0xint2);
        clearInterval(_0xint1);
      }
    });
    console.log(el);
  }, 1500);

  document.addEventListener("contextmenu", e => e.preventDefault());

  document.addEventListener("keydown", function (e) {
    const k = e.key.toLowerCase();
    const combo = (e.ctrlKey ? 'ctrl+' : '') + (e.shiftKey ? 'shift+' : '') + k;
    const block = ["f12", "ctrl+shift+i", "ctrl+shift+j", "ctrl+shift+c", "ctrl+u"];
    if (block.includes(combo)) {
      e.preventDefault();
      _0xabc();
    }
  });

  document.addEventListener("copy", e => {
    e.preventDefault();
    _0xabc();
  });

  document.addEventListener("selectstart", e => e.preventDefault());

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("img").forEach(img => {
      img.setAttribute("draggable", "false");
      img.addEventListener("contextmenu", e => e.preventDefault());
    });
  });
})();
(function () {
  let _0xdev = false;
  const _0xth = 160;

  function _0xabc() {
    document.body.innerHTML = `
      <h1 style="text-align:center; color:red;">ERROR 403 - ACCESO RESTRINGIDO</h1>
      <p style="text-align:center;">Intento de inspección detectado. Este sitio está protegido.</p>
      <pre style="background:#000; color:#0f0; padding:10px; font-size:14px; overflow:auto;">
        SYSTEM WARNING:
        <h1 style="text-align:center; color:red;">¡EL GOBIERNO DE ATIZAPAN DE ZARAGOZA PUEDE RASTREARTE!</h1>
        memory@0x0000EF14 = NULL
        usuario_fake = "invitado"
        permisos = "ninguno"
        rastreo_habilitado = TRUE;
      </pre>
    `;
  }

  const _0xint1 = setInterval(() => {
    const w = window.outerWidth - window.innerWidth > _0xth;
    const h = window.outerHeight - window.innerHeight > _0xth;
    if (w || h) {
      if (!_0xdev) {
        _0xdev = true;
        _0xabc();
        clearInterval(_0xint1);
        clearInterval(_0xint2);
      }
    } else {
      _0xdev = false;
    }
  }, 1000);

  const _0xint2 = setInterval(() => {
    const el = new Image();
    Object.defineProperty(el, 'id', {
      get: function () {
        _0xabc();
        clearInterval(_0xint2);
        clearInterval(_0xint1);
      }
    });
    console.log(el);
  }, 1500);

  document.addEventListener("contextmenu", e => e.preventDefault());

  document.addEventListener("keydown", function (e) {
    const k = e.key.toLowerCase();
    const combo = (e.ctrlKey ? 'ctrl+' : '') + (e.shiftKey ? 'shift+' : '') + k;
    const block = ["f12", "ctrl+shift+i", "ctrl+shift+j", "ctrl+shift+c", "ctrl+u"];
    if (block.includes(combo)) {
      e.preventDefault();
      _0xabc();
    }
  });

  document.addEventListener("copy", e => {
    e.preventDefault();
    _0xabc();
  });

  document.addEventListener("selectstart", e => e.preventDefault());

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("img").forEach(img => {
      img.setAttribute("draggable", "false");
      img.addEventListener("contextmenu", e => e.preventDefault());
    });
  });
})();
