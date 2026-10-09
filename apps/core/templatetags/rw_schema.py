# -*- coding: utf-8 -*-
"""``{% json_ld obj %}`` — der einzige Weg, JSON-LD auszugeben (F5).

Serialisiert mit ``json.dumps``. Damit ist das Dezimalkomma-Problem strukturell
erledigt: Floats bekommen immer einen Punkt, unabhaengig von ``LANGUAGE_CODE``.
``|unlocalize`` wird fuer strukturierte Daten nicht mehr gebraucht.

``</script>`` wird escaped - sonst koennte ein Text aus dem CMS (Block 4) den
Script-Block vorzeitig schliessen und den Rest der Seite als Markup ausliefern.
"""
import json

from django import template
from django.utils.safestring import mark_safe
from django.utils.text import slugify

register = template.Library()


_CONTEXT = 'https://schema.org'


def _knoten(obj):
    """Bloecke flach einsammeln - Listen in Listen kommen vor."""
    if not obj:
        return []
    if not isinstance(obj, (list, tuple)):
        obj = [obj]
    aus = []
    for block in obj:
        if not block:
            continue
        if isinstance(block, (list, tuple)):
            aus += _knoten(block)
        else:
            aus.append(block)
    return aus


def graph_dokument(obj):
    """Ein einziges JSON-LD-Dokument je Seite: ``@context`` + ``@graph`` (G1).

    Vorher gab jeder Block sein eigenes ``<script>`` aus - auf den Stadt- und
    Leistungsseiten waren das vier. **Google loest ``@id``-Referenzen ueber
    getrennte Bloecke hinweg nicht auf.** Das hat die drei ``JobPosting``-Bloecke
    aus den Rich Results geworfen, obwohl jeder fuer sich gueltiges JSON war:
    ``hiringOrganization`` war nur eine ``@id``, und der zugehoerige Knoten stand
    im Nachbarblock. Innerhalb eines ``@graph`` findet Google ihn.

    ``@context`` gehoert genau einmal an die Spitze des Dokuments. Die Bausteine
    in ``schema.py`` setzen es weiterhin selbst - sie bleiben dadurch einzeln
    verwendbar und testbar -, hier wird es abgeraeumt.
    """
    knoten = _knoten(obj)
    if not knoten:
        return None
    ohne_context = [
        {s: w for s, w in k.items() if s != '@context'} if isinstance(k, dict)
        else k
        for k in knoten
    ]
    return {'@context': _CONTEXT, '@graph': ohne_context}


@register.simple_tag
def json_ld(obj):
    """Der einzige Weg, JSON-LD auszugeben (F5) - seit G1 **ein** Block je Aufruf.

    Wer diesen Tag ein zweites Mal auf derselben Seite aufruft, macht G1
    rueckgaengig. ``check_seo`` schlaegt deshalb an, sobald eine Seite mehr als
    einen ``ld+json``-Block ausliefert.
    """
    dokument = graph_dokument(obj)
    if not dokument:
        return ''
    text = json.dumps(dokument, ensure_ascii=False, separators=(',', ':'))
    # Der Ersatz ist die JSON-Schreibweise <\/ – der Backslash muss deshalb
    # im Python-String maskiert werden. Mit '<\/' meinte Python dasselbe,
    # warnte aber bei jedem Start (`SyntaxWarning: invalid escape sequence`)
    # und wird ab einer kuenftigen Version einen Fehler daraus machen.
    text = text.replace('</', '<\\/')
    # ``<!--`` schaltet den HTML-Parser im Skriptinhalt in einen Zustand, in dem
    # ein späteres ``<script`` das Ende verschiebt. ``!`` ist in JSON
    # dasselbe Ausrufezeichen, im HTML aber kein Kommentaranfang mehr.
    text = text.replace('<!--', '<\\u0021--')
    # audit-ok K18: ``text`` ist json.dumps-Ausgabe (Anführungszeichen maskiert),
    # ``</`` und ``<!--`` sind oben entschärft - aus dem Skriptblock kommt nichts heraus.
    return mark_safe('<script type="application/ld+json">%s</script>' % text)


_UMLAUTE = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
            'Ä': 'ae', 'Ö': 'oe', 'Ü': 'ue'}


