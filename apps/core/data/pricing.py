"""Preise – die einzige Wahrheit im Projekt.

Jede Preiszahl, die irgendwo auf der Website erscheint, stammt aus diesem Modul:
der Preisrechner (Server *und* Browser), die Texte auf den Stadtseiten, das
FAQ-Schema, `llms.txt` und die Preistabelle. Eine Zahl in ein Template zu tippen
ist ab jetzt ein Fehler, kein Stilproblem.

Warum das nötig war (in F1/F2 nachgemessen, siehe `seo-geo-plan/BASELINE.md`):

* **11 Fundstellen in 3 Templates** nannten noch den alten Einstiegspreis von
  180 € – der Rechner verlangte längst 300 €.
* Die JS-Rabattstädte im Wizard und `_STANDORT_RABATT_STAEDTE` in Python waren
  auseinandergelaufen: Wer „Köthen" eintippte, sah keinen Rabatt, bekam aber
  serverseitig 5 % abgezogen.
* Python rundet kaufmännisch-symmetrisch (`round(472.5) == 472`), JavaScript
  rundet auf (`Math.round(472.5) === 473`). Über den gesamten Eingaberaum des
  Rechners gemessen wichen **6.447 von 120.000 Kombinationen um 1 €** ab – der
  Kunde sah immer den höheren Wert, die Bestätigungsmail nannte den niedrigeren.
  Deshalb rundet `_round_preis()` hier explizit auf, wie der Browser.

Das Modul kennt Django nicht und importiert nichts aus `apps.core` – sonst
entsteht ein Zirkel über `context_processors` ← `views`.
"""

import functools
import math
import re
import unicodedata

from .stand import deutsch as _stand_deutsch

__all__ = [
    '_PER_QM_PREISE', '_MALER_PER_QM', '_STOCKWERK_AUFPREIS',
    '_FUELLGRAD_FAKTOR', '_SONDERABFALL_AUFPREIS', '_KLEIN_SAN_ITEMS',
    '_KLEIN_SONSTIGES_AUFPREIS', '_STOCKWERK_OBJEKTE', '_SONDERABFALL_OBJEKTE',
    '_STOCKWERK_LABELS', '_FUELLGRAD_LABELS', '_SONDERABFALL_LABELS',
    '_STANDORT_RABATT_STAEDTE', '_STANDORT_RABATT_FAKTOR', '_OBJEKTART_LABELS',
    '_OBJEKTART_LABELS_KURZ', '_TYPISCHE_GROESSE', '_PREISSTAND',
    '_PREISSTAND_ISO',
    'berechne_preis', 'auswahl_text', 'preis_context', 'js_konstanten', 'euro',
    'hat_standort_rabatt', 'ort_normalisiert',
]

# ── Grundpreise ──────────────────────────────────────────────────────────────
# rate = €/m², min_preis = Mindestpreis. Der kleinste Mindestpreis (300 €) ist
# zugleich der beworbene Einstiegspreis der Website.
_PER_QM_PREISE = {
    'keller':  {'rate': 32, 'min_preis': 300},
    'wohnung': {'rate': 36, 'min_preis': 675},
    'haus':    {'rate': 44, 'min_preis': 1450},
    'gewerbe': {'rate': 25, 'min_preis': 750},
    'garten':  {'rate': 13, 'min_preis': 300},
    'scheune': {'rate': 22, 'min_preis': 550},
}

# ── Modifikatoren, in genau dieser Reihenfolge angewendet ────────────────────
_MALER_PER_QM          = {'rate': 17, 'min_preis': 400}
_STOCKWERK_AUFPREIS    = {'eg': 0, '1og': 150, '2og': 270, '3og': 405, '4og': 590}
_FUELLGRAD_FAKTOR      = {'leicht': 1.00, 'mittel': 1.20, 'voll': 1.35,
                          'verschmutzt': 1.55, 'messi': 1.75}
_SONDERABFALL_AUFPREIS = {'keine': 0, 'wenige': 170, 'viele': 460}

