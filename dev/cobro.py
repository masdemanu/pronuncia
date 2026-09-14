# -*- coding: utf-8 -*-
"""Enciende o apaga en el sitio todo lo referente a precios y pago.

    python3 dev/cobro.py off    # mientras la versión de pago no esté publicada
    python3 dev/cobro.py on     # el día que se publique

No oculta con CSS a propósito: el texto se quita del HTML. Un precio
escondido con `display:none` lo indexa Google igual y lo ve cualquiera que
mire el código, y ahora mismo sería anunciar un cobro que la extensión
publicada ni siquiera sabe hacer.

Cada pareja es (texto cuando se cobra, texto cuando no). El script exige
encontrar el lado del que parte, así que no puede dejar el sitio a medias.
"""
import io, sys, os

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OFERTAS_EN = '''      "offers": [
            {
                  "@type": "Offer",
                  "price": "10",
                  "priceCurrency": "USD",
                  "description": "Monthly subscription",
                  "url": "https://pronuncia.dev/#pricing"
            },
            {
                  "@type": "Offer",
                  "price": "100",
                  "priceCurrency": "USD",
                  "description": "Annual subscription",
                  "url": "https://pronuncia.dev/#pricing"
            }
      ],
'''

# El bloque es idéntico en los dos archivos: la ficha JSON-LD se generó una
# sola vez y sus descripciones van en inglés en ambos.
OFERTAS_ES = OFERTAS_EN

PRECIOS_EN = '''      <h2 id="pricing">Pricing</h2>
      <p><strong>21-day free trial</strong>, no card required. After that, pick a plan:</p>

      <div class="precios">
        <div class="plan">
          <span class="cantidad">US$10</span>
          <span class="suave">per month</span>
        </div>
        <div class="plan destacado">
          <span class="etiqueta">Two months free</span>
          <span class="cantidad">US$100</span>
          <span class="suave">per year · the price of 10 months</span>
        </div>
      </div>

      <p class="suave">
        Prices are in US dollars. Any tax due in your country is calculated and shown at
        checkout. You can cancel whenever you like and keep access until the end of the
        period you have already paid for.
      </p>

      <p>
        You subscribe from inside the extension itself, because that is what knows which
        account to activate. See also the <a href="terms/">terms</a>, the
        <a href="refunds/">refund policy</a> and the <a href="privacy/">privacy policy</a>.
      </p>
'''

SIN_PRECIOS_EN = '''      <p>
        See also the <a href="terms/">terms</a>, the
        <a href="refunds/">refund policy</a> and the <a href="privacy/">privacy policy</a>.
      </p>
'''

PRECIOS_ES = '''      <h2 id="precios">Precios</h2>
      <p><strong>21 días de prueba gratis</strong>, sin tarjeta. Después, elige plan:</p>

      <div class="precios">
        <div class="plan">
          <span class="cantidad">US$10</span>
          <span class="suave">al mes</span>
        </div>
        <div class="plan destacado">
          <span class="etiqueta">Dos meses gratis</span>
          <span class="cantidad">US$100</span>
          <span class="suave">al año · equivale a 10 meses</span>
        </div>
      </div>

      <p class="suave">
        Los precios están en dólares estadounidenses. Los impuestos aplicables según tu
        país se calculan y se muestran en el momento del pago. Puedes cancelar cuando
        quieras y seguirás teniendo acceso hasta el final del periodo que ya pagaste.
      </p>

      <p>
        La suscripción se contrata desde la propia extensión, que es la que sabe a qué
        cuenta hay que activarla. Consulta también los
        <a href="terminos/">términos</a>, la <a href="reembolsos/">política de reembolsos</a>
        y la <a href="privacidad/">política de privacidad</a>.
      </p>
'''

SIN_PRECIOS_ES = '''      <p>
        Consulta también los
        <a href="terminos/">términos</a>, la <a href="reembolsos/">política de reembolsos</a>
        y la <a href="privacidad/">política de privacidad</a>.
      </p>
'''

PAREJAS = {
  'index.html': [
    (OFERTAS_EN, ''),
    ('        <a href="#pricing">Pricing</a>\n', ''),
    ('<span class="suave">Free for 21 days, no card required.</span>',
     '<span class="suave">Free to use right now.</span>'),
    (PRECIOS_EN, SIN_PRECIOS_EN),
    ('<h2>Before you subscribe, you should know</h2>',
     '<h2>Before you install it, you should know</h2>'),
    ('''        You need <strong>Google Chrome</strong>, a microphone and an internet connection. The
        21-day trial is there so you can find out whether it works for you before paying
        anything.''',
     '''        You need <strong>Google Chrome</strong>, a microphone and an internet
        connection.'''),
  ],
  'es/index.html': [
    (OFERTAS_ES, ''),
    ('        <a href="#precios">Precios</a>\n', ''),
    ('<span class="suave">Gratis 21 días, sin tarjeta.</span>',
     '<span class="suave">Ahora mismo es gratis.</span>'),
    (PRECIOS_ES, SIN_PRECIOS_ES),
    ('<h2>Antes de suscribirte, conviene que sepas</h2>',
     '<h2>Antes de instalarla, conviene que sepas</h2>'),
    ('''        Necesitas <strong>Google Chrome</strong>, micrófono y conexión a internet. Los 21 días
        de prueba están para comprobar si te sirve antes de pagar nada.''',
     '''        Necesitas <strong>Google Chrome</strong>, micrófono y conexión a
        internet.'''),
  ],
}

def aplicar(estado):
    for archivo, parejas in PAREJAS.items():
        ruta = os.path.join(AQUI, archivo)
        s = io.open(ruta, encoding='utf-8').read()
        for con, sin in parejas:
            desde, hasta = (sin, con) if estado == 'on' else (con, sin)
            if desde == hasta:
                continue
            # Para una eliminación, `hasta` es la cadena vacía y preguntarle
            # `in s` no dice nada: siempre es cierta. El centinela es lo que
            # de verdad distingue «ya aplicado» de «no encontré el texto».
            centinela = hasta if hasta else None
            if desde not in s and (centinela is None or centinela in s):
                continue                       # ya estaba en ese estado
            if desde not in s:
                raise SystemExit(f'ABORTADO: no se encontró un fragmento en {archivo}.\n'
                                 f'Empieza por: {desde.strip()[:70]}…')
            s = s.replace(desde, hasta, 1)
        io.open(ruta, 'w', encoding='utf-8').write(s)
        print(f'  {archivo}: cobro {estado}')

if __name__ == '__main__':
    estado = sys.argv[1] if len(sys.argv) > 1 else ''
    if estado not in ('on', 'off'):
        raise SystemExit('uso: python3 dev/cobro.py on|off')
    aplicar(estado)