@register.filter
def faq_anker(frage):
    """Stabiler Fragment-Anker fuer eine FAQ-Antwort (G4).

    ``'Was kostet eine Haushaltsaufloesung?'`` ->
    ``'faq-was-kostet-eine-haushaltsaufloesung'``. Damit laesst sich **eine
    Antwort** verlinken statt nur die Seite - das ist der Punkt: Eine
    Antwortmaschine, die eine Passage zitiert, kann auf genau sie zeigen.

    Umlaute werden ausgeschrieben, nicht weggeworfen. ``slugify`` macht aus
    "Haushaltsaufloesung" sonst "haushaltsauflosung" - ein Anker, den niemand
    von Hand tippt und der beim Lesen wie ein Tippfehler aussieht.

    **Der Anker haengt am Fragetext.** Wird eine Frage umformuliert, aendert
    sich der Anker; ein alter Link zeigt dann auf die Seite statt auf die
    Antwort. Das ist der Preis dafuer, keine zweite Liste von Ankern pflegen zu
    muessen - und die kleinere Gefahr, denn eine gepflegte Ankerliste laeuft
    irgendwann gegen die Fragen (Regel 12).

    Doppelte ``id`` faengt ``check_seo`` ab: Es prueft jede Seite auf doppelte
    Sprungziele, weil das in diesem Projekt schon zweimal live gegangen ist.
    """
    text = slugify(''.join(_UMLAUTE.get(z, z) for z in (frage or '')))
    if len(text) > 60:
        # An der Wortgrenze kuerzen, nicht mitten im Wort: Ein Anker wie
        # '…-kellerentruempelun' sieht aus wie ein Fehler und laedt dazu ein,
        # ihn "zu korrigieren".
        text = text[:60].rsplit('-', 1)[0]
    return 'faq-%s' % (text or 'frage')


@register.filter
def kritisch(name):
    """Kandidatenliste fuer das Inline-CSS: erst die Seite, dann der Rueckfall.

    ``{% include %}`` waehlt aus einer Liste die erste Vorlage, die es gibt.
    Vorher stand dort ein einzelner Name - und eine Seite, deren Block noch
    nicht erzeugt war, endete mit ``TemplateDoesNotExist`` als **500**, obwohl
    genau fuer diesen Fall ein gemeinsamer Block existiert. Aufgefallen beim
    Anlegen der ersten Leistungsseite (A3): ``build_critical_css`` laeuft im
    Deploy bewusst weich (``|| echo``), sein Ausfall haette die neue Seite also
    komplett unerreichbar gemacht statt nur groesser.
    """
    return ('components/critical/%s' % name, 'components/rw_critical_css.html')