# Label gehört zur Zahl – sonst driften Preis und Beschriftung auseinander.
_KLEIN_SAN_ITEMS = {
    'wasserhahn':    {'preis': 140, 'label': 'Wasserhahn / Armatur reparieren'},
    'tuer':          {'preis': 165, 'label': 'Tür reparieren / einstellen'},
    'fenster_r':     {'preis': 200, 'label': 'Fenster reparieren / abdichten'},
    'wand_loch':     {'preis': 115, 'label': 'Loch in Wand schließen / spachteln'},
    'schimmel':      {'preis': 200, 'label': 'Schimmel beseitigen'},
    'fliesen':       {'preis': 250, 'label': 'Fliesen ersetzen (bis 10 Stück)'},
    'sockelleisten': {'preis': 140, 'label': 'Sockelleisten erneuern'},
    'dichtungen':    {'preis': 120, 'label': 'Dusche / Badewanne abdichten'},
    'steckdosen':    {'preis': 140, 'label': 'Steckdosen / Schalter erneuern'},
}
_KLEIN_SONSTIGES_AUFPREIS = 190

# Beschriftungen zu den Modifikatoren. Sie stehen hier und nicht im Template,
# aus demselben Grund wie das 'label' in _KLEIN_SAN_ITEMS: Wer eine Zahl aendert,
# sieht ihre Beschriftung daneben. Sie speisen den Rechenweg (siehe unten).
_STOCKWERK_LABELS = {'eg': 'Erdgeschoss', '1og': '1. Obergeschoss',
                     '2og': '2. Obergeschoss', '3og': '3. Obergeschoss',
                     '4og': '4. Obergeschoss'}
_FUELLGRAD_LABELS = {'leicht': 'leicht', 'mittel': 'mittel', 'voll': 'voll',
                     'verschmutzt': 'stark verschmutzt', 'messi': 'Messie-Fall'}
_SONDERABFALL_LABELS = {'keine': 'keiner', 'wenige': 'einzelne Posten',
                        'viele': 'viele Posten'}

_STOCKWERK_OBJEKTE    = frozenset({'wohnung', 'keller'})
_SONDERABFALL_OBJEKTE = frozenset({'keller', 'wohnung', 'haus', 'gewerbe', 'scheune'})

# Ganzwort-Vergleich auf dem normalisierten, frei getippten Ort (EIG126, seit
# 24.09.2026). Bis dahin war es ein Teilstring-Vergleich: „Hallesche Straße 5,
# Bitterfeld" traf 'halle', „Leipziger Str., Grimma" traf 'leipzig' - und das
# Angebot ging mit 5 % Nachlass per Mail hinaus. Ein Eintrag ist deshalb genau
# ein Wort (bzw. eine Wortfolge) des Ortsnamens, nicht ein Wortanfang.
_STANDORT_RABATT_STAEDTE = frozenset({
    'leipzig', 'halle', 'schkeuditz', 'markranstädt', 'borna', 'delitzsch', 'merseburg',
    'magdeburg', 'halberstadt', 'stendal', 'dessau', 'köthen',
    'hannover', 'hildesheim', 'wolfsburg', 'braunschweig', 'celle', 'hameln',
    'dresden', 'chemnitz', 'pirna', 'meißen', 'zwickau', 'freiberg', 'riesa',
})
_STANDORT_RABATT_FAKTOR = 0.95
#: Zusaetze, die einen gleichnamigen Ort **ausserhalb** kennzeichnen (EIG255,
#: SEO-Audit 25.09.2026): "Halle (Westf.)" traf bis dahin den Eintrag 'halle'
#: und bekam den Nachlass des Standorts Halle (Saale). Ganze Woerter wie beim
#: Treffer selbst; ``rw_rechner.js`` bekommt dieselbe Liste.
_STANDORT_FREMDE_ZUSAETZE = frozenset({'westfalen', 'westf'})

_OBJEKTART_LABELS = {
    'keller':  'Kellerentrümpelung',
    'wohnung': 'Wohnungsauflösung',
    'haus':    'Haushaltsauflösung',
    'gewerbe': 'Gewerbeentrümpelung',
    'garten':  'Gartenräumung',
    'scheune': 'Scheune / Schuppen räumen',
}

# Kurzform für Buttons und Tabellenzeilen.
_OBJEKTART_LABELS_KURZ = {
    'keller': 'Keller', 'wohnung': 'Wohnung', 'haus': 'Haus',
    'gewerbe': 'Gewerbe', 'garten': 'Garten', 'scheune': 'Scheune',
}

