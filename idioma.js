/*
  Sugerencia de idioma. Nada más.

  El sitio NO redirige por idioma. Una redirección automática se equivoca a
  menudo —hay quien navega en un idioma y quiere leer en otro— y cuando se
  equivoca no deja salida, porque al volver te vuelve a redirigir. Aquí solo
  aparece un aviso, en el idioma que se ofrece, y la decisión se recuerda.

  La detección es `navigator.languages`, que es lo que el usuario ya eligió en
  su navegador. No hay GeoIP: haría falta llamar a un tercero con la IP del
  visitante, y la política de privacidad de este sitio promete que no se llama a
  ninguno. Por un cambio de idioma no compensa romper esa promesa.

  El país tampoco es el dato bueno: alguien puede vivir en Escocia y querer leer
  en español. El idioma del navegador acierta mucho más.
*/
(function () {
  'use strict';

  var CLAVE = 'pronuncia-idioma';

  var TEXTO = {
    es: { mensaje: '¿Prefieres leer esto en español?', ir: 'Ver en español', no: 'No, gracias' },
    en: { mensaje: 'Would you rather read this in English?', ir: 'Switch to English', no: 'No thanks' }
  };

  var actual = (document.documentElement.lang || 'en').slice(0, 2);

  // El destino es el propio selector de idioma de la cabecera, no una lista
  // aparte: si ese enlace cambia, cambia en un solo sitio. Y su `href` es
  // relativo, así que el aviso sigue funcionando cuando el sitio se sirve desde
  // una subcarpeta —el banco de pruebas local lo hace, en /web/—, cosa que las
  // etiquetas `hreflang` no permiten porque exigen URLs absolutas.
  var alterno = document.querySelector('a.idioma[hreflang]');
  if (!alterno || alterno.getAttribute('hreflang') === actual) return;

  var otro = alterno.getAttribute('hreflang');
  if (!TEXTO[otro]) return;

  // Si ya eligió una vez, se respeta y no se vuelve a preguntar. localStorage
  // puede fallar (modo privado de Safari, almacenamiento bloqueado); si falla,
  // se sigue adelante sin recordar en vez de romper la página.
  var recordado = null;
  try { recordado = localStorage.getItem(CLAVE); } catch (e) {}
  if (recordado) return;

  var preferidos = navigator.languages || [navigator.language || ''];
  var quiereOtro = false;
  for (var j = 0; j < preferidos.length; j++) {
    var pref = String(preferidos[j]).slice(0, 2).toLowerCase();
    if (pref === actual) return;   // el idioma de esta página le vale: no molestar
    if (pref === otro) { quiereOtro = true; break; }
  }
  if (!quiereOtro) return;

  var t = TEXTO[otro];
  var aviso = document.createElement('div');
  aviso.className = 'aviso-idioma';
  aviso.lang = otro;

  var texto = document.createElement('span');
  texto.textContent = t.mensaje;

  var acciones = document.createElement('span');
  var ir = document.createElement('a');
  ir.href = alterno.getAttribute('href');
  ir.textContent = t.ir;
  ir.addEventListener('click', function () { recordar(otro); });

  var no = document.createElement('button');
  no.type = 'button';
  no.textContent = t.no;
  no.addEventListener('click', function () { recordar(actual); aviso.remove(); });

  acciones.appendChild(ir);
  acciones.appendChild(document.createTextNode(' · '));
  acciones.appendChild(no);
  aviso.appendChild(texto);
  aviso.appendChild(acciones);

  document.body.insertBefore(aviso, document.body.firstChild);

  function recordar(valor) {
    try { localStorage.setItem(CLAVE, valor); } catch (e) {}
  }
})();