@register.simple_tag(takes_context=True)
def rw_head_schema(context):
    """**Die einzige Stelle, an der eine Seite JSON-LD ausgibt** (G1).

    Als Tag und nicht als Context-Processor, weil ``seo_path`` und
    ``seo_breadcrumb_name`` Argumente eines ``{% include ... with %}`` sind -
    ein Context-Processor sieht die nicht.

    Seit G1 sammelt der Tag **auch** ``schema_bloecke`` aus dem View-Context
    ein. Vorher gaben die Seitenvorlagen die selbst aus (``{% json_ld
    schema_bloecke %}``, in acht Templates) - dadurch standen zwangslaeufig
    mindestens zwei ``<script>``-Bloecke auf der Seite, und genau das ist die
    Ursache, die G1 behebt. Die Zeile ist aus allen acht Vorlagen entfernt;
    wer sie wieder einbaut, macht die Aufgabe rueckgaengig.

    ``{% include %}`` ohne ``only`` reicht den View-Context durch, der Tag
    sieht ``schema_bloecke`` also auch aus ``rw_seo.html`` heraus.
    """
    from apps.core import schema as S
    from apps.core.data import _CITY_DATA

    site_url = context.get('SITE_URL', '')
    pfad = context.get('seo_path', '')
    bloecke = []

    # WebSite und LocalBusiness stehen seit G1 im Graph **jeder** Seite, nicht
    # mehr nur auf der Startseite. Das ist der eigentliche Zweck der Aufgabe:
    # Die halbe Website verweist per '@id' auf '…/#business' - 'provider' der
    # Leistungsseiten, 'hiringOrganization' der Stellenanzeigen,
    # 'parentOrganization' der 54 Stadtseiten, 'about'/'isPartOf' des Hubs.
    # Solange der Knoten nur auf '/' stand, lief **jede** dieser Referenzen ins
    # Leere, und die Bausteine mussten Name und Adresse ein zweites Mal
    # mitschleppen, damit Google ueberhaupt etwas sah.
    #
    # Was auf der Startseite bleibt: 'areaServed' mit den 20 Staedten - das ist
    # der groesste Teil des Knotens und fuer die '@id'-Aufloesung ohne Belang.
    startseite = pfad == '/'
    staedte = ([c['name'] for slug, c in _CITY_DATA.items()
                if not c.get('randgebiet')][:20] if startseite else ())
    bloecke.append(S.website_schema(site_url))
    bloecke.append(S.business_schema(site_url, context.get('CONTACT_EMAIL', ''),
                                     staedte=staedte))

    name = context.get('seo_breadcrumb_name')
    if name:
        # Zwischenstufen als "Name|/pfad/", mehrere durch ";" getrennt.
        # Ein echtes Listenargument gaebe es hier nicht: seo_breadcrumb_name
        # kommt aus einem {% include ... with x="..." %} und ist immer ein
        # String. Gebraucht wird das von den Stellenseiten, deren sichtbarer
        # Brotkrumen drei Stufen zeigt - das Schema nannte bis A16 nur zwei.
        roh = context.get('seo_breadcrumb_zwischen') or ''
        zwischen = [tuple(teil.split('|', 1)) for teil in roh.split(';')
                    if '|' in teil]
        bloecke.append(S.breadcrumb_schema(site_url, name, pfad,
                                           zwischen=zwischen or None))

    # Zuletzt die seitenspezifischen Bloecke aus der View - Service, FAQPage,
    # HowTo, JobPosting. Reihenfolge im Graph: erst die Entitaet (WebSite,
    # LocalBusiness), dann die Navigation, dann der Seiteninhalt.
    bloecke += _knoten(context.get('schema_bloecke'))

    # GE17 (19.09.2026): Die Frage ueber dem Antwort-zuerst-Block ist sichtbar -
    # also auch ausgezeichnet, mit demselben Text aus derselben Kontextvariable,
    # die rw_antwort.html rendert (Regel 12). Betrifft die Seiten, deren View
    # den Block ueber ``_antwort_ctx`` fuellt (ueber-uns, standorte, aktuelles,
    # galerie, jobs, kooperationspartner, drei Stellenseiten). Seiten mit
    # eigener FAQPage behalten sie unveraendert: Dort gleicht check_seo (G14)
    # das Schema gegen die sichtbaren <summary>-Fragen ab, eine zusaetzliche
    # Frage stuende also "im Schema, aber nicht sichtbar" in der Meldung.
    frage, antwort = context.get('antwort_frage'), context.get('antwort_text')
    if not (frage and antwort):
        # /anfrage/ und /preisangebot/ haben keinen Antwortblock, aber eine
        # sichtbare Frage mit Antwortsatz direkt darunter (Nachbesserung GE17,
        # 19.09.2026). Das Paar steht in data/antworten.py; der Pfad waehlt es
        # hier statt in der View aus, weil beide Views in einer anderen Zone
        # von views.py liegen (24.09.2026). AntwortblockFaqTests haelt den
        # Wortlaut gegen den sichtbaren Text.
        from apps.core.data.antworten import FORMULAR_FAQ
        paar = FORMULAR_FAQ.get(pfad)
        if paar:
            frage, antwort = paar()
    if frage and antwort and not any(
            isinstance(k, dict) and 'FAQPage' in (
                k.get('@type') if isinstance(k.get('@type'), list) else [k.get('@type')])
            for k in bloecke):
        bloecke.append(S.faq_schema([(frage, antwort)]))

    # Der Knoten fuer die Seite selbst (G9). Er traegt 'speakable' und loest
    # 'isPartOf' auf die WebSite auf. 'seo_speakable' ist eine kommagetrennte
    # Selektorliste und kommt aus dem {% include 'components/rw_seo.html'
    # with ... %} der jeweiligen Vorlage - genau wie seo_title. Vorlagen ohne
    # vorlesbare Kernaussage (Impressum, AGB, Formulare, Galerie) lassen sie
    # weg; check_seo prueft beide Richtungen, siehe dort.
    #
    # Gebaut wird er ZULETZT und dann nach vorn gestellt: Ob die Seite einen
    # Brotkrumen hat, steht erst fest, wenn alle Bloecke beisammen sind. Die
    # Stadt- und Leistungsseiten bauen ihn naemlich in der View und reichen
    # ihn ueber 'schema_bloecke' herein, nicht ueber 'seo_breadcrumb_name' -
    # ein 'mit_breadcrumb=bool(name)' haette 69 Seiten die Verknuepfung
    # gekostet und dabei ausgesehen, als stimme alles.
    hat_brotkrumen = any(
        isinstance(k, dict) and 'BreadcrumbList' in (
            k.get('@type') if isinstance(k.get('@type'), list) else [k.get('@type')])
        for k in _knoten(bloecke))
    selektoren = [s.strip() for s in (context.get('seo_speakable') or '').split(',')
                  if s.strip()]
    # 'dateModified' (D2). Der Seitentyp wird aus 'pfad' abgeleitet - nach
    # demselben Muster wie 'startseite = pfad == "/"' weiter oben, denn mehr
    # als den Pfad weiss dieser Tag ueber die Seite nicht: seo_title und
    # seo_path sind Argumente eines {% include %}, es gibt keinen View-Kontext,
    # aus dem sich "das ist eine Stadtseite" ablesen liesse.
    #
    # Die Zuordnung steht bewusst NICHT hier, sondern in
    # apps/core/sitemaps.py::lastmod_fuer_pfad - dieselbe Funktion, die auch
    # das lastmod der Sitemap bestimmt. Eine zweite Fallunterscheidung an
    # dieser Stelle waere die naechste Liste, die auseinanderlaeuft (Regel 12);
    # der Fehler faellt nicht auf, weil beide Daten plausibel aussehen.
    #
    # Der Import steht in der Funktion, nicht oben: templatetags werden beim
    # Start eingelesen, sitemaps.py zieht Models nach - das ist genau die Sorte
    # Kette, aus der ein Zirkel wird (Regel 4, eine Ebene hoeher).
    from apps.core.sitemaps import lastmod_fuer_pfad
    geaendert = lastmod_fuer_pfad(pfad) if pfad else None
    seite = S.webpage_schema(
        site_url, pfad,
        context.get('seo_title') or '',
        context.get('seo_description'),
        speakable=selektoren,
        mit_breadcrumb=hat_brotkrumen,
        geaendert=geaendert,
    )
    # Reihenfolge im Graph: Entitaet (WebSite, LocalBusiness), dann die Seite,
    # dann Navigation und Seiteninhalt.
    bloecke.insert(2, seite)
    return json_ld(_mit_kennung(_knoten(bloecke), site_url, pfad))