# Nur für die Beispielspalte der Preistabelle (F4). Keine Preislogik – der
# Beispielpreis wird damit durch `berechne_preis()` geschickt, damit er nicht
# von Hand geschätzt wird.
_TYPISCHE_GROESSE = {
    'keller': 15, 'wohnung': 65, 'haus': 140,
    'gewerbe': 200, 'garten': 150, 'scheune': 80,
}

# ISO ist die Quelle, der deutsche Text wird daraus gerechnet - sonst
# stehen zwei Schreibweisen desselben Datums nebeneinander (G12).
_PREISSTAND_ISO = '2026-08'
_PREISSTAND = _stand_deutsch(_PREISSTAND_ISO)


# ── Rechnung ─────────────────────────────────────────────────────────────────

def _round_preis(x):
    """Rundet auf, wie ``Math.round`` im Browser.

    Nicht durch ``round()`` ersetzen: Python rundet .5 auf die gerade Zahl und
    lieferte dadurch bei jeder zwanzigsten Eingabe 1 € weniger, als der Kunde
    im Rechner gesehen hatte.
    """
    return int(math.floor(x + 0.5))


def euro(betrag):
    """1450 → '1.450'. Ohne Währungszeichen, das setzt das Template."""
    return f'{int(betrag):,}'.replace(',', '.')


_UMSCHRIFT = str.maketrans({'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'})


def ort_normalisiert(text):
    """``'Meißen'`` und ``'Meissen'`` -> ``'meissen'``.

    NFC, weil der Browser normalisiert, bevor er prüft – ein 'ö' aus zwei
    Codepoints hätte serverseitig sonst nicht getroffen. Dazu die Umschrift
    der Umlaute, weil Besucher „Koethen" oder „Meissen" tippen (EIG164).
    ``rw_rechner.js::normOrt`` rechnet genau dasselbe.
    """
    t = unicodedata.normalize('NFC', str(text or '')).lower()
    return t.translate(_UMSCHRIFT)


def _woerter(text):
    """Die Wörter eines Ortstextes; jedes Zeichen außer Buchstabe/Ziffer trennt.

    Absichtlich dieselbe Regel wie im Browser (``/[^\\p{L}\\p{N}]+/u``):
    Bindestrich, Klammer, Komma und Leerzeichen trennen, Buchstaben nicht.
    """
    return [w for w in re.split(r'[\W_]+', ort_normalisiert(text)) if w]


def hat_standort_rabatt(stadtort):
    """Erkennt ein Servicegebiet im frei getippten Ortsnamen – als ganzes Wort.

    „04103 Leipzig-Mitte" und „Halle (Saale)" treffen, „Hallesche Straße,
    Bitterfeld" und „Leipziger Str., Grimma" nicht mehr (EIG126).
    **Was sie nicht erkennt:** einen gleichnamigen Ort außerhalb, etwa
    „Halle (Westfalen)" – dafür bräuchte es eine Ortsdatenbank. Die
    häufigste Verwechslung, „Halle (Westf.)", fängt seit dem 25.09.2026
    ``_STANDORT_FREMDE_ZUSAETZE`` ab (EIG255).
    """
    woerter = _woerter(stadtort)
    if not woerter:
        return False
    if any(w in _STANDORT_FREMDE_ZUSAETZE for w in woerter):
        return False
    for eintrag in _STANDORT_RABATT_STAEDTE:
        teile = _woerter(eintrag)
        n = len(teile)
        if any(woerter[i:i + n] == teile for i in range(len(woerter) - n + 1)):
            return True
    return False


def auswahl_text(objektart, stockwerk='eg', aufzug=False, fuellgrad='mittel',
                 sonderabfall='keine', klein_items=(), klein_sonstiges=''):
    """Die gewählten Zuschlagsangaben als ein lesbarer Satzteil (EIG276).

    Nur was ``berechne_preis`` für diese Objektart auch rechnet: Stockwerk
    und Aufzug nur bei Wohnung und Keller, Sonderabfall nur bei den Objekten
    aus ``_SONDERABFALL_OBJEKTE``. Die Beschriftungen kommen aus den Labels
    dieses Moduls, hier steht keine Zahl. Der Freitext der Sonstigen
    Reparaturen erscheint bewusst nur als Hinweis „Sonstiges“: Er ist
    Kundentext, geht in Mail und Telegram-Nachricht und würde die 500 Zeichen
    des Feldes ``groesse_label`` sprengen.
    """
    teile = []
    if objektart in _STOCKWERK_OBJEKTE:
        etage = _STOCKWERK_LABELS.get(stockwerk, stockwerk)
        if stockwerk != 'eg':
            etage += ' mit Aufzug' if aufzug else ' ohne Aufzug'
        teile.append(etage)
    teile.append(f'Füllgrad {_FUELLGRAD_LABELS.get(fuellgrad, fuellgrad)}')
    if objektart in _SONDERABFALL_OBJEKTE:
        teile.append(f'Sonderabfall: {_SONDERABFALL_LABELS.get(sonderabfall, sonderabfall)}')
    reparaturen = [_KLEIN_SAN_ITEMS[i]['label'] for i in klein_items
                   if i in _KLEIN_SAN_ITEMS]
    if str(klein_sonstiges).strip():
        reparaturen.append('Sonstiges')
    if reparaturen:
        teile.append('Reparaturen: ' + ', '.join(reparaturen))
    return ', '.join(teile)


def berechne_preis(objektart, qm, stockwerk='eg', aufzug=False, fuellgrad='mittel',
                   sonderabfall='keine', with_maler=False, klein_items=(),
                   klein_sonstiges='', stadtort=''):
    """Der Festpreis. Einzige Rechnung im Projekt – das JS spiegelt sie nur.

    Gibt ``(preis, details)`` zurück; ``details`` trägt die Aufschlüsselung für
    Anzeige und E-Mail. Reihenfolge der Modifikatoren ist bindend, weil der
    Füllgrad multiplikativ auf die Grundsumme wirkt, die Aufpreise danach aber
    additiv – vertauscht ergäbe das andere Zahlen.
    """
    rates = _PER_QM_PREISE[objektart]
    nach_flaeche = _round_preis(rates['rate'] * qm)
    preis = max(rates['min_preis'], nach_flaeche)

    # Der Rechenweg entsteht HIER, waehrend gerechnet wird - nicht in einer
    # zweiten Funktion, die die Schritte nachbildet. Ein nachgebauter Rechenweg
    # waere die naechste Preisquelle im Projekt und beim ersten Satzwechsel als
    # Erstes falsch (siehe Modulkopf). Er ist reine Anzeige und beeinflusst das
    # Ergebnis nicht.
    schritte = []
    if nach_flaeche >= rates['min_preis']:
        schritte.append({
            'label': f"{_OBJEKTART_LABELS[objektart]}: {rates['rate']} €/m² × {qm} m²",
            'wert': f'{euro(preis)} €'})
    else:
        schritte.append({
            'label': (f"Mindestpreis {_OBJEKTART_LABELS[objektart]} "
                      f"({rates['rate']} €/m² × {qm} m² = {euro(nach_flaeche)} € "
                      f"liegt darunter)"),
            'wert': f'{euro(preis)} €'})

    if objektart in _STOCKWERK_OBJEKTE and not aufzug:
        aufpreis = _STOCKWERK_AUFPREIS.get(stockwerk, 0)
        preis += aufpreis
        if aufpreis:
            schritte.append({
                'label': (f"{_STOCKWERK_LABELS.get(stockwerk, stockwerk)} "
                          f"ohne Aufzug: + {euro(aufpreis)} €"),
                'wert': f'{euro(preis)} €'})

    faktor_fuell = _FUELLGRAD_FAKTOR.get(fuellgrad, 1.20)
    preis = _round_preis(preis * faktor_fuell)
    if faktor_fuell != 1.00:
        schritte.append({
            'label': (f"Füllgrad {_FUELLGRAD_LABELS.get(fuellgrad, fuellgrad)}: "
                      f"× {f'{faktor_fuell:.2f}'.replace('.', ',')}"),
            'wert': f'{euro(preis)} €'})

    if objektart in _SONDERABFALL_OBJEKTE:
        aufpreis = _SONDERABFALL_AUFPREIS.get(sonderabfall, 0)
        preis += aufpreis
        if aufpreis:
            schritte.append({
                'label': (f"Sonderabfall, "
                          f"{_SONDERABFALL_LABELS.get(sonderabfall, sonderabfall)}: "
                          f"+ {euro(aufpreis)} €"),
                'wert': f'{euro(preis)} €'})

    basis = preis

    maler = 0
    if with_maler:
        maler = max(_MALER_PER_QM['min_preis'], _round_preis(_MALER_PER_QM['rate'] * qm))
        preis += maler
        schritte.append({
            'label': f"Malerarbeiten {_MALER_PER_QM['rate']} €/m²: + {euro(maler)} €",
            'wert': f'{euro(preis)} €'})

    klein = 0
    for item_id in klein_items:
        if item_id in _KLEIN_SAN_ITEMS:
            klein += _KLEIN_SAN_ITEMS[item_id]['preis']
    if str(klein_sonstiges).strip():
        klein += _KLEIN_SONSTIGES_AUFPREIS
    preis += klein
    if klein:
        schritte.append({'label': f'Kleinreparaturen: + {euro(klein)} €',
                         'wert': f'{euro(preis)} €'})

    rabatt = hat_standort_rabatt(stadtort)
    faktor = _STANDORT_RABATT_FAKTOR if rabatt else 1.0
    # Der Nachlass endet am Mindestpreis (EIG165, 24.09.2026): Ohne den Deckel
    # kostete ein leichter Keller in Leipzig 285 € - überall steht „ab 300 €“,
    # und die Mindestpauschale war eine ausdrückliche Entscheidung. Greifen
    # kann der Deckel nur ohne Zusatzleistungen (Maler und Kleinreparaturen
    # heben die Summe weit über die Schwelle) - deshalb trägt ``basis`` unten
    # denselben Deckel. ``rw_rechner.js::berechne`` rechnet genauso.
    nach_rabatt = _round_preis(preis * faktor)
    gedeckelt = nach_rabatt < rates['min_preis']
    preis = max(rates['min_preis'], nach_rabatt)
    if rabatt:
        prozent = int(round((1 - _STANDORT_RABATT_FAKTOR) * 100))
        schritte.append({'label': (f'Standort im Servicegebiet: − {prozent} %'
                                   + (', nicht unter den Mindestpreis'
                                      if gedeckelt else '')),
                         'wert': f'{euro(preis)} €'})

    return preis, {
        'basis':           max(rates['min_preis'], _round_preis(basis * faktor)),
        'maler':           _round_preis(maler * faktor),
        'klein':           _round_preis(klein * faktor),
        'standort_rabatt': rabatt,
        # Nur fuer die Anzeige. Der Wizard im Browser liest 'details' nicht, die
        # Bestaetigungsmail nur basis/maler/klein/standort_rabatt - ein
        # zusaetzlicher Schluessel ist deshalb rueckwaertskompatibel.
        'schritte':        schritte,
    }