def _mit_kennung(knoten, site_url, pfad):
    """Jedem Knoten der obersten Ebene eine stabile ``@id`` geben (GE07).

    Die Messung vom 15.09.2026 fand im Schnitt 76 % der Knoten mit ``@id`` -
    ohne Kennung ist ein Knoten fuer eine Maschine bei jedem Abruf ein neues,
    unbekanntes Ding, auf das nichts verweisen kann. Betroffen waren vor allem
    ``FAQPage`` und ``HowTo``, deren Bausteine die Seite nicht kennen.

    Die Kennung ist ``<Seite>#<typ>``, bei Wiederholung mit laufender Nummer -
    abgeleitet aus Pfad und Typ, also bei jedem Abruf dieselbe. Knoten, die
    ihre ``@id`` selbst setzen, bleiben unberuehrt; die Kopie verhindert, dass
    ein gecachter Baustein veraendert wird.
    """
    vergeben = {k.get('@id') for k in knoten if isinstance(k, dict)}
    aus = []
    for k in knoten:
        if isinstance(k, dict) and not k.get('@id') and k.get('@type'):
            typ = k['@type'][0] if isinstance(k['@type'], list) else k['@type']
            basis = f'{site_url}{pfad}#{str(typ).lower()}'
            kennung, n = basis, 1
            while kennung in vergeben:
                n += 1
                kennung = f'{basis}-{n}'
            vergeben.add(kennung)
            k = dict(k, **{'@id': kennung})
        aus.append(k)
    return aus