# ── Anzeige ──────────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=1)
def preis_context():
    """Aufbereitete Preise für jedes Template. Speist den Context-Processor.

    Gecacht, weil der Context-Processor bei *jeder* Antwort läuft und die
    Preise Konstanten sind. Templates lesen das Dict nur.

    Bewusst vorformatiert: Tausenderpunkte im Template zu setzen hieße,
    ``USE_THOUSAND_SEPARATOR`` global umzulegen – das würde auch Zahlen in
    JSON-LD treffen und dort wieder ungültiges JSON erzeugen.
    """
    zeilen = []
    for key, werte in _PER_QM_PREISE.items():
        qm = _TYPISCHE_GROESSE[key]
        beispiel, _ = berechne_preis(key, qm)
        zeilen.append({
            'key':          key,
            'label':        _OBJEKTART_LABELS[key],
            'label_kurz':   _OBJEKTART_LABELS_KURZ[key],
            'min':          werte['min_preis'],
            'min_txt':      euro(werte['min_preis']),
            'ab_txt':       f"ab {euro(werte['min_preis'])} €",
            'rate':         werte['rate'],
            'rate_txt':     f"{werte['rate']} €/m²",
            'qm_typisch':   qm,
            'beispiel':     beispiel,
            'beispiel_txt': f'{euro(beispiel)} €',
        })

    einstieg = min(v['min_preis'] for v in _PER_QM_PREISE.values())

    return {
        'PREISE':        {z['key']: z for z in zeilen},
        'PREISE_LISTE':  zeilen,
        'PREIS_EINSTIEG':     einstieg,
        'PREIS_EINSTIEG_TXT': f'{euro(einstieg)} €',
        'PREISSTAND':     _PREISSTAND,
        'PREISSTAND_ISO': _PREISSTAND_ISO,
        'PREIS_MODIFIKATOREN': {
            'fuellgrad':    _FUELLGRAD_FAKTOR,
            'stockwerk':    _STOCKWERK_AUFPREIS,
            'sonderabfall': _SONDERABFALL_AUFPREIS,
            'maler_rate':   _MALER_PER_QM['rate'],
            'maler_min':    _MALER_PER_QM['min_preis'],
            'rabatt_prozent': int(round((1 - _STANDORT_RABATT_FAKTOR) * 100)),
        },
        # Aufbereitet fuer die Modifikatoren-Tabelle auf /entruempelung-kosten/
        # (A12). Dieselben Zahlen wie oben, nur mit ihrer Beschriftung - damit
        # das Template keine Faktoren beschriften muss und dabei drueber kommt.
        'PREIS_MOD_LISTE': {
            'fuellgrad': [
                {'key': k, 'label': _FUELLGRAD_LABELS[k], 'faktor': v,
                 'faktor_txt': f'{v:.2f}'.replace('.', ',')}
                for k, v in _FUELLGRAD_FAKTOR.items()],
            'stockwerk': [
                {'key': k, 'label': _STOCKWERK_LABELS[k], 'aufpreis': v,
                 'aufpreis_txt': f'{euro(v)} €' if v else 'entfällt'}
                for k, v in _STOCKWERK_AUFPREIS.items()],
            'sonderabfall': [
                {'key': k, 'label': _SONDERABFALL_LABELS[k], 'aufpreis': v,
                 'aufpreis_txt': f'{euro(v)} €' if v else 'entfällt'}
                for k, v in _SONDERABFALL_AUFPREIS.items()],
        },
        # Preise der Sanierungs-/Renovierungsleistung (A11). Sie stehen NICHT in
        # PREISE_LISTE, weil das die Entruempelungs-Objektarten sind - eine
        # gemeinsame Tabelle haette zwei Preislogiken in einer Spalte gemischt.
        'PREIS_SANIERUNG': {
            'maler_rate':    _MALER_PER_QM['rate'],
            'maler_min':     _MALER_PER_QM['min_preis'],
            'maler_min_txt': euro(_MALER_PER_QM['min_preis']),
            'items': [{'id': k, 'label': v['label'], 'preis': v['preis'],
                       'preis_txt': euro(v['preis'])}
                      for k, v in _KLEIN_SAN_ITEMS.items()],
            'sonstiges':     _KLEIN_SONSTIGES_AUFPREIS,
            'sonstiges_txt': euro(_KLEIN_SONSTIGES_AUFPREIS),
        },
    }


def js_konstanten():
    """Genau die Werte, die der Wizard im Browser zum Rechnen braucht.

    Wird als ``application/json`` in die Seite geschrieben, nicht als
    JS-Literal – so kann keine Zahl beim Kopieren zwischen den Sprachen
    verloren gehen, und die Doppelrechnung (die bleiben muss, weil der Server
    dem Client-Preis nicht trauen darf) kann nicht mehr auseinanderlaufen.

    Beschriftungen, die reine Optik sind (SVG-Icons, Füllgrad-Umschreibungen),
    bleiben absichtlich im Template.
    """
    return {
        'perQm': {k: {'rate': v['rate'], 'minPreis': v['min_preis']}
                  for k, v in _PER_QM_PREISE.items()},
        'maler': {'rate': _MALER_PER_QM['rate'], 'minPreis': _MALER_PER_QM['min_preis']},
        'stockwerk':      _STOCKWERK_AUFPREIS,
        'fuellgrad':      _FUELLGRAD_FAKTOR,
        'sonderabfall':   _SONDERABFALL_AUFPREIS,
        'kleinItems':     [{'id': k, 'preis': v['preis'], 'label': v['label']}
                           for k, v in _KLEIN_SAN_ITEMS.items()],
        'kleinSonstiges': _KLEIN_SONSTIGES_AUFPREIS,
        'stockwerkObjekte':    sorted(_STOCKWERK_OBJEKTE),
        'sonderabfallObjekte': sorted(_SONDERABFALL_OBJEKTE),
        'objektartLabels':     _OBJEKTART_LABELS_KURZ,
        'standortStaedte':     sorted(_STANDORT_RABATT_STAEDTE),
        'standortFremd':       sorted(_STANDORT_FREMDE_ZUSAETZE),
        'standortFaktor':      _STANDORT_RABATT_FAKTOR,
    }
