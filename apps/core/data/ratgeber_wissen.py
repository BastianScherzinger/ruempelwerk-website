# -*- coding: utf-8 -*-
"""Achtzehn Wissensseiten zu Entsorgung, Nachlass und Raeumung (SU07, 02.10.2026).

Die achtzehnte (``halteverbot-entruempelung-beantragen``) kam am 02.10.2026
nachmittags dazu, weil drei neue Matrixseiten das Verhaeltnis wieder unter
eins zu drei gedrueckt hatten.

**Warum es dieses Modul gibt.** Die Messung vom 01.10.2026 zaehlte acht
Wissensseiten auf 73 Verkaufsseiten (Ziel: eine je drei, ``SU07``). Diese
Artikel stuetzen sich ausschliesslich auf Gesetzestexte und amtliche Seiten, die
am 01.10.2026 abgerufen und von einem zweiten Pruefer gegen die Quelle gelesen
wurden; jede Fundstelle steht am Ende ihres Abschnitts (``quellen.py``).

**Format wie in ``ratgeber.py``** (dort die Pflichtfelder), mit zwei
Besonderheiten: ``kategorie`` ist eine der drei neuen Gruppen aus
``ratgeber.KATEGORIEN``, und ``stand_iso`` setzt den Rechtsstand dieses Artikels
(``{stand}``), unabhaengig vom Stand der aelteren Artikel.

**Was hier nicht steht:** Aussagen ueber die Firma jenseits dessen, was die
Website ohnehin sagt (raeumt, trennt nach Fraktionen, Entsorgungsnachweis auf
Wunsch, Festpreis bei der Besichtigung, Fundstuecke bei Nachlass werden
gesichert). Keine Zulassung, keine Erfahrung, keine Reaktionszeit, kein Preis
ausser ueber die Platzhalter. Einzelfaelle verweisen auf Gericht, Behoerde oder
Rechtsberatung.

Regel 4: Das Modul importiert nichts.
"""

WISSEN = {
    'altholz-moebel-entsorgen': {
        'stand_iso': '2026-10',
        'kategorie': 'Entsorgung und Schadstoffe',
        'titel': 'Altholz und Möbel entsorgen',
        'h1': 'Altholz: Möbel und Holzreste richtig einordnen',
        'h1_em': 'Was A I bis A IV bedeuten und warum Lack den Unterschied macht',
        'teaser': (
            'Nicht jedes alte Holz ist gleich: Die Altholzverordnung teilt es '
            'nach Belastung in vier Kategorien. Was das für Schrank, Gartenzaun '
            'und Holzreste bedeutet und wie die Abgabe am Wertstoffhof läuft.'
        ),
        'seo_title': 'Altholz entsorgen: 4 Kategorien, A I bis A IV | Rümpelwerk',
        'seo_description': (
            'Was Altholz ist, warum lackierte Möbel anders gelten als '
            'naturbelassenes Holz und was A IV bedeutet. Mit Beispiel '
            'vom Wertstoffhof Leipzig. Jetzt lesen.'
        ),
        'seo_keywords': ('altholz entsorgen, altholzkategorien a1 a2 a3 a4, '
                         'altholzverordnung möbel, lackiertes holz entsorgen, '
                         'imprägniertes holz entsorgen, altholz wertstoffhof'),

        'answer_frage': 'Was bedeutet Altholz bei Möbeln und Holzresten?',
        'answer': (
            'Altholz bezeichnet gebrauchte Holzerzeugnisse und Holzreste, '
            'die Abfall sind. Die Altholzverordnung teilt sie nach Belastung '
            'in A I (naturbelassen) bis A IV (mit Holzschutzmitteln '
            'behandelt). Lackierte oder beschichtete Möbel fallen in A II '
            'oder A III, imprägniertes Holz in A IV. Was der Wertstoffhof '
            'annimmt, regelt der örtliche Entsorger. Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'altholzv-1', 'abschnitt': 'begriff',
             'bezug': 'Die Verordnung gilt für Erzeuger und Besitzer von '
                      'Altholz'},
            {'schluessel': 'altholzv-2', 'abschnitt': 'begriff',
             'bezug': 'Definition von Altholz und Gebrauchtholz sowie der '
                      'vier Altholzkategorien'},
            {'schluessel': 'altholzv-2', 'abschnitt': 'kategorien',
             'bezug': 'Wortlaut der Kategorien A I bis A IV und der '
                      'Holzschutzmittel-Definition'},
            {'schluessel': 'altholzv-anhang-3', 'abschnitt': 'moebel',
             'bezug': 'Regelzuordnung gängiger Sortimente, darunter Möbel, '
                      'imprägnierte Gartenmöbel und imprägnierte Bauhölzer'},
            {'schluessel': 'altholzv-5', 'abschnitt': 'moebel',
             'bezug': 'Regelvermutung nach Anhang III und Einstufung in '
                      'die höhere Kategorie bei Zweifeln'},
            {'schluessel': 'altholzv-3', 'abschnitt': 'trennen',
             'bezug': 'Bei Gemischen richtet sich die Verwertung nach der '
                      'höchsten Altholzkategorie'},
            {'schluessel': 'altholzv-10', 'abschnitt': 'trennen',
             'bezug': 'Pflicht zur getrennten Erfassung ab einer '
                      'Mengenschwelle'},
            {'schluessel': 'uba-altholz', 'abschnitt': 'kategorien',
             'bezug': 'Einordnung der Kategorien durch das Umweltbundesamt '
                      'und Zulassung von A I und A II für Holzwerkstoffe'},
            {'schluessel': 'leipzig-altholz', 'abschnitt': 'wertstoffhof',
             'bezug': 'Annahmebedingungen für unbehandeltes und behandeltes '
                      'Holz auf den Wertstoffhöfen der Stadtreinigung Leipzig'},
        ],

        'abschnitte': [
            {
                'id': 'begriff',
                'titel': 'Was „Altholz“ rechtlich ist',
                'absaetze': [
                    'Im Sprachgebrauch ist Altholz einfach altes Holz. '
                    'Die Altholzverordnung (AltholzV) definiert es enger: '
                    'Altholz ist Industrierestholz und Gebrauchtholz, „soweit '
                    'diese Abfall im Sinne des § 3 Absatz 1 des '
                    'Kreislaufwirtschaftsgesetzes sind“ (§2 Nummer 1 '
                    'AltholzV). Gebrauchtholz sind gebrauchte Erzeugnisse aus '
                    'Massivholz, Holzwerkstoffen oder Verbundstoffen mit '
                    'überwiegendem Holzanteil – also mehr als 50 '
                    'Masseprozent (Nummer 3).',
                    'Für Sie heißt das: Ein Schrank, den Sie weiterverschenken '
                    'oder verkaufen, ist kein Altholz. Erst wenn er Abfall '
                    'wird, also entsorgt werden soll, greift die Verordnung. '
                    'Sie gilt dann auch für Sie als Erzeuger oder Besitzer '
                    'von Altholz (§1 Absatz 2 AltholzV).',
                ],
            },
            {
                'id': 'kategorien',
                'titel': 'Die vier Kategorien nach Belastung',
                'absaetze': [
                    'Entscheidend ist, womit das Holz behandelt wurde. '
                    '§2 Nummer 4 AltholzV unterscheidet vier Kategorien; '
                    'das Umweltbundesamt beschreibt sie als Einteilung nach '
                    'der Belastung mit Schadstoffen:',
                ],
                'liste': [
                    '<strong>A I:</strong> naturbelassenes oder nur '
                    'mechanisch bearbeitetes Holz, das nicht mehr als '
                    'unerheblich mit holzfremden Stoffen verunreinigt wurde.',
                    '<strong>A II:</strong> verleimtes, gestrichenes, '
                    'beschichtetes, lackiertes oder anders behandeltes Holz '
                    'ohne halogenorganische Verbindungen in der Beschichtung '
                    'und ohne Holzschutzmittel.',
                    '<strong>A III:</strong> Holz mit halogenorganischen '
                    'Verbindungen in der Beschichtung, aber ohne '
                    'Holzschutzmittel.',
                    '<strong>A IV:</strong> mit Holzschutzmitteln behandeltes '
                    'Holz, genannt werden Bahnschwellen, Leitungsmasten, '
                    'Hopfenstangen und Rebpfähle, sowie sonstiges Holz, das '
                    'wegen seiner Schadstoffbelastung nicht in A I bis A III '
                    'passt.',
                ],
                'absaetze': [
                    'Daneben gibt es PCB-Altholz, etwa Dämm- und '
                    'Schallschutzplatten mit PCB-haltigen Mitteln; es wird '
                    'nach der PCB/PCT-Abfallverordnung entsorgt und gehört '
                    'nicht zu A IV. Als Holzschutzmittel zählt die '
                    'Verordnung Stoffe mit biozider Wirkung gegen Holz '
                    'zerstörende Insekten oder Pilze sowie Holz verfärbende '
                    'Pilze, ferner Stoffe zur Herabsetzung der '
                    'Entflammbarkeit.',
                ],
            },
            {
                'id': 'moebel',
                'titel': 'Möbel: warum Lack und Beschichtung zählen',
                'absaetze': [
                    'Anhang III der Verordnung ordnet gängige Sortimente im '
                    'Regelfall zu. Bei Möbeln steht dort: naturbelassenes '
                    'Vollholz A I, Möbel ohne halogenorganische Verbindungen '
                    'in der Beschichtung A II, mit solchen Verbindungen '
                    'A III. Ein lackierter Esstisch, dessen Beschichtung keine '
                    'halogenorganischen Verbindungen enthält, ist danach A II, '
                    'kein A I – er gilt also nicht als naturbelassenes Holz. '
                    'Imprägnierte Gartenmöbel nennt Anhang III dagegen unter '
                    'A IV, ebenso imprägnierte Bauhölzer aus dem '
                    'Außenbereich. Für gemischtes Altholz aus dem Sperrmüll '
                    'sieht Anhang III im Regelfall A III vor.',
                    'Diese Zuordnung ist eine Regelvermutung für die Betreiber '
                    'von Altholzanlagen (§5 Absatz 1 AltholzV). Sie sortieren '
                    'nach Sichtkontrolle; lässt sich Altholz nicht eindeutig '
                    'zuordnen, ist es in die höhere Kategorie einzustufen. '
                    'Wer selbst nicht erkennen kann, ob eine Beschichtung '
                    'halogenorganische Verbindungen enthält oder ein Holz '
                    'imprägniert wurde, sollte das Stück deshalb nicht in '
                    'die „unbehandelt“-Mulde legen, sondern den Entsorger '
                    'fragen.',
                    'Warum das wichtig ist, zeigt das Umweltbundesamt: Für '
                    'die Herstellung von Holzwerkstoffen sind Althölzer der '
                    'Kategorien A I und A II zugelassen, A III nur dann, wenn '
                    'Lack und Beschichtung weitgehend entfernt wurden. '
                    'Je höher die Kategorie, desto enger ist der Verwertungsweg.',
                ],
            },
            {
                'id': 'trennen',
                'titel': 'Getrennt halten beim Räumen',
                'absaetze': [
                    'Für Gemische gilt der strengere Maßstab: Bei einem '
                    'Gemisch unterschiedlicher Kategorien richten sich die '
                    'Anforderungen nach der jeweils höchsten Kategorie '
                    '(§3 Absatz 3 AltholzV). Wirft man imprägnierte Gartenzaunlatten '
                    'zu lackierten Schränken, gelten für das Gemisch '
                    'also die Anforderungen der Kategorie A IV.',
                    'Die Pflicht zur getrennten Erfassung an der Anfallstelle '
                    'nennt §10 AltholzV '
                    'für Altholz, das in Mengen von insgesamt mehr als einem '
                    'Kubikmeter loses Schüttvolumen oder 0,3 Tonnen pro Tag '
                    'anfällt, außerdem für PCB-Altholz sowie kyanisiertes '
                    'oder mit Teeröl behandeltes Altholz – jeweils soweit '
                    'dies zur Erfüllung der Anforderungen nach den §§3, 8 '
                    'und 9 erforderlich ist. Bei der Arbeit in <a href="/haushaltsaufloesung/">'
                    'Haushaltsauflösungen</a> trennt Rümpelwerk '
                    'Mitteldeutschland deshalb nach Fraktionen.',
                    'Praktisch: Naturbelassene Holzreste, lackierte Möbel '
                    'und imprägniertes Außenholz in drei getrennten '
                    'Bereichen sammeln, Stücke mit Zweifel zur höheren '
                    'Gruppe legen, Altholz nicht selbst verbrennen. Wer bei Sperrgut '
                    'unsicher ist, findet Hinweise unter '
                    '<a href="/sperrmuell-entsorgung/">Sperrmüll '
                    'entsorgen</a>.',
                ],
            },
            {
                'id': 'wertstoffhof',
                'titel': 'Am Wertstoffhof: Beispiel Leipzig',
                'absaetze': [
                    'Was angenommen wird, legt der örtliche Entsorger fest. '
                    'Als Beispiel das Merkblatt der Stadt Leipzig zum Umgang '
                    'mit Altholz (Stand 04.2022, vor einem Besuch '
                    'aktuelle Angaben prüfen): Sperrmüll ohne gefährliche '
                    'Stoffe, auch Möbel, kann auf den Wertstoffhöfen der '
                    'Stadtreinigung Leipzig abgegeben werden. Unbehandeltes '
                    'Holz nehmen die Höfe in haushaltsüblichen Mengen bis '
                    'einen Kubikmeter an.',
                    'Behandeltes Holz – die Stadt nennt Verlegeplatten, '
                    'Zäune, lackiertes Holz und OSB-Platten – wird laut '
                    'Merkblatt in haushaltsüblicher Menge von höchstens '
                    '0,5 Kubikmetern auf dem Wertstoffhof Geithainer '
                    'Straße 13 angenommen; größere Mengen sind über private '
                    'Entsorgungsfirmen zu entsorgen. An den Höfen ist ein '
                    'Nachweis der Leipziger Meldeadresse erforderlich. '
                    'Andere Entsorger können andere Mengen und Regeln haben – '
                    'fragen Sie beim Entsorger Ihrer Kommune nach.',
                    'Das Verbrennen von Altholz, auch von Möbeln, ist laut '
                    'Merkblatt grundsätzlich untersagt.',
                ],
            },
        ],

        'faq': [
            ('Ist lackierte Spanplatte Sondermüll?',
             'Nach der Altholzverordnung nicht automatisch: Lackiertes oder '
             'beschichtetes Holz ohne halogenorganische Verbindungen und '
             'ohne Holzschutzmittel gehört zu A II, mit halogenorganischen '
             'Verbindungen in der Beschichtung zu A III. Als A IV, also '
             'belastet, gelten Hölzer mit Holzschutzmitteln. Ob ein Stück '
             'als gefährlicher Abfall einzustufen ist, hängt von seiner '
             'Kategorie ab; das Leipziger Merkblatt unterscheidet '
             'nicht gefährliches Altholz (A I bis A III) von gefährlichem '
             '(A IV und PCB-Altholz).'),
            ('Wie erkenne ich imprägniertes Holz?',
             'Die Verordnung nennt als typische A-IV-Beispiele '
             'Bahnschwellen, Leitungsmasten, Hopfenstangen und Rebpfähle; '
             'nach Anhang III gehören auch imprägnierte Gartenmöbel und '
             'imprägnierte Bauhölzer aus dem Außenbereich dazu. Wenn Sie unsicher sind, '
             'behandeln Sie das Stück wie A IV und fragen den Entsorger.'),
            ('Darf ich altes Holz im Ofen oder Garten verbrennen?',
             'Die Stadt Leipzig weist in ihrem Merkblatt darauf hin, dass '
             'die Verbrennung von Altholz grundsätzlich untersagt ist. '
             'Für Ihren Wohnort gelten die dortigen Regeln; die '
             'Abfallbehörde Ihrer Kommune gibt Auskunft.'),
            ('Gilt das auch für Holzreste aus einem Betrieb?',
             'Ja, die Verordnung gilt für Erzeuger und Besitzer von '
             'Altholz, ebenso für Industrierestholz aus der Holzbe- und '
             '-verarbeitung. Für gewerbliche Abfälle gilt zusätzlich die '
             'Gewerbeabfallverordnung – siehe '
             '<a href="/ratgeber/gewerbeabfall-bei-geschaeftsaufloesung/">'
             'Gewerbeabfall bei der Geschäftsauflösung</a>.'),
        ],

        'leistungen': ['sperrmuell-entsorgung', 'haushaltsaufloesung'],
        'staedte': ['leipzig'],
    },

    'altkleider-textilien-entsorgen': {
        'stand_iso': '2026-10',
        'kategorie': 'Vorbereitung und Übergabe',
        'titel': 'Altkleider und Textilien',
        'h1': 'Altkleider und Textilien beim Räumen entsorgen',
        'h1_em': 'Was in den Container darf und was nicht',
        'teaser': (
            'Kleidung, Bettwäsche, Gardinen und Schuhe aus einer Räumung: '
            'was das Kreislaufwirtschaftsgesetz seit 2025 vorsieht und was '
            'Kommunen im Container annehmen.'
        ),
        'seo_title': 'Altkleider entsorgen: Regeln seit 2025 | Rümpelwerk',
        'seo_description': (
            'Seit 2025 Getrenntsammlung für Textilien: Was in den '
            'Altkleidercontainer darf, was in den Restabfall gehört und was '
            'bei der Räumung gilt. Jetzt lesen.'
        ),
        'seo_keywords': ('altkleider entsorgen, alttextilien entsorgen, '
                         'altkleidercontainer was darf rein, textilien '
                         'getrennte sammlung 2025, bettwäsche entsorgen, '
                         'kleidung bei haushaltsauflösung'),

        'answer_frage': 'Wohin mit Altkleidern und Textilien bei einer Räumung?',
        'answer': (
            'Saubere, trockene, tragbare Kleidung, Bettwäsche und Schuhe '
            'kommen nach den Angaben der Kommunen in den Altkleidercontainer '
            'oder zum Wertstoffhof; stark verschmutzte oder kaputte '
            'Textilien gehören nach Angabe von Halle, Leipzig und Dresden in '
            'den Restabfall (Leipzig: Textilien mit Öl, Fett oder Benzin in '
            'die Schadstoffsammlung). Die Pflicht nach §20 Absatz 2 KrWG '
            'bedeutet seit dem 1. Januar 2025: Die öffentlich-rechtlichen '
            'Entsorgungsträger müssen Textilabfälle aus Haushalten getrennt '
            'sammeln. Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'alttex-krwg-20', 'abschnitt': 'pflicht',
             'bezug': 'Die Pflicht zur getrennten Sammlung von Textilabfällen '
                      'und ihr Beginn am 1. Januar 2025 stehen in §20 Absatz 2 '
                      'KrWG'},
            {'schluessel': 'alttex-halle', 'abschnitt': 'pflicht',
             'bezug': 'Die Stadt Halle (Saale) erklärt, was die Pflicht für '
                      'Haushalte bedeutet'},
            {'schluessel': 'alttex-leipzig-container', 'abschnitt': 'nicht-rein',
             'bezug': 'Leipzig nennt, was nicht in die Container gehört, und '
                      'nennt dabei auch Matratzen'},
            {'schluessel': 'alttex-dresden', 'abschnitt': 'nicht-rein',
             'bezug': 'Dresden beschreibt, welcher Zustand für den Einwurf '
                      'verlangt wird'},
            {'schluessel': 'alttex-aha', 'abschnitt': 'rein',
             'bezug': 'aha Region Hannover listet auf, was in den Container '
                      'darf, darunter Gardinen und Bettwäsche'},
            {'schluessel': 'alttex-leipzig-container', 'abschnitt': 'abgeben',
             'bezug': 'Leipzig nennt Wertstoffhöfe und Kleiderkammern als '
                      'weitere Wege'},
        ],

        'abschnitte': [
            {
                'id': 'pflicht',
                'titel': 'Was seit 2025 gilt',
                'absaetze': [
                    '§20 Absatz 2 des Kreislaufwirtschaftsgesetzes zählt auf, '
                    'welche Abfälle aus privaten Haushaltungen die '
                    'öffentlich-rechtlichen Entsorgungsträger getrennt sammeln '
                    'müssen. Unter Nummer 6 stehen die Textilabfälle. Satz 2 '
                    'fügt an, diese Verpflichtung gelte „ab dem 1. Januar '
                    '2025“. Adressat der Norm sind also die Entsorgungsträger '
                    'der Kommunen, nicht der einzelne Haushalt.',
                    'Die Stadt Halle (Saale) übersetzt das so: Seit dem '
                    '1. Januar 2025 müssten Alttextilien getrennt vom Restmüll '
                    'entsorgt werden; dafür stünden Container gemeinnütziger '
                    'und gewerblicher Sammler bereit. Für Räumungen heißt das: '
                    'Was an Kleidung, Wäsche und Schuhen noch brauchbar ist, '
                    'soll nicht im Container für gemischten Abfall landen. '
                    'Wie Ihre Gemeinde die Einzelheiten regelt, erfahren Sie '
                    'bei deren Abfallberatung.',
                ],
            },
            {
                'id': 'rein',
                'titel': 'Was in den Altkleidercontainer darf',
                'absaetze': [
                    'Die Kommunen im Einsatzgebiet beschreiben es ähnlich, '
                    'aber nicht gleich. Für die Region Hannover führt der '
                    'Zweckverband aha als Einwurf auf: Hosen, Pullis und '
                    'Jacken, Bettwäsche, Woll- und Steppdecken, Gardinen, '
                    'Schuhe, Taschen und Tischdecken. Dresden nennt '
                    'Kleidungsstücke, Wäsche, Tischwäsche, Decken und Schuhe, '
                    'die sauber, ohne Flecken und trocken sind. Leipzig '
                    'verlangt, dass alles trocken und in Tüten verpackt '
                    'eingeworfen wird.',
                    'Allen gemeinsam ist, dass nur Brauchbares hineingehört: '
                    'Dresden fordert sauber, fleckenfrei und trocken, Leipzig '
                    'Sachen, die weiterverwendet werden können, aha schließt '
                    'stark verschmutzte, nasse oder kaputte Kleidung aus. aha rät außerdem, Schuhe paarweise '
                    'zusammenzubinden – einzelne Schuhe gehören nicht in den '
                    'Container.',
                ],
            },
            {
                'id': 'nicht-rein',
                'titel': 'Was nicht hineingehört – und wohin stattdessen',
                'absaetze': [
                    'Dresden schreibt, nasse, verschimmelte, verölte oder '
                    'verunreinigte Textilien gehörten „definitiv in den '
                    'Restabfall“; Teppiche und Koffer zählten nicht zu den '
                    'Alttextilien. Sind sie zu groß für die Tonne, nimmt sie '
                    'dort einer der städtischen Wertstoffhöfe an. Halle nennt '
                    'für stark verschmutzte, zerschlissene oder nicht '
                    'recyclingfähige Textilien ebenfalls die Restmülltonne.',
                    'Leipzig unterscheidet feiner: Textilien mit gefährlichen '
                    'Anhaftungen wie Fett, Öl oder Benzin gehören in die '
                    'Schadstoffsammlung, kaputte oder verschmutzte in die '
                    'Restabfalltonne. Dort stehen außerdem Matratzen und '
                    'Federbetten auf der Liste dessen, was nicht in den '
                    'Container darf; sie gehen zum Wertstoffhof. Bei '
                    'Federbetten urteilen die Kommunen verschieden: Dresden '
                    'und aha nehmen sie sauber und trocken beziehungsweise '
                    'unbeschädigt im Container an. Entscheidend ist deshalb '
                    'immer die Regel am Wohnort. Wie sperrige Teile '
                    'sonst abgegeben werden, steht unter <a '
                    'href="/sperrmuell-entsorgung/">Sperrmüll</a>.',
                ],
            },
            {
                'id': 'raeumen',
                'titel': 'So sortieren Sie beim Räumen (praktische Empfehlung)',
                'absaetze': [
                    'Bei einer <a href="/haushaltsaufloesung/">'
                    'Haushaltsauflösung</a> fällt Textiles in großer Menge an, '
                    'und der Zustand entscheidet über den Weg. Die folgende '
                    'Reihenfolge ist eine Arbeitsempfehlung, keine Vorschrift:',
                ],
                'schritte': [
                    '<strong>Drei Stapel bilden.</strong> Tragbar und trocken; '
                    'kaputt oder verschmutzt; Sonderfälle wie Teppiche, '
                    'Matratzen, Federbetten.',
                    '<strong>Feuchtes sofort aussortieren.</strong> Nasse oder '
                    'schimmelige Stücke gehören nach den Kommunalangaben nicht '
                    'in den Container – trennen Sie sie früh vom Rest.',
                    '<strong>Tragbares in feste Säcke packen,</strong> Schuhe '
                    'paarweise binden und die Säcke trocken lagern, bis sie '
                    'abgegeben werden.',
                    '<strong>Nachschauen, bevor es weggeht.</strong> Taschen '
                    'von Jacken und Mänteln leeren; bei Nachlässen können dort '
                    'Papiere oder Wertsachen stecken.',
                    '<strong>Das Übrige getrennt abgeben</strong> – Restabfall, '
                    'Wertstoffhof, Schadstoffsammlung oder Sperrmüll, je nach '
                    'Kommune.',
                ],
            },
            {
                'id': 'abgeben',
                'titel': 'Statt Container: abgeben und weitergeben',
                'absaetze': [
                    'Gut erhaltene Kleidung muss nicht in den Container. '
                    'Leipzig nennt Kleiderkammern karitativer Einrichtungen, '
                    'einen Online-Verschenkemarkt und die städtischen '
                    'Wertstoffhöfe als weitere Wege; aha empfiehlt, direkt dem '
                    'Secondhandladen oder der Kleiderkammer vor Ort zu '
                    'spenden. Fragen Sie vorher nach, was dort angenommen '
                    'wird – Annahmebedingungen und Öffnungszeiten legt jede '
                    'Einrichtung selbst fest.',
                    'Rümpelwerk Mitteldeutschland trennt beim Räumen nach '
                    'Fraktionen und gibt Entsorgungen über zugelassene '
                    'Entsorgungsbetriebe ab; auf Wunsch erhalten Sie einen '
                    'schriftlichen Entsorgungsnachweis.',
                    'Wer mehr Sicherheit über den Verbleib der Spende '
                    'möchte, achtet laut aha auf das Siegel „FairWertung“ am '
                    'Container: Es zeige an, dass die Kleiderspende an eine '
                    'gemeinnützige Organisation weitergegeben wird. Und wer '
                    'die Säcke nicht selbst fahren will: In Halle können '
                    'saubere, gebrauchsfähige Alttextilien an den '
                    'Wertstoffmärkten der Stadt abgegeben werden, in Leipzig '
                    'an den kommunalen Wertstoffhöfen; dort fließen die '
                    'Erlöse nach Angabe der Stadt gebührenmindernd in die '
                    'Abfallgebühren ein.',
                ],
            },
        ],

        'faq': [
            ('Muss ich Altkleider seit 2025 getrennt entsorgen?',
             'Das Gesetz verpflichtet in §20 Absatz 2 KrWG die '
             'öffentlich-rechtlichen Entsorgungsträger, Textilabfälle ab dem '
             '1. Januar 2025 getrennt zu sammeln. Die Stadt Halle teilt '
             'mit, Alttextilien müssten seitdem getrennt vom Restmüll '
             'entsorgt werden. Welche Regeln im Einzelnen vor Ort gelten, '
             'sagt Ihre Abfallberatung.'),
            ('Gehören kaputte oder verschmutzte Textilien in den Container?',
             'Nach den Angaben von Halle, Leipzig und Dresden nicht: Kaputte, '
             'zerschlissene oder stark verschmutzte Stücke kommen in den '
             'Restabfall, nach Dresden auch nasse und verschimmelte; '
             'Textilien mit Öl, Fett oder Benzin nennt Leipzig als Fall für '
             'die Schadstoffsammlung (Dresden dagegen rechnet verölte '
             'Textilien zum Restabfall). Fragen Sie im Zweifel Ihre '
             'Abfallberatung.'),
            ('Was geschieht mit Matratzen?',
             'Leipzig führt Matratzen unter dem, was nicht in die '
             'Alttextilcontainer gehört, und verweist auf die Wertstoffhöfe. '
             'Andere Kommunen regeln das eigenständig; fragen Sie die '
             'Abfallberatung vor Ort. Hinweise zum Sperrmüll '
             'finden Sie unter <a href="/sperrmuell-entsorgung/">'
             'Sperrmüll entsorgen</a>.'),
            ('Kann ich Kleidung auch spenden?',
             'Ja, etwa an Kleiderkammern oder Secondhandläden, wie sie '
             'Leipzig und aha nennen. Ob und was dort angenommen wird, '
             'entscheidet die jeweilige Einrichtung; fragen Sie vor der '
             'Abgabe kurz nach.'),
        ],

        'leistungen': ['haushaltsaufloesung', 'sperrmuell-entsorgung'],
        'staedte': ['leipzig', 'halle'],
    },

    'asbest-im-haushalt': {
        'stand_iso': '2026-10',
        'kategorie': 'Entsorgung und Schadstoffe',
        'titel': 'Asbest im Haushalt',
        'h1': 'Asbest im Altbau und beim Räumen',
        'h1_em': 'Erkennen, nicht anfassen, richtig entsorgen',
        'teaser': (
            'Wo in älteren Häusern Asbest stecken kann, wann Fasern frei '
            'werden, was Privatleute selbst tun dürfen und wie asbesthaltiger '
            'Abfall entsorgt wird.'
        ),
        'seo_title': 'Asbest im Altbau: Verbote nach §11 GefStoffV | Rümpelwerk',
        'seo_description': (
            'Asbest im Haus erkennen, Faserfreisetzung vermeiden, Entsorgung '
            'und Pflichten für Privatleute nach Gefahrstoffverordnung. '
            'Jetzt lesen.'
        ),
        'seo_keywords': ('asbest im haushalt, asbest altbau, asbest erkennen, '
                         'asbestzement entsorgen, nachtspeicherofen asbest, '
                         'asbest entrümpelung, asbest privat entfernen'),

        'answer_frage': 'Was muss ich bei Asbestverdacht im Altbau beachten?',
        'answer': (
            'Asbestverdacht im Altbau bedeutet: das Material nicht '
            'zerbrechen oder schleifen, denn gefährlich wird Asbest, wenn '
            'Fasern frei werden. Ob es drin ist, zeigt nur eine '
            'Materialuntersuchung. Typisch steckt Asbest in '
            'Asbestzementplatten, Bodenbelägen und Klebern, Putzen, '
            'Spachtelmassen und Nachtspeicheröfen. Für Privathaushalte '
            'gelten dieselben Verbote wie für Betriebe (§11 GefStoffV). '
            'Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'asbest-uba', 'abschnitt': 'erkennen',
             'bezug': 'Das Umweltbundesamt nennt die typischen asbesthaltigen '
                      'Produkte, ihre Verwechslungsgefahr und das Verbotsdatum '
                      '31. Oktober 1993'},
            {'schluessel': 'asbest-gefstoffv-11a', 'abschnitt': 'erkennen',
             'bezug': 'Bei Bauwerken, deren Bau nach dem 31. Oktober 1993 '
                      'begann, wird in der Regel kein Asbest vermutet'},
            {'schluessel': 'asbest-uba', 'abschnitt': 'freisetzung',
             'bezug': 'Fest gebundener Asbest ist bei normaler Nutzung '
                      'unkritisch, kritisch sind Bohren, Sägen, Schleifen, '
                      'Brechen und Zerschlagen'},
            {'schluessel': 'asbest-gefstoffv-11', 'abschnitt': 'recht',
             'bezug': 'Tätigkeiten an asbesthaltigen Materialien sind '
                      'verboten, Ausnahmen sind eng gefasst, und die Regeln '
                      'gelten ausdrücklich auch für private Haushalte'},
            {'schluessel': 'asbest-gefstoffv-11a', 'abschnitt': 'recht',
             'bezug': 'Genehmigung für Abbrucharbeiten niedrigen oder mittleren Risikos, Zulassung für Tätigkeiten hohen Risikos'},
            {'schluessel': 'asbest-uba', 'abschnitt': 'recht',
             'bezug': 'Nach Darstellung des UBA dürfen Abbruch-, Sanierungs- '
                      'und Instandhaltungsarbeiten nur Firmen mit Zulassung '
                      'ausführen; die TRGS 519 ist auch von Privatpersonen '
                      'einzuhalten'},
            {'schluessel': 'uba-ratgeber-haushalt', 'abschnitt': 'recht',
             'bezug': 'Für Nachtspeicheröfen verweist das UBA auf die '
                      'kommunale Abfallberatung und eine Fachfirma'},
            {'schluessel': 'krwg-17', 'abschnitt': 'entsorgung',
             'bezug': 'Abfälle aus privaten Haushalten sind dem '
                      'öffentlich-rechtlichen Entsorgungsträger zu überlassen'},
            {'schluessel': 'krwg-20', 'abschnitt': 'entsorgung',
             'bezug': 'Die Entsorgungsträger stellen sicher, dass sich gefährliche Abfälle bei der Sammlung nicht mit anderen vermischen'},
            {'schluessel': 'asbest-uba', 'abschnitt': 'entsorgung',
             'bezug': 'Schon der positive Nachweis in einer Probe macht den '
                      'gesamten Mischabfall zu gefährlichem Abfall'},
            {'schluessel': 'asbest-uba', 'abschnitt': 'raeumung',
             'bezug': 'Das UBA verweist auf Informationen der Länderbehörden '
                      'und auf die Leitlinie zur Asbesterkundung von 2020'},
            {'schluessel': 'gefstoffv-5a', 'abschnitt': 'raeumung',
             'bezug': 'Mitwirkungspflicht des Veranlassers, auch privater '
                      'Haushalte, bei Tätigkeiten an Gebäuden'},
            {'schluessel': 'asbest-zaw', 'abschnitt': 'entsorgung',
             'bezug': 'Beispiel eines kommunalen Entsorgers in Sachsen: '
                      'Asbest wird nur staubdicht verpackt angenommen'},
        ],

        'abschnitte': [
            {
                'id': 'erkennen',
                'titel': 'Woran Sie verdächtige Materialien erkennen',
                'absaetze': [
                    'Das Umweltbundesamt zählt als typische Fundstellen '
                    'Asbestzementprodukte auf: Dach- und Fassadenplatten, '
                    'Blumenkästen, Fallrohre und Kabelkanäle. Hinzu kommen '
                    'Putze, Spachtelmassen und Fliesenkleber. Bei Fußböden '
                    'sind Vinylbeläge aus den 1960er Jahren (Cushion-Vinyl) '
                    'und die sogenannten Flex-Platten bekannt; der '
                    'schwarzbraune Bitumenkleber darunter kann ebenfalls '
                    'Asbest enthalten. Auch Nachtspeicheröfen können '
                    'schwach gebundenen Asbest enthalten.',
                    'Das Aussehen entscheidet nichts. Cushion-Vinyl lässt '
                    'sich laut UBA leicht mit asbestfreiem PVC verwechseln, '
                    'und in Putzen oder Spachtelmassen ist Asbest mit bloßem '
                    'Auge nicht zu erkennen. Gewissheit bringt deshalb nur '
                    'eine Untersuchung des Materials; Prüfinstitute bieten '
                    'sie an.',
                    'Ein Anhaltspunkt ist das Alter. Seit dem 31. Oktober '
                    '1993 sind Herstellung, Inverkehrbringen und Verwendung '
                    'von Asbest in Deutschland verboten. Bei der Gefährdungsbeurteilung vor Arbeiten kann nach §11a Abs. 1 GefStoffV in der Regel vermutet werden, dass in Objekten, mit deren Bau danach begonnen wurde, kein Asbest steckt (für einzelne Stoffe gelten andere Fristen). '
                    'Besonders viele asbesthaltige Bauten stammen nach UBA-'
                    'Angaben aus den 1960er und 1970er Jahren.',
                ],
            },
            {
                'id': 'freisetzung',
                'titel': 'Wann aus dem Material eine Gefahr wird',
                'absaetze': [
                    'Gefährlich sind eingeatmete Fasern. Von fest gebundenem '
                    'Asbest, etwa in Asbestzement, geht nach Darstellung des '
                    'UBA bei normaler Nutzung keine Gesundheitsgefahr aus, '
                    'solange das Produkt intakt ist und nicht mechanisch '
                    'oder thermisch beansprucht wird. Kritisch sind Bohren, '
                    'Sägen, Schleifen, Fräsen, Brechen und Zerschlagen; '
                    'besonders ungünstig ist das Abschleifen oder '
                    'großflächige Abstemmen. Ein einzelnes Bohrloch in '
                    'asbesthaltigem Putz birgt nach UBA-Angaben dagegen im '
                    'Allgemeinen kein erhöhtes Risiko.',
                    'Für eine Räumung bedeutet das: Eine intakte Platte, die '
                    'an ihrem Platz bleibt, ist kein Notfall, und das UBA '
                    'warnt ausdrücklich vor unnötiger Panik. Heikel wird es, '
                    'wenn beim Ausräumen etwas bricht, ein Blumenkasten '
                    'zerspringt oder sich ein alter Bodenbelag löst. Lose oder angebrochene asbesthaltige Bodenbeläge müssen nach UBA-Angaben entfernt werden; ein generelles '
                    'Sanierungsgebot besteht für Asbestzement dagegen nicht.',
                ],
            },
            {
                'id': 'recht',
                'titel': 'Was Privatleute selbst dürfen – und was nicht',
                'absaetze': [
                    '§11 GefStoffV verbietet grundsätzlich Tätigkeiten an '
                    'asbesthaltigen Materialien in oder an baulichen '
                    'Anlagen. Ausgenommen vom Verbot sind unter anderem das vollständige Entfernen (Abbrucharbeiten), bestimmte Sanierungsarbeiten (Abs. 2 Nr. 2; eine räumliche Trennung ist nach Abs. 4 zu kennzeichnen und zu dokumentieren) und Instandhaltungsarbeiten, diese nur unter Bedingungen (Abs. 5). Ausdrücklich nicht unter die '
                    'Ausnahmen fällt das feste Überdecken asbesthaltiger '
                    'Bodenbeläge (Abs. 3). Und: Die Regeln gelten nach '
                    'Absatz 7 auch für private Haushalte; wer eine erlaubte '
                    'Tätigkeit selbst ausführt, muss die Freisetzung von '
                    'Fasern und Staub so weit wie möglich verhindern und im '
                    'Übrigen minimieren.',
                    'Betriebe brauchen für Abbrucharbeiten im Bereich niedrigen oder mittleren Risikos eine Genehmigung und für Tätigkeiten im Bereich hohen Risikos eine Zulassung der Behörde (§11a Abs. 3 und 4a), außerdem eine sachkundige aufsichtführende Person (Abs. 5); jede Tätigkeit mit Asbest ist der Behörde spätestens eine Woche vorher anzuzeigen (Abs. 4). Das UBA schreibt auf seiner Asbestseite '
                    '(Stand Juli 2024, also vor der Neufassung der '
                    'Gefahrstoffverordnung vom Dezember 2024), die Technische '
                    'Regel TRGS 519 sei auch von Privatpersonen einzuhalten. '
                    'Das vollständige Entfernen ist zwar vom Verbot ausgenommen (§11 Abs. 2 Nr. 1), aber an diese Regeln gebunden. Wer ein verdächtiges Bauteil – Platten, Beläge, einen Nachtspeicherofen – auf eigene Faust ausbauen will, sollte deshalb vorher klären, ob das zulässig ist. Für Nachtspeicheröfen verweist das '
                    'UBA in seinem Ratgeber auf die kommunale Abfallberatung '
                    'und eine Fachfirma.',
                    'Ob ein konkreter Handgriff erlaubt ist, hängt vom '
                    'Einzelfall ab. Fragen Sie im Zweifel die zuständige '
                    'Arbeitsschutz- oder Umweltbehörde; das ist keine '
                    'Rechtsberatung.',
                ],
            },
            {
                'id': 'entsorgung',
                'titel': 'Wie asbesthaltiger Abfall entsorgt wird',
                'absaetze': [
                    'Abfälle aus privaten Haushalten sind grundsätzlich dem öffentlich-rechtlichen Entsorgungsträger zu überlassen (§17 Abs. 1 KrWG), also dem nach Landesrecht zuständigen Träger, etwa Stadt oder Landkreis. Bei gefährlichen Abfällen müssen diese Träger sicherstellen, dass sie sich bei der Sammlung nicht mit anderen Abfällen vermischen (§20 Abs. 2 Nr. 8 KrWG). Hinzu kommt eine Besonderheit, die das UBA '
                    'nennt: Es gibt keine Untergrenze, ab wann ein Bauabfall '
                    'als asbesthaltig gilt; schon der positive Nachweis in '
                    'einer Probe macht den ganzen Mischabfall zu gefährlichem '
                    'Abfall. Wer Asbest vermutet oder nachgewiesen hat, sollte das Material deshalb nicht mit Bauschutt oder Sperrmüll mischen.',
                    'Wie die Annahme aussieht, legt der örtliche Entsorger '
                    'fest. Als Beispiel führt der Zweckverband Abfallwirtschaft Westsachsen in seinem Abfall-ABC Asbest, Eternitplatten und Wellasbest unter der Containerart Asbest auf; angenommen wird ausschließlich '
                    'staubdicht verpackt, in Folie, Müllsäcken oder speziellen '
                    'Big-Bags, gegen Entgelt. Anderswo können Mengengrenzen, '
                    'Anmeldung oder andere Verpackungsregeln gelten. Klären Sie '
                    'das vor der Anlieferung bei Ihrer Abfallberatung.',
                ],
            },
            {
                'id': 'raeumung',
                'titel': 'Was vor einer Räumung bei Verdacht zu klären ist',
                'absaetze': [
                    'Wer ein Objekt mit möglichem Asbest räumen lassen '
                    'will, sollte vor dem ersten Termin diese Punkte '
                    'durchgehen:',
                ],
                'schritte': [
                    '<strong>Verdacht eingrenzen.</strong> Welches Bauteil, '
                    'wo, welches Baujahr, gibt es Unterlagen über frühere '
                    'Umbauten? Notieren Sie es und machen Sie Fotos.',
                    '<strong>Nichts anbohren, abschlagen oder zerbrechen.</strong> '
                    'Genau diese Bearbeitung setzt nach dem UBA Fasern '
                    'frei.',
                    '<strong>Material untersuchen lassen,</strong> wenn es '
                    'ausgebaut oder entsorgt werden soll. Hinweise zur '
                    'Erkundung vor Arbeiten an älteren Gebäuden gibt die '
                    'Leitlinie, die UBA, BAuA und BBSR 2020 gemeinsam '
                    'veröffentlicht haben.',
                    '<strong>Behörde und Entsorger fragen.</strong> Die '
                    'Umweltbehörden der Länder und viele Kommunen bieten '
                    'Informationen zu Asbest an; die Abfallberatung nennt '
                    'die Annahmebedingungen vor Ort.',
                    '<strong>Verdacht vor der Besichtigung mitteilen.</strong> '
                    'Sagen Sie bei der Terminvereinbarung, dass Sie Asbest '
                    'vermuten, damit es bei der kostenlosen Besichtigung '
                    'zur Sprache kommt. Das ist seit Dezember 2024 auch '
                    'Pflicht: Wer Arbeiten an Gebäuden veranlasst, muss dem '
                    'ausführenden Betrieb vorher mitteilen, was er über '
                    'vorhandene oder vermutete Gefahrstoffe und das Baujahr '
                    'weiß – ausdrücklich auch als Privathaushalt (§5a '
                    'GefStoffV). Allgemeines zum Ablauf finden Sie '
                    'unter <a href="/haushaltsaufloesung/">Haushaltsauflösung</a> '
                    'und <a href="/kellerentruempelung/">Kellerentrümpelung</a>.',
                ],
            },
        ],

        'faq': [
            ('Ist jede alte Wellplatte aus Asbest?',
             'Das lässt sich von außen nicht sagen. Asbestzement war '
             'verbreitet, seit dem 31. Oktober 1993 ist Asbest aber '
             'verboten. Sicherheit gibt nur eine Untersuchung. Bis dahin '
             'gilt: nicht zerbrechen, nicht zersägen, nicht abschleifen.'),
            ('Ich habe beim Ausräumen Staub eingeatmet – muss ich zum Arzt?',
             'Das UBA nennt als ersten Ansprechpartner den Hausarzt, falls '
             'Sie über Jahre hohen Konzentrationen ausgesetzt waren. Bei '
             'häuslicher Belastung und gelegentlichem Heimwerken sind '
             'weitere Vorsorgeuntersuchungen in der Regel nicht angezeigt.'),
            ('Darf ich Asbestzement-Reste selbst zum Wertstoffhof bringen?',
             'Entscheidend ist der örtliche Entsorgungsträger. Manche '
             'Entsorger nehmen Asbest aus Haushalten staubdicht verpackt '
             'an, oft gegen Entgelt. Fragen Sie vorher nach Menge, '
             'Verpackung und Anmeldung, und zerkleinern Sie nichts, um '
             'es handlicher zu machen.'),
            ('Muss ein asbestverdächtiger Boden vor der Räumung raus?',
             'Nicht automatisch. Nach UBA-Angaben besteht für Asbestzement '
             'kein generelles Sanierungsgebot, und intakte Produkte '
             'gefährden nicht von selbst. Lose oder angebrochene asbesthaltige Bodenbeläge müssen nach UBA entfernt werden. Wer dafür zuständig ist, klärt bei '
             'Mietobjekten der Mieterverein oder eine Rechtsberatung.'),
        ],

        'leistungen': ['haushaltsaufloesung', 'kellerentruempelung'],
        'staedte': [],
    },

    'batterien-akkus-entsorgen': {
        'stand_iso': '2026-10',
        'kategorie': 'Entsorgung und Schadstoffe',
        'titel': 'Batterien und Akkus entsorgen',
        'h1': 'Batterien und Akkus beim Räumen richtig entsorgen',
        'h1_em': 'Rückgabepflicht, Rückgabewege und der Umgang mit Lithium-Akkus',
        'teaser': (
            'Alte Batterien und Akkus aus Schubladen, Kellern und Garagen: '
            'Warum sie nicht in den Hausmüll dürfen, wo die Rückgabe kostenlos '
            'ist und was beim Sammeln und Transportieren zu beachten ist.'
        ),
        'seo_title': 'Batterien & Akkus entsorgen: Rückgabe kostenlos | Rümpelwerk',
        'seo_description': (
            'Batterien und Akkus beim Räumen richtig entsorgen: Rückgabepflicht '
            'nach BattDG, kostenlose Abgabe, Brandgefahr bei Lithium-Akkus. Jetzt lesen.'
        ),
        'seo_keywords': ('batterien entsorgen, akkus entsorgen, altbatterien rückgabe, '
                         'battdg rückgabepflicht, lithium akku entsorgen, '
                         'autobatterie entsorgen keller'),

        'answer_frage': 'Wohin mit alten Batterien und Akkus beim Räumen?',
        'answer': (
            'Alte Batterien und Akkus gehören zur Rückgabe in den Handel, '
            'der die jeweilige Art führt, oder zur Kommune, etwa an den '
            'Wertstoffhof – nie in den Hausmüll: Endnutzer müssen sie '
            'getrennt erfassen lassen (§6 BattDG). Die Rückgabe von Geräte- '
            'und E-Bike-Batterien kostet nichts. Beschädigte Lithium-Akkus '
            'brauchen besondere Vorsicht. Rümpelwerk Mitteldeutschland '
            'trennt beim Räumen nach Fraktionen. Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'battdg-gesamt', 'abschnitt': 'pflicht',
             'bezug': 'Das Gesetz ist am 7. Oktober 2025 in Kraft getreten und löste '
                      'das frühere Batteriegesetz ab'},
            {'schluessel': 'battdg-6', 'abschnitt': 'pflicht',
             'bezug': 'Endnutzer müssen Altbatterien getrennt vom unsortierten '
                      'Siedlungsabfall erfassen lassen; in andere Produkte eingebaute '
                      'Batterien fallen unter das ElektroG'},
            {'schluessel': 'uba-batterien-akkus', 'abschnitt': 'pflicht',
             'bezug': 'Das Umweltbundesamt nennt Hausmüll, Sperrmüll, Verpackungsmüll '
                      'und Metallschrott als falsche Wege und erklärt die Pflicht'},
            {'schluessel': 'battdg-14', 'abschnitt': 'rueckgabe',
             'bezug': 'Händler müssen Gerätealtbatterien und Altbatterien für leichte '
                      'Verkehrsmittel unentgeltlich zurücknehmen, beschränkt auf ihr '
                      'Sortiment und die übliche Menge privater Endnutzer'},
            {'schluessel': 'battdg-15', 'abschnitt': 'rueckgabe',
             'bezug': 'Die öffentlich-rechtlichen Entsorgungsträger müssen diese '
                      'Altbatterien aus privaten Haushaltungen unentgeltlich annehmen'},
            {'schluessel': 'uba-batterien-akkus', 'abschnitt': 'rueckgabe',
             'bezug': 'Sammelboxen im Handel, Wertstoffhöfe, Schadstoffmobile, '
                      'einheitliches Sammelstellenlogo; Händler müssen auch beschädigte '
                      'Batterien zurücknehmen'},
            {'schluessel': 'battdg-6', 'abschnitt': 'arten',
             'bezug': 'Starter- und Industriealtbatterien dürfen nur über Händler, '
                      'öffentlich-rechtliche Entsorgungsträger oder ausgewählte '
                      'Abfallbewirtschafter erfasst werden'},
            {'schluessel': 'battdg-18', 'abschnitt': 'arten',
             'bezug': 'Händler müssen Starter-, Industrie- und Elektrofahrzeugaltbatterien nur '
                      'der Kategorie zurücknehmen, die sie als Neubatterie führen oder führten'},
            {'schluessel': 'battdg-20', 'abschnitt': 'arten',
             'bezug': 'Öffentlich-rechtliche Entsorgungsträger können sich an der Rücknahme '
                      'von Starter- und Industriealtbatterien beteiligen'},
            {'schluessel': 'uba-batterien-akkus', 'abschnitt': 'arten',
             'bezug': 'Auch Starter- und E-Bike-Batterien nehmen Händler kostenfrei zurück; '
                      'Kommunen nehmen bestimmte Altbatterien an'},
            {'schluessel': 'uba-lithium-akkus', 'abschnitt': 'lithium',
             'bezug': 'Das Umweltbundesamt rät, die Enden abzukleben, kaputte oder '
                      'aufgeblähte Akkus nicht zu benutzen und Akkus in einem sicheren '
                      'Behälter zur Sammelstelle zu bringen'},
            {'schluessel': 'uba-batterien-akkus', 'abschnitt': 'lithium',
             'bezug': 'Mechanische Beschädigungen können zu Kurzschluss, Brand oder '
                      'Explosion führen'},
        ],

        'abschnitte': [
            {
                'id': 'pflicht',
                'titel': 'Die Pflicht: getrennt erfassen, nie in den Hausmüll',
                'absaetze': [
                    'Seit dem 7. Oktober 2025 regelt das Batterierecht-Durchführungsgesetz '
                    '(BattDG) die Rückgabe von Altbatterien. Nach §6 Absatz 1 haben '
                    'Endnutzer Altbatterien einer Erfassung zuzuführen, die vom '
                    'unsortierten Siedlungsabfall getrennt ist. Diese Pflicht trifft '
                    'also nicht erst den Entsorger, sondern schon den Haushalt, aus '
                    'dem die Batterien kommen.',
                    'Das Umweltbundesamt wird deutlicher: Batterien und Akkus gehören '
                    'keinesfalls in den Hausmüll (Restmüll), den Sperrmüll, den '
                    'Verpackungsmüll oder in den Metallschrott. Auf dem Gerät oder der '
                    'Batterie zeigt das Symbol der durchgestrichenen Mülltonne an, '
                    'dass sie getrennt zu entsorgen sind. Als Grund nennt das Amt '
                    'Brand- und Umweltgefahren.',
                    'Ein Abgrenzungshinweis: Altbatterien, die in andere '
                    'Produkte eingebaut sind, fallen nach §6 Absatz 1 Satz 2 nicht unter diese '
                    'Regel, dafür gilt das Elektrogerätegesetz. Das behandelt der '
                    'Beitrag <a href="/ratgeber/elektroaltgeraete-entsorgen/">Elektroaltgeräte '
                    'entsorgen</a>. Hier geht es um Batterien und Akkus, die einzeln vorliegen.',
                ],
            },
            {
                'id': 'rueckgabe',
                'titel': 'Wo die Rückgabe kostenlos ist',
                'absaetze': [
                    'Es gibt zwei Wege, und beide kosten nichts. Der erste ist der '
                    'Handel: Händler müssen Gerätealtbatterien und Altbatterien für '
                    'leichte Verkehrsmittel wie E-Bike-Akkus unentgeltlich zurücknehmen '
                    '(§14 Absatz 1 BattDG). Die Pflicht ist auf Batteriekategorien '
                    'beschränkt, die der Händler im Sortiment führt oder führte, und '
                    'auf die Menge, derer sich private Endnutzer üblicherweise entledigen. Das Umweltbundesamt nennt als Beispiele '
                    'Supermärkte, Drogeriemärkte, Elektro-Fachgeschäfte und Baumärkte; '
                    'meist stehen dort Sammelboxen.',
                    'Der zweite Weg ist die Kommune: Die öffentlich-rechtlichen '
                    'Entsorgungsträger müssen Gerätealtbatterien und Altbatterien für '
                    'leichte Verkehrsmittel aus privaten Haushaltungen unentgeltlich '
                    'annehmen, unabhängig von chemischer Zusammensetzung, Marke, Herkunft, '
                    'Baugröße und Beschaffenheit (§15 Absatz 1). In der Praxis ist das der '
                    'Wertstoffhof oder das Schadstoffmobil. Ein einheitliches '
                    'Sammelstellenlogo zeigt an, wo Altbatterien abgegeben werden können.',
                    'Bei einer Haushaltsauflösung fällt oft mehr an, als in eine '
                    'Ladenbox passt: Kisten aus der Schublade, ganze Beutel aus dem '
                    'Keller. Weil der Handel nur die übliche Menge privater Endnutzer annehmen muss, '
                    'ist für größere Mengen der Wertstoffhof der sicherere Weg; '
                    'fragen Sie bei Ihrer Kommune nach den Annahmebedingungen. '
                    'Beim Räumen trennt Rümpelwerk Mitteldeutschland nach Fraktionen '
                    'und gibt Entsorgungen über zugelassene Entsorgungsbetriebe, '
                    'auf Wunsch mit schriftlichem Entsorgungsnachweis, etwa bei einer '
                    '<a href="/kellerentruempelung/">Kellerentrümpelung</a>.',
                ],
            },
            {
                'id': 'arten',
                'titel': 'Autobatterie im Keller, E-Bike-Akku in der Garage',
                'absaetze': [
                    'Nicht jede Batterie geht denselben Weg. Starter- und '
                    'Industriealtbatterien, zum Beispiel eine alte Autobatterie, dürfen '
                    'nach §6 Absatz 3 BattDG ausschließlich über Händler, '
                    'öffentlich-rechtliche Entsorgungsträger oder ausgewählte '
                    'Abfallbewirtschafter erfasst werden. Das Umweltbundesamt nennt als '
                    'Händlerbeispiele Fachgeschäfte für Autoteile, Autowerkstätten und '
                    'Baumärkte; auch der Fahrrad-Fachhandel nimmt Akkus von '
                    'E-Fahrrädern und E-Scootern kostenfrei zurück.',
                    'Händler müssen Starterbatterien nur zurücknehmen, wenn sie solche '
                    'Batterien als Neuware im Sortiment führen oder geführt haben '
                    '(§18 Absatz 1). Die Kommune ist für diese Arten kein Pflichtweg: '
                    'Sie kann sich nach §20 beteiligen, muss es aber nicht. Fragen Sie '
                    'bei Ihrem Wertstoffhof nach, bevor Sie eine Autobatterie hinbringen.',
                ],
            },
            {
                'id': 'lithium',
                'titel': 'Lithium-Akkus: Brandgefahr beim Sammeln und Transport',
                'absaetze': [
                    'Das Umweltbundesamt warnt vor einer hohen Brandgefahr durch '
                    'lithiumhaltige Batterien und Akkus bei Sammlung und Behandlung: '
                    'Mechanische Beschädigungen und Hitze können zu inneren und '
                    'äußeren Kurzschlüssen führen, ein Kurzschluss kann Brand oder '
                    'Explosion auslösen. Brände dieser Art haben vor allem in '
                    'Abfallbehandlungs- und Recyclinganlagen in den vergangenen Jahren stark '
                    'zugenommen.',
                    'Ausgelaufene Akkus nicht mit bloßen Händen anfassen: Handschuhe tragen. '
                    'Brennt ein Akku, rufen Sie die Feuerwehr; im Brandfall können '
                    'giftige Gase entstehen.',
                    'Für den Umgang beim Räumen gibt das Amt in seinem Merkblatt zu '
                    'Lithium-Akkus konkrete Hinweise:',
                ],
                'liste': [
                    'Kaputte oder aufgeblähte Akkus nicht mehr benutzen und nicht öffnen: '
                    'Sie können explodieren oder brennen. Sofort zur Sammelstelle '
                    'bringen und dem Personal Bescheid sagen.',
                    'Die Enden der Akkus abkleben.',
                    'Akkus in einem sicheren Behälter transportieren, zum Beispiel '
                    'in einer Dose mit Deckel oder mit Sand.',
                    'Nicht draußen, an feuchten oder heißen Orten lagern, zum Beispiel '
                    'nicht im Auto in der Sonne.',
                ],
            },
            {
                'id': 'raeumen',
                'titel': 'So gehen Sie beim Räumen vor',
                'absaetze': [
                    'Die Reihenfolge, die sich aus den Regeln ergibt:',
                ],
                'schritte': [
                    '<strong>Einzeln halten, nicht in den Müllsack.</strong> Batterien '
                    'und Akkus aus Schubladen, Fernbedienungen und Werkzeugkisten kommen '
                    'nicht zum Restmüll und nicht zum Sperrmüll, sondern in einen eigenen Behälter.',
                    '<strong>Beschädigte aussortieren.</strong> Ausgelaufene oder '
                    'aufgeblähte Akkus getrennt halten, nicht mehr benutzen, nicht öffnen.',
                    '<strong>Art bestimmen.</strong> Gerätebatterien, Akkus von E-Bikes und '
                    'Rollern, Starterbatterien: Je nach Art unterscheidet sich der '
                    'Rückgabeweg, siehe oben.',
                    '<strong>Enden abkleben</strong> bei Akkus, wie vom '
                    'Umweltbundesamt empfohlen, und in einem sicheren Behälter zur Sammelstelle bringen.',
                ],
                'absaetze': [
                    'Wer die Räumung nicht selbst stemmen will oder viele Batterien '
                    'findet, kann sie bei der <a href="/haushaltsaufloesung/">'
                    'Haushaltsauflösung</a> mitgeben lassen; die Sortierung nach '
                    'Fraktionen gehört dort zum Ablauf.',
                ],
            },
        ],

        'faq': [
            ('Darf ich einzelne leere Batterien in den Restmüll werfen?',
             'Nein. Auch wenige Batterien gehören laut Umweltbundesamt keinesfalls '
             'in den Hausmüll. Endnutzer müssen sie getrennt erfassen lassen (§6 '
             'Absatz 1 BattDG); abgegeben werden sie kostenlos im Handel oder bei der Kommune.'),
            ('Muss ich für die Rückgabe von Batterien bezahlen?',
             'Nein. Händler nehmen Gerätealtbatterien unentgeltlich zurück (§14 '
             'Absatz 1 BattDG), die öffentlich-rechtlichen Entsorgungsträger '
             'nehmen sie aus privaten Haushalten unentgeltlich an (§15 Absatz 1).'),
            ('Muss ich die Pole bei Akkus abkleben?',
             'Das Umweltbundesamt rät in seinem Merkblatt zu Lithium-Akkus, die '
             'Enden abzukleben, und empfiehlt einen sicheren Behälter für den '
             'Transport. Es ist die Empfehlung einer Behörde, die auf Kurzschlüsse '
             'und Brandgefahr zielt.'),
            ('Wohin mit der alten Autobatterie aus dem Keller?',
             'Starterbatterien gehen nach §6 Absatz 3 BattDG über Händler, '
             'öffentlich-rechtliche Entsorgungsträger oder ausgewählte '
             'Abfallbewirtschafter. Fragen Sie vorab bei Händler oder Wertstoffhof, '
             'ob sie die Batterie annehmen.'),
        ],

        'leistungen': ['haushaltsaufloesung', 'kellerentruempelung', 'wohnungsaufloesung'],
        'staedte': [],
    },

    'daten-loeschen-vor-der-entsorgung': {
        'stand_iso': '2026-10',
        'kategorie': 'Vorbereitung und Übergabe',
        'titel': 'Daten vor der Entsorgung löschen',
        'h1': 'Daten löschen, bevor Geräte aus dem Haus gehen',
        'h1_em': 'Computer, Handy, Festplatte, Router, Smart-TV',
        'teaser': (
            'Was das BSI zum sicheren Löschen empfiehlt, welche Methode zu '
            'welchem Gerät passt und was bei den Geräten Verstorbener '
            'vorher zu klären ist.'
        ),
        'seo_title': 'Daten löschen vor der Entsorgung: Anleitung | Rümpelwerk',
        'seo_description': (
            'PC, Handy, Festplatte oder Speicherkarte entsorgen? So löschen '
            'Sie Daten sicher, wie das BSI es empfiehlt – und was bei '
            'Nachlässen gilt. Jetzt lesen.'
        ),
        'seo_keywords': ('daten sicher löschen, festplatte löschen vor '
                         'entsorgung, handy zurücksetzen, bsi daten löschen, '
                         'altgeräte daten löschen, geräte nachlass daten'),

        'answer_frage': 'Muss ich Daten löschen, bevor ich Geräte entsorge?',
        'answer': (
            'Gesetzlich ausdrücklich vorgeschrieben ist es nicht, aber '
            'dringend empfohlen: Das BSI rät, persönliche Daten vor dem Verkauf, der '
            'Entsorgung im Elektroschrott oder der Reparatur zu löschen, '
            'sofern sie nicht sicher verschlüsselt sind. Sicheres Löschen '
            'bedeutet mehr als Löschen oder Formatieren: geeignet sind '
            'Überschreiben, Löschbefehl, Verschlüsselung mit '
            'Schlüssel-Löschung, bei aktuellen Smartphones der Werksreset '
            'oder physische Zerstörung. Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'daten-bsi-loeschen', 'abschnitt': 'warum',
             'bezug': 'Das BSI nennt den Anlass, die Beispiele für '
                      'schützenswerte Daten und die Empfehlung zum Löschen '
                      'vor der Weitergabe'},
            {'schluessel': 'daten-elektrog-18', 'abschnitt': 'warum',
             'bezug': 'Das ElektroG spricht von der Eigenverantwortung der '
                      'Endnutzer beim Löschen personenbezogener Daten'},
            {'schluessel': 'daten-bsi-loeschen', 'abschnitt': 'methoden',
             'bezug': 'Die Löschmethoden und ihre Grenzen stammen aus der '
                      'BSI-Anleitung'},
            {'schluessel': 'daten-bsi-loeschen', 'abschnitt': 'geraete',
             'bezug': 'Das BSI unterscheidet Smartphones und Tablets von '
                      'Desktop-Betriebssystemen und nennt Speicherkarten'},
        ],

        'abschnitte': [
            {
                'id': 'warum',
                'titel': 'Warum Daten vor der Entsorgung verschwinden müssen',
                'absaetze': [
                    'Nach der Räumung ist ein Laptop nur noch ein Gerät, das '
                    'weg soll – für den, der ihn in die Hand bekommt, aber ein '
                    'Archiv. Das Bundesamt für Sicherheit in der '
                    'Informationstechnik (BSI) rät, persönliche Daten zu '
                    'löschen, bevor man PC, Smartphone, Tablet, USB-Stick oder '
                    'externe Festplatte verkauft, im Elektroschrott entsorgt, '
                    'reparieren lässt oder verleiht. Als Beispiele nennt es '
                    'E-Mails, private Fotos, Videos, Dokumente, Chats und '
                    'gespeicherte Passwörter. Sind die Daten sicher '
                    'verschlüsselt, erübrige sich das Löschen.',
                    'Rechtlich ist die Lage bescheidener, als man vermutet: Im '
                    'Wortlaut des ElektroG steht kein Satz, der Besitzer '
                    'ausdrücklich zum Löschen verpflichtet; §18 verlangt von '
                    'Entsorgungsträgern, rücknahmepflichtigen Händlern und '
                    'Herstellern (Absatz 1 Nummer 7, Absatz 3 Nummer 6, Absatz 4 '
                    'Nummer 6), dass sie über die '
                    '„Eigenverantwortung der Endnutzer im Hinblick auf das '
                    'Löschen personenbezogener Daten auf den zu entsorgenden '
                    'Altgeräten“ informieren. Eine eigene Löschpflicht folgt '
                    'daraus nach dem Wortlaut nicht; das BSI empfiehlt das '
                    'Löschen dennoch. Zur '
                    'Rückgabe der Geräte selbst lesen Sie '
                    '<a href="/ratgeber/elektroaltgeraete-entsorgen/">'
                    'Elektroaltgeräte entsorgen</a>.',
                ],
            },
            {
                'id': 'methoden',
                'titel': 'Die Löschwege nach BSI – und was nicht löscht',
                'absaetze': [
                    'Zuerst sichern: Das BSI empfiehlt, vor dem Löschen eine '
                    'Kopie der noch benötigten Daten anzulegen und '
                    'auszuprobieren, ob sie sich wiederherstellen lässt. Dann '
                    'führt es diese Methoden auf (der Werksreset für Smartphones '
                    'folgt weiter unten):',
                ],
                'liste': [
                    '<strong>Überschreiben</strong> – mit spezieller Software, '
                    'die den Datenträger mit festen Zeichen oder Zufallszahlen '
                    'beschreibt. Das BSI hält das für die meisten Fälle für '
                    'ausreichend.',
                    '<strong>Löschbefehl des Datenträgers</strong> – viele SSDs '
                    'und manche Festplatten kennen einen Befehl wie ATA „'
                    'Enhanced Security Erase“, der eine Herstellerroutine '
                    'anstößt.',
                    '<strong>Verschlüsseln und Schlüssel löschen</strong> – '
                    'waren die Daten verschlüsselt, genügt es nach BSI, alle '
                    'Schlüssel sicher zu löschen.',
                    '<strong>Physisch zerstören</strong> – wenn man nicht '
                    'überschreiben will oder wegen eines Defekts nicht kann. '
                    'Bei Festplatten macht nach BSI schon das Verbiegen der '
                    'Scheiben die gängigen Methoden der Datenrettung '
                    'unanwendbar; bei SD-Karten genügt das Zerbrechen. Schutzbrille tragen; von der '
                    'Mikrowelle rät das BSI ab.',
                ],
            },
            {
                'id': 'geraete',
                'titel': 'Gerät für Gerät',
                'absaetze': [
                    '<strong>Computer und Laptops:</strong> Den Papierkorb '
                    'leeren oder die Platte formatieren genügt laut BSI nicht, '
                    'auch ein Werksreset löscht bei Desktop-Betriebssystemen '
                    'unter Umständen nur das Inhaltsverzeichnis. Zu empfehlen '
                    'ist Überschreiben, bei Defekt Zerstörung des Datenträgers.',
                    '<strong>Smartphones und Tablets:</strong> Bei aktuellen '
                    'Geräten ist der Werksreset nach BSI normalerweise '
                    'ausreichend – gewählt werden '
                    'muss die Variante, die Inhalte löscht, nicht nur '
                    'Einstellungen. Speicherkarten und SIM-Karten vorher '
                    'herausnehmen.',
                    '<strong>Speicherkarten, USB-Sticks, externe '
                    'Festplatten:</strong> überschreiben oder zerstören.',
                    '<strong>Router und Smart-TVs:</strong> Die BSI-Seite '
                    'behandelt sie nicht. Unsere Empfehlung, nicht '
                    'aus der Quelle: Lesen Sie in der Bedienungsanleitung des '
                    'Herstellers nach, wie man das Gerät auf Werkszustand '
                    'zurücksetzt und Konten abmeldet – und tun Sie das vor '
                    'dem Abtransport.',
                    'Die Grenze nennt das BSI selbst: Die Methoden schützen vor '
                    'einfachem Zugriff durch Dritte, nicht vor hochspezialisierten '
                    'Angreifern; dort hilft oft nur Zerstörung.',
                    'Zwei Hinweise aus der Anleitung sparen Ärger. Erstens: '
                    'Eine Löschung kann in seltenen Fällen scheitern, ohne dass '
                    'das Programm es meldet. Das BSI rät deshalb, nach dem '
                    'Löschen noch einmal zu versuchen, auf die Daten zuzugreifen; '
                    'gelingt das, war der Vorgang nicht erfolgreich und eine '
                    'andere Methode ist zu wählen. Zweitens: Wer den '
                    'Datenträger mit dem Betriebssystem im Ganzen überschreibt, '
                    'löscht womöglich auch die Wiederherstellungspartition des '
                    'Herstellers – vorher ein externes Medium zur '
                    'Neuinstallation erstellen, falls das Gerät weitergegeben '
                    'und weiterverwendet werden soll.',
                ],
            },
            {
                'id': 'nachlass',
                'titel': 'Geräte Verstorbener: erst sichten, dann löschen',
                'absaetze': [
                    '<strong>Praktische Empfehlung, keine Rechtsauskunft:</strong> '
                    'Bei einer <a href="/nachlassraeumung/">Nachlassräumung</a> '
                    'sollten Computer, Handys, Festplatten und Speicherkarten '
                    'nicht in der ersten Räumungswelle verschwinden. Auf '
                    'ihnen liegen oft Fotos, Verträge oder Unterlagen, die '
                    'Angehörige noch brauchen, und was gelöscht ist, lässt sich '
                    'nicht zurückholen.',
                    'Legen Sie solche Geräte vor Beginn gesondert beiseite und '
                    'sprechen Sie mit den Erben, wer sie sichtet und wann '
                    'gelöscht wird. Rümpelwerk sichert bei Nachlässen '
                    'Fundstücke wie Papiere, Schmuck und Fotos und übergibt '
                    'sie den Angehörigen. Wer auf Konten und Online-Dienste '
                    'des Verstorbenen zugreifen darf, ist eine Rechtsfrage '
                    'für Nachlassgericht oder Rechtsberatung – dazu '
                    'machen wir hier keine Angaben.',
                ],
            },
        ],

        'faq': [
            ('Reicht es, Dateien zu löschen und den Papierkorb zu leeren?',
             'Nein. Das BSI erklärt, dass dabei lediglich Verweise im '
             'Inhaltsverzeichnis entfernt werden; die Daten können mit wenig '
             'Aufwand wiederhergestellt werden. Auch normales Formatieren '
             'nennt es ungeeignet.'),
            ('Muss ich das Handy vor der Entsorgung auf Werkszustand '
             'zurücksetzen?',
             'Das BSI hält den Werksreset bei aktuellen Smartphones und '
             'Tablets normalerweise für ausreichend, sofern die Variante mit Löschung der '
             'Inhalte gewählt wird. Speicher- und SIM-Karten sollten Sie '
             'vorher herausnehmen.'),
            ('Gibt das ElektroG eine Löschpflicht vor?',
             'Der Gesetzeswortlaut nennt sie nicht ausdrücklich. '
             '§18 Absatz 1 Nummer 7 ElektroG spricht von der '
             '„Eigenverantwortung der Endnutzer“ für das Löschen '
             'personenbezogener Daten. Verbindlich klären lassen sich '
             'Einzelfälle durch Rechtsberatung.'),
            ('Was mache ich mit den Geräten eines Verstorbenen?',
             'Nicht sofort entsorgen oder löschen, sondern beiseitelegen und '
             'mit den Erben klären, wer sie sichtet (praktische '
             'Empfehlung). Zur Räumung eines Nachlasses siehe '
             '<a href="/nachlassraeumung/">Nachlassräumung</a>.'),
        ],

        'leistungen': ['nachlassraeumung', 'haushaltsaufloesung'],
        'staedte': [],
    },

    'elektroaltgeraete-entsorgen': {
        'stand_iso': '2026-10',
        'kategorie': 'Entsorgung und Schadstoffe',
        'titel': 'Elektroaltgeräte entsorgen',
        'h1': 'Elektroaltgeräte bei der Haushaltsauflösung entsorgen',
        'h1_em': 'Wohin sie gehören, was der Handel zurücknehmen muss und was mit den Daten ist',
        'teaser': (
            'Kühlschrank, Fernseher, Laptop: Wo Elektroaltgeräte abgegeben '
            'werden, wann der Handel sie zurücknehmen muss und wer für die '
            'Daten auf den Geräten verantwortlich ist.'
        ),
        'seo_title': 'Elektroaltgeräte entsorgen: kostenlose Rückgabe | Rümpelwerk',
        'seo_description': (
            'Elektroaltgeräte bei Haushaltsauflösung richtig entsorgen: '
            'Wertstoffhof, Rücknahme im Handel nach ElektroG, Daten löschen. '
            'Jetzt informieren.'
        ),
        'seo_keywords': ('elektroaltgeräte entsorgen, elektroschrott haushaltsauflösung, '
                         'elektrog rücknahme, altgeräte wertstoffhof, '
                         'kühlschrank entsorgen, daten löschen altgeräte'),

        'answer_frage': 'Wohin mit alten Elektrogeräten bei einer Haushaltsauflösung?',
        'answer': (
            'Elektroaltgeräte gehören weder in den Rest- noch in den '
            'Sperrmüll, sondern zum Wertstoffhof oder zurück in den Handel. '
            'Die Abgabe aus privaten Haushalten kostet an den kommunalen '
            'Sammelstellen nichts; größere Händler müssen nur beim Neukauf '
            'oder bei Kleingeräten bis 25 Zentimeter zurücknehmen. '
            'Rümpelwerk Mitteldeutschland trennt beim Räumen nach '
            'Fraktionen. Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'elektrog-13', 'abschnitt': 'wohin',
             'bezug': 'Die öffentlich-rechtlichen Entsorgungsträger richten Sammelstellen '
                      'für Altgeräte aus privaten Haushalten ein, die Anlieferung ist '
                      'entgeltfrei, bei mehr als 20 Geräten der Gruppen 1, 4 und 6 ist '
                      'vorab abzustimmen'},
            {'schluessel': 'uba-elektroaltgeraete', 'abschnitt': 'wohin',
             'bezug': 'Das Umweltbundesamt nennt Wertstoffhof, Handel und die '
                      'kommunalen Zusatzangebote und rät von Schrottsammlern ab'},
            {'schluessel': 'elektrog-17', 'abschnitt': 'handel',
             'bezug': 'Rücknahmepflicht der Vertreiber: Flächengrenzen, Neukauf-Bedingung, '
                      '25-Zentimeter-Regel, höchstens drei Altgeräte je Geräteart'},
            {'schluessel': 'elektrog-10', 'abschnitt': 'getrennt',
             'bezug': 'Endnutzer müssen Altgeräte getrennt vom unsortierten '
                      'Siedlungsabfall erfassen lassen; Lampen und nicht umschlossene '
                      'Batterien sind vorher zu trennen'},
            {'schluessel': 'uba-elektroaltgeraete', 'abschnitt': 'getrennt',
             'bezug': 'Auch Sperrmüll, Verpackungsmüll und Metallschrott sind '
                      'falsche Wege; falsch entsorgte batteriehaltige Geräte lösen Brände aus'},
            {'schluessel': 'elektrog-14', 'abschnitt': 'sonderfaelle',
             'bezug': 'Batteriebetriebene Altgeräte und asbesthaltige Nachtspeicherheizgeräte '
                      'werden an der Übergabestelle gesondert gesammelt'},
            {'schluessel': 'elektrog-13', 'abschnitt': 'sonderfaelle',
             'bezug': 'Annahme asbesthaltiger Nachtspeicherheizgeräte kann abgelehnt werden, '
                      'wenn sie nicht ordnungsgemäß durch Fachpersonal abgebaut und verpackt wurden'},
            {'schluessel': 'uba-elektroaltgeraete', 'abschnitt': 'daten',
             'bezug': 'Personenbezogene Daten sollen vor der Entsorgung gelöscht werden; '
                      'die Verantwortung liegt laut UBA bei den Verbrauchern'},
        ],

        'abschnitte': [
            {
                'id': 'wohin',
                'titel': 'Wohin: Wertstoffhof und kommunale Sammelstellen',
                'absaetze': [
                    'Für Altgeräte aus privaten Haushalten sind die '
                    'öffentlich-rechtlichen Entsorgungsträger zuständig, in der '
                    'Praxis Stadt, Landkreis oder deren Abfallbetrieb. Sie richten '
                    'Sammelstellen ein, an denen die Geräte angeliefert werden '
                    'können (§13 Absatz 1 ElektroG), und dürfen für die Anlieferung '
                    'kein Entgelt verlangen (§13 Absatz 4). Auch das Umweltbundesamt '
                    'nennt den Wertstoffhof an erster Stelle.',
                    'Manche Kommunen bieten mehr an: Schadstoffmobile, Container für '
                    'Kleingeräte auf öffentlichen Plätzen oder eine Abholung neben '
                    'dem Sperrmüll. Einige Kommunen bieten nach Angaben des '
                    'Umweltbundesamts auch eine anmeldepflichtige Abholung an der '
                    'Haustür an, gegebenenfalls gegen Gebühr. '
                    'Was in Ihrem Gebiet gilt, steht im Abfallkalender oder bei der '
                    'Abfallberatung der Kommune.',
                    '<strong>Wichtig bei großen Räumungen:</strong> Wer mehr als 20 '
                    'Geräte der Gruppen 1, 4 oder 6 anliefert, muss Ort und Zeitpunkt '
                    'vorher mit dem Entsorgungsträger abstimmen (§13 Absatz 5 '
                    'Satz 3). Gruppe 1 sind Wärmeüberträger, Gruppe 4 Großgeräte, '
                    'Gruppe 6 Photovoltaikmodule (§14 Absatz 1). Wer bei einer '
                    'Auflösung mehrere Großgeräte zusammen hat, ruft also besser vorher an.',
                    'Geben Sie Altgeräte nicht an Schrottsammler, die per '
                    'Postwurfsendung werben: Das Umweltbundesamt weist darauf hin, '
                    'dass diese in aller Regel keine Altgeräte sammeln dürfen und '
                    'die Gefahr einer nicht umweltgerechten Entsorgung besteht.',
                ],
            },
            {
                'id': 'handel',
                'titel': 'Rücknahme im Handel: die zwei Fälle und ihre Grenzen',
                'absaetze': [
                    'Der Handel ist nicht überall und nicht für alles zuständig. '
                    '§17 ElektroG verpflichtet Vertreiber mit mindestens 400 '
                    'Quadratmetern Verkaufsfläche für Elektrogeräte sowie '
                    'Lebensmittelhändler mit mindestens 800 Quadratmetern '
                    'Gesamtverkaufsfläche, die mehrmals im Kalenderjahr oder dauerhaft '
                    'Elektrogeräte anbieten. Für diese gelten '
                    'zwei Regeln:',
                ],
                'liste': [
                    '<strong>Mit Neukauf:</strong> Wer ein neues Gerät erhält, kann ein '
                    'Altgerät derselben Geräteart mit im Wesentlichen gleichen Funktionen '
                    'unentgeltlich abgeben. Bei Lieferung nach Hause ist die Abholung '
                    'kostenlos. Das Umweltbundesamt nennt als Beispiele Fernseher und Kühlschrank.',
                    '<strong>Ohne Neukauf:</strong> Altgeräte, die in keiner Abmessung größer '
                    'als 25 Zentimeter sind, nimmt der Händler auf Verlangen zurück, auch '
                    'ohne Kauf, höchstens drei Stück je Geräteart.',
                ],
                'absaetze': [
                    'Für eine Haushaltsauflösung heißt das: Der Neukauf-Fall passt '
                    'selten, und die Kleingeräte-Regel reicht bei einem vollen Haushalt '
                    'nicht. Die Hauptmenge geht deshalb zum Wertstoffhof. Manche '
                    'Händler nehmen laut Umweltbundesamt aus Kulanz mehr zurück; fragen '
                    'kostet nichts, ein Anspruch besteht darauf aber nicht.',
                    'Auch beim Online-Kauf gilt die Pflicht (§17 Absatz 2), dann '
                    'gerechnet nach der Lager- und Versandfläche des Anbieters; die '
                    'kostenlose Abholung ist dort auf die Gerätekategorien 1, 2 und 4 '
                    'beschränkt. Eine Ausnahme von den Flächengrenzen gilt für '
                    'elektronische Zigaretten und Tabakerhitzer: Wer sie im Sortiment '
                    'führt, muss sie als Altgeräte zurücknehmen (§17 Absatz 1a).',
                ],
            },
            {
                'id': 'getrennt',
                'titel': 'Warum Altgeräte nicht in Rest- oder Sperrmüll gehören',
                'absaetze': [
                    'Das Gesetz schreibt es vor: Endnutzer müssen Altgeräte einer '
                    'Erfassung zuführen, die vom unsortierten Siedlungsabfall getrennt '
                    'ist (§10 Absatz 1 ElektroG). Das Umweltbundesamt zählt die '
                    'verbotenen Wege auf: Hausmüll, Verpackungsmüll, Sperrmüll und '
                    'Metallschrott. Die Erfassung soll nach §10 Absatz 2 außerdem Brandrisiken '
                    'minimieren, und genau dort liegt das praktische Problem: '
                    'Falsch entsorgte batteriehaltige Altgeräte sorgen laut Umweltbundesamt '
                    'immer wieder für schwere Brände in Entsorgungsunternehmen.',
                    'Legen Sie Elektrogeräte deshalb nicht in die angemeldete '
                    'Sperrmüllmenge, es sei denn, Ihre Kommune bietet ausdrücklich eine '
                    'gemeinsame Abholung an. Fragen Sie bei der Anmeldung nach; mehr '
                    'zum Sperrmüll steht unter <a href="/sperrmuell-entsorgung/">'
                    'Sperrmüll-Entsorgung</a>.',
                    'Beim Räumen trennt Rümpelwerk Mitteldeutschland nach Fraktionen, '
                    'gibt Entsorgungen über zugelassene Entsorgungsbetriebe und '
                    'stellt auf Wunsch einen schriftlichen Entsorgungsnachweis aus. '
                    'Wie das bei einer <a href="/haushaltsaufloesung/">Haushaltsauflösung</a> '
                    'abläuft, steht dort.',
                ],
            },
            {
                'id': 'sonderfaelle',
                'titel': 'Sonderfälle: Lampen, Nachtspeicherheizungen, Geräte mit Akku',
                'absaetze': [
                    '<strong>Lampen</strong> in Leuchten und Geräten müssen vor der '
                    'Abgabe getrennt werden, wenn sie sich zerstörungsfrei entnehmen '
                    'lassen (§10 Absatz 1 Satz 2). Das Umweltbundesamt rät, sie '
                    'ebenfalls getrennt als Elektroaltgeräte abzugeben.',
                    '<strong>Nachtspeicherheizgeräte</strong> sind ein Sonderfall: '
                    'Enthalten sie Asbest oder sechswertiges Chrom, werden sie an der '
                    'Übergabestelle gesondert gesammelt (§14 Absatz 1 Satz 2). Der '
                    'Entsorgungsträger darf die kostenlose Annahme ablehnen, wenn '
                    'asbesthaltige Geräte nicht ordnungsgemäß durch Fachpersonal '
                    'abgebaut und verpackt wurden oder beschädigt ankommen (§13 '
                    'Absatz 5 Satz 2). Bauen Sie so ein Gerät nicht selbst aus, '
                    'sondern klären Sie den Weg vorab mit der Kommune.',
                    '<strong>Fest eingebaute Akkus</strong> in Smartphones, Laptops '
                    'oder Elektrowerkzeug: Batterien müssen nur getrennt werden, wenn '
                    'sie nicht vom Gerät umschlossen sind (§10 Absatz 1 Satz 2); '
                    'das Umweltbundesamt sagt „soweit möglich und zerstörungsfrei“ entnehmbar. '
                    'Lässt sich der Akku nicht herausnehmen, geben Sie das Gerät als Ganzes ab '
                    'und weisen das Personal darauf hin; batteriebetriebene Geräte der Gruppen 2, 4 und 5 werden '
                    'an der Übergabestelle in einem eigenen Behältnis gesammelt '
                    '(§14 Absatz 1 Satz 2). Lose Batterien und herausgenommene Akkus '
                    'gehören auf einen anderen Weg, beschrieben in '
                    '<a href="/ratgeber/batterien-akkus-entsorgen/">Batterien und Akkus '
                    'entsorgen</a>.',
                ],
            },
            {
                'id': 'daten',
                'titel': 'Daten auf Smartphone, Laptop und Festplatte',
                'absaetze': [
                    'Auf Smartphones, Tablets, Laptops und Festplatten sind '
                    'personenbezogene Daten gespeichert. Das Umweltbundesamt rät, sie '
                    'vor der Entsorgung zu löschen, und stellt klar: „Die '
                    'Verantwortung hierfür liegt bei den Verbraucher*innen selbst.“ '
                    'Für die Löschung verweist das Amt auf das Bundesamt für Sicherheit '
                    'in der Informationstechnik.',
                    'Bei einer Auflösung gilt deshalb eine feste Reihenfolge: erst '
                    'alle Speichermedien im Haushalt finden, dann prüfen, was daraus '
                    'zu sichern ist, erst danach löschen und entsorgen. Bei einem '
                    'Todesfall liegen auf alten Geräten oft Fotos und Dokumente, die '
                    'die Familie noch braucht; wie bei Papieren und Schmuck gilt '
                    'bei der <a href="/nachlassraeumung/">Nachlassräumung</a>: nichts '
                    'wegwerfen, bevor es die Angehörigen gesehen haben.',
                    'Ob und wie Erben auf Konten und Dateien einer verstorbenen Person '
                    'zugreifen dürfen, hängt vom Einzelfall ab und ist eine Frage für '
                    'eine Rechtsberatung.',
                ],
            },
        ],

        'faq': [
            ('Darf ich einen alten Kühlschrank zum Sperrmüll stellen?',
             'Nein, nicht in die normale Sperrmüllabfuhr. Elektroaltgeräte müssen '
             'getrennt vom unsortierten Siedlungsabfall erfasst werden (§10 Absatz 1 '
             'ElektroG). Geben Sie ihn beim Neukauf eines Kühlschranks an den Händler, '
             'am Wertstoffhof ab oder fragen Sie Ihre Kommune nach einer eigenen Abholung.'),
            ('Muss mir ein Händler Altgeräte abnehmen, wenn ich nichts kaufe?',
             'Nur Kleingeräte bis 25 Zentimeter, höchstens drei je Geräteart, und nur '
             'bei Händlern ab 400 Quadratmetern Elektro-Verkaufsfläche (bei Lebensmittel'
             'händlern ab 800 Quadratmetern Gesamtfläche). Größere Geräte müssen '
             'Händler nur beim Neukauf zurücknehmen; Ausnahme sind E-Zigaretten (§17 ElektroG).'),
            ('Kostet die Abgabe am Wertstoffhof etwas?',
             'Für die Anlieferung von Altgeräten darf der Entsorgungsträger kein '
             'Entgelt erheben (§13 Absatz 4 ElektroG). Kosten können bei einer Abholung '
             'an der Haustür entstehen; das richtet sich nach Ihrer Kommune.'),
            ('Wer ist für die Daten auf einem Gerät verantwortlich, das ich abgebe?',
             'Nach dem Umweltbundesamt liegt die Verantwortung für die Löschung '
             'persönlicher Daten bei Ihnen als Verbraucher. Löschen Sie vorher oder '
             'nehmen Sie den Datenträger heraus und behalten Sie ihn. Einzelfragen '
             'klärt eine Rechtsberatung.'),
        ],

        'leistungen': ['haushaltsaufloesung', 'wohnungsaufloesung', 'sperrmuell-entsorgung'],
        'staedte': [],
    },

    'erbe-ausschlagen-nachlass-raeumen': {
        'stand_iso': '2026-10',
        'kategorie': 'Erbe und Nachlass',
        'titel': 'Erbe ausschlagen und räumen',
        'h1': 'Erbe ausschlagen – und die Wohnung?',
        'h1_em': 'Frist, Form und die Vorsicht beim Räumen',
        'teaser': (
            'Die Ausschlagungsfrist läuft, die Wohnung ist noch voll: Was das '
            'Gesetz zu Frist und Form sagt, warum Räumen und Entscheiden '
            'zusammenhängen und was bis dahin nur gesichtet wird.'
        ),
        'seo_title': 'Erbe ausschlagen: 6 Wochen Frist und Räumung | Rümpelwerk',
        'seo_description': (
            'Sechs Wochen Ausschlagungsfrist (§1944 BGB): Was Sie vor der '
            'Entscheidung sichern, warum Räumen Folgen haben kann und wen Sie fragen.'
        ),
        'seo_keywords': ('erbe ausschlagen frist, erbschaft ausschlagen '
                         'wohnung räumen, ausschlagungsfrist nachlass, '
                         'erbschaft annahme durch verhalten, nachlass '
                         'räumen vor ausschlagung'),

        'answer_frage': 'Darf ich den Nachlass räumen, bevor ich über die Ausschlagung entschieden habe?',
        'answer': (
            'Räumen Sie vor der Entscheidung nichts unumkehrbar: Ob eine '
            'Räumung schon als Annahme zählt, hängt vom Einzelfall ab. Die '
            'Frist für die Ausschlagung beträgt nach §1944 BGB grundsätzlich '
            '6 Wochen; danach gilt die Erbschaft als angenommen (§1943 '
            'BGB). Sichten und sichern Sie deshalb nur, und holen Sie vorher '
            'Rechtsrat ein. Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'nachlass-bgb-1942', 'abschnitt': 'grundsatz',
             'bezug': 'Die Erbschaft geht auf den Erben über, unbeschadet '
                      'des Rechts zur Ausschlagung'},
            {'schluessel': 'nachlass-bgb-1944', 'abschnitt': 'frist',
             'bezug': 'Wortlaut zur sechswöchigen Frist, Fristbeginn und '
                      'Auslandsfrist'},
            {'schluessel': 'nachlass-bgb-1943', 'abschnitt': 'annahme',
             'bezug': 'Nach Annahme oder Fristablauf keine Ausschlagung '
                      'mehr; mit Fristablauf gilt die Erbschaft als angenommen'},
            {'schluessel': 'nachlass-bgb-1945', 'abschnitt': 'form',
             'bezug': 'Form der Ausschlagung und Vollmacht'},
            {'schluessel': 'nachlass-justiz-nrw', 'abschnitt': 'form',
             'bezug': 'Amtliche Hinweise zu Zuständigkeit, Formerfordernis '
                      'und schlüssigem Verhalten'},
            {'schluessel': 'nachlass-famfg-344', 'abschnitt': 'form',
             'bezug': 'Zuständigkeit auch des Gerichts am eigenen '
                      'gewöhnlichen Aufenthalt (Absatz 7)'},
            {'schluessel': 'nachlass-justiz-nrw', 'abschnitt': 'annahme',
             'bezug': 'Annahme kann sich aus schlüssigem Verhalten ergeben; '
                      'Sicherungsmaßnahmen müssen nicht Annahme bedeuten'},
            {'schluessel': 'nachlass-bgb-1953', 'abschnitt': 'grundsatz',
             'bezug': 'Wirkung der Ausschlagung: Anfall gilt als nicht erfolgt'},
            {'schluessel': 'nachlass-bgb-1959', 'abschnitt': 'vorher',
             'bezug': 'Geschäfte vor der Ausschlagung und Wirksamkeit '
                      'eilbedürftiger Verfügungen'},
            {'schluessel': 'nachlass-bgb-1960', 'abschnitt': 'vorher',
             'bezug': 'Das Nachlassgericht sorgt bis zur Annahme für die '
                      'Sicherung des Nachlasses, soweit ein Bedürfnis besteht'},
        ],

        'abschnitte': [
            {
                'id': 'grundsatz',
                'titel': 'Erst Erbe, dann vielleicht nicht mehr',
                'absaetze': [
                    'Nach §1942 Abs. 1 BGB geht die Erbschaft auf den '
                    'berufenen Erben über, „unbeschadet des Rechts“, sie '
                    'auszuschlagen. Wer also berufen ist, wird zunächst '
                    'Erbe und kann diese Stellung noch ausschlagen.',
                    'Schlägt jemand aus, gilt nach §1953 Abs. 1 BGB der '
                    'Anfall an ihn als nicht erfolgt. Ob eine Ausschlagung '
                    'sinnvoll ist, etwa bei erkennbaren Schulden, ist eine '
                    'Frage für Rechtsberatung, nicht für Räumkräfte.',
                ],
            },
            {
                'id': 'frist',
                'titel': 'Die Frist: sechs Wochen, Beginn mit Kenntnis',
                'absaetze': [
                    '§1944 Abs. 1 BGB: Die Ausschlagung kann nur binnen sechs '
                    'Wochen erfolgen. Die Frist beginnt nach Absatz 2 mit dem '
                    'Zeitpunkt, in dem der Erbe vom Anfall und dem Grund der '
                    'Berufung Kenntnis erlangt. Ist er durch Testament oder '
                    'Erbvertrag berufen, beginnt sie nicht vor der Bekanntgabe '
                    'der Verfügung durch das Nachlassgericht.',
                    'Die Frist beträgt sechs Monate, wenn der Erblasser seinen '
                    'letzten Wohnsitz nur im Ausland hatte oder wenn sich der '
                    'Erbe bei Fristbeginn im Ausland aufhält (Absatz 3). Auf '
                    'den Lauf der Frist sind die Verjährungsvorschriften der '
                    '§§206 und 210 BGB entsprechend anzuwenden; was das im '
                    'Einzelfall heißt, klärt die Rechtsberatung.',
                    'Rechnen Sie praktisch ab dem Tag, an dem Sie vom Todesfall '
                    'und Ihrer Berufung erfahren haben – und fragen Sie im '
                    'Zweifel beim Nachlassgericht nach, ob die Frist schon '
                    'läuft. Wenn ein Testament vorliegt, lesen Sie '
                    '<a href="/ratgeber/testament-beim-raeumen-gefunden/">'
                    'Testament beim Räumen gefunden</a>.',
                ],
            },
            {
                'id': 'form',
                'titel': 'Form und Zuständigkeit',
                'absaetze': [
                    '§1945 Abs. 1 BGB: Die Ausschlagung erfolgt durch Erklärung '
                    'gegenüber dem Nachlassgericht, zur Niederschrift des '
                    'Gerichts oder in öffentlich beglaubigter Form. Ein '
                    'Bevollmächtigter braucht nach Absatz 3 eine öffentlich '
                    'beglaubigte Vollmacht, die der Erklärung beigefügt oder '
                    'innerhalb der Frist nachgebracht werden muss.',
                    'Die Justiz Nordrhein-Westfalens beschreibt auf ihrer '
                    'Informationsseite, zuständig sei grundsätzlich das '
                    'Amtsgericht, in dessen Bezirk der Erblasser zuletzt seinen '
                    'gewöhnlichen Aufenthalt hatte. Nach §344 Absatz 7 FamFG '
                    'kann die Ausschlagung auch beim Nachlassgericht am eigenen '
                    'gewöhnlichen Aufenthalt erklärt werden, das sie '
                    'weiterleitet. Eine einfache Schriftform, privatschriftlich oder '
                    'telegrafisch, genüge nicht. Welches Gericht in Ihrem Fall '
                    'zuständig ist, erfragen Sie dort direkt.',
                ],
            },
            {
                'id': 'annahme',
                'titel': 'Wann Räumen zur Annahme werden kann',
                'absaetze': [
                    'Nach §1943 BGB kann der Erbe die Erbschaft nicht mehr '
                    'ausschlagen, wenn er sie angenommen hat oder wenn die '
                    'Frist verstrichen ist; mit Fristablauf gilt sie als '
                    'angenommen.',
                    'Die amtliche Informationsseite der Justiz NRW sagt dazu, '
                    'es genüge, wenn sich aus dem schlüssigen Verhalten ergebe, '
                    'dass die Erbin oder der Erbe die Erbschaft annehmen '
                    'möchte; genannt werden etwa die Geltendmachung von '
                    'Ansprüchen oder die Besitzergreifung. Wo die Grenze '
                    'zwischen bloßem Sichern und „Besitzergreifung“ verläuft, '
                    'lässt sich nicht allgemein sagen. Dieselbe Seite hält '
                    'fest, dass Sicherungsmaßnahmen oder die bloße Begleichung '
                    'der Beerdigungskosten nicht unbedingt eine Annahme '
                    'bedeuten müssen. Das hängt vom Einzelfall '
                    'ab; wer vor der Entscheidung räumen, verkaufen oder '
                    'verschenken will, lässt sich vorher rechtlich beraten.',
                ],
            },
            {
                'id': 'vorher',
                'titel': 'Was bis zur Entscheidung sinnvoll ist: sichten statt entsorgen',
                'absaetze': [
                    'Das Gesetz kennt die Zeit vor der Entscheidung ausdrücklich: '
                    'Wer vor der Ausschlagung erbschaftliche Geschäfte besorgt, '
                    'ist nach §1959 Abs. 1 BGB gegenüber dem späteren Erben wie '
                    'ein Geschäftsführer ohne Auftrag berechtigt und '
                    'verpflichtet; §1959 Abs. 2 BGB lässt eine Verfügung '
                    'über einen Nachlassgegenstand wirksam, wenn sie nicht ohne '
                    'Nachteil für den Nachlass verschoben werden konnte. Nach '
                    '§1960 Abs. 1 BGB hat außerdem bis zur Annahme das '
                    'Nachlassgericht für die Sicherung des Nachlasses zu sorgen, '
                    'soweit ein Bedürfnis besteht. Beides ersetzt keine '
                    'Beratung, zeigt aber, dass das Gesetz die Zeit vor der '
                    'Entscheidung kennt und Sicherung vorsieht.',
                    'Praktisch heißt das: Der Bestand bleibt bis zur '
                    'Entscheidung möglichst unverändert. Eine Sichtung – was ist da, was könnte '
                    'wertvoll oder wichtig sein, welche Papiere liegen '
                    'herum? – lässt sich jederzeit nachholen, ein '
                    'entsorgter Hausstand nicht. Halten Sie außerdem '
                    'schriftlich fest, wann Sie vom Todesfall erfahren haben '
                    'und wer die Schlüssel hat; beides kann für die Frist und '
                    'für spätere Rückfragen wichtig sein.',
                    'Konkret hilft diese Reihenfolge:',
                ],
                'liste': [
                    'Wohnung abschließen, Schlüsselübergabe notieren, Fotos vom '
                    'Zustand machen.',
                    'Unterlagen, Schmuck, Bargeld und Fotos zusammentragen und '
                    'verwahren, nicht aussortieren.',
                    'Verderbliches und Müll im Sinne von Hygiene entfernen – '
                    'und die Entscheidung dazu dokumentieren.',
                    'Mietwohnung: Kündigungsfragen vorab klären (siehe '
                    '<a href="/ratgeber/besenrein-wohnungsuebergabe/">besenrein '
                    'übergeben</a>).',
                    'Erst nach Klärung der Erbfrage die '
                    '<a href="/nachlassraeumung/">Nachlassräumung</a> '
                    'beauftragen – bei Rümpelwerk Mitteldeutschland werden '
                    'Fundstücke gesichert und den Angehörigen übergeben.',
                ],
            },
        ],

        'faq': [
            ('Wann beginnt die Sechs-Wochen-Frist?',
             'Mit dem Zeitpunkt, in dem der Erbe vom Anfall und vom Grund der '
             'Berufung Kenntnis erlangt (§1944 Abs. 2 BGB); bei Testament oder '
             'Erbvertrag nicht vor der Bekanntgabe durch das Nachlassgericht.'),
            ('Reicht eine E-Mail oder ein Brief ans Gericht für die Ausschlagung?',
             'Nein. Nach §1945 BGB erfolgt die Erklärung zur Niederschrift des '
             'Nachlassgerichts oder in öffentlich beglaubigter Form; die '
             'Justiz NRW weist darauf hin, dass einfache Schriftform nicht '
             'genügt.'),
            ('Darf ich schon den Müll rausbringen oder Schlüssel behalten?',
             'Ob einzelne Handlungen als Annahme gelten, hängt vom Einzelfall '
             'ab. Lassen Sie sich vor jeder Entscheidung, die sich nicht '
             'rückgängig machen lässt, rechtlich beraten.'),
            ('Wer berät mich zur Ausschlagung?',
             'Das Nachlassgericht nimmt die Erklärung entgegen (§1945 BGB). '
             'Ob Sie ausschlagen sollten, ist eine Rechtsfrage: Wenden Sie sich '
             'dafür an eine Rechtsberatung Ihrer Wahl.'),
        ],

        'leistungen': ['nachlassraeumung', 'wohnungsaufloesung'],
        'staedte': [],
    },

    'gewerbeabfall-bei-geschaeftsaufloesung': {
        'stand_iso': '2026-10',
        'kategorie': 'Vorbereitung und Übergabe',
        'titel': 'Gewerbeabfall bei Geschäftsauflösung',
        'h1': 'Gewerbeabfall bei der Geschäftsauflösung',
        'h1_em': 'Was die Gewerbeabfallverordnung vom Räumenden verlangt',
        'teaser': (
            'Wer ein Büro, Lager, eine Praxis oder einen Laden räumt, kann '
            'Abfallerzeuger oder Abfallbesitzer sein. Welche Fraktionen getrennt '
            'bleiben müssen, was zu dokumentieren ist und wo Ausnahmen gelten.'
        ),
        'seo_title': 'Gewerbeabfall bei Auflösung: 8 Fraktionen | Rümpelwerk',
        'seo_description': (
            'Büro, Lager oder Praxis räumen: Welche Abfälle die '
            'Gewerbeabfallverordnung getrennt verlangt und was zu dokumentieren '
            'ist. Jetzt lesen.'
        ),
        'seo_keywords': ('gewerbeabfallverordnung geschäftsauflösung, '
                         'gewerbeabfall getrennt sammeln, gewabfv '
                         'dokumentation, büro räumen entsorgung, '
                         'bau- und abbruchabfälle gewabfv'),

        'answer_frage': ('Welche Abfallpflichten gelten bei der Räumung '
                         'gewerblicher Räume?'),
        'answer': (
            'Die Pflicht zur Getrenntsammlung nach §3 GewAbfV umfasst acht '
            'Fraktionen: Erzeuger und Besitzer gewerblicher Siedlungsabfälle '
            'müssen unter anderem Papier, Glas, Kunststoffe, Metalle, Holz '
            'und Textilien getrennt sammeln und die Erfüllung dokumentieren. '
            'Ausnahmen gibt es bei technischer Unmöglichkeit oder '
            'wirtschaftlicher Unzumutbarkeit, sie müssen dargelegt werden. '
            'Abfälle, die dem Elektro- und Elektronikgerätegesetz '
            'unterliegen, fallen nicht unter die Verordnung. Rechtsstand: '
            '{stand}.'
        ),

        'quellen': [
            {'schluessel': 'gewabfv-1', 'abschnitt': 'geltungsbereich',
             'bezug': 'Anwendungsbereich der Verordnung und die '
                      'ausdrücklich ausgenommenen Abfälle (Absatz 4)'},
            {'schluessel': 'gewabfv-2', 'abschnitt': 'geltungsbereich',
             'bezug': 'Die Begriffe gewerbliche Siedlungsabfälle sowie '
                      'Bau- und Abbruchabfälle'},
            {'schluessel': 'krwg-3', 'abschnitt': 'geltungsbereich',
             'bezug': 'Wer Erzeuger und wer Besitzer von Abfällen ist '
                      '(Absätze 8 und 9)'},
            {'schluessel': 'gewabfv-3', 'abschnitt': 'trennen',
             'bezug': 'Die acht Fraktionen, die Ausnahmen und die '
                      'Dokumentation nach den Absätzen 1 bis 3'},
            {'schluessel': 'gewabfv-3', 'abschnitt': 'dokumentation',
             'bezug': 'Welche Nachweise Absatz 3 für Sammlung, Verwertung '
                      'und Abweichung nennt'},
            {'schluessel': 'gewabfv-4', 'abschnitt': 'ausnahmen',
             'bezug': 'Vorbehandlungspflicht für nicht getrennt gehaltene '
                      'Abfälle samt Entfallgründen und Dokumentation'},
            {'schluessel': 'gewabfv-5', 'abschnitt': 'ausnahmen',
             'bezug': 'Gemeinsame Erfassung geringer Mengen mit '
                      'Haushaltsabfall'},
            {'schluessel': 'gewabfv-8', 'abschnitt': 'bauabfall',
             'bezug': 'Zehn Fraktionen bei Bau- und Abbruchabfällen, '
                      'Ausnahmen und die 10-Kubikmeter-Grenze'},
            {'schluessel': 'krwg-7', 'abschnitt': 'geltungsbereich',
             'bezug': 'Verwertungspflicht von Erzeugern und Besitzern '
                      'nach Absatz 2 und deren Grenze nach Absatz 4'},
        ],

        'abschnitte': [
            {
                'id': 'geltungsbereich',
                'titel': 'Wen die Verordnung trifft und was sie nicht erfasst',
                'absaetze': [
                    'Die Gewerbeabfallverordnung richtet sich an „Erzeuger und '
                    'Besitzer“ bestimmter Abfälle (§1 Absatz 2 GewAbfV). '
                    'Erzeuger ist nach dem Kreislaufwirtschaftsgesetz jede '
                    'Person, durch deren Tätigkeit Abfälle anfallen oder die sie '
                    'so vorbehandelt oder mischt, dass sich ihre Beschaffenheit '
                    'verändert; Besitzer ist, wer '
                    'die tatsächliche Sachherrschaft darüber hat (§3 Absatz 8 '
                    'und 9 KrWG). Bei einer Geschäftsauflösung kann das der '
                    'Betriebsinhaber sein oder wer sonst die Sachherrschaft hat – '
                    'wer es im Einzelfall ist, hängt von den Umständen ab. '
                    'Das Gesetz verpflichtet beide zur Verwertung ihrer '
                    'Abfälle, soweit das technisch möglich und wirtschaftlich '
                    'zumutbar ist (§7 Absatz 2 und 4 KrWG).',
                    'Die Verordnung unterscheidet zwei Abfallgruppen: '
                    'gewerbliche Siedlungsabfälle – Siedlungsabfälle aus anderen '
                    'Herkunftsbereichen als privaten Haushaltungen, insbesondere '
                    'gewerbliche und industrielle Abfälle sowie Abfälle aus '
                    'privaten und öffentlichen Einrichtungen, die Haushaltsabfällen '
                    'ähnlich sind – und Bau- und '
                    'Abbruchabfälle aus Kapitel 17 des Abfallverzeichnisses, '
                    'ausgenommen Boden und Steine der Gruppe 17 05 '
                    '(§2 Nummer 1 und 3 GewAbfV).',
                    'Ausdrücklich nicht erfasst sind Abfälle, die dem '
                    'Elektro- und Elektronikgerätegesetz unterliegen, sowie '
                    'Batterien (§1 Absatz 4 GewAbfV). Computer, Monitore und '
                    'Kopierer aus einem Büro laufen also nicht über die '
                    'Fraktionen dieses Artikels, sondern über ihren eigenen '
                    'Rücknahme- und Entsorgungsweg.',
                ],
            },
            {
                'id': 'trennen',
                'titel': 'Die acht Fraktionen, die getrennt bleiben müssen',
                'absaetze': [
                    '§3 Absatz 1 GewAbfV verlangt, die folgenden Fraktionen '
                    'jeweils getrennt zu sammeln und zu befördern und '
                    'vorrangig der Vorbereitung zur Wiederverwendung oder dem '
                    'Recycling zuzuführen:',
                ],
                'liste': [
                    'Papier, Pappe und Karton (ohne Hygienepapier) – etwa '
                    'Ordner und Verpackungen',
                    'Glas',
                    'Kunststoffe',
                    'Metalle – zum Beispiel Regale, Aktenschränke, '
                    'Rollcontainer',
                    'Holz – etwa Schreibtische, Regalböden, Theken',
                    'Textilien',
                    'Bioabfälle, getrennt nach verpackten und unverpackten',
                    'weitere Abfallfraktionen, die in den „weiteren“ '
                    'gewerblichen und industriellen Abfällen nach §2 Nummer 1 '
                    'Buchstabe b enthalten sind',
                ],
            },
            {
                'id': 'ausnahmen',
                'titel': 'Wann die Trennung entfällt und was dann gilt',
                'absaetze': [
                    'Wer die Fraktionen noch feiner trennen will, darf das. '
                    'Gefährliche Abfälle – etwa Farben, Lösemittel oder '
                    'Chemikalien aus Lager oder Praxis, sofern sie als '
                    'gefährlich einzustufen sind – dürfen grundsätzlich nicht '
                    'mit anderen Abfällen vermischt werden; das '
                    'Vermischungsverbot des §9a KrWG (mit eng begrenzten '
                    'Ausnahmen in dessen Absatz 2) bleibt ausdrücklich '
                    'unberührt.',
                    'Praktisch heißt das beim Räumen: Behälter oder '
                    'Bereiche je Fraktion einrichten, bevor das erste Möbel '
                    'bewegt wird. So lässt sich die getrennte Sammlung später '
                    'auch belegen.',
                    'Die Pflicht entfällt, „soweit die getrennte Sammlung der '
                    'jeweiligen Abfallfraktion technisch nicht möglich oder '
                    'wirtschaftlich nicht zumutbar ist“ (§3 Absatz 2 Satz 1 '
                    'GewAbfV). Die Verordnung nennt Beispiele: Technisch '
                    'nicht möglich ist die Trennung insbesondere, wenn für '
                    'zusätzliche Abfallbehälter nicht genug Platz ist. '
                    'Wirtschaftlich nicht zumutbar ist sie, wenn die Kosten '
                    'außer Verhältnis zu einer gemischten Sammlung mit '
                    'anschließender Vorbehandlung stehen, insbesondere wegen '
                    'einer sehr geringen Menge der Fraktion.',
                    'Das ist keine Pauschalbefreiung. Wer sich darauf '
                    'beruft, muss den Grund darlegen (siehe nächster '
                    'Abschnitt). Für geringe Mengen sieht §5 GewAbfV '
                    'außerdem vor, dass Gewerbeabfälle gemeinsam mit den auf '
                    'dem Grundstück anfallenden Haushaltsabfällen in den dafür '
                    'vorgesehenen Behältern '
                    'erfasst werden dürfen, wenn die Pflichten nach §3 und '
                    '§4 wirtschaftlich nicht zumutbar sind.',

                    'Entfällt die Trennpflicht zu Recht, gilt für die nicht '
                    'getrennt gehaltenen Abfälle eine Folgepflicht: Sie sind '
                    'unverzüglich einer Vorbehandlungsanlage zuzuführen '
                    '(§4 Absatz 1 GewAbfV) – einer Anlage, in der die Abfälle '
                    'insbesondere sortiert oder zerkleinert werden. Abfälle '
                    'aus der Human- und Tiermedizin dürfen in diesen '
                    'Gemischen nicht enthalten sein (Kapitel 18 des '
                    'Abfallverzeichnisses); das ist bei '
                    'Praxisauflösungen zu beachten. Bei der ersten Übergabe '
                    'verlangt die Verordnung eine Bestätigung des '
                    'Anlagenbetreibers in Textform, dass die Anlage die '
                    'technischen Anforderungen erfüllt (§4 Absatz 2).',
                    'Auch hier gibt es Ausnahmen, etwa bei technischer '
                    'Unmöglichkeit oder wirtschaftlicher Unzumutbarkeit '
                    '(§4 Absatz 3), und auch hier ist zu dokumentieren '
                    '(§4 Absatz 5). Dann sind die Gemische getrennt zu halten '
                    'und vorrangig einer hochwertigen sonstigen, insbesondere '
                    'energetischen Verwertung zuzuführen (§4 Absatz 4).',
                ],
            },
            {
                'id': 'dokumentation',
                'titel': 'Was zu dokumentieren ist',
                'absaetze': [
                    '§3 Absatz 3 GewAbfV verlangt, die Erfüllung der '
                    'Trennpflicht zu dokumentieren – oder, wenn man davon '
                    'abweicht, die Gründe. Die Verordnung nennt drei '
                    'Bausteine:',
                ],
                'schritte': [
                    '<strong>Die getrennte Sammlung belegen</strong> durch '
                    'Lagepläne, Lichtbilder und Praxisbelege wie Liefer- '
                    'oder Wiegescheine. Fotos der aufgestellten Behälter '
                    'vom Räumungstag können also als Beleg dienen.',
                    '<strong>Die Verwertung belegen</strong> durch eine '
                    'Erklärung desjenigen, der die Abfälle übernimmt. Sie '
                    'muss dessen Namen und Anschrift, die Masse, die '
                    'Verwertungsart und den beabsichtigten Verbleib '
                    'enthalten. Fragen Sie den Entsorger vorab, ob seine '
                    'Belege diese Angaben tragen.',
                    '<strong>Eine Abweichung begründen</strong> durch eine '
                    'Darlegung der technischen Unmöglichkeit oder '
                    'wirtschaftlichen Unzumutbarkeit.',
                ],
            },
            {
                'id': 'bauabfall',
                'titel': 'Bau- und Abbruchabfälle: eigene Fraktionen, eigene '
                         'Bagatellgrenze',
                'absaetze': [
                    'Fallen bei der Räumung auch Bau- oder Abbrucharbeiten '
                    'an – ausgebaute Böden, Fliesen, Dämmung –, gilt für '
                    'diese Abfälle §8 GewAbfV. Er nennt zehn Fraktionen, die '
                    'getrennt zu sammeln sind: Glas, Kunststoff, Metalle, '
                    'Holz, Dämmmaterial, Bitumengemische, Baustoffe auf '
                    'Gipsbasis, Beton, Ziegel sowie Fliesen und Keramik. '
                    'Die Ausnahmen entsprechen im Kern denen für '
                    'Siedlungsabfälle; bei mineralischen Abfällen kommen '
                    'rückbaustatische und rückbautechnische Gründe hinzu.',
                    'Die Dokumentationspflicht nach §8 Absatz 3 gilt nicht für '
                    'Maßnahmen, bei denen insgesamt höchstens 10 Kubikmeter '
                    'Abfälle anfallen. Die Pflicht zur getrennten Sammlung '
                    'selbst bleibt davon nach dem Wortlaut unberührt. Wo '
                    'die Grenze zwischen bloßer Räumung und Bauarbeit '
                    'verläuft, klären Sie bei Zweifeln mit der zuständigen '
                    'Behörde.',
                    'Beim Räumen trennt Rümpelwerk Mitteldeutschland nach '
                    'Fraktionen, gibt Entsorgungen an zugelassene '
                    'Entsorgungsbetriebe und stellt auf Wunsch einen '
                    'schriftlichen Entsorgungsnachweis aus. Weitere '
                    'Informationen zur Räumung von Gewerbeflächen finden Sie '
                    'unter <a href="/gewerbeentruempelung/">Gewerbeentrümpelung'
                    '</a>.',
                ],
            },
        ],

        'faq': [
            ('Gilt die Gewerbeabfallverordnung auch für eine kleine Praxis '
             'oder ein Einzelhandelsgeschäft?',
             'Der Anwendungsbereich knüpft an Abfallart und Herkunft an '
             '(§1, §2 GewAbfV): Die Verordnung gilt für gewerbliche '
             'Siedlungsabfälle und bestimmte Bau- und Abbruchabfälle. Bei '
             'sehr geringen Mengen kann die Trennung wirtschaftlich nicht '
             'zumutbar sein; für diesen Fall erlaubt §5 GewAbfV die '
             'gemeinsame Erfassung mit den auf dem Grundstück anfallenden '
             'Haushaltsabfällen in den vorgesehenen Behältern. Eine eigene '
             'Dokumentationspflicht nennt §5 dafür nicht; dass die Menge '
             'gering ist, sollten Sie im Streitfall aber belegen können.'),
            ('Müssen alte Computer und Drucker getrennt gesammelt werden?',
             'Nicht nach dieser Verordnung: Abfälle, die dem Elektro- und '
             'Elektronikgerätegesetz unterliegen, sind vom Anwendungsbereich '
             'ausgenommen (§1 Absatz 4 GewAbfV). Sie gehören auf den '
             'dafür vorgesehenen Entsorgungsweg. Das gilt ebenso für '
             'Batterien.'),
            ('Wer muss die Dokumentation aufbewahren und vorlegen?',
             'Die Pflicht trifft Erzeuger und Besitzer der Abfälle. Die '
             'Dokumentation ist der zuständigen Behörde auf Verlangen '
             'vorzulegen, auf Verlangen auch elektronisch (§3 Absatz 3 '
             'Satz 3 GewAbfV). Eine Aufbewahrungsfrist für die '
             'Dokumentation nennt §3 GewAbfV nicht; fragen Sie dazu die '
             'zuständige Behörde.'),
            ('Ersetzt ein Entsorgungsnachweis die Dokumentation?',
             'Nicht automatisch. Die Verordnung nennt für die Verwertung '
             'eine Erklärung des Übernehmers mit Name, Anschrift, Masse, '
             'Verwertungsart und Verbleib. Hinzu kommen Lichtbilder oder '
             'Lagepläne zur getrennten Sammlung. Ein Nachweis hilft, wenn er '
             'diese Angaben enthält; ob das im Einzelfall genügt, beurteilt '
             'die Behörde.'),
        ],

        'leistungen': ['gewerbeentruempelung'],
        'staedte': [],
    },

    'schadstoffe-im-haushalt-farben-lacke-chemikalien': {
        'stand_iso': '2026-10',
        'kategorie': 'Entsorgung und Schadstoffe',
        'titel': 'Schadstoffe im Haushalt',
        'h1': 'Schadstoffe im Haushalt: Farben, Lacke, Chemikalien',
        'h1_em': 'Was als Schadstoff gilt und wohin damit',
        'teaser': (
            'Farbreste, Lösemittel, Pflanzenschutzmittel, Leuchtstoffröhren: '
            'Was Kommunen als Schadstoff sammeln, was das Kreislaufwirtschafts'
            'gesetz verlangt und was nie in den Ausguss gehört.'
        ),
        'seo_title': 'Schadstoffe entsorgen: Beispiel Halle (Saale) | Rümpelwerk',
        'seo_description': (
            'Farben, Lacke, Lösemittel und Chemikalien beim Entrümpeln: '
            'Schadstoffmobil, Annahmestelle und gesetzliche Pflichten nach '
            'KrWG. Jetzt informieren.'
        ),
        'seo_keywords': ('schadstoffe entsorgen, farben lacke entsorgen, '
                         'schadstoffmobil, problemstoffe haushalt, '
                         'lösemittel entsorgen, altöl entsorgen, '
                         'leuchtstoffröhren entsorgen, giftmüll entrümpelung'),

        'answer_frage': 'Wohin mit Farben, Lacken und Chemikalien aus dem Haushalt?',
        'answer': (
            'Farben, Lacke und Chemikalien aus dem Haushalt gehören zur '
            'Schadstoffsammlung, also zum Schadstoffmobil oder zur '
            'kommunalen Annahmestelle, nicht in Restmüll oder Ausguss. Unter '
            'Schadstoffen versteht man dabei flüssige Farben und Lacke, '
            'Lösemittel, Pflanzenschutzmittel und andere Chemikalien. '
            'Haushalte müssen solche Abfälle grundsätzlich dem '
            'öffentlich-rechtlichen Entsorgungsträger überlassen (§17 KrWG); '
            'was genau angenommen wird, regelt Ihre Kommune. Rechtsstand: '
            '{stand}.'
        ),

        'quellen': [
            {'schluessel': 'uba-ratgeber-haushalt', 'abschnitt': 'begriff',
             'bezug': 'Das Umweltbundesamt zählt die Problemstoffe aus dem '
                      'Haushalt auf und stellt klar, dass es keine einheitliche '
                      'Definition gibt'},
            {'schluessel': 'schadstoff-halle-abfallabc', 'abschnitt': 'begriff',
             'bezug': 'Die Stadt Halle (Saale) nennt als Beispiel einer '
                      'Kommune ihre Liste schadstoffhaltiger Haushaltsabfälle'},
            {'schluessel': 'krwg-17', 'abschnitt': 'recht',
             'bezug': 'Abfälle aus privaten Haushalten sind dem '
                      'öffentlich-rechtlichen Entsorgungsträger zu überlassen; '
                      'Rücknahmepflichten bilden eine Ausnahme'},
            {'schluessel': 'krwg-20', 'abschnitt': 'recht',
             'bezug': 'Die Entsorgungsträger sammeln gefährliche Abfälle so, '
                      'dass sie sich nicht mit anderen Abfällen vermischen'},
            {'schluessel': 'krwg-9', 'abschnitt': 'recht',
             'bezug': 'Abfälle sind getrennt zu sammeln, soweit dies für die '
                      'Verwertung erforderlich ist'},
            {'schluessel': 'krwg-3', 'abschnitt': 'recht',
             'bezug': 'Welche Abfälle als gefährlich gelten, bestimmt eine '
                      'Rechtsverordnung'},
            {'schluessel': 'schadstoff-halle-abfallabc', 'abschnitt': 'annahme',
             'bezug': 'Beispiel Halle: Schadstoffannahmestelle und '
                      'Schadstoffmobil, Gebinde bis 25 Liter gebührenfrei, '
                      'Altöl über den Handel'},
            {'schluessel': 'schadstoff-halle-mobil', 'abschnitt': 'annahme',
             'bezug': 'Beispiel Halle: Standort und Termin des '
                      'Schadstoffmobils'},
            {'schluessel': 'uba-ratgeber-haushalt', 'abschnitt': 'annahme',
             'bezug': 'Schadstoffmobile oder stationäre Sammelstellen nehmen '
                      'Problemstoffe zurück; Leuchtstoffröhren und '
                      'Energiesparlampen enthalten Quecksilber'},
            {'schluessel': 'schadstoff-uba-toilette', 'abschnitt': 'alltag',
             'bezug': 'Farb- und Lackreste sowie Lösungsmittel gehören nicht '
                      'in die Toilette; flüssige Reste müssen zur '
                      'Schadstoffsammelstelle'},
            {'schluessel': 'krwg-15', 'abschnitt': 'alltag',
             'bezug': 'Abfälle sind so zu beseitigen, dass das Wohl der Allgemeinheit nicht beeinträchtigt wird; dazu zählt, dass Gewässer oder Böden nicht schädlich beeinflusst werden'},
            {'schluessel': 'schadstoff-uba-haushalt', 'abschnitt': 'begriff',
             'bezug': 'Schadstoffe wie flüssige Farben und Lacke, Haushalts- '
                      'und Gartenchemikalien, Klebstoffe und Altöle gehören '
                      'nicht in den Restmüll'},
        ],

        'abschnitte': [
            {
                'id': 'begriff',
                'titel': 'Was als Schadstoff aus dem Haushalt gilt',
                'absaetze': [
                    'Einen einheitlichen Begriff gibt es nicht. Das '
                    'Umweltbundesamt nennt „Problemabfälle“, „Problemstoffe“ '
                    'und „Schadstoffe“ nebeneinander und schreibt, dass die '
                    'Kommunen in ihrer Abfallwirtschaftssatzung festlegen, '
                    'was nicht in die graue Tonne darf. Als Beispiele führt '
                    'es auf: Farbreste, Pflanzenschutz- und '
                    'Schädlingsbekämpfungsmittel, Chemikalienreste aus Hobby und Handwerk wie Fixierbäder und Klebstoffe, Fahrzeugpflege- und Betriebsmittel wie Motorenöle, Lösemittelreste, Batterien und Akkus, '
                    'Leuchtstoffröhren und Energiesparlampen.',
                    'Die Stadt Halle (Saale) führt als Beispiel einer '
                    'Kommune zusätzlich Säuren, Laugen, Fotochemikalien, '
                    'Frostschutz- und Autopflegemittel sowie schadstoffhaltige '
                    'Verpackungen wie PU-Schaumdosen auf. Zu den Zeichen auf '
                    'der Verpackung rät sie: Symbole und Sicherheitshinweise '
                    'beachten.',
                    'Eine Unterscheidung spart Wege: Eingetrocknete Farben und '
                    'Lacke gehören nach UBA-Angaben in die Restmülltonne, '
                    'flüssige in die Problemstoffsammlung; bei '
                    'Dispersionsfarben nennt das UBA eine Ausnahme und rät, '
                    'die Abfallberatung der Kommune zu fragen. Asbest ist '
                    'ein Sonderfall mit eigenen Regeln, mehr dazu in '
                    '<a href="/ratgeber/asbest-im-haushalt/">Asbest im Altbau '
                    'und beim Räumen</a>.',
                ],
            },
            {
                'id': 'recht',
                'titel': 'Der gesetzliche Rahmen',
                'absaetze': [
                    '§17 Abs. 1 des Kreislaufwirtschaftsgesetzes (KrWG) '
                    'verpflichtet Erzeuger und Besitzer von Abfällen aus '
                    'privaten Haushalten, diese dem öffentlich-rechtlichen '
                    'Entsorgungsträger zu überlassen, also der nach Landesrecht zuständigen juristischen Person, etwa Stadt oder Landkreis. '
                    'Ausgenommen sind nach Absatz 2 unter anderem Abfälle, '
                    'für die eine Rücknahmepflicht besteht; so verweist '
                    'Halle für Motoren- und Getriebeöle auf den Handel.',
                    'Die Entsorgungsträger müssen gefährliche Abfälle aus '
                    'Haushalten getrennt sammeln und sicherstellen, dass '
                    'sie sich dabei nicht mit anderen Abfällen vermischen '
                    '(§20 Abs. 2 Nr. 8 KrWG). Allgemein verlangt §9 Abs. 1 '
                    'KrWG die getrennte Sammlung, soweit sie für die '
                    'Verwertung erforderlich ist. Wer ein Gebinde in die Restmülltonne oder den Sperrmüll wirft, verstößt zudem gegen die Vorgaben der Kommune, die in ihrer Abfallwirtschaftssatzung festlegt, was nicht in die graue Tonne darf. Welche Abfälle als „gefährlich“ gelten, '
                    'bestimmt eine Rechtsverordnung (§3 Abs. 5 KrWG); für '
                    'den Alltag genügt die Faustregel der Kommunen.',
                    'Das ist eine Orientierung, keine Rechtsberatung. Was '
                    'im Einzelfall zu tun ist, sagt die Abfallberatung Ihres '
                    'Entsorgungsträgers.',
                ],
            },
            {
                'id': 'annahme',
                'titel': 'Schadstoffmobil, Annahmestelle und Wertstoffhof',
                'absaetze': [
                    'Nach UBA-Angaben sammeln Schadstoffmobile die Abfälle '
                    'ein, oder sie werden bei stationären Systemen wie '
                    'Problemstoffsammelstellen oder Wertstoffhöfen '
                    'abgegeben. Welche Stelle was annimmt, entscheidet vor '
                    'Ort der Entsorger.',
                    'Als Beispiel: In Halle (Saale) steht das Schadstoffmobil der HWS nach einer Mitteilung der Stadt vom 24.06.2024 (Stand dieser Mitteilung, Termin und Standort können sich ändern) grundsätzlich am ersten Montag im Monat von 10 bis 17 Uhr auf dem Hallmarkt. Zusätzlich gibt es die Schadstoffannahmestelle '
                    'in der Äußeren Hordorfer Straße 12. Gebinde bis 25 Liter '
                    'sind gebührenfrei, möglichst in der Originalverpackung. '
                    'Motoren- und Getriebeöle nimmt die HWS nur kostenpflichtig '
                    'an der Annahmestelle an, nicht am Mobil; PU-Schaumdosen '
                    'müssen Hersteller und Vertreiber unentgeltlich '
                    'zurücknehmen. Aktuelle Termine stehen beim Entsorger (HWS) und bei der städtischen Abfallberatung, '
                    'Mengen über 25 Liter und Gewerbeabfall klären Sie vorab.',
                    'Leuchtstoffröhren und Energiesparlampen enthalten '
                    'nach UBA-Angaben geringe Mengen Quecksilber und dürfen '
                    'nicht in den Hausmüll. Sie gehen zur kommunalen '
                    'Sammelstelle oder zum Handel; Schadstoffmobile nehmen '
                    'sie oft ebenfalls an. Wer alte Geräte und Lampen '
                    'mitzugeben hat, findet mehr unter '
                    '<a href="/ratgeber/elektroaltgeraete-entsorgen/">'
                    'Elektroaltgeräte entsorgen</a> und '
                    '<a href="/ratgeber/batterien-akkus-entsorgen/">Batterien '
                    'und Akkus entsorgen</a>.',
                ],
            },
            {
                'id': 'alltag',
                'titel': 'Aufbewahren, mitnehmen, nicht ausgießen',
                'absaetze': [
                    'Für Lagerung und Transport gibt es vor allem einen '
                    'amtlichen Rat: Schadstoffe möglichst in der Originalverpackung '
                    'abzugeben und die Symbole auf dem Etikett zu beachten. '
                    'Alles Weitere, etwa Mengenlimits oder Pflichten beim '
                    'Fahren, klären Sie bei Ihrem Entsorger.',
                    'Klar ist dagegen, was nicht geschehen darf. Farb- und '
                    'Lackreste sowie Lösungsmittel gehören laut UBA nicht in '
                    'die Toilette: Sie können die Bausubstanz und Technik der '
                    'Abwasseranlagen angreifen und den biologischen Abbau '
                    'in der Kläranlage gefährden. Abfälle über Toilette oder '
                    'Ausguss zu entsorgen, ist nach UBA-Darstellung '
                    'grundsätzlich verboten. Und §15 Abs. 2 KrWG verlangt, Abfälle so zu beseitigen, dass das Wohl der Allgemeinheit nicht beeinträchtigt wird; eine Beeinträchtigung liegt insbesondere vor, wenn Gewässer oder Böden schädlich beeinflusst werden. Wer Reste im Garten oder auf dem Hof auskippt, riskiert genau das. Manche '
                    'Baumärkte nehmen Reste zurück; fragen Sie beim Kauf '
                    'danach.',
                ],
            },
            {
                'id': 'raeumung',
                'titel': 'So gehen Sie bei einer Räumung vor',
                'absaetze': [
                    'Gerade bei Haushalts- und Kellerauflösungen steht oft '
                    'ein Regal voll Restbestände. Eine Reihenfolge, die '
                    'sich bewährt:',
                ],
                'schritte': [
                    '<strong>Gebinde sichten und beiseite stellen.</strong> '
                    'Alles mit Gefahrensymbol, Lösemittel, Spritzmittel für '
                    'den Garten, Altöl: nicht ausgießen, nicht umfüllen, '
                    'getrennt vom übrigen Räumgut halten.',
                    '<strong>Eingetrocknet oder flüssig?</strong> Das '
                    'entscheidet nach UBA über Restmüll oder Schadstoffsammlung. '
                    'Im Zweifel die Abfallberatung fragen.',
                    '<strong>Annahmeweg und Termin klären:</strong> '
                    'Schadstoffmobil, Annahmestelle oder Wertstoffhof, '
                    'Mengengrenze, Öffnungszeit, Gebühr.',
                    '<strong>Rücknahme nutzen,</strong> wo sie besteht, etwa '
                    'für Altöl oder Batterien über den Handel.',
                    '<strong>Bei größeren Mengen früh Bescheid geben.</strong> '
                    'Rümpelwerk Mitteldeutschland stellt Gebinde mit '
                    'Farben, Lacken oder Chemikalien beim Räumen getrennt und '
                    'bespricht mit Ihnen den Annahmeweg. Nennen Sie '
                    'Schadstoffe bei der kostenlosen Besichtigung, damit '
                    'sie in den Ablauf passen. Mehr zu den Leistungen: '
                    '<a href="/kellerentruempelung/">Kellerentrümpelung</a> '
                    'und <a href="/haushaltsaufloesung/">Haushaltsauflösung</a>.',
                ],
            },
        ],

        'faq': [
            ('Darf ich Farbreste in die Restmülltonne werfen?',
             'Eingetrocknete Farben und Lacke ja, sagt das Umweltbundesamt. '
             'Flüssige gehören in die Problemstoffsammlung; für '
             'Dispersionsfarben nennt das UBA eine Ausnahme und rät, die '
             'kommunale Abfallberatung zu fragen.'),
            ('Was kostet die Abgabe am Schadstoffmobil?',
             'Das legt der Entsorger fest. In Halle (Saale) ist die Abgabe '
             'von Gebinden bis 25 Liter gebührenfrei, bei Altöl nennt die '
             'Stadt Ausnahmen. Fragen Sie bei Ihrem Entsorger nach.'),
            ('Wohin mit Leuchtstoffröhren?',
             'Nicht in den Hausmüll. Nach UBA-Angaben nehmen kommunale '
             'Sammelstellen wie Wertstoffhöfe, oft auch Schadstoffmobile '
             'und der Handel sie an, weil sie Quecksilber enthalten.'),
            ('Was passiert, wenn ich Reste in den Abfluss kippe?',
             'Sie können laut UBA Abwasseranlagen angreifen und den '
             'biologischen Abbau in der Kläranlage stören. Abfälle über '
             'den Ausguss zu entsorgen, ist grundsätzlich verboten.'),
        ],

        'leistungen': ['haushaltsaufloesung', 'kellerentruempelung',
                       'sperrmuell-entsorgung'],
        'staedte': ['halle'],
    },

    'testament-beim-raeumen-gefunden': {
        'stand_iso': '2026-10',
        'kategorie': 'Erbe und Nachlass',
        'titel': 'Testament beim Räumen gefunden',
        'h1': 'Testament beim Räumen gefunden',
        'h1_em': 'Abliefern, nicht aussortieren',
        'teaser': (
            'Ein Umschlag mit „Mein letzter Wille“ in der Schublade: Was das '
            'Gesetz zur Ablieferung sagt, wer das Testament eröffnet und wie '
            'Sie Fundstücke bis dahin sichern.'
        ),
        'seo_title': 'Testament gefunden: Ablieferung nach §2259 BGB | Rümpelwerk',
        'seo_description': (
            'Testament bei der Nachlassräumung gefunden? Was § 2259 BGB '
            'verlangt, wer es eröffnet und wie Sie Fundstücke richtig sichern.'
        ),
        'seo_keywords': ('testament gefunden, testament abliefern, '
                         'ablieferungspflicht testament, erbvertrag gefunden, '
                         'nachlassgericht testament eröffnen, '
                         'nachlassräumung testament'),

        'answer_frage': 'Was muss ich tun, wenn ich beim Räumen ein Testament finde?',
        'answer': (
            'Ein gefundenes Testament sichern Sie unverändert und liefern es '
            'beim Nachlassgericht ab. Die Ablieferungspflicht nach §2259 '
            'BGB bedeutet: Wer ein Testament besitzt, das nicht in '
            'besonderer amtlicher Verwahrung liegt, muss es unverzüglich '
            'abliefern, sobald er vom Tod des Erblassers weiß. Für einen '
            'Erbvertrag gilt das entsprechend (§2300 BGB). Den Fund deshalb '
            'nicht aussortieren. Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'nachlass-bgb-2259', 'abschnitt': 'pflicht',
             'bezug': 'Wortlaut der Ablieferungspflicht für Testamente, auch '
                      'für Testamente bei einer anderen Behörde'},
            {'schluessel': 'nachlass-bgb-2300', 'abschnitt': 'pflicht',
             'bezug': 'Die Ablieferungspflicht gilt entsprechend für den '
                      'Erbvertrag'},
            {'schluessel': 'nachlass-famfg-343', 'abschnitt': 'eroeffnung',
             'bezug': 'Örtliche Zuständigkeit: Gericht des gewöhnlichen '
                      'Aufenthalts des Erblassers zur Todeszeit'},
            {'schluessel': 'nachlass-famfg-344', 'abschnitt': 'eroeffnung',
             'bezug': 'Ist ein anderes Gericht Verwahrer, eröffnet dieses'},
            {'schluessel': 'nachlass-famfg-348', 'abschnitt': 'eroeffnung',
             'bezug': 'Das Gericht eröffnet die in seiner Verwahrung '
                      'befindliche Verfügung und kann einen Termin ansetzen'},
            {'schluessel': 'nachlass-bgb-2255', 'abschnitt': 'nicht-vernichten',
             'bezug': 'Widerruf durch Vernichtung ist im Gesetz an die '
                      'Absicht des Erblassers geknüpft'},
            {'schluessel': 'nachlass-stgb-274', 'abschnitt': 'nicht-vernichten',
             'bezug': 'Strafnorm zur Urkundenunterdrückung'},
            {'schluessel': 'nachlass-bgb-1944', 'abschnitt': 'danach',
             'bezug': 'Ausschlagungsfrist beginnt bei Verfügung von Todes '
                      'wegen nicht vor Bekanntgabe durch das Nachlassgericht'},
        ],

        'abschnitte': [
            {
                'id': 'pflicht',
                'titel': 'Die Pflicht zur Ablieferung',
                'absaetze': [
                    'Das Gesetz sagt es knapp: Wer ein Testament besitzt, das '
                    'nicht in besondere amtliche Verwahrung gebracht wurde, muss '
                    'es „unverzüglich“ an das Nachlassgericht abliefern, sobald '
                    'er vom Tod des Erblassers erfahren hat (§2259 Abs. 1 BGB). '
                    'Die Pflicht trifft den Besitzer – nicht erst den, der das '
                    'Dokument gelesen oder für wichtig gehalten hat.',
                    'Absatz 2 regelt den Sonderfall, dass ein Testament bei '
                    'einer anderen Behörde als einem Gericht liegt: Es ist '
                    'ebenfalls nach dem Tod an das Nachlassgericht abzuliefern, '
                    'und das Nachlassgericht hat die Ablieferung zu '
                    'veranlassen, sobald es von dem Testament erfährt. Für einen Erbvertrag verweist '
                    '§2300 Abs. 1 BGB ausdrücklich auf diese Vorschrift.',
                    'Ob ein Schriftstück überhaupt ein wirksames Testament ist, '
                    'entscheiden weder Sie noch wir beim Räumen. Das ist Sache '
                    'des Gerichts und gegebenenfalls einer Rechtsberatung.',
                ],
            },
            {
                'id': 'eroeffnung',
                'titel': 'Wer eröffnet – und wo liefern Sie ab',
                'absaetze': [
                    'Örtlich zuständig ist nach §343 Abs. 1 FamFG das Gericht, '
                    'in dessen Bezirk der Erblasser im Zeitpunkt seines Todes '
                    'seinen gewöhnlichen Aufenthalt hatte. Welches Gericht das im '
                    'Einzelfall ist, erfragen Sie bei einem Amtsgericht in der '
                    'Nähe des letzten Wohnorts.',
                    'Das Gericht eröffnet das Testament, nicht Sie. Nach '
                    '§348 Abs. 1 FamFG muss es, sobald es vom Tod weiß, eine in '
                    'seiner Verwahrung befindliche Verfügung von Todes wegen '
                    'eröffnen; zur Eröffnung darf es nach Absatz 2 einen Termin '
                    'bestimmen und die gesetzlichen Erben sowie die sonstigen '
                    'Beteiligten dazu laden. Hat ein anderes als das nach '
                    '§343 zuständige Gericht die Verfügung in amtlicher '
                    'Verwahrung, ist nach §344 Abs. 6 FamFG dieses Gericht für '
                    'die Eröffnung zuständig.',
                    'Praktisch folgt daraus: Das Gesetz weist die Eröffnung dem '
                    'Gericht zu; Ladung der Erben und Bekanntgabe des Inhalts '
                    'übernehmen nicht Sie. Wie das Gericht die Abgabe '
                    'entgegennimmt (persönlich, per Post, mit welchem Nachweis), '
                    'fragen Sie vorab bei der Geschäftsstelle nach.',
                ],
            },
            {
                'id': 'nicht-vernichten',
                'titel': 'Warum nichts im Container landen darf',
                'absaetze': [
                    'Das Gesetz erlaubt es dem Erblasser selbst, ein Testament '
                    'durch Vernichtung oder Veränderung der Urkunde zu '
                    'widerrufen – aber nur „in der Absicht, es aufzuheben“ '
                    '(§2255 BGB). Diese Möglichkeit steht dem Erblasser zu, nicht '
                    'den Angehörigen oder der Räumkraft. Wer ein Testament '
                    'wegwirft, weil es „alt aussieht“, ersetzt also nicht etwa '
                    'den Willen des Erblassers durch seinen eigenen – er riskiert, '
                    'dass der letzte Wille nie bekannt wird.',
                    'Hinzu kommt das Strafrecht: §274 Abs. 1 Nr. 1 StGB bedroht '
                    'mit Freiheitsstrafe bis zu fünf Jahren oder Geldstrafe, wer '
                    'eine Urkunde, die ihm nicht ausschließlich gehört, in der '
                    'Absicht vernichtet, beschädigt oder unterdrückt, einem '
                    'anderen Nachteil zuzufügen. Ob ein bestimmter Fall darunter '
                    'fällt, hängt von Absicht und Einzelfall ab; das beurteilen '
                    'Gerichte, nicht dieser Text.',
                    'Unser Rat: Einen verschlossenen Umschlag lassen Sie zu, auch wenn die '
                    'Neugier groß ist. Das Gesetz verlangt von Ihnen die '
                    'Ablieferung, nicht die Auswertung. Bei einer verschlossenen '
                    'Verfügung hält das Gericht in der Niederschrift fest, ob '
                    'der Verschluss unversehrt war (§348 Abs. 1 Satz 3 FamFG).',
                ],
            },
            {
                'id': 'sichern',
                'titel': 'So sichern Sie Fundstücke bis zur Abgabe',
                'absaetze': [
                    'Tauchen beim Ausräumen Papiere auf, die nach letztem Willen '
                    'aussehen, hilft eine feste Reihenfolge. Sie ist eine '
                    'praktische Empfehlung, keine gesetzliche Vorgabe:',
                ],
                'schritte': [
                    '<strong>Stopp an der Fundstelle.</strong> Nicht weiter '
                    'sortieren, bis klar ist, was gefunden wurde. Wer räumt, '
                    'sagt dem Auftraggeber sofort Bescheid.',
                    '<strong>Fundort festhalten.</strong> Ein Foto der Schublade '
                    'oder des Ordners samt Datum und Uhrzeit; wer hat es '
                    'gefunden, wo genau lag es?',
                    '<strong>Unverändert aufheben.</strong> Nicht heften, '
                    'knicken, beschriften oder in andere Hüllen stecken; '
                    'Umschläge bleiben, wie sie sind.',
                    '<strong>Trocken und getrennt lagern.</strong> In einer '
                    'Mappe, die nicht mit dem übrigen Räumgut verwechselt werden '
                    'kann, am besten bei der Person, die für den Nachlass '
                    'verantwortlich ist.',
                    '<strong>Zügig abgeben.</strong> Das Gesetz sagt '
                    '„unverzüglich“; planen Sie die Abgabe also nicht erst '
                    'nach Abschluss der Räumung.',
                ],
            },
            {
                'id': 'danach',
                'titel': 'Was nach der Abgabe geschieht – und was Sie parallel im Blick haben',
                'absaetze': [
                    'Bis das Gericht das Testament bekannt gegeben hat, gibt es '
                    'Fristen, die noch nicht laufen: Wer durch Verfügung von '
                    'Todes wegen zum Erben berufen ist, dessen Frist zur '
                    'Ausschlagung beginnt nach §1944 Abs. 2 Satz 2 BGB nicht '
                    'vor der Bekanntgabe durch das Nachlassgericht. Wie Sie '
                    'Räumung und Entscheidung über die Erbschaft zusammen '
                    'denken, steht im Beitrag '
                    '<a href="/ratgeber/erbe-ausschlagen-nachlass-raeumen/">Erbe '
                    'ausschlagen und Nachlass räumen</a>.',
                    'Weitere Papiere im Nachlass, die nicht in den Müll gehören, '
                    'beschreibt der Beitrag '
                    '<a href="/ratgeber/unterlagen-aufbewahren-oder-wegwerfen/">'
                    'Unterlagen aufbewahren oder wegwerfen</a>. Wie wir bei '
                    'einer <a href="/nachlassraeumung/">Nachlassräumung</a> '
                    'Fundstücke wie Papiere, Schmuck und Fotos sichern und an die '
                    'Angehörigen übergeben, steht auf der Leistungsseite; zu '
                    'Mietwohnungen im Nachlass lesen Sie auch '
                    '<a href="/ratgeber/besenrein-wohnungsuebergabe/">besenrein '
                    'übergeben</a>.',
                ],
            },
        ],

        'faq': [
            ('Darf ich ein gefundenes Testament selbst öffnen und lesen?',
             'Das Gesetz verlangt von Ihnen die Ablieferung beim Nachlassgericht '
             '(§2259 BGB), und das Gericht eröffnet (§348 FamFG). Als '
             'praktische Empfehlung bleibt ein verschlossener Umschlag '
             'verschlossen. Sind Sie unsicher, fragen Sie bei der '
             'Geschäftsstelle des Nachlassgerichts nach.'),
            ('Was gilt, wenn ich nicht sicher bin, ob es ein Testament ist?',
             'Die Einordnung als wirksames Testament trifft das Gericht, nicht '
             'Sie. Wenn ein Schriftstück wie ein letzter Wille aussieht, heben '
             'Sie es unverändert auf und fragen beim Nachlassgericht, wie Sie '
             'vorgehen sollen.'),
            ('Gilt die Pflicht auch für einen Erbvertrag?',
             '§2300 Abs. 1 BGB erklärt §2259 BGB auf den Erbvertrag für '
             'entsprechend anwendbar. Auch hier wenden Sie sich an das '
             'Nachlassgericht.'),
            ('Wohin liefere ich ab, wenn der Verstorbene zuletzt im Pflegeheim lebte?',
             'Maßgeblich ist nach §343 Abs. 1 FamFG der gewöhnliche Aufenthalt '
             'zur Todeszeit. Welches Amtsgericht das ist, erfragen Sie am besten '
             'direkt bei einem Amtsgericht; dort wird die Zuständigkeit geprüft.'),
        ],

        'leistungen': ['nachlassraeumung', 'haushaltsaufloesung'],
        'staedte': [],
    },

    'unterlagen-aufbewahren-oder-wegwerfen': {
        'stand_iso': '2026-10',
        'kategorie': 'Erbe und Nachlass',
        'titel': 'Unterlagen: aufheben oder weg?',
        'h1': 'Unterlagen beim Räumen: behalten oder wegwerfen?',
        'h1_em': 'Aufbewahrungsfristen und sichere Entsorgung',
        'teaser': (
            'Aktenordner, Belege, Rechnungen: Welche Fristen das Gesetz '
            'für Steuer- und Handelsunterlagen nennt, was für Privatpersonen '
            'gilt und wie Papier mit persönlichen Daten vernichtet wird.'
        ),
        'seo_title': 'Unterlagen aufbewahren: 6 bis 10 Jahre Frist | Rümpelwerk',
        'seo_description': (
            'Welche Unterlagen beim Entrümpeln nicht in die Tonne gehören: '
            'Fristen nach AO, HGB und UStG, Verjährung, Papier sicher vernichten. Jetzt lesen.'
        ),
        'seo_keywords': ('unterlagen aufbewahren, aufbewahrungsfristen, '
                         'unterlagen entrümpeln, akten vernichten, '
                         'rechnungen aufbewahren, nachlass unterlagen, '
                         'aufbewahrungsfrist gewerbe nachlass'),

        'answer_frage': 'Welche Unterlagen darf ich beim Entrümpeln nicht wegwerfen?',
        'answer': (
            'Das hängt davon ab, wer die Unterlagen hatte: Für Steuer- und '
            'Geschäftsunterlagen nennt §147 AO Fristen von 6, 8 oder 10 '
            'Jahren, für Kaufleute §257 HGB grundsätzlich dieselben. Was '
            'davon für Privatpersonen gilt, hängt vom Einzelfall ab. Im '
            'Zweifel erst sichten, dann Steuerberatung fragen. Rechtsstand: '
            '{stand}.'
        ),

        'quellen': [
            {'schluessel': 'nachlass-ao-147', 'abschnitt': 'steuer',
             'bezug': 'Katalog der aufzubewahrenden Unterlagen, Fristen von '
                      'sechs, acht und zehn Jahren und Fristbeginn'},
            {'schluessel': 'nachlass-hgb-257', 'abschnitt': 'gewerbe',
             'bezug': 'Aufbewahrungspflicht und Fristen für Kaufleute'},
            {'schluessel': 'nachlass-ustg-14b', 'abschnitt': 'gewerbe',
             'bezug': 'Rechnungsaufbewahrung: acht Jahre für Unternehmer; '
                      'zwei Jahre für den Leistungsempfänger, der nicht '
                      'Unternehmer ist oder die Leistung privat nutzt'},
            {'schluessel': 'nachlass-ustg-14', 'abschnitt': 'gewerbe',
             'bezug': 'Welche Leistungen unter § 14 Abs. 2 Satz 2 Nr. 3 fallen'},
            {'schluessel': 'nachlass-bgb-195', 'abschnitt': 'verjaehrung',
             'bezug': 'Regelmäßige Verjährungsfrist von drei Jahren'},
            {'schluessel': 'nachlass-bgb-199', 'abschnitt': 'verjaehrung',
             'bezug': 'Beginn der regelmäßigen Verjährung am Jahresende'},
            {'schluessel': 'nachlass-bsi-con6', 'abschnitt': 'papier',
             'bezug': 'Anforderung an die Papiervernichtung nach '
                      'Sicherheitsstufe P-3 (für Institutionen)'},
            {'schluessel': 'nachlass-tlfdi-datentraeger', 'abschnitt': 'papier',
             'bezug': 'Schutzklassen, Büroaktenvernichter und Cross-Cut-Geräte '
                      'in der Orientierungshilfe der Datenschutzbehörde'},
        ],

        'abschnitte': [
            {
                'id': 'steuer',
                'titel': 'Steuerliche Aufbewahrung: was §147 AO regelt',
                'absaetze': [
                    '§147 Abs. 1 AO zählt auf, welche Unterlagen „geordnet '
                    'aufzubewahren“ sind: Bücher und Aufzeichnungen, Inventare, '
                    'Jahresabschlüsse, empfangene Handels- oder '
                    'Geschäftsbriefe, Wiedergaben abgesandter Briefe, '
                    'Buchungsbelege und sonstige Unterlagen, soweit sie für die '
                    'Besteuerung von Bedeutung sind.',
                    'Die Fristen nennt Absatz 3: zehn Jahre für Bücher, '
                    'Aufzeichnungen, Inventare und Jahresabschlüsse, acht Jahre '
                    'für Buchungsbelege und sechs Jahre für die übrigen '
                    'aufgeführten Unterlagen, sofern andere Steuergesetze keine '
                    'kürzeren Fristen zulassen. Nach Absatz 4 beginnt die Frist '
                    'mit dem Schluss des Kalenderjahres, in dem der Beleg '
                    'entstanden oder der Brief empfangen oder abgesandt wurde. '
                    'Wichtig: Nach Absatz 3 Satz 5 läuft die Frist nicht ab, '
                    'soweit und solange die Unterlagen für Steuern von '
                    'Bedeutung sind, für die die Festsetzungsfrist noch nicht '
                    'abgelaufen ist; ein Ablauf der Jahre allein erlaubt das '
                    'Wegwerfen also nicht automatisch.',
                    'Ob diese Pflichten bei dem Verstorbenen oder jetzt bei den '
                    'Erben bestehen, hängt vom Einzelfall ab und ist eine Frage '
                    'für Steuerberatung – ebenso, welche Unterlage im '
                    'Einzelfall darunter fällt.',
                ],
            },
            {
                'id': 'gewerbe',
                'titel': 'Gehört ein Gewerbe zum Nachlass?',
                'absaetze': [
                    'Dann lohnt der genaue Blick auf drei Vorschriften. '
                    '§257 Abs. 1 HGB verpflichtet Kaufleute, Handelsbücher, '
                    'Inventare, Jahresabschlüsse, die empfangenen '
                    'Handelsbriefe, Wiedergaben der abgesandten Handelsbriefe '
                    'und Buchungsbelege geordnet '
                    'aufzubewahren; die Fristen in Absatz 4 sind zehn, acht und '
                    'sechs Jahre – bei Buchungsbelegen acht Jahre.',
                    '§14b Abs. 1 UStG verlangt vom Unternehmer, ein Doppel der '
                    'ausgestellten und alle erhaltenen Rechnungen acht Jahre '
                    'aufzubewahren. Eine Ausnahme nennt Absatz 1 Satz 5: In den '
                    'Fällen des §14 Abs. 2 Satz 2 Nr. 3 UStG (Werklieferung '
                    'oder sonstige Leistung im Zusammenhang mit einem '
                    'Grundstück) muss der Leistungsempfänger Rechnung, '
                    'Zahlungsbeleg oder eine andere beweiskräftige Unterlage '
                    'zwei Jahre aufbewahren, soweit er nicht Unternehmer ist '
                    'oder die Leistung für seinen nichtunternehmerischen '
                    'Bereich verwendet. Die Zwei-Jahres-Frist gilt also für '
                    'den Empfänger, nicht für den ausstellenden Unternehmer. '
                    'Ob das auf Ihre Belege zutrifft, prüft die '
                    'Steuerberatung.',
                    'Praktisch heißt das: Geschäftsordner, Rechnungen und '
                    'Buchhaltung eines Betriebs gehören nicht in die '
                    'Räumungsmulde, sondern werden ungeprüft gesichert und dem '
                    'Steuerberater oder den Erben übergeben. Gewerbliche '
                    'Hinterlassenschaften behandelt auch unsere Seite zur '
                    '<a href="/gewerbeentruempelung/">Gewerbeentrümpelung</a>.',
                ],
            },
            {
                'id': 'verjaehrung',
                'titel': 'Verjährung: warum drei Jahre nicht die ganze Antwort sind',
                'absaetze': [
                    '§195 BGB: Die regelmäßige Verjährungsfrist beträgt drei '
                    'Jahre. Nach §199 Abs. 1 BGB beginnt sie mit dem Schluss '
                    'des Jahres, in dem der Anspruch entstanden ist und der '
                    'Gläubiger von den Umständen und der Person des Schuldners '
                    'Kenntnis erlangt oder ohne grobe Fahrlässigkeit erlangen '
                    'müsste.',
                    'Das ist die Regel, nicht die einzige Frist: Für andere '
                    'Ansprüche gelten andere Zeiträume, die wir hier nicht '
                    'prüfen. Praktisch bewährt hat sich: Wer offene Rechnungen, Mahnungen, '
                    'Darlehens- oder Mietverträge findet, hebt sie auf, bis '
                    'geklärt ist, ob daraus noch Ansprüche bestehen – und '
                    'fragt dafür Rechtsberatung oder Nachlassgericht.',
                ],
            },
            {
                'id': 'papier',
                'titel': 'Papier mit persönlichen Daten richtig vernichten',
                'absaetze': [
                    'Wenn Papier nicht mehr gebraucht wird, steckt es dennoch '
                    'voll persönlicher Angaben: Kontoauszüge, Bescheide, '
                    'Arztbriefe. Das BSI verlangt in seinem Baustein CON.6 '
                    '(IT-Grundschutz-Kompendium, für Institutionen '
                    'geschrieben) unter den Basis-Anforderungen, dass '
                    'schützenswerte Datenträger vernichtet werden, Papier '
                    'mindestens nach Sicherheitsstufe P-3 der ISO/IEC 21964-2.',
                    'Der Thüringer Landesbeauftragte für den Datenschutz '
                    'beschreibt in einer Orientierungshilfe (Stand Juli 2017) '
                    'Schutzklassen für Datenträger mit personenbezogenen Daten '
                    'und hält fest, dass '
                    'Büroaktenvernichter mit Cross-Cut-Schnitt nach '
                    'Sicherheitsstufe 4 die Anforderungen für Papier der '
                    'Schutzklasse 2 (hoher Schutzbedarf) in der Regel nicht '
                    'erfüllen, weil sich '
                    'Informationen wegen der Partikelgröße leicht '
                    'wiederherstellen lassen. Beide Texte richten sich nicht an '
                    'Privatpersonen, taugen aber als Maßstab für sensible '
                    'Unterlagen.',
                    'Ein Rat aus der Praxis: Papier mit Konto-, Gesundheits- oder Steuerdaten gehört '
                    'nicht in den offenen Container. Es wird gebündelt '
                    'separiert, geschreddert oder einem Dienstleister '
                    'übergeben, der die Vernichtung bestätigt.',
                ],
            },
            {
                'id': 'sortierung',
                'titel': 'Eine Reihenfolge für den Papierberg',
                'absaetze': [
                    'Diese Sortierung ist eine praktische Empfehlung ohne '
                    'Rechtsbehauptung; sie soll verhindern, dass Wichtiges im '
                    'Sack landet:',
                ],
                'schritte': [
                    '<strong>Grüne Mappe: Nachweise.</strong> Erbschein, '
                    'Sterbeurkunde, Rentenbescheide, '
                    'Versicherungspolicen, Verträge, Grundbuch- und '
                    'Mietunterlagen. Ein Testament gehört nicht in die Mappe, '
                    'sondern wird beim Nachlassgericht abgeliefert, siehe '
                    '<a href="/ratgeber/testament-beim-raeumen-gefunden/">'
                    'Testament gefunden</a>.',
                    '<strong>Gelbe Mappe: Geld.</strong> Kontoauszüge, '
                    'Steuerbescheide, offene Rechnungen, Mahnungen, '
                    'Darlehensunterlagen.',
                    '<strong>Blaue Mappe: Erinnerung.</strong> Fotos, '
                    'Briefe, Zeugnisse, Urkunden – an Angehörige.',
                    '<strong>Rest prüfen, dann vernichten.</strong> Werbung und '
                    'Zeitschriften ohne Namen in den Altpapiercontainer, alles '
                    'mit persönlichen Daten in die Vernichtung.',
                ],
            },
            {
                'id': 'erbfrage',
                'titel': 'Wie das mit dem Räumen zusammenhängt',
                'absaetze': [
                    'Bevor ein ganzer Hausstand verschwindet, sollte die '
                    'Erbfrage geklärt sein – dazu der Beitrag '
                    '<a href="/ratgeber/erbe-ausschlagen-nachlass-raeumen/">'
                    'Erbe ausschlagen und Nachlass räumen</a>. Bei einer '
                    '<a href="/nachlassraeumung/">Nachlassräumung</a> '
                    'sichern wir Fundstücke wie Papiere, Schmuck und Fotos '
                    'und übergeben sie den Angehörigen.',
                ],
            },
        ],

        'faq': [
            ('Wie lange muss ich Rechnungen aufbewahren?',
             'Unternehmer nach §14b Abs. 1 Satz 1 UStG acht Jahre. Zwei Jahre '
             'nennt Satz 5 für den Leistungsempfänger bei Leistungen im '
             'Zusammenhang mit einem Grundstück (§14 Abs. 2 Satz 2 Nr. 3 '
             'UStG), soweit er nicht Unternehmer ist oder die Leistung für '
             'seinen nichtunternehmerischen Bereich verwendet. Ob das auf '
             'Ihre Unterlagen zutrifft, klärt die Steuerberatung.'),
            ('Was gilt für Kaufleute im Nachlass?',
             '§257 Abs. 4 HGB nennt zehn Jahre für Handelsbücher und '
             'Abschlüsse, acht Jahre für Buchungsbelege und sechs Jahre für '
             'sonstige Unterlagen; Sonderregeln gibt es etwa für Kreditinstitute '
             'und Versicherer. Die Frist beginnt nach §257 Abs. 5 HGB mit '
             'dem Schluss des Kalenderjahres, in dem der Beleg entstanden '
             'oder der Brief empfangen oder abgesandt wurde.'),
            ('Reicht es, Papier von Hand zu zerreißen?',
             'Die Datenschutzbehörde Thüringen hält bei Schutzklasse 2 '
             '(hoher Schutzbedarf) Cross-Cut-Büroaktenvernichter der '
             'Sicherheitsstufe 4 in der Regel nicht für ausreichend, weil sich '
             'die Informationen aus den Partikeln leicht wiederherstellen '
             'lassen. Zum Zerreißen von Hand äußert sich die Orientierungshilfe '
             'nicht; als praktische Empfehlung gehören sensible Unterlagen '
             'in einen feinen Schredder oder zu einem Dienstleister.'),
            ('Darf ich alles Private nach drei Jahren wegwerfen?',
             'Nein, das lässt sich so nicht sagen. §195 BGB nennt drei Jahre '
             'als regelmäßige Verjährung, aber der Beginn richtet sich nach '
             '§199 BGB, und für andere Ansprüche gelten andere Fristen. '
             'Fragen Sie im Zweifel eine Rechtsberatung.'),
        ],

        'leistungen': ['nachlassraeumung', 'gewerbeentruempelung'],
        'staedte': [],
    },

    'wohnung-aufloesen-pflegeheim-vollmacht-betreuung': {
        'stand_iso': '2026-10',
        'kategorie': 'Miete und Räumung',
        'titel': 'Wohnung auflösen: Pflegeheim',
        'h1': 'Wohnung auflösen, wenn jemand ins Pflegeheim zieht',
        'h1_em': 'Vollmacht, Betreuung und Genehmigung des Gerichts',
        'teaser': (
            'Wer darf die Mietwohnung eines Menschen kündigen und räumen, der '
            'ins Heim zieht oder nicht mehr selbst entscheiden kann – und '
            'wann das Betreuungsgericht zustimmen muss.'
        ),
        'seo_title': 'Wohnung auflösen fürs Pflegeheim: §1833 BGB | Rümpelwerk',
        'seo_description': (
            'Wer darf die Wohnung eines Pflegebedürftigen kündigen und räumen? '
            'Vorsorgevollmacht, Betreuer, Genehmigung nach §1833 BGB. Jetzt lesen.'
        ),
        'seo_keywords': ('wohnung auflösen pflegeheim, vorsorgevollmacht '
                         'wohnung kündigen, betreuer wohnung auflösen, '
                         '§ 1833 bgb, betreuungsgericht genehmigung mietwohnung, '
                         'haushaltsauflösung pflegeheim'),

        'answer_frage': ('Wer darf die Wohnung eines Menschen auflösen, der '
                         'ins Pflegeheim zieht?'),
        'answer': (
            'Die Wohnung auflösen darf, wer für den Menschen handeln darf: '
            'der Betroffene selbst, ein Bevollmächtigter oder ein vom '
            'Betreuungsgericht bestellter Betreuer. Für den Betreuer '
            'bedeutet §1833 BGB: Kündigt er die selbst genutzte Mietwohnung, '
            'braucht er dafür die Genehmigung des Betreuungsgerichts. '
            'Geräumt werden sollte erst danach. Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'bgb-1833', 'abschnitt': 'genehmigung',
             'bezug': 'Der Wortlaut regelt Anzeige, Maßgabe der Wünsche des '
                      'Betreuten und die Genehmigung zur Kündigung der '
                      'selbst genutzten Wohnung'},
            {'schluessel': 'bgb-1858', 'abschnitt': 'genehmigung',
             'bezug': 'Einseitige Rechtsgeschäfte ohne erforderliche '
                      'Genehmigung sind unwirksam'},
            {'schluessel': 'bgb-1814', 'abschnitt': 'wer-handelt',
             'bezug': 'Der Wortlaut sagt, wann das Betreuungsgericht einen '
                      'Betreuer bestellt und wann das nicht erforderlich ist'},
            {'schluessel': 'bgb-1820', 'abschnitt': 'wer-handelt',
             'bezug': 'Der Wortlaut verpflichtet Besitzer einer Vollmacht, das '
                      'Gericht über ein Betreuungsverfahren zu unterrichten'},
            {'schluessel': 'bgb-1821', 'abschnitt': 'hausrat',
             'bezug': 'Der Wortlaut verpflichtet den Betreuer, die Wünsche des '
                      'Betreuten festzustellen und ihnen zu entsprechen'},
            {'schluessel': 'justiz-sachsen-betreuung', 'abschnitt': 'wer-handelt',
             'bezug': 'Die Justiz des Freistaats nennt die Betreuungsabteilung '
                      'des Amtsgerichts und die Betreuungsbehörde der Stadt '
                      'als Ansprechpartner'},
        ],

        'abschnitte': [
            {
                'id': 'wer-handelt',
                'titel': 'Wer für den Menschen handeln darf',
                'absaetze': [
                    'Zieht jemand ins Pflegeheim, stellt sich zuerst die Frage, wer '
                    'für ihn handeln darf. Das Gesetz kennt dafür zwei Wege: eine <strong>Vollmacht</strong>, '
                    'die der Mensch früher selbst erteilt hat, oder ein '
                    '<strong>rechtlicher Betreuer</strong>, den das '
                    'Betreuungsgericht bestellt. Nach §1814 BGB geschieht das, '
                    'wenn ein Volljähriger seine Angelegenheiten wegen einer '
                    'Krankheit oder Behinderung ganz oder teilweise rechtlich '
                    'nicht besorgen kann – nur, wenn es erforderlich ist, und '
                    'nicht gegen seinen freien Willen.',
                    'Erforderlich ist ein Betreuer ausdrücklich nicht, soweit '
                    'ein Bevollmächtigter die Angelegenheiten gleichermaßen '
                    'besorgen kann (§1814 Absatz 3 Nummer 1 BGB). Auf der '
                    'Seite des Amtsgerichts Leipzig heißt es entsprechend: '
                    '„Eine Betreuung ist nicht erforderlich, wenn eine '
                    'sogenannte Vorsorgevollmacht vorliegt.“ Für Fragen zur '
                    'Vorsorgevollmacht oder zur Anregung einer Betreuung '
                    'verweist die Seite an die Betreuungsbehörde der Stadt.',
                    'Haben Sie eine Vollmacht, aber läuft bereits ein '
                    'Betreuungsverfahren, gilt §1820 Absatz 1 BGB: Wer davon '
                    'erfährt und ein Dokument mit einer Bevollmächtigung '
                    'besitzt, hat das Betreuungsgericht unverzüglich zu '
                    'unterrichten; das Gericht kann eine Abschrift verlangen.',
                ],
            },
            {
                'id': 'genehmigung',
                'titel': 'Kündigung der Wohnung: Was §1833 BGB verlangt',
                'absaetze': [
                    'Für den <strong>Betreuer</strong> regelt §1833 BGB die '
                    'Aufgabe von Wohnraum, den der Betreute selbst nutzt. '
                    'Beabsichtigt er sie, hat er das dem Betreuungsgericht '
                    'unverzüglich anzuzeigen, mit den Gründen und der Sichtweise '
                    'des Betreuten (Absatz 2). Zulässig ist die Aufgabe nur '
                    'nach Maßgabe von §1821 Absatz 2 bis 4 BGB (Absatz 1) – also '
                    'nach den Wünschen des Betreuten, oder, wenn sich diese nicht '
                    'feststellen lassen, nach seinem mutmaßlichen Willen, '
                    'jeweils mit den Ausnahmen des Absatzes 3.',
                    'Absatz 3 nennt vier Handlungen, für die der Betreuer bei '
                    'selbst genutztem Wohnraum die Genehmigung des '
                    'Betreuungsgerichts braucht: die Kündigung des '
                    'Mietverhältnisses, eine Willenserklärung, die auf dessen '
                    'Aufhebung gerichtet ist, die Vermietung des Wohnraums und '
                    'eine damit verbundene Verfügung über ein Grundstück oder '
                    'ein Recht daran. Eine Kündigung ohne die erforderliche '
                    'Genehmigung ist unwirksam (§1858 Absatz 1 BGB); legt der '
                    'Betreuer die Genehmigung nicht vor, kann der Vermieter die '
                    'Kündigung unverzüglich zurückweisen (Absatz 2). Erst mit '
                    'der Genehmigung sollte an die Räumung gedacht werden.',
                    'Der Bevollmächtigte wird in §1833 BGB nicht genannt, die '
                    'Norm spricht vom Betreuer. Was eine Vollmacht umfasst, '
                    'steht in ihrem eigenen Text; §1820 Absatz 2 BGB verlangt '
                    'Schriftform und ausdrückliche Erwähnung nur für die dort '
                    'aufgezählten Maßnahmen (bestimmte ärztliche '
                    'Maßnahmen, Unterbringung, ärztliche Zwangsmaßnahmen). Ob der Bevollmächtigte '
                    'für die Wohnungskündigung zusätzlich etwas beachten muss, '
                    'klären Sie mit der Betreuungsbehörde oder einem '
                    'Rechtsanwalt, bevor Sie kündigen.',
                ],
            },
            {
                'id': 'hausrat',
                'titel': 'Hausrat und Erinnerungsstücke',
                'absaetze': [
                    'Ein Betreuer hat nach §1821 Absatz 2 BGB die Wünsche des '
                    'Betreuten festzustellen und ihnen grundsätzlich zu '
                    'entsprechen; Ausnahmen nennt Absatz 3. Praktisch heißt das '
                    'für die Auflösung: Fragen Sie den Menschen, was er '
                    'behalten will, soweit er sich äußern kann, und nehmen Sie '
                    'seine früheren Äußerungen ernst. Das Heimzimmer bietet '
                    'wenig Platz – ein vertrauter Sessel, Bilder, Bettwäsche und '
                    'Fotoalben sind meist wichtiger als der Hausrat im '
                    'Ganzen.',
                    'Papiere, Schmuck, Fotos und Datenträger gehören aussortiert '
                    'und sicher verwahrt, bevor irgendetwas abtransportiert '
                    'wird. Möbel und Hausrat, die niemand übernimmt, werden '
                    'danach entsorgt.',
                ],
            },
            {
                'id': 'ablauf',
                'titel': 'Reihenfolge und Dokumentation',
                'absaetze': [
                    'Eine Reihenfolge, die die Zuständigkeiten sauber '
                    'auseinanderhält:',
                ],
                'schritte': [
                    '<strong>Nachweis prüfen.</strong> Liegt die Vollmacht im '
                    'Original vor, oder gibt es einen Beschluss des '
                    'Betreuungsgerichts, der die Wohnungsangelegenheiten '
                    'umfasst? Ohne eines von beiden sollte niemand für den '
                    'Menschen kündigen oder räumen.',
                    '<strong>Gericht beteiligen.</strong> Ist ein Betreuer '
                    'bestellt: Anzeige und Genehmigung nach §1833 BGB '
                    'einholen, schriftlich aufbewahren.',
                    '<strong>Mietverhältnis beenden.</strong> Kündigung '
                    'beziehungsweise Aufhebungsvertrag mit dem Vermieter; '
                    'Übergabetermin und Schlüsselzahl vereinbaren.',
                    '<strong>Bestand dokumentieren.</strong> Raum für Raum '
                    'fotografieren, bevor etwas weggeschafft wird; '
                    'festhalten, was behalten, übergeben, verkauft oder '
                    'entsorgt wird, mit Datum und Namen.',
                    '<strong>Räumen lassen.</strong> Rümpelwerk Mitteldeutschland '
                    'räumt Wohnungen, trennt nach Fraktionen und gibt auf '
                    'Wunsch einen schriftlichen Entsorgungsnachweis; das '
                    'Festpreisangebot gibt es bei der kostenlosen Besichtigung.',
                ],
            },
            {
                'id': 'weiter',
                'titel': 'Weiterführend',
                'absaetze': [
                    'Zum Ablauf einer Räumung siehe '
                    '<a href="/wohnungsaufloesung/">Wohnungsauflösung</a> und '
                    '<a href="/haushaltsaufloesung/">Haushaltsauflösung</a>. '
                    'Fragen zu Sozialleistungen oder Kosten des Heimplatzes '
                    'beantwortet dieser Text nicht; wenden Sie sich dafür an '
                    'die zuständige Stelle.',
                ],
            },
        ],

        'faq': [
            ('Reicht eine Vorsorgevollmacht, um die Mietwohnung zu kündigen?',
             'Das hängt vom Wortlaut der Vollmacht ab. §1833 BGB nennt nur den '
             'Betreuer. Lassen Sie den Einzelfall vor der Kündigung bei der '
             'Betreuungsbehörde oder durch einen Rechtsanwalt klären.'),
            ('Braucht der Betreuer für die Kündigung immer das Gericht?',
             'Bei Wohnraum, den der Betreute selbst nutzt, ja: §1833 Absatz 3 '
             'BGB verlangt die Genehmigung des Betreuungsgerichts zur Kündigung '
             'des Mietverhältnisses und zu einer Aufhebungsvereinbarung.'),
            ('Darf ich schon räumen, bevor gekündigt ist?',
             'Davon raten wir ab. Ohne Nachweis über Ihre Befugnis und ohne '
             'geklärtes Mietverhältnis fehlt die Grundlage; ob und wann die '
             'Wohnung geräumt werden darf, hängt vom Einzelfall ab. Erst der '
             'Nachweis, dann die Kündigung, dann die Räumung.'),
            ('Wer entscheidet, was aus dem Hausrat wird?',
             'Soweit möglich der Mensch selbst. Ein Betreuer hat dessen Wünsche '
             'festzustellen und ihnen grundsätzlich zu entsprechen (§1821 '
             'Absatz 2 BGB). Kann der Betreuer die Wünsche nicht feststellen, '
             'soll nahen Angehörigen bei der Ermittlung des mutmaßlichen '
             'Willens Gelegenheit zur Äußerung gegeben werden (§1821 '
             'Absatz 4 BGB).'),
        ],

        'leistungen': ['wohnungsaufloesung', 'haushaltsaufloesung'],
        'staedte': [],
    },

    'zurueckgelassene-sachen-nach-auszug-raeumung': {
        'stand_iso': '2026-10',
        'kategorie': 'Miete und Räumung',
        'titel': 'Zurückgelassene Sachen',
        'h1': 'Zurückgelassene Sachen nach Auszug oder Räumung',
        'h1_em': 'Wer sie verwahren, verwerten oder vernichten darf',
        'teaser': (
            'Was nach einer Räumungsvollstreckung mit dem Hausrat des Mieters '
            'geschieht, welche Fristen gelten und was Mieter und Vermieter vor '
            'der Schlüsselübergabe klären sollten.'
        ),
        'seo_title': 'Sachen nach Zwangsräumung: 1 Monat Frist | Rümpelwerk',
        'seo_description': (
            'Was passiert mit Sachen, die nach Auszug oder Zwangsräumung '
            'bleiben? §885 und §885a ZPO, Monatsfrist, Vermieterpfandrecht. Jetzt lesen.'
        ),
        'seo_keywords': ('zurückgelassene sachen mieter, räumung hausrat '
                         'vermieter, § 885a zpo, beschränkter '
                         'vollstreckungsauftrag, vermieterpfandrecht, '
                         'zwangsräumung eingelagert'),

        'answer_frage': ('Was geschieht mit Sachen, die nach einer '
                         'Zwangsräumung zurückbleiben?'),
        'answer': (
            'Bei der Räumungsvollstreckung beträgt die Frist einen Monat: '
            'Fordert der Schuldner seine beweglichen Sachen nicht binnen '
            'eines Monats ab, dürfen sie verwertet werden; Unverwertbares '
            'soll (§885) beziehungsweise darf (§885a) vernichtet werden. Wer '
            'verwahrt, hängt davon ab, ob der Gerichtsvollzieher '
            'vollständig oder nur beschränkt räumt (§885, §885a ZPO). '
            'Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'zpo-885', 'abschnitt': 'vollstreckung',
             'bezug': 'Der Wortlaut regelt Wegschaffen, Verwahrung, Vernichtung '
                      'und die Fristen von einem und zwei Monaten bei der '
                      'vollständigen Räumung'},
            {'schluessel': 'zpo-885a', 'abschnitt': 'beschraenkt',
             'bezug': 'Der Wortlaut regelt, was der Gläubiger bei beschränktem '
                      'Vollstreckungsauftrag verwahren, verwerten oder '
                      'vernichten darf und wer die Kosten trägt'},
            {'schluessel': 'bgb-562-pfandrecht', 'abschnitt': 'pfandrecht',
             'bezug': 'Der Wortlaut nennt das Pfandrecht des Vermieters an den '
                      'eingebrachten Sachen und seine Grenzen'},
            {'schluessel': 'bgb-858', 'abschnitt': 'vorher-klaeren',
             'bezug': 'Verbotene Eigenmacht: Besitzentzug ohne Willen des '
                      'Besitzers, wenn das Gesetz ihn nicht gestattet'},
            {'schluessel': 'justiz-nrw-herausgabe', 'abschnitt': 'vorher-klaeren',
             'bezug': 'Die Justiz des Landes beschreibt Räumungsfrist, '
                      'Vollstreckungsschutz und die Kosten von Spedition und '
                      'Einlagerung'},
        ],

        'abschnitte': [
            {
                'id': 'vollstreckung',
                'titel': 'Räumungsvollstreckung: Der Gerichtsvollzieher räumt',
                'absaetze': [
                    'Muss ein Mieter die Wohnung auf Grund eines Räumungstitels '
                    'verlassen, liegt die Vollstreckung beim Gerichtsvollzieher: '
                    'Er setzt den Schuldner aus dem Besitz und weist den '
                    'Gläubiger – meist den Vermieter – ein (§885 Absatz 1 ZPO). '
                    'Dabei fordert er den Schuldner auf, eine Anschrift für '
                    'Zustellungen zu nennen.',
                    'Was mit den beweglichen Sachen geschieht, die nicht '
                    'gepfändet werden, regeln die Absätze 2 bis 5. Der '
                    'Gerichtsvollzieher schafft sie weg und übergibt sie dem '
                    'Schuldner oder bestimmten Personen, die an seiner Stelle '
                    'anwesend sind. Ist niemand da oder wird die Annahme '
                    'verweigert, kommen die Sachen auf Kosten des Schuldners in '
                    'die Pfandkammer oder anderweitig in Verwahrung. Sachen, an '
                    'deren Aufbewahrung „offensichtlich kein Interesse '
                    'besteht“, sollen unverzüglich vernichtet werden.',
                    'Die Fristen: Fordert der Schuldner seine Sachen nicht '
                    'binnen eines Monats nach der Räumung ab, veräußert der '
                    'Gerichtsvollzieher sie und hinterlegt den Erlös. Dasselbe '
                    'gilt, wenn er sie zwar abfordert, aber binnen zwei Monaten '
                    'nach der Räumung die Kosten nicht zahlt. Unpfändbare '
                    'Sachen und solche ohne zu erwartenden Verwertungserlös '
                    'sind auf Verlangen jederzeit herauszugeben (Absatz 5). Sachen, die '
                    'sich nicht verwerten lassen, sollen vernichtet werden '
                    '(Absatz 4).',
                ],
            },
            {
                'id': 'beschraenkt',
                'titel': 'Beschränkter Auftrag: Dann verwahrt der Vermieter',
                'absaetze': [
                    'Der Gläubiger kann den Auftrag nach §885a ZPO auf die '
                    'Besitzeinweisung beschränken. Der Gerichtsvollzieher '
                    'weist dann nur noch den Gläubiger in den Besitz ein. Er hält im Protokoll die frei '
                    'ersichtlichen beweglichen Sachen fest und darf dafür '
                    'Bildaufnahmen in elektronischer Form machen (Absatz 2).',
                    'Die Sachen, die nicht gepfändet werden, darf der Gläubiger '
                    'danach jederzeit wegschaffen, und er hat sie zu verwahren. '
                    'Sachen, an deren Aufbewahrung offensichtlich kein '
                    'Interesse besteht, darf er jederzeit vernichten. Für diese '
                    'Maßnahmen haftet er nur bei Vorsatz und grober '
                    'Fahrlässigkeit (Absatz 3).',
                    'Fordert der Schuldner die Sachen nicht binnen eines Monats '
                    'nach der Einweisung des Gläubigers beim Gläubiger ab, darf '
                    'dieser sie verwerten – nach den im Gesetz genannten '
                    'Vorschriften des Bürgerlichen Gesetzbuchs, ohne dass die '
                    'Versteigerung vorher angedroht werden muss. Sachen, die '
                    'sich nicht verwerten lassen, dürfen vernichtet werden '
                    '(Absatz 4). Unpfändbare Sachen und solche ohne zu '
                    'erwartenden Verwertungserlös sind auf Verlangen '
                    'des Schuldners jederzeit herauszugeben (Absatz 5). Die '
                    'Kosten für Verwahrung und Verwertung gelten als Kosten der '
                    'Zwangsvollstreckung (Absatz 7).',
                    'Beide Seiten weist der Gerichtsvollzieher mit der '
                    'Mitteilung des Räumungstermins auf diese Regeln hin '
                    '(Absatz 6). Der Unterschied zur vollständigen '
                    'Räumung: Die Monatsfrist läuft hier gegenüber dem '
                    'Vermieter, nicht gegenüber dem Gerichtsvollzieher.',
                ],
            },
            {
                'id': 'pfandrecht',
                'titel': 'Das Vermieterpfandrecht als Grenze',
                'absaetze': [
                    'Unabhängig von der Räumung räumt §562 BGB dem Vermieter '
                    'für seine Forderungen aus dem Mietverhältnis ein '
                    'Pfandrecht an den eingebrachten Sachen des Mieters ein. '
                    'Es erstreckt sich nicht auf Sachen, die der Pfändung nicht '
                    'unterliegen. Für künftige Entschädigungsforderungen und '
                    'für Miete, die über das laufende und das folgende '
                    'Mietjahr hinausgeht, kann es nicht geltend gemacht werden.',
                    'Ob der Vermieter es im '
                    'Einzelfall durchsetzen darf, welche Sachen darunter fallen '
                    'und wie es sich zu einem Räumungstitel verhält, ist eine '
                    'Frage für Rechtsberatung oder Mieterverein; dieser Text '
                    'beantwortet sie nicht.',
                ],
            },
            {
                'id': 'vorher-klaeren',
                'titel': 'Vor der Schlüsselübergabe klären',
                'absaetze': [
                    'Wer freiwillig auszieht, kann vieles vorab regeln. Wer '
                    'eine Räumung fürchtet, '
                    'findet auf der Seite der Justiz Nordrhein-Westfalen den '
                    'Hinweis, dass der Mieter im Räumungsurteil eine verlängerbare '
                    'Räumungsfrist erwirken kann und dass bei besonderer Härte '
                    'ein Vollstreckungsschutzantrag nach §765a ZPO möglich ist. '
                    'Dieselbe Seite warnt vor erheblichen Zusatzkosten, wenn '
                    'ein Spediteur die Sachen entfernt und sie eingelagert '
                    'werden müssen.',
                    'Praktische Reihenfolge für beide Seiten:',
                ],
                'schritte': [
                    '<strong>Bestand festhalten.</strong> Liste und Fotos von '
                    'allem, was in der Wohnung bleibt, mit Datum. Das schützt '
                    'beide vor dem Streit, was zurückgelassen wurde.',
                    '<strong>Wichtiges vorab sichern.</strong> Papiere, '
                    'Schmuck, Fotos und Datenträger nehmen Sie rechtzeitig '
                    'selbst mit, damit sie gar nicht erst in Verwahrung oder '
                    'Verwertung geraten.',
                    '<strong>Anschrift hinterlassen.</strong> Ohne erreichbare '
                    'Adresse kann niemand die Sachen übergeben oder eine Frist '
                    'wahren.',
                    '<strong>Frist notieren.</strong> Bei einer Vollstreckung '
                    'läuft ein Monat ab der Räumung beziehungsweise der '
                    'Einweisung – notieren Sie sich das Datum im '
                    'Kalender.',
                    '<strong>Vor jeder Räumung auf eigene Faust Rechtsrat '
                    'holen.</strong> Das Gesetz legt die Besitzeinweisung beim '
                    'Räumungstitel in die Hände des Gerichtsvollziehers. Ob und '
                    'wie ein Vermieter ohne Titel Sachen entfernen darf, '
                    'beurteilt im Einzelfall ein Rechtsanwalt oder der '
                    'Mieterverein. Eigenmächtiges Räumen ohne Titel ist '
                    'verbotene Eigenmacht (§858 BGB); nach dem '
                    'Bundesgerichtshof haftet ein Vermieter, der so räumt, '
                    'für die vorgefundenen Sachen und muss ihren Bestand und '
                    'Wert belegen (Urteil vom 14.07.2010, Az. VIII ZR 45/09).',
                ],
            },
            {
                'id': 'abraeumen',
                'titel': 'Wenn danach tatsächlich geräumt werden soll',
                'absaetze': [
                    'Ist geklärt, dass der Gläubiger oder der Eigentümer die '
                    'Sachen entfernen darf, ist das eine gewöhnliche '
                    'Räumungsarbeit. Rümpelwerk Mitteldeutschland räumt '
                    'Wohnungen und Häuser, trennt dabei nach Fraktionen und '
                    'gibt auf Wunsch einen schriftlichen Entsorgungsnachweis; '
                    'das Festpreisangebot gibt es direkt bei der kostenlosen '
                    'Besichtigung. Die rechtliche Freigabe holt der Auftraggeber '
                    'vorher selbst ein. Zum Ablauf siehe '
                    '<a href="/wohnungsaufloesung/">Wohnungsauflösung</a> und '
                    '<a href="/haushaltsaufloesung/">Haushaltsauflösung</a>; zu '
                    'Besenreinheit und Rückgabepflicht '
                    '<a href="/ratgeber/besenrein-wohnungsuebergabe/">Besenrein '
                    'übergeben</a>.',
                ],
            },
        ],

        'faq': [
            ('Wie lange werden zurückgelassene Sachen aufbewahrt?',
             'Bei der vollständigen Räumung hat der Schuldner einen Monat, um '
             'die Sachen beim Gerichtsvollzieher abzufordern; die Kosten müssen '
             'binnen zwei Monaten gezahlt sein (§885 Absatz 4 ZPO). Bei '
             'beschränktem Auftrag läuft ein Monat ab der Einweisung des '
             'Gläubigers (§885a Absatz 4 ZPO).'),
            ('Wer zahlt Spedition und Einlagerung?',
             'Nach §885 Absatz 3 ZPO bringt der Gerichtsvollzieher die Sachen '
             'auf Kosten des Schuldners in Verwahrung. Bei beschränktem Auftrag '
             'gelten die Kosten für Verwahrung und Verwertung als Kosten der '
             'Zwangsvollstreckung (§885a Absatz 7 ZPO).'),
            ('Darf der Vermieter einfach alles wegwerfen?',
             'Nur im Rahmen einer Räumungsvollstreckung mit Titel: Dann darf '
             'der Gläubiger bei beschränktem Auftrag Sachen vernichten, an '
             'deren Aufbewahrung offensichtlich kein Interesse besteht, und '
             'Unverwertbares nach Ablauf der Monatsfrist (§885a Absatz 3 und 4 '
             'ZPO). Unpfändbare Sachen und solche ohne zu erwartenden Erlös '
             'sind auf Verlangen herauszugeben. Ohne Titel ist eigenmächtiges '
             'Räumen verbotene Eigenmacht (§858 BGB). Wie das im Einzelfall zu beurteilen '
             'ist, klärt der Mieterverein oder ein Rechtsanwalt.'),
            ('Kann ich noch etwas abholen, wenn die Frist abgelaufen ist?',
             'Unpfändbare Sachen und solche ohne zu erwartenden Erlös sind '
             'nach §885 Absatz 5 und §885a Absatz 5 ZPO auf Verlangen jederzeit '
             'herauszugeben, solange sie noch vorhanden sind. Fragen Sie '
             'sofort beim Gerichtsvollzieher oder beim Vermieter nach.'),
        ],

        'leistungen': ['wohnungsaufloesung', 'haushaltsaufloesung'],
        'staedte': [],
    },

    'sperrmuell-chemnitz-abholung-wertstoffhof': {
        'stand_iso': '2026-10',
        'kategorie': 'Entsorgung und Schadstoffe',
        'titel': 'Sperrmüll in Chemnitz: Abholung und Wertstoffhof',
        'h1': 'Sperrmüll in Chemnitz: Abholung, Wertstoffhof und Ausnahmen',
        'h1_em': 'Was der ASR kostenlos abholt, was er nicht mitnimmt und was bei einer Räumung gilt',
        'teaser': (
            'In Chemnitz heißt Sperrmüll „Sperrabfall“ und wird vom ASR '
            'abgeholt oder auf fünf Wertstoffhöfen angenommen. Wie die '
            'Anmeldung läuft, wie man bereitstellt und was ausgeschlossen ist.'
        ),
        'seo_title': 'Sperrmüll Chemnitz: einmal im Jahr kostenlos | Rümpelwerk',
        'seo_description': (
            'So entsorgen Sie Sperrmüll in Chemnitz: Anmeldung beim ASR, '
            'Bereitstellung, Wertstoffhöfe und was nicht dazugehört. '
            'Nach Angaben der Stadt. Jetzt lesen.'
        ),
        'seo_keywords': ('sperrmüll chemnitz, sperrabfall chemnitz anmelden, '
                         'asr chemnitz sperrabfallkarte, wertstoffhof chemnitz, '
                         'sperrmüll abholung chemnitz, entrümpelung chemnitz '
                         'sperrmüll'),

        'answer_frage': 'Wie entsorge ich Sperrmüll in Chemnitz?',
        'answer': (
            'Sperrabfall ist der Chemnitzer Name für Sperrmüll. Der '
            'Abfallentsorgungs- und Stadtreinigungsbetrieb (ASR) holt ihn '
            'nach Anmeldung per Sperrabfallkarte oder online ab, einmal '
            'jährlich je Haushalt gebührenfrei. Alternativ nehmen die fünf '
            'Wertstoffhöfe des ASR Sperrabfall bis 2 m³ pro Anlieferung und '
            'Tag an, nur von Chemnitzer Abfallgebührenzahlern. Rechtsstand: '
            '{stand}.'
        ),

        'quellen': [
            {'schluessel': 'chemnitz-asr-sperrabfall', 'abschnitt': 'abholung',
             'bezug': 'Definition von Sperrabfall, gebührenfreie Abholung, '
                      'Mengen, Frist und Ankündigung des Termins'},
            {'schluessel': 'chemnitz-asr-faq', 'abschnitt': 'abholung',
             'bezug': 'Anmeldung per Sperrabfallkarte oder Online-System, '
                      'eine gebührenfreie Abholung je Kalenderjahr'},
            {'schluessel': 'chemnitz-asr-sperrabfall',
             'abschnitt': 'bereitstellung',
             'bezug': 'Bereitstellungszeit am Fahrbahnrand, Sortierung und '
                      'Bedingungen bei Abholung aus der Wohnung'},
            {'schluessel': 'chemnitz-asr-spezielle-leistungen',
             'abschnitt': 'bereitstellung',
             'bezug': 'Abholung aus Wohnung, Nebengelass und Komplettberäumung '
                      'als gebührenpflichtige Zusatzleistung'},
            {'schluessel': 'chemnitz-asr-wertstoffhoefe',
             'abschnitt': 'wertstoffhoefe',
             'bezug': 'Standorte, Annahmebedingungen, Mengen und Nachweis '
                      'der Wertstoffhöfe'},
            {'schluessel': 'chemnitz-asr-sperrabfall',
             'abschnitt': 'wertstoffhoefe',
             'bezug': 'Selbstanlieferung an den Wertstoffhöfen'},
            {'schluessel': 'chemnitz-asr-sperrabfall',
             'abschnitt': 'ausnahmen',
             'bezug': 'Liste dessen, was nicht zum Sperrabfall gehört, und '
                      'der jeweilige Entsorgungsweg'},
            {'schluessel': 'chemnitz-awvc-annahme', 'abschnitt': 'umwege',
             'bezug': 'Kleinmengenannahme des AWVC am Weißer Weg: Adresse, '
                      'gebührenpflichtig, Elektrogeräte ausgenommen'},
            {'schluessel': 'chemnitz-asr-elektro', 'abschnitt': 'umwege',
             'bezug': 'Elektrogeräte: Wertstoffhof, Mitnahme bei der '
                      'Sperrabfallabholung, Hinweis zu Batterien und Daten'},
            {'schluessel': 'chemnitz-asr-problemabfall',
             'abschnitt': 'umwege',
             'bezug': 'Schadstoffmobil und Abgabemengen für Problemabfall'},
            {'schluessel': 'chemnitz-asr-spezielle-leistungen',
             'abschnitt': 'raeumung',
             'bezug': 'Komplettberäumung nach Arbeitszeitaufwand'},
            {'schluessel': 'chemnitz-asr-sperrabfall', 'abschnitt': 'raeumung',
             'bezug': 'Komplettberäumung mit Vorortbesichtigung, '
                      'Sortierempfehlung, Höchstgewicht je Stück'},
        ],

        'abschnitte': [
            {
                'id': 'abholung',
                'titel': 'Abholung beim ASR: anmelden statt abstellen',
                'absaetze': [
                    'Der Abfallentsorgungs- und Stadtreinigungsbetrieb der '
                    'Stadt Chemnitz (ASR) nennt Sperrabfall, umgangssprachlich '
                    'Sperrmüll, „sperrigen Hausrat, der wegen seines Umfangs, '
                    'seiner Masse oder seiner Beschaffenheit nicht in die von '
                    'der Stadt zur Verfügung gestellten Abfallbehälter passt“. '
                    'Als Beispiele führt die Stadtseite Möbelteile, Koffer, '
                    'Teppiche, Matratzen, Haushaltsschrott und sperrige '
                    'Kunststofferzeugnisse wie Plastikstühle oder -tische auf.',
                    'Angemeldet wird mit der Sperrabfallkarte, die an den '
                    'Wertstoffhöfen, im Kundenservice und in den '
                    'Bürgerservicestellen erhältlich ist, oder über das '
                    'Online-System des ASR; wer die Abholung mit einer '
                    'gebührenpflichtigen Zusatzleistung wie Terminabholung, '
                    'Abholung aus der Wohnung oder Komplettberäumung '
                    'verbindet, füllt laut ASR die Karte in Druckform oder '
                    'das PDF-Formular aus. Nach den Angaben des ASR erhält '
                    'jeder Haushalt eine gebührenfreie Abholung je '
                    'Kalenderjahr; weitere Abholungen im selben Jahr kosten '
                    'nach der aktuellen Gebührenregelung. Die Obergrenze '
                    'nennt die Stadtseite je Jahr: höchstens 20 m³ je '
                    'Haushalt, für Unternehmen höchstens 10 m³.',
                    'Zum Zeitplan heißt es: Die Abholung erfolgt in der Regel '
                    'innerhalb von vier Wochen nach Eingang der Bestellung, '
                    'montags bis freitags, und der Termin wird mindestens '
                    'vier Kalendertage vorher schriftlich mitgeteilt. Wer '
                    'einen festen Tag braucht, kann eine gebührenpflichtige '
                    'Terminabholung wählen; sie liegt laut ASR frühestens '
                    'zehn Tage nach Auftragseingang. Angaben zu Terminen und '
                    'Gebühren können sich ändern (Stand 01.10.2026, vor der '
                    'Bestellung prüfen).',
                ],
            },
            {
                'id': 'bereitstellung',
                'titel': 'Richtig bereitstellen',
                'absaetze': [
                    'Für die Straßenabholung nennt der ASR eine feste Zeit: '
                    'Die Gegenstände sind am Abholtag bis 6 Uhr bereitzustellen, '
                    'frühestens am Vortag ab 18 Uhr, und zwar am Fahrbahnrand. '
                    'Empfohlen wird, nach Holz, Metall und sonstigem '
                    'Sperrabfall zu sortieren.',
                    'Bei einer Abholung aus der Wohnung gelten zusätzliche '
                    'Bedingungen: Der Zugang muss ungehindert sein, größere '
                    'Gegenstände sind so zu zerlegen, dass zwei Personen sie '
                    'problemlos befördern können (höchstens 80 kg pro '
                    'Stück), und die Transportwege müssen trittsicher '
                    'und beleuchtet sein, im Winter schnee- und glättefrei. '
                    'Diese Abholung aus Wohnung oder Nebengelass gehört zu '
                    'den gebührenpflichtigen Zusatzleistungen und wird nach '
                    'Arbeitszeitaufwand berechnet: In der Gebührenübersicht '
                    'zählt jede angefangene Zeiteinheit von sechs Minuten.',
                ],
            },
            {
                'id': 'wertstoffhoefe',
                'titel': 'Selbst anliefern: die fünf Wertstoffhöfe',
                'absaetze': [
                    'Wer nicht auf einen Abholtermin warten will, kann '
                    'Sperrabfall selbst bringen; der ASR nennt die Abgabe an '
                    'den Wertstoffhöfen kostenlos. Auf der Seite stehen fünf '
                    'Höfe: Blankenburgstraße 62, Weißer Weg, '
                    'Jägerschlößchenstraße 15a, Straße Usti nad Labem 30 und '
                    'Kalkstraße 47. Sperrabfall, etwa Matratzen, Möbel, '
                    'Teppiche, Regale und Koffer, wird laut Seite bis 2 m³ '
                    'pro Anlieferung und Tag angenommen, in haushaltsüblichen '
                    'Mengen.',
                    'Die Höfe sind ausschließlich für Chemnitzer '
                    'Abfallgebührenzahler vorgesehen. Wer mit ortsfremdem '
                    'Kennzeichen kommt, weist den Bezug zum Stadtgebiet mit '
                    'Personalausweis (Original), Mietvertrag oder '
                    'Abfallgebührenbescheid nach. Die Öffnungszeiten stehen auf '
                    'der Seite je Hof und sind für die geöffneten Höfe '
                    'einheitlich: montags, dienstags, donnerstags und freitags '
                    '8 bis 18 Uhr, mittwochs 10 bis 19 Uhr, samstags 7 bis '
                    '15 Uhr, sonntags geschlossen. Stand 02.10.2026, vor '
                    'dem Besuch prüfen. Der Hof Blankenburgstraße war Anfang '
                    'Oktober 2026 wegen Bauarbeiten geschlossen (laut ASR bis '
                    'zum 03. bzw. 04.10.2026); ob er wieder geöffnet hat, '
                    'zeigt die Wertstoffhof-Seite des ASR.',
                    'Holzmöbel und Möbelteile aus Holz nehmen die Höfe an; '
                    'Türen, Türrahmen, Fensterrahmen, Abbruchholz und '
                    'Zaunfelder dagegen nicht. Fragen beantwortet der '
                    'Kundenservice des ASR unter 0371 4095-777.',
                ],
            },
            {
                'id': 'ausnahmen',
                'titel': 'Was nicht zum Sperrabfall gehört',
                'absaetze': [
                    'Der ASR führt auf seiner Sperrabfall-Seite ausdrücklich '
                    'auf, was nicht dazugehört, und nennt jeweils den Weg:',
                ],
                'liste': [
                    'Gummi und Abdeckfolie gehören in den Restabfallbehälter.',
                    'Türen, Fenster und Bauschutt gehen zur Kleinmengenannahme des '
                    'AWVC.',
                    'Autoteile gehören zu zertifizierten Annahmestellen.',
                    'Alttextilien gehören in den Alttextiliencontainer.',
                    'Bioabfälle und Gartenabfälle gehören in die Biotonne oder '
                    'auf den eigenen Kompost.',
                    'Farben und Lacke gehören in die Schadstoffsammlung.',
                    'Verpackungen aus Papier, Pappe und Kartonagen gehören in die '
                    'Blaue Tonne.',
                ],
            },
            {
                'id': 'umwege',
                'titel': 'Wohin stattdessen: Bauteile, Elektro, Schadstoffe',
                'absaetze': [
                    'Zum AWVC: Der Abfallwirtschaftsverband Chemnitz nimmt am '
                    'Weißer Weg 180 wohnortunabhängig verschiedene Abfälle '
                    'gegen Gebühr an, darunter Bauschutt; Elektrogeräte '
                    'nimmt er nicht an.',
                    'Elektro- und Elektronikgroßgeräte wie Waschmaschine, '
                    'Kühlschrank oder Fernseher können laut ASR bei der '
                    'Sperrabfallabholung mit beauftragt werden (eine '
                    'separate Abholung kostet Gebühr); alternativ nehmen die '
                    'Wertstoffhöfe große Geräte laut ASR kostenlos an. '
                    'Batterien und Akkus müssen vorher entfernt, persönliche '
                    'Daten gelöscht werden.',
                    'Problemabfall wie Farben und Lacke '
                    'gehört in die Schadstoffsammlung. Laut ASR fährt das '
                    'Schadstoffmobil samstags '
                    'von 8 bis 13 Uhr wechselnde Wertstoffhöfe an und '
                    'nimmt haushaltsübliche Mengen bis 5 kg oder bei Altfarben '
                    'bis 25 kg je Anlieferung gebührenfrei an '
                    '(Stand 01.10.2026, Standorte und Termine beim ASR '
                    'prüfen).',
                ],
            },
            {
                'id': 'raeumung',
                'titel': 'Bei Haushaltsauflösung und Räumung',
                'absaetze': [
                    'Eine ganze Wohnung sprengt das, wofür die Sperrabfall-'
                    'karte gedacht ist. Der ASR bietet für die Komplett-'
                    'beräumung eine eigene gebührenpflichtige Leistung an: '
                    'abgerechnet wird nach Arbeitszeitaufwand, und zur '
                    'Ermittlung ist eine Besichtigung vor Ort erforderlich.',
                    'Praktisch entsteht bei einer Auflösung ein Gemisch aus '
                    'Möbeln, Elektrogeräten, Textilien, Schadstoffen und '
                    'Bauteilen, und für jede dieser Gruppen nennt der ASR '
                    'einen eigenen Weg. Rümpelwerk Mitteldeutschland räumt '
                    'und trennt dabei nach Fraktionen, auf Wunsch gibt es '
                    'einen Entsorgungsnachweis, und das Festpreis-Angebot '
                    'kommt direkt bei der Besichtigung. Wie das in Chemnitz '
                    'aussieht, steht auf der Seite '
                    '<a href="/entrumpelung/chemnitz/">Entrümpelung '
                    'Chemnitz</a>; zur Leistung selbst unter '
                    '<a href="/haushaltsaufloesung/">Haushaltsauflösung</a> '
                    'und <a href="/sperrmuell-entsorgung/">Sperrmüll '
                    'entsorgen</a>.',
                    'Wer selbst räumt, sortiert wie vom ASR empfohlen nach '
                    'Holz, Metall und sonstigem Sperrabfall und legt '
                    'Elektrogeräte, Schadstoffe, Textilien und Bauteile '
                    'getrennt, damit jede Gruppe ihren Weg nehmen kann.',
                ],
            },
        ],

        'faq': [
            ('Ist die Sperrabfallabholung in Chemnitz kostenlos?',
             'Nach den Angaben des ASR ist eine Abholung je Haushalt und '
             'Kalenderjahr gebührenfrei, weitere Abholungen im selben Jahr '
             'kosten nach der aktuellen Gebührenregelung. Terminabholung und '
             'Abholung aus der Wohnung sind gebührenpflichtig.'),
            ('Wie lange dauert es bis zur Abholung?',
             'Der ASR nennt in der Regel vier Wochen nach Eingang der '
             'Bestellung und kündigt den Termin mindestens vier Kalendertage '
             'vorher schriftlich an.'),
            ('Wann darf ich den Sperrabfall rausstellen?',
             'Am Abholtag bis 6 Uhr, frühestens am Vortag ab 18 Uhr, am '
             'Fahrbahnrand. So steht es auf der Seite des ASR.'),
            ('Kann ich Sperrabfall selbst zum Wertstoffhof bringen?',
             'Ja, die fünf Wertstoffhöfe des ASR nehmen Sperrabfall bis 2 m³ '
             'pro Anlieferung und Tag an, aber nur von Chemnitzer '
             'Abfallgebührenzahlern. Bei ortsfremdem Kennzeichen sind '
             'Personalausweis, Mietvertrag oder Abfallgebührenbescheid '
             'nachzuweisen.'),
        ],

        'leistungen': ['sperrmuell-entsorgung', 'haushaltsaufloesung'],
        'staedte': ['chemnitz'],
    },

    'sperrmuell-dresden-abholung-wertstoffhof': {
        'stand_iso': '2026-10',
        'kategorie': 'Entsorgung und Schadstoffe',
        'titel': 'Sperrmüll in Dresden entsorgen',
        'h1': 'Sperrmüll in Dresden: Abholung oder Wertstoffhof',
        'h1_em': 'Was die Stadtreinigung annimmt, was nicht und worauf es beim Räumen ankommt',
        'teaser': (
            'In Dresden gibt es zwei Wege für Sperrmüll: die Abholung vor der '
            'Tür, die online bestellt wird, und die Abgabe auf einem der fünf '
            'Wertstoffhöfe. Was jeweils gilt und was nicht in den Sperrmüll '
            'gehört.'
        ),
        'seo_title': 'Sperrmüll Dresden: Abholung & 5 Wertstoffhöfe | Rümpelwerk',
        'seo_description': (
            'Sperrmüll in Dresden: Abholung online bestellen oder auf dem '
            'Wertstoffhof abgeben. Mengen, Wege und was nicht hineingehört.'
        ),
        'seo_keywords': ('sperrmüll dresden, sperrmüll abholung dresden, '
                         'wertstoffhof dresden, stadtreinigung dresden sperrmüll, '
                         'sperrmüll anmelden dresden, express sperrmüll dresden, '
                         'haushaltsauflösung dresden sperrmüll'),

        'answer_frage': 'Wie wird Sperrmüll in Dresden entsorgt?',
        'answer': (
            'In Dresden geben Haushalte Sperrmüll entweder auf einem der fünf '
            'Wertstoffhöfe der Stadtreinigung Dresden (SRD) ab oder lassen ihn '
            'vor der Tür abholen. Nach den Angaben der SRD sind auf den Höfen '
            'pro Haushalt und Halbjahr vier Kubikmeter kostenfrei; die '
            'Abholung bis vier Kubikmeter kostet eine Gebühr und wird online '
            'bestellt, telefonisch gibt es keine Termine. Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'dresden-srd-sperrmuell', 'abschnitt': 'abholung',
             'bezug': 'Anmeldung online oder per Sperrmüllkarte, keine '
                      'telefonische Terminvergabe, Frist, Bereitstellung am '
                      'Gehwegrand und Gebührenhöhe laut Stadtreinigung'},
            {'schluessel': 'dresden-srd-haushalte', 'abschnitt': 'abholung',
             'bezug': 'Höchstmenge vier Kubikmeter, Bestellung über das '
                      'Online-Formular der Stadt, kein Bargeld vor Ort'},
            {'schluessel': 'dresden-srd-hoefe', 'abschnitt': 'hof',
             'bezug': 'Standorte, Öffnungszeiten, angenommene Materialien und '
                      'Hinweis zu den Bauarbeiten am Hammerweg'},
            {'schluessel': 'dresden-srd-az', 'abschnitt': 'hof',
             'bezug': 'Sperrmüll bis vier Kubikmeter auf den Wertstoffhöfen '
                      'und Containerdienst von 1,5 bis 30 Kubikmetern'},
            {'schluessel': 'dresden-stadt-sperrmuell', 'abschnitt': 'hof',
             'bezug': 'Altholz und Sperrmüll zusammen bis 4 m³ je Halbjahr'},
            {'schluessel': 'dresden-stadt-sperrmuell', 'abschnitt': 'abholung',
             'bezug': 'Die Expressabholung ist nur online bestellbar'},
            {'schluessel': 'dresden-srd-az', 'abschnitt': 'nicht-sperrmuell',
             'bezug': 'Elektroaltgeräte und Schadstoffe mit Mengengrenzen '
                      'sowie Containerdienst für Bauabfälle'},
            {'schluessel': 'dresden-srd-hoefe', 'abschnitt': 'nicht-sperrmuell',
             'bezug': 'Schadstoffe höchstens 25 Liter je Haushalt und '
                      'Halbjahr, Gebrauchtwaren, Schadstoffmobil'},
            {'schluessel': 'dresden-srd-haushalte', 'abschnitt': 'raeumen',
             'bezug': 'Die SRD bietet als Zusatzleistung eine '
                      'Komplettberäumung und einen Container-Service an'},
        ],

        'abschnitte': [
            {
                'id': 'abholung',
                'titel': 'Abholung vor der Tür: so läuft sie in Dresden',
                'absaetze': [
                    'Die Stadtreinigung Dresden GmbH (SRD) holt Sperrmüll aus '
                    'Haushalten ab, bis zu einem Volumen von maximal vier '
                    'Kubikmetern. Angemeldet wird entweder online über das '
                    'Formular der Landeshauptstadt (dresden.de/sperrmuell); '
                    'die Expressabholung lässt sich laut Stadt nur online '
                    'bestellen. Die '
                    'SRD schreibt ausdrücklich, dass in Dresden eine '
                    'telefonische Vergabe von Abholterminen nicht möglich '
                    'ist. Wer anruft, bekommt also keinen Termin, sondern '
                    'höchstens Auskunft.',
                    'Laut Stadtreinigung kostet die Standardabholung 29,37 '
                    'Euro und erfolgt üblicherweise innerhalb von vier Wochen; '
                    'die Expressabholung kostet 88,12 Euro und erfolgt '
                    'üblicherweise innerhalb von drei Werktagen nach '
                    'Bestelleingang (Stand 01.10.2026; Gebühren und Fristen '
                    'können sich ändern, vor der Bestellung auf der Seite der '
                    'SRD prüfen). Der genaue Termin wird nach Angaben der SRD '
                    'schriftlich vom beauftragten Entsorgungsunternehmen '
                    'mitgeteilt, ebenso, bis wann der Sperrmüll am Gehwegrand '
                    'bereitgestellt sein muss.',
                    'Ein Hinweis, den die SRD selbst gibt: Sie verlangt für '
                    'gebührenpflichtige Zusatzleistungen generell kein Bargeld '
                    'vor Ort. Wer vor der Tür Bargeld fordert, handelt damit '
                    'nicht nach dem Verfahren, das die Stadtreinigung '
                    'beschreibt.',
                ],
            },
            {
                'id': 'hof',
                'titel': 'Die fünf Wertstoffhöfe: Standorte und Menge',
                'absaetze': [
                    'Wer den Sperrmüll selbst fährt, nutzt die Wertstoffhöfe '
                    'der SRD. Pro Haushalt und Halbjahr können dort vier '
                    'Kubikmeter Sperrmüll kostenfrei abgegeben werden. Die '
                    'Höfe liegen an diesen Adressen: Friedrichstadt '
                    '(Altonaer Straße 15), Reick (Georg-Mehrtens-Straße 1), '
                    'Hammerweg (Hammerweg 23), Johannstadt (Hertelstraße 3) '
                    'und Kaditz (Scharfenberger Straße 146).',
                    'Laut Seite der SRD (Stand 01.10.2026, vor dem Besuch '
                    'prüfen) sind Friedrichstadt, Reick und Hammerweg montags '
                    'bis freitags von 7 bis 19 Uhr geöffnet, Johannstadt und '
                    'Kaditz montags bis freitags von 12 bis 19 Uhr; samstags '
                    'sind alle fünf von 8 bis 14 Uhr geöffnet. Für den '
                    'Wertstoffhof Hammerweg nennt die SRD Einschränkungen '
                    'durch externe Bauarbeiten bis zum 24.07.2027 und '
                    'empfiehlt, in der Zwischenzeit auf einen anderen Hof '
                    'auszuweichen.',
                    'Neben Sperrmüll nennt die SRD als angenommene Stoffe '
                    'unter anderem Altholz, Alttextilien, Batterien, '
                    'mineralischen Bauschutt (nicht in Johannstadt, am '
                    'Hammerweg und in Kaditz), Elektroschrott, Grünabfall, '
                    'Haushaltsschrott, Kunststoffabfall, Papier und Glas. '
                    'Wer größere Mengen als vier Kubikmeter hat, findet bei '
                    'der SRD außerdem einen Containerdienst mit Größen von '
                    '1,5 bis 30 Kubikmetern. Die Benutzungsordnung der Höfe '
                    'und die Anweisungen des Annahmepersonals gelten vor Ort.',
                ],
            },
            {
                'id': 'nicht-sperrmuell',
                'titel': 'Was nicht in den Sperrmüll gehört',
                'absaetze': [
                    'Sperrmüll meint nach der Beschreibung der SRD sperrige '
                    'Haushaltsabfälle wie Teppiche, Matratzen und Fahrräder. '
                    'Für anderes gibt es eigene Wege. Elektroaltgeräte wie '
                    'Fernseher, Radioanlagen und Monitore nehmen die '
                    'Wertstoffhöfe kostenfrei an; sie gehören nicht einfach '
                    'zum Sperrmüll an den Gehwegrand.',
                    'Schadstoffe sind eine eigene Fraktion. Die SRD nennt '
                    'zwei Wege: das Schadstoffmobil, bei dem bis maximal 10 '
                    'Kilogramm kostenfrei abgegeben werden können, und die '
                    'Wertstoffhöfe, wo je Haushalt und Halbjahr höchstens 25 '
                    'Liter angenommen werden, berechnet über die '
                    'Verpackungsgrößen. Als Beispiel für das Schadstoffmobil '
                    'nennt die SRD übrig gebliebene Desinfektionsmittel und '
                    'Haushaltsreiniger. Die Menge von 10 Kilogramm steht '
                    'auf der A-bis-Z-Seite der SRD, die 25 Liter stehen '
                    'auf der Seite der Wertstoffhöfe; die beiden Angaben '
                    'beziehen sich auf unterschiedliche Wege und sind '
                    'nicht umrechenbar.',
                    'Für Bau- und Abbruchabfälle bietet die SRD Container von '
                    '1,5 bis 30 Kubikmetern an; mineralischen Bauschutt '
                    'nehmen zudem die Höfe Friedrichstadt und Reick an. '
                    'Gebrauchtwaren zur Wiederverwendung führt '
                    'die SRD unter den Stoffen der Höfe auf, mit dem '
                    'Zusatz „nicht beim WSH Johannstadt“. Brauchbare Dinge gar nicht erst in den '
                    'Sperrmüll zu werfen, spart Volumen.',
                ],
            },
            {
                'id': 'raeumen',
                'titel': 'Bei Haushaltsauflösung und Räumung: Fraktionen trennen',
                'absaetze': [
                    'Eine Wohnung bringt schnell mehr zusammen als die vier '
                    'Kubikmeter, die der Haushalt je Halbjahr hat, und '
                    'darunter liegt fast immer mehr als Sperrmüll: Elektrogeräte, '
                    'Schadstoffe, Altholz, Textilien, Papier. Die Dresdner '
                    'Regeln legen nahe, schon beim Ausräumen in Gruppen zu '
                    'denken: Sperrmüll, Elektroaltgeräte, Schadstoffe mit '
                    'Mengenbegrenzung, Wertstoffe wie Papier und Glas, '
                    'Brauchbares zur Wiederverwendung.',
                    'Rümpelwerk Mitteldeutschland räumt Wohnungen und Häuser in '
                    'Dresden und trennt dabei nach Fraktionen; auf Wunsch gibt '
                    'es einen Entsorgungsnachweis. Das Festpreis-Angebot '
                    'gibt es direkt bei der Besichtigung. Wie das bei einer '
                    '<a href="/haushaltsaufloesung/">Haushaltsauflösung</a> '
                    'abläuft, steht auf der Leistungsseite; Grundsätzliches '
                    'zu Sperrgut finden Sie unter '
                    '<a href="/sperrmuell-entsorgung/">Sperrmüll entsorgen</a> '
                    'und unter <a href="/entrumpelung/dresden/">Entrümpelung '
                    'in Dresden</a>.',
                    'Die Wahl des Wegs hängt an Menge und Zeit. Auf dem Hof '
                    'sind vier Kubikmeter je Haushalt und Halbjahr '
                    'kostenfrei, dafür müssen Sie selbst laden, fahren und '
                    'sich nach den Öffnungszeiten richten. Die Abholung '
                    'kostet laut SRD eine Gebühr, nimmt aber bis zu vier '
                    'Kubikmeter vor der Tür mit, und wer die Frist von '
                    'üblicherweise vier Wochen nicht abwarten kann, wählt '
                    'die Expressabholung. Alles, was nicht zum Sperrmüll '
                    'zählt, bleibt in beiden Fällen außen vor und braucht '
                    'seinen eigenen Weg.',
                    'Die SRD bietet selbst eine Komplettberäumung als '
                    'Zusatzleistung an, ebenso den Container-Service. Wer '
                    'Sperrmüll nur in kleinen Mengen hat, kommt mit Abholung '
                    'oder Hof allein aus; je mehr aus der Wohnung kommt, '
                    'desto eher lohnt der Blick auf Aufwand, Fristen und '
                    'Trennung, bevor ein Termin bestellt wird.',
                ],
            },
        ],

        'faq': [
            ('Kann ich einen Abholtermin für Sperrmüll in Dresden telefonisch '
             'vereinbaren?',
             'Nein. Die Stadtreinigung Dresden schreibt, dass eine telefonische '
             'Vergabe von Abholterminen in Dresden nicht möglich ist; '
             'angemeldet wird online über dresden.de/sperrmuell. Die SRD nennt '
             'als Kundenhotline (0351) 44 55-118.'),
            ('Wie viel Sperrmüll darf ich auf dem Wertstoffhof abgeben?',
             'Laut Stadtreinigung vier Kubikmeter je Haushalt und Halbjahr '
             'kostenfrei – laut Stadt Dresden zusammen mit Altholz '
             '(Möbelholz), nicht zusätzlich dazu. Größere Mengen lassen sich über den Containerdienst '
             'der SRD abwickeln.'),
            ('Was kostet die Abholung und wie schnell geht sie?',
             'Laut SRD (Stand 01.10.2026) 29,37 Euro für die '
             'Standardabholung, üblicherweise innerhalb von vier Wochen, und '
             '88,12 Euro für die Expressabholung, üblicherweise innerhalb von '
             'drei Werktagen. Vor der Bestellung die aktuellen Angaben der '
             'SRD prüfen.'),
            ('Wohin mit Farbresten und Haushaltsreinigern?',
             'Nicht in den Sperrmüll. Die SRD nimmt Schadstoffe am '
             'Schadstoffmobil bis maximal 10 Kilogramm kostenfrei an; auf den '
             'Wertstoffhöfen sind es je Haushalt und Halbjahr höchstens 25 '
             'Liter, berechnet über die Verpackungsgrößen.'),
        ],

        'leistungen': ['sperrmuell-entsorgung', 'haushaltsaufloesung'],
        'staedte': ['dresden'],
    },

    'sperrmuell-halle-saale-abholung-wertstoffhof': {
        'stand_iso': '2026-10',
        'kategorie': 'Entsorgung und Schadstoffe',
        'titel': 'Sperrmüll in Halle (Saale): Abholung und Wertstoffmarkt',
        'h1': 'Sperrmüll in Halle (Saale): Abholung, Wertstoffmarkt, Ausnahmen',
        'h1_em': 'Was die HWS gebührenfrei abholt und was nicht auf den Sperrmüll gehört',
        'teaser': (
            'In Halle holt die Hallesche Wasser und Stadtwirtschaft Sperrmüll '
            'einmal jährlich bis zu einer Höchstmenge ab, drei Wertstoffmärkte '
            'nehmen Kleinmengen an. Wie die Anmeldung läuft, was bereitgestellt '
            'werden darf und was bei einer Räumung anders gilt.'
        ),
        'seo_title': 'Sperrmüll Halle (Saale): Abholung & Annahme | Rümpelwerk',
        'seo_description': (
            'Sperrmüll in Halle (Saale): gebührenfreie Abholung durch die HWS, '
            'Wertstoffmärkte, Ausnahmen und was bei einer Haushaltsauflösung '
            'gilt. Jetzt lesen.'
        ),
        'seo_keywords': ('sperrmüll halle saale, sperrmüll abholung halle, '
                         'sperrmüllabrufkarte halle, wertstoffmarkt halle, '
                         'hws halle sperrmüll, sperrmüll anmelden halle, '
                         'haushaltsauflösung halle sperrmüll'),

        'answer_frage': 'Wie wird Sperrmüll in Halle (Saale) entsorgt?',
        'answer': (
            'In Halle (Saale) kostet die Sperrmüllabholung der Halleschen '
            'Wasser und Stadtwirtschaft (HWS) einmal jährlich nichts, bis zu '
            '2 m³ je im Haushalt lebender Person; die Anmeldung läuft über '
            'eine Abrufkarte oder online. Alternativ nehmen die '
            'Wertstoffmärkte der HWS Sperrmüll an, der erste Kubikmeter ist '
            'gebührenfrei. Größere Mengen, etwa bei einer '
            'Haushaltsauflösung, sind gebührenpflichtig. Rechtsstand: '
            '{stand}.'
        ),

        'quellen': [
            {'schluessel': 'sperrmuell-halle-abfallabc', 'abschnitt': 'abholung',
             'bezug': 'Definition von Sperrmüll, Jahresmenge von 2 m³ je '
                      'Person, Maße und Gewicht je Einzelstück'},
            {'schluessel': 'sperrmuell-halle-hws', 'abschnitt': 'abholung',
             'bezug': 'Jährliche gebührenfreie Abholung und weitere '
                      'Entsorgungswege der HWS'},
            {'schluessel': 'sperrmuell-halle-bestellung', 'abschnitt': 'abholung',
             'bezug': 'Ablauf der Anmeldung, Abholung innerhalb von fünf '
                      'Wochen, Wunschtermin gegen Gebühr'},
            {'schluessel': 'sperrmuell-halle-portal', 'abschnitt': 'abholung',
             'bezug': 'Frist, Termingebühr und Zuständigkeit im '
                      'Serviceportal der Stadt'},
            {'schluessel': 'sperrmuell-halle-abrufkarte', 'abschnitt': 'abholung',
             'bezug': 'Orientierungswerte je Gegenstand und gebührenpflichtige '
                      'Abfuhr größerer Mengen (Formular Stand 2023)'},
            {'schluessel': 'sperrmuell-halle-bestellung', 'abschnitt': 'bereitstellung',
             'bezug': 'Bereitstellung bis 6:00 Uhr außerhalb des Grundstücks, '
                      'keine Abholung an Sonn- und Feiertagen'},
            {'schluessel': 'sperrmuell-halle-abrufkarte', 'abschnitt': 'bereitstellung',
             'bezug': 'Nur angemeldeter Sperrmüll wird entsorgt; der '
                      'Auftraggeber ist für die Bereitstellung verantwortlich'},
            {'schluessel': 'sperrmuell-halle-markt', 'abschnitt': 'wertstoffmarkt',
             'bezug': 'Anschriften und Öffnungszeiten der drei Wertstoffmärkte '
                      'sowie der Second-Hand-Container'},
            {'schluessel': 'sperrmuell-halle-portal-abfall', 'abschnitt': 'wertstoffmarkt',
             'bezug': 'Erster Kubikmeter gebührenfrei, größere Mengen nach '
                      'Abfallgebührensatzung'},
            {'schluessel': 'sperrmuell-halle-abrufkarte', 'abschnitt': 'wertstoffmarkt',
             'bezug': 'Selbstanlieferung bis 1 m³ gebührenfrei, Gebühr bei '
                      'größeren Mengen am Wertstoffmarkt'},
            {'schluessel': 'sperrmuell-halle-pressemeldung', 'abschnitt': 'wertstoffmarkt',
             'bezug': 'Sammelcontainer werden als illegale Abladeorte für '
                      'Sperrmüll missbraucht'},
            {'schluessel': 'sperrmuell-halle-abfallabc', 'abschnitt': 'ausnahmen',
             'bezug': 'Ausnahmen: Linoleum, Elektroaltgeräte, verpackte '
                      'Kleinteile'},
            {'schluessel': 'sperrmuell-halle-abrufkarte', 'abschnitt': 'ausnahmen',
             'bezug': 'Aufzählung dessen, was nicht zum Sperrmüll gehört '
                      '(Formular Stand 2023)'},
            {'schluessel': 'sperrmuell-halle-elektro', 'abschnitt': 'ausnahmen',
             'bezug': 'Elektroaltgeräte: kostenlose Abgabe am Wertstoffmarkt '
                      'und kostenlose Abholung großer Geräte'},
            {'schluessel': 'sperrmuell-halle-bau', 'abschnitt': 'ausnahmen',
             'bezug': 'Bau- und Abbruchabfälle getrennt halten; Container '
                      'der HWS und Kleinmengen am Wertstoffmarkt'},
            {'schluessel': 'sperrmuell-halle-abrufkarte', 'abschnitt': 'aufloesung',
             'bezug': 'Größere Mengen, etwa eine Haushaltsauflösung, per '
                      'Antrag und gebührenpflichtig über Container oder '
                      'Pressfahrzeug'},
        ],

        'abschnitte': [
            {
                'id': 'abholung',
                'titel': 'Die Abholung: einmal im Jahr, nach Menge begrenzt',
                'absaetze': [
                    'Die Stadt Halle (Saale) definiert Sperrmüll als Abfall, '
                    'der „selbst nach einer zumutbaren Zerkleinerung auf Grund '
                    'seiner Ausmaße, seiner Sperrigkeit, seines Gewichtes oder '
                    'seiner Materialbeschaffenheit nicht in die '
                    'Restmüllbehälter passt“. Dazu zählt sie sperrige Möbel '
                    'wie Schrankwände, Küchenmöbel, Sessel, Truhen, Regale und '
                    'Bettgestelle, außerdem Matratzen, Teppiche, Fahrräder, '
                    'Kinderwagen, Koffer, Bügelbretter und Leitern.',
                    'Die Abholung übernimmt die Hallesche Wasser und '
                    'Stadtwirtschaft GmbH (HWS). Nach der Stadtseite wird '
                    'Sperrmüll „einmal jährlich bis zu einer Menge von max. '
                    '2 m³ pro im Haushalt lebender Person auf Bestellung mit '
                    'der Sperrmüllabrufkarte gebührenfrei“ abgeholt. Ein '
                    'Einzelstück darf höchstens 2,20 m × 1,50 m × 0,75 m '
                    'messen und nicht schwerer als 70 kg sein. Die Bestellung '
                    'geht online über die Seite der HWS; nach der Abrufkarte '
                    'sind auch Post und E-Mail an den Kundenservice der HWS '
                    'möglich. Wer die Karte schickt, trägt dort die '
                    'Gegenstände mit Stückzahl ein und gibt die Zahl der im '
                    'Haushalt lebenden Personen an.',
                    'Ohne Wunschtermin wird der Sperrmüll nach den Angaben der '
                    'HWS innerhalb von fünf Wochen nach Karteneingang abgeholt; der Termin wird '
                    'mindestens drei Tage vorher mitgeteilt. Ein individueller '
                    'Wunschtermin kostet laut Stadtseite 20,00 Euro Termin'
                    'gebühr und muss spätestens drei Arbeitstage vorher '
                    'bezahlt sein (Stand 01.10.2026; vor Nutzung prüfen). Die '
                    'Abrufkarte von 2023 nennt dafür noch 18 Euro – hier '
                    'gilt der neuere Betrag der Stadt- und HWS-Seite. '
                    'Jeder Haushalt kann die Abholung nur einmal pro Jahr '
                    'anmelden.',
                    'Wie schnell die zwei Kubikmeter je Person erreicht sind, '
                    'zeigt die Orientierungstabelle auf der Abrufkarte '
                    '(Durchschnittswerte, Formular Stand 2023): ein Fahrrad '
                    '0,2 m³, eine Matratze 0,3 m³, eine Kommode 0,6 m³, ein '
                    'Sofa 0,8 m³, ein großer Kleiderschrank oder eine '
                    'Schrankwand 1,0 m³, eine Eckcouch 1,5 m³. Schrankwand und '
                    'Eckcouch zusammen ergeben 2,5 m³ – das übersteigt die '
                    'Jahresmenge einer einzelnen Person bereits. Für größere '
                    'Mengen, schwerere oder größere Einzelstücke und '
                    'häufigere Abholungen ist die Abfuhr auf schriftlichen '
                    'Antrag bei der HWS gebührenpflichtig.',
                ],
            },
            {
                'id': 'bereitstellung',
                'titel': 'Bereitstellen: Uhrzeit, Ort, Verantwortung',
                'absaetze': [
                    'Die Bestellseite der HWS nennt als Bereitstellung, dass '
                    'der Sperrmüll am Abholtag bis 6:00 Uhr außerhalb des '
                    'Grundstücks stehen muss; Abholungen finden nicht an Sonn- '
                    'und Feiertagen statt. Die Abrufkarte (Stand 2023) '
                    'nennt dagegen 7 Uhr – ein offener Widerspruch zwischen '
                    'den Quellen. Maßgeblich ist, was die Bestätigung zu '
                    'Ihrem Termin sagt. Außerdem verlangt die Karte, die '
                    'Stücke geordnet so abzustellen, dass der öffentliche '
                    'Verkehrsraum nicht verschmutzt und die '
                    'Verkehrssicherheit nicht beeinträchtigt wird.',
                    'Entsorgt wird nur, was angemeldet wurde. Nach der '
                    'Abrufkarte werden Teile, die nicht zum Sperrmüll gehören, '
                    'nicht entsorgt; der Auftraggeber ist für die '
                    'Bereitstellung verantwortlich und soll darauf achten, '
                    'dass niemand anderes etwas dazustellt. Deshalb '
                    'lohnt es sich, die Liste bei der Anmeldung so vollständig '
                    'zu führen, wie der Haufen später aussieht, und '
                    'Kleinteile nicht in Kartons oder Säcken danebenzustellen.',
                ],
            },
            {
                'id': 'wertstoffmarkt',
                'titel': 'Selbst anliefern: die drei Wertstoffmärkte',
                'absaetze': [
                    'Sperrmüll lässt sich auch ohne Termin selbst '
                    'abgeben. Die Stadt schreibt dazu: „Sperrmüll kann '
                    'vom Abfallbesitzer auch an den Wertstoffmärkten der HWS '
                    'abgegeben werden, wobei der erste Kubikmeter gebührenfrei '
                    'ist.“ Für größere Mengen verweist sie auf die '
                    'Abfallgebührensatzung; nach der Abrufkarte ist die Gebühr '
                    'bei der Abgabe am Wertstoffmarkt zu zahlen.',
                    'Die Wertstoffmärkte liegen in der Äußeren Hordorfer '
                    'Straße 12 (06114), in der Äußeren Radeweller Straße 15 '
                    '(06132) und in der Schieferstraße 2 (06126). Laut HWS '
                    'sind alle drei montags bis freitags von 6:00 bis 20:30 '
                    'Uhr und samstags von 7:00 bis 12:00 Uhr geöffnet, '
                    'sonntags und an Feiertagen geschlossen (Stand '
                    '01.10.2026; vor einem Besuch prüfen). In der Äußeren '
                    'Hordorfer Straße gelten von März bis Oktober zusätzliche '
                    'Zeiten für Grünschnitt.',
                    'In der Äußeren Hordorfer Straße steht auch ein '
                    'Second-Hand-Container. Gut erhaltene, saubere und '
                    'funktionsfähige Dinge wie Geschirr, Kleinmöbel, Spielzeug '
                    'oder Fahrräder nimmt die HWS während der Öffnungszeiten '
                    'der Wertstoffmärkte an; der Container, in dem sie günstig '
                    'weitergegeben werden, ist montags bis freitags von 15 bis '
                    '18 Uhr geöffnet. Abgeben kann man solche Dinge laut HWS '
                    'auch an den beiden anderen Standorten. Für Brauchbares lohnt sich '
                    'der Umweg also, bevor es als Sperrmüll endet.',
                    'Ein Hinweis der Stadt vom 19.06.2025: Container für '
                    'Altglas oder Altkleider werden „als illegale Abladeorte '
                    'für Sperrmüll oder Elektroschrott missbraucht“. Sperrmüll '
                    'gehört dorthin nicht, auch nicht „nur kurz“.',
                ],
            },
            {
                'id': 'ausnahmen',
                'titel': 'Was nicht zum Sperrmüll gehört und wohin stattdessen',
                'absaetze': [
                    'Die Stadtseite nennt als Ausnahmen Linoleum, '
                    'Elektroaltgeräte und in Säcken, Kartons oder anderen '
                    'Behältnissen verpackte Kleinteile. Die Abrufkarte (Stand '
                    '2023) führt weitere Beispiele auf: Autowracks und '
                    'Kfz-Teile wie Reifen und Batterien, Abfälle von Bau- und '
                    'Umbauarbeiten wie Türen, Fenster, Rohre, Sanitär und '
                    'Heizungsanlagen, Laminat, Verpackungsmaterial, '
                    'Gartenabfälle, Schadstoffe, Altkleider, Federbetten, '
                    'Decken, Geschirr und Lampen.',
                    'Die Wege dafür sind getrennt. Elektro- und '
                    'Elektronikaltgeräte nehmen die Wertstoffmärkte der HWS '
                    'kostenlos an; große oder schwere Geräte werden nach '
                    'Terminabsprache kostenlos abgeholt (Telefon 0345 '
                    '581-4100 oder online). Kleine Geräte gehören ins '
                    'Schadstoffmobil oder in stadtweite Sammelbehälter, '
                    'und vor der Rückgabe sollten personenbezogene Daten '
                    'gelöscht werden. Mehr dazu unter '
                    '<a href="/ratgeber/elektroaltgeraete-entsorgen/">'
                    'Elektroaltgeräte entsorgen</a>.',
                    'Bau- und Abbruchabfälle – die Stadt nennt Bauschutt, '
                    'Fenster, Türen, Abbruchholz, Boden, Steine und '
                    'Dämmmaterial – sind „getrennt voneinander und von anderen '
                    'Abfällen zu halten und zu entsorgen“. Dafür gibt es '
                    'gebührenpflichtige HWS-Container; Kleinmengen bis 1 m³ '
                    'nehmen die Wertstoffmärkte gegen Gebühr an. Asbesthaltige '
                    'Abfälle müssen staubdicht in zugelassenen, '
                    'gekennzeichneten Big Bags verpackt werden – siehe '
                    '<a href="/ratgeber/asbest-im-haushalt/">Asbest im '
                    'Haushalt</a>. Für Farben, Lacke und Chemikalien gilt '
                    '<a href="/ratgeber/schadstoffe-im-haushalt-farben-lacke-'
                    'chemikalien/">der Weg über die Schadstoffannahme</a>; '
                    'Altholz behandelt <a href="/ratgeber/'
                    'altholz-moebel-entsorgen/">ein eigener Beitrag</a>.',
                ],
            },
            {
                'id': 'aufloesung',
                'titel': 'Ganze Wohnung: wenn die Jahresmenge nicht reicht',
                'absaetze': [
                    'Eine ganze Wohnung sprengt die Jahresmenge schnell. Die '
                    'Abrufkarte nennt die Haushaltsauflösung selbst als '
                    'Beispiel für „größere Mengen als 2 m³ pro Person“: Sie '
                    'sind schriftlich zu beantragen und gebührenpflichtig, '
                    'die Entsorgung läuft über Container oder Pressfahrzeug, '
                    'die Höhe hängt von der Tonnage ab. Die Abrufkarte lässt '
                    'sich in diesem Fall nicht nutzen, auch nicht anteilig.',
                    'Die Liste der Ausnahmen zeigt, dass bei einer Räumung '
                    'mehrere Wege nebeneinander laufen: Sperrmüll im engeren '
                    'Sinn, Elektroaltgeräte, Bau- und Umbauteile, Schadstoffe, '
                    'Altkleider und Gebrauchsfähiges werden getrennt '
                    'behandelt. '
                    'Rümpelwerk Mitteldeutschland räumt bei einer '
                    '<a href="/haushaltsaufloesung/">Haushaltsauflösung</a> '
                    'und trennt dabei nach Fraktionen; auf Wunsch gibt es '
                    'einen Entsorgungsnachweis. Das Festpreis-Angebot nennt '
                    'der Betrieb direkt bei der Besichtigung, auch für '
                    '<a href="/entrumpelung/halle/">Halle (Saale)</a>.',
                    'Wer nur einzelne Stücke loswerden will, kommt mit der '
                    'Abrufkarte oder dem Wertstoffmarkt aus; Hinweise zu '
                    'Sperrgut allgemein stehen unter '
                    '<a href="/sperrmuell-entsorgung/">Sperrmüll '
                    'entsorgen</a>. Ob die eigene Menge noch unter die '
                    'Jahresmenge fällt, lässt sich mit der Orientierungstabelle '
                    'vorab überschlagen.',
                ],
            },
        ],

        'faq': [
            ('Wie viel Sperrmüll holt die HWS kostenlos ab?',
             'Nach der Stadt Halle (Saale) einmal jährlich bis zu 2 m³ je im '
             'Haushalt lebender Person. Einzelstücke dürfen höchstens '
             '2,20 m × 1,50 m × 0,75 m messen und nicht mehr als 70 kg '
             'wiegen; darüber hinaus ist die Abholung gebührenpflichtig.'),
            ('Kann ich Sperrmüll selbst zum Wertstoffmarkt bringen?',
             'Ja. Die Wertstoffmärkte der HWS in der Äußeren Hordorfer Straße '
             '12, der Äußeren Radeweller Straße 15 und der Schieferstraße 2 '
             'nehmen Sperrmüll an; der erste Kubikmeter ist laut Stadt '
             'gebührenfrei, für mehr gilt die Abfallgebührensatzung. '
             'Öffnungszeiten vor dem Besuch auf der Seite der HWS prüfen.'),
            ('Gehören Kühlschrank und Waschmaschine zum Sperrmüll?',
             'Nein, Elektroaltgeräte sind nach der Stadtseite ausgenommen. '
             'Sie werden an den Wertstoffmärkten kostenlos angenommen; große '
             'oder schwere Geräte holt die HWS nach Terminabsprache '
             'kostenlos ab.'),
            ('Reicht die Sperrmüllabrufkarte für eine Haushaltsauflösung?',
             'Meist nicht. Größere Mengen als 2 m³ je Person fallen unter die '
             'gebührenpflichtige Entsorgung auf Antrag bei der HWS, die '
             'Abrufkarte ist dafür nicht nutzbar. Wie Rümpelwerk '
             'Mitteldeutschland eine Räumung angeht, steht unter '
             '<a href="/haushaltsaufloesung/">Haushaltsauflösung</a>.'),
        ],

        'leistungen': ['sperrmuell-entsorgung', 'haushaltsaufloesung'],
        'staedte': ['halle'],
    },

    'sperrmuell-magdeburg-abholung-wertstoffhof': {
        'stand_iso': '2026-10',
        'kategorie': 'Entsorgung und Schadstoffe',
        'titel': 'Sperrmüll in Magdeburg',
        'h1': 'Sperrmüll in Magdeburg: Abholung und Wertstoffhof',
        'h1_em': 'Was die Stadt kostenfrei abholt, was sie nicht annimmt und wie man trennt',
        'teaser': (
            'Magdeburg holt Sperrmüll aus Haushalten gebührenfrei ab, mit '
            'Mengengrenze und Wartezeit. Dazu drei Wertstoffhöfe. Was '
            'dazugehört, was nicht und was das bei einer Räumung heißt.'
        ),
        'seo_title': 'Sperrmüll Magdeburg: bis 4 m³ kostenfrei | Rümpelwerk',
        'seo_description': (
            'Sperrmüll in Magdeburg: kostenfreie Abholung, Anmeldung, die drei '
            'Wertstoffhöfe, was nicht dazugehört und Trennen bei einer '
            'Räumung. Jetzt lesen.'
        ),
        'seo_keywords': ('sperrmüll magdeburg, sperrmüll abholung magdeburg, '
                         'wertstoffhof magdeburg, sperrmüll anmelden magdeburg, '
                         'sab magdeburg sperrmüll, haushaltsauflösung magdeburg'),

        'answer_frage': 'Wie wird Sperrmüll in Magdeburg abgeholt oder abgegeben?',
        'answer': (
            'Haushalte in Magdeburg können laut Stadt zweimal im Jahr bis zu '
            '2 m³ oder einmal bis zu 4 m³ Sperrmüll gebührenfrei abholen '
            'lassen; die Planungszeit beträgt bis zu vier Wochen. Anmelden '
            'lässt sich online, per Telefon, Fax, Postkarte oder persönlich '
            'beim Städtischen Abfallwirtschaftsbetrieb. Alternativ nehmen '
            'drei Wertstoffhöfe Sperrmüll an. Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'magdeburg-sperrmuell', 'abschnitt': 'abholung',
             'bezug': 'Kontingent, Anmeldewege, Planungszeit, Wunschtermin '
                      'und Hinweise zur Bereitstellung'},
            {'schluessel': 'magdeburg-sperrmuell', 'abschnitt': 'ausschluss',
             'bezug': 'Gegenstände, die nicht zum Sperrmüll gehören, und die '
                      'Größen- und Gewichtsgrenze'},
            {'schluessel': 'magdeburg-wertstoffhoefe', 'abschnitt': 'hoefe',
             'bezug': 'Standorte, Öffnungszeiten, Mengengrenzen, '
                      'Kleinanlieferer-Regelung und Schadstoffsammelstellen '
                      'der drei Wertstoffhöfe'},
            {'schluessel': 'magdeburg-wertstoffhof-abgeben',
             'abschnitt': 'hoefe',
             'bezug': 'angenommene Abfallarten, Schadstoff-Standorte, '
                      'Herkunftsnachweis, Hausmüll ausgenommen'},
            {'schluessel': 'magdeburg-schadstoffe', 'abschnitt': 'ausschluss',
             'bezug': 'Annahme von Schadstoffen, Mengen und Hinweis zur '
                      'Verpackung'},
            {'schluessel': 'magdeburg-sperrmuell', 'abschnitt': 'raeumung',
             'bezug': 'Sortierung nach Holz, Altmetall, Elektrogeräten, '
                      'Kunststoff und Sonstigem bei der Bereitstellung'},
            {'schluessel': 'magdeburg-wertstoffhof-abgeben',
             'abschnitt': 'raeumung',
             'bezug': 'Abfallarten, die getrennt am Wertstoffhof angenommen '
                      'werden'},
        ],

        'abschnitte': [
            {
                'id': 'abholung',
                'titel': 'Die Abholung durch die Stadt',
                'absaetze': [
                    'Die Landeshauptstadt Magdeburg bietet Haushalten eine '
                    'gebührenfreie Sperrmüllabfuhr an. Nach der Stadtseite '
                    'zur Sperrmüllentsorgung können Haushalte zweimal im '
                    'Jahr bis zu 2 m³ oder einmal bis zu 4 m³ abholen lassen. '
                    'Den Termin legt der Betrieb fest; bis dahin ist mit '
                    'einer Planungszeit von bis zu vier Wochen zu rechnen. '
                    'Wer das nicht abwarten kann, hat zwei Wege: einen '
                    'Wunschtermin gegen eine Servicegebühr (laut Stadtseite '
                    '50 Euro, Anmeldung spätestens eine Woche vorher) oder '
                    'den Wertstoffhof.',
                    'Angemeldet wird laut Stadt über das Online-Formular, über '
                    'das Service-Telefon des Sperrmüllservice, per Fax, per '
                    'Postkarte an den Städtischen Abfallwirtschaftsbetrieb '
                    '(Sternstraße 13, 39104 Magdeburg) oder persönlich '
                    'während der Öffnungszeiten. Die aktuelle Rufnummer und '
                    'die Zeiten stehen auf der Stadtseite; sie ändern sich '
                    'gelegentlich und sollten vor dem Anruf nachgelesen '
                    'werden (Stand der Angaben: 01.10.2026).',
                    'Bereitgestellt wird der Sperrmüll laut Stadt bis 7 Uhr, '
                    'frühestens am Vorabend, ordnungsgemäß am Fahrbahnrand '
                    'und nach Materialien sortiert. Genannt werden Holz, '
                    'Altmetall, Elektrogeräte, Kunststoff und Sonstiges. Wer '
                    'mehr loswerden will als das Kontingent, kann nach der '
                    'Stadtseite einen Transportservice gegen Entgelt nutzen; '
                    'dort stehen 15,40 Euro je angefangener halber '
                    'Kubikmeter und 13 Euro je Elektroaltgerät (Stand '
                    '01.10.2026).',
                ],
            },
            {
                'id': 'hoefe',
                'titel': 'Die drei Wertstoffhöfe',
                'absaetze': [
                    'Magdeburg betreibt drei Wertstoffhöfe: Hängelsberge '
                    '(Königstraße 96), Cracauer Anger (An der Lake 3) und '
                    'Silberbergweg (Silberbergweg 26). Laut Stadtseite hat '
                    'Hängelsberge montags bis freitags von 7 bis 17 Uhr '
                    'geöffnet, mittwochs bis 16 Uhr, samstags von 8 bis 13 '
                    'Uhr; die beiden anderen Höfe öffnen montags bis freitags '
                    'von 9.30 bis 12 und von 13 bis 17 Uhr, mittwochs bis '
                    '16 Uhr, samstags von 8 bis 13 Uhr (Angaben vom '
                    '01.10.2026, laut Seite gültig ab 01.01.2026; Zeiten '
                    'ändern sich, vor der Fahrt prüfen). Zu den Mengen sagt '
                    'die Wertstoffhofseite: Hängelsberge hat keine '
                    'Mengenbegrenzung, Cracauer Anger und Silberbergweg '
                    'nehmen nur Mengen bis zu einem Kubikmeter an, '
                    'Gartenabfälle bis 2 m³.',
                    'Angenommen werden nach der Stadt unter anderem '
                    'Sperrmüll, Bauabfälle, Holz, Grünabfälle, Metallschrott, '
                    'Elektronikschrott, Waschmaschinen, Herde und Kühlgeräte, '
                    'Pappen, Pkw-Altreifen und Textilien, dazu Schadstoffe. '
                    'Hausmüll nimmt der Hof ausdrücklich nicht an. Bei den '
                    'Schadstoffen widersprechen sich die Seiten der Stadt: '
                    'Die Seite zum Abgeben nennt zwei Standorte (Hängelsberge '
                    'und Cracauer Anger, nicht Silberbergweg), die Übersicht '
                    'der Höfe nennt Schadstoffsammelstellen an allen drei. '
                    'Fragen Sie vor der Fahrt nach. Sperrmüll ist auf den '
                    'Höfen bis 1 m³ gebührenfrei; mehr als 1 bis 2 m³ kosten '
                    'laut Stadt 10 Euro, größere Mengen werden gewogen und nur '
                    'auf dem Hof Hängelsberge angenommen. Die Grenze von 0,2 '
                    'Kubikmetern je Tag und Haushalt aus der '
                    'Kleinanlieferer-Regelung gilt für die übrigen '
                    'Abfallarten, nicht für Sperrmüll; Dachpappe, Pkw-Reifen '
                    'und Asbest sind laut Stadt immer gebührenpflichtig. '
                    'Grünabfälle sind bis 1 m³ je Anlieferung gebührenfrei; '
                    'Cracauer Anger und Silberbergweg nehmen davon höchstens '
                    '2 m³ an.',
                    'Wichtig ist der Herkunftsnachweis: Es werden nur '
                    'Abfälle angenommen, die in der Stadt Magdeburg '
                    'angefallen sind, bei Zweifeln auch gegen Vorlage der '
                    'Ausweispapiere. Für eine Wohnung außerhalb der Stadt '
                    'gilt das Angebot also nicht.',
                ],
            },
            {
                'id': 'ausschluss',
                'titel': 'Was nicht zum Sperrmüll gehört',
                'absaetze': [
                    'Die Stadt schließt vom Sperrmüll aus: Baumaterialien, '
                    'Schadstoffe, Sanitäreinrichtungen, Verpackungen, '
                    'Autoteile sowie Gegenstände über 2,20 m × 1,50 m × '
                    '0,75 m oder schwerer als 75 kg. Bauteile, Sanitär und '
                    'Verpackungen gehören bei einer Räumung deshalb nicht '
                    'in den Sperrmüllhaufen, sondern in eigene Fraktionen.',
                    'Schadstoffe haben ihren eigenen Weg: Nach der '
                    'Schadstoffsammlung der Stadt nehmen die Sammelstellen '
                    'Farben, Lacke, Verdünner, Säuren, Laugen, Altöl, '
                    'Batterien, Leuchtstoffröhren, Energiesparlampen, '
                    'Schädlingsbekämpfungs- und Pflanzenschutzmittel, '
                    'Haushaltschemikalien, Thermometer, Spraydosen sowie '
                    'Druckerpatronen und Tonerkartuschen an. Das Schadstoffmobil '
                    'nimmt bis zu 20 Liter beziehungsweise 20 kg an; '
                    'Hängelsberge kennt keine Mengenbegrenzung und erhebt '
                    'Gebühren nach der Abfallgebührensatzung. Gebracht wird '
                    'laut Stadt in Originalverpackung, in Kisten oder '
                    'Kartons, nicht in Säcken.',
                    'Mehr zur Einordnung der Stoffe finden Sie im Beitrag zu '
                    '<a href="/ratgeber/schadstoffe-im-haushalt-farben-lacke-chemikalien/">'
                    'Schadstoffen im Haushalt</a>.',
                ],
            },
            {
                'id': 'raeumung',
                'titel': 'Bei Haushaltsauflösung und Räumung',
                'absaetze': [
                    'Eine Wohnung enthält fast immer mehr, als die '
                    'kostenfreie Abholung fasst: Möbel, Elektrogeräte, '
                    'Textilien, Reste von Farbe oder Chemikalien, dazu Dinge, '
                    'die gar nicht zum Sperrmüll zählen. Die Stadt verlangt eine Sortierung '
                    'schon bei der Bereitstellung nach Holz, Altmetall, '
                    'Elektrogeräten, Kunststoff und Sonstigem, und der '
                    'Wertstoffhof nimmt Holz, Metallschrott, Elektronikschrott, Textilien '
                    'und Bauabfälle als eigene Arten an. Wer räumt, trennt '
                    'deshalb von Anfang an nach diesen Fraktionen, statt '
                    'alles in einen Haufen zu legen.',
                    'Praktisch heißt das: Schadstoffe vorab herausnehmen '
                    'und getrennt zur Schadstoffsammlung bringen, '
                    'Elektrogeräte, Holz, Altmetall und Kunststoff getrennt '
                    'legen, Verpackungen und Bauteile gesondert halten, und '
                    'vor jeder Abholung '
                    'die Größen- und Gewichtsgrenze prüfen. Bei einer '
                    'ganzen Wohnung lohnt der Blick auf die '
                    '<a href="/sperrmuell-entsorgung/">Sperrmüll-Entsorgung</a> '
                    'oder die <a href="/haushaltsaufloesung/">'
                    'Haushaltsauflösung</a>: Rümpelwerk Mitteldeutschland '
                    'räumt, trennt nach Fraktionen und stellt auf Wunsch '
                    'einen Entsorgungsnachweis aus. Das Festpreis-Angebot '
                    'gibt es direkt bei der Besichtigung. Für Magdeburg gibt es '
                    'die <a href="/entrumpelung/magdeburg/">Seite zur '
                    'Entrümpelung in Magdeburg</a>.',
                ],
            },
        ],

        'faq': [
            ('Wie viel Sperrmüll holt die Stadt Magdeburg kostenfrei ab?',
             'Laut Stadtseite zweimal im Jahr bis zu 2 m³ oder einmal bis zu '
             '4 m³ je Haushalt. Die Planungszeit beträgt bis zu vier Wochen; '
             'einen Wunschtermin gibt es gegen eine Servicegebühr.'),
            ('Wo melde ich Sperrmüll in Magdeburg an?',
             'Beim Städtischen Abfallwirtschaftsbetrieb: online, per '
             'Telefon, Fax, Postkarte (Sternstraße 13, 39104 Magdeburg) oder '
             'persönlich. Die aktuelle Rufnummer steht auf der Stadtseite zur '
             'Sperrmüllentsorgung.'),
            ('Kann ich Sperrmüll selbst zum Wertstoffhof bringen?',
             'Ja, Magdeburg hat drei Wertstoffhöfe, die Sperrmüll annehmen; '
             'Cracauer Anger und Silberbergweg nur bis zu einem Kubikmeter. '
             'Es werden nur Abfälle aus der Stadt Magdeburg angenommen; bei '
             'Zweifeln ist die Herkunft nachzuweisen. Hausmüll gehört nicht '
             'dazu.'),
            ('Was gehört nicht in den Sperrmüll?',
             'Nach der Stadt Baumaterialien, Schadstoffe, Sanitäreinrichtungen, '
             'Verpackungen, Autoteile und Gegenstände über 2,20 m × 1,50 m × '
             '0,75 m oder schwerer als 75 kg. Schadstoffe gehören zur '
             'Schadstoffsammlung.'),
        ],

        'leistungen': ['sperrmuell-entsorgung', 'haushaltsaufloesung'],
        'staedte': ['magdeburg'],
    },

    # ── SU07 (02.10.2026, Zweig fix/2026-10-02-halteverbot) ────────────────
    # Achtzehnte Wissensseite, weil die drei Matrixseiten vom 02.10. das
    # Verhaeltnis auf 25 zu 76 gedrueckt hatten. Jede Ortsangabe stammt von der
    # Behoerdenseite der jeweiligen Stadt (am 02.10.2026 abgerufen), die
    # Rechtslage aus der StVO. **Keine Aussage, dass der Betrieb die Zone
    # beantragt** - das ist beim Inhaber unbestaetigt; der Text verweist auf
    # die Besichtigung. Gebuehren in "Euro" ausgeschrieben wie in den
    # Sperrmuellartikeln, jede mit Quelle am Abschnittsende.
    'halteverbot-entruempelung-beantragen': {
        'stand_iso': '2026-10',
        'kategorie': 'Vorbereitung und Übergabe',
        'titel': 'Halteverbot für Entrümpelung beantragen',
        'h1': 'Halteverbot für Entrümpelung und Haushaltsauflösung beantragen',
        'h1_em': 'Wer es genehmigt, wie viel Vorlauf die Städte verlangen und wer die Schilder stellt',
        'teaser': (
            'Bei einer Räumung entscheidet oft der Platz vor der Haustür, wie '
            'gut der Tag läuft. Wie eine Halteverbotszone zustande kommt, '
            'welche Fristen Halle, Leipzig, Magdeburg und Dresden nennen und '
            'was die Genehmigung kostet.'
        ),
        'seo_title': 'Halteverbot bei Entrümpelung: 4 Städte im Vergleich | Rümpelwerk',
        'seo_description': (
            'Halteverbot für Entrümpelung oder '
            'Haushaltsauflösung: zuständige Behörde, Vorlauf, Schilder und '
            'Gebühr in Halle, Leipzig, Magdeburg und Dresden. Jetzt lesen.'
        ),
        'seo_keywords': ('halteverbot entrümpelung, halteverbot beantragen '
                         'halle, haltverbotszone umzug leipzig, halteverbot '
                         'magdeburg möbelumzug, halteverbot dresden umzug, '
                         'halteverbotszone haushaltsauflösung'),

        'answer_frage': 'Wie beantragt man ein Halteverbot für eine Entrümpelung?',
        'answer': (
            'Eine Halteverbotszone ist ein zeitlich begrenztes Haltverbot vor '
            'dem Haus, das die Straßenverkehrsbehörde der Stadt nach § 45 StVO '
            'anordnet. Beantragt wird es mit einem Verkehrszeichenplan, in '
            'Halle und Magdeburg mindestens 14 Tage vorher, in Dresden nach '
            'Möglichkeit ebenso, in Leipzig 14 behördliche Arbeitstage '
            'vorher. Die Schilder stellt '
            'nicht die Stadt auf, sondern der Antragsteller oder eine '
            'beauftragte Firma, je nach Stadt drei bis vier Tage vor dem '
            'Termin. Rechtsstand: {stand}.'
        ),

        'quellen': [
            {'schluessel': 'halteverbot-halle', 'abschnitt': 'wozu',
             'bezug': 'Halteverbotsbereich ist genehmigungspflichtig, wenn '
                      'der Möbelwagen nicht problemlos stehen kann; Absperren '
                      'mit Leinen, Kartons oder Stühlen ist abzuraten'},
            {'schluessel': 'halteverbot-leipzig', 'abschnitt': 'wozu',
             'bezug': 'Sperrung zum Be- oder Entladen nur mit Verkehrszeichen '
                      'nach der StVO, nicht mit Stühlen, Kisten oder Eimern'},
            {'schluessel': 'stvo-45', 'abschnitt': 'recht',
             'bezug': 'Die Straßenverkehrsbehörden beschränken die Benutzung '
                      'von Straßen und bestimmen, wo welche Verkehrszeichen '
                      'anzubringen sind (Absätze 1 und 3)'},
            {'schluessel': 'stvo-anlage-2', 'abschnitt': 'recht',
             'bezug': 'Zeichen 283 und 286, Geltung nur auf der beschilderten '
                      'Straßenseite, mobile Haltverbote heben Parkerlaubnisse '
                      'auf'},
            {'schluessel': 'halteverbot-halle', 'abschnitt': 'antrag',
             'bezug': 'Halle: Team Sperrungen, Antrag mit Lage- und '
                      'Verkehrszeichenplan 1:500, Fristen von sieben Werktagen '
                      'und 14 Tagen'},
            {'schluessel': 'halteverbot-magdeburg', 'abschnitt': 'antrag',
             'bezug': 'Magdeburg: Straßenverkehrsbehörde, Unterlagen, Antrag '
                      'mindestens 14 Tage vorher'},
            {'schluessel': 'halteverbot-dresden', 'abschnitt': 'antrag',
             'bezug': 'Dresden: Straßen- und Tiefbauamt, Antrag auf '
                      'Ausnahmegenehmigung nach Möglichkeit 14 Tage vorher'},
            {'schluessel': 'halteverbot-leipzig-formular', 'abschnitt': 'antrag',
             'bezug': 'Leipzig: Mobilitäts- und Tiefbauamt, Antragsformular, '
                      'Inhalt des Verkehrszeichenplans, Eingang spätestens 14 '
                      'behördliche Arbeitstage vorher'},
            {'schluessel': 'halteverbot-halle', 'abschnitt': 'schilder',
             'bezug': 'Halle: Schilder drei volle Tage vorher, erst nach der '
                      'Genehmigung, Aufstellungsprotokoll, eigene Anordnung '
                      'für Ein- und Auszugsort'},
            {'schluessel': 'halteverbot-magdeburg', 'abschnitt': 'schilder',
             'bezug': 'Magdeburg: Absperrfirma muss beauftragt werden, '
                      'Schilder mindestens zweiundsiebzig Stunden vor dem '
                      'Umzugstag'},
            {'schluessel': 'halteverbot-dresden', 'abschnitt': 'schilder',
             'bezug': 'Dresden: Haltverbote mindestens vier Tage vor dem '
                      'Termin, Schilder von einer Verkehrssicherungsfirma '
                      'leihbar'},
            {'schluessel': 'halteverbot-leipzig', 'abschnitt': 'schilder',
             'bezug': 'Leipzig: Behörde stellt keine Schilder auf, Aufstellen '
                      'spätestens vier Tage vorher, parkende Fahrzeuge erfassen, '
                      'kein Rechtsanspruch auf Freimachung'},
            {'schluessel': 'halteverbot-halle', 'abschnitt': 'kosten',
             'bezug': 'Halle: Gebühren je Fall, ohne Kosten der '
                      'Verkehrssicherung'},
            {'schluessel': 'halteverbot-magdeburg', 'abschnitt': 'kosten',
             'bezug': 'Magdeburg: Gebühr'},
            {'schluessel': 'halteverbot-leipzig', 'abschnitt': 'kosten',
             'bezug': 'Leipzig: Verwaltungsgebühr für die verkehrsrechtliche '
                      'Anordnung'},
            {'schluessel': 'halteverbot-dresden', 'abschnitt': 'kosten',
             'bezug': 'Dresden: Kostenbescheid nach GebOSt, '
                      'Sondernutzungsgebühr für Möbellift oder Schrägaufzug'},
            {'schluessel': 'halteverbot-halle', 'abschnitt': 'raeumung',
             'bezug': 'Halle: Zone für Umzüge sowie für das Be- und Entladen; '
                      'für einen Container auf der Straße gegebenenfalls ein '
                      'Sondernutzungsantrag'},
        ],

        'abschnitte': [
            {
                'id': 'wozu',
                'titel': 'Wozu eine Halteverbotszone bei einer Räumung dient',
                'absaetze': [
                    'Bei einer Entrümpelung oder Haushaltsauflösung wird alles, '
                    'was aus der Wohnung kommt, zum Fahrzeug getragen. Steht '
                    'der Wagen zwei Querstraßen weiter, verlängert jeder Gang '
                    'die Arbeit; steht er in zweiter Reihe, behindert er den '
                    'Verkehr. Eine Halteverbotszone hält für einen festgelegten '
                    'Zeitraum ein Stück Straße vor dem Haus frei.',
                    'Die Stadt Halle (Saale) beschreibt den Fall so: Ist das '
                    'problemlose Abstellen eines Möbelwagens nicht möglich '
                    'oder soll ein Möbellift oder Schrägaufzug aufgestellt '
                    'werden, muss ein Halteverbotsbereich eingerichtet werden, '
                    'und der ist genehmigungspflichtig. Einen Platz mit Leinen, '
                    'Bändern, Kartons oder Stühlen freizuhalten, rät die Stadt '
                    'ab: Andere dürfen solche Hindernisse beiseiteräumen, und '
                    'die Polizei erhebt dann häufig ein Verwarn- oder '
                    'Bußgeld. Leipzig sagt dasselbe kürzer: Die Sperrung darf '
                    'nur mit Verkehrszeichen nach der StVO eingerichtet werden, '
                    'nicht mit Stühlen, Kisten oder Eimern.',
                    'Zum Wort: Die Straßenverkehrs-Ordnung schreibt '
                    '„Haltverbot“, im Alltag heißt es meist „Halteverbot“. '
                    'Gemeint ist dasselbe.',
                ],
            },
            {
                'id': 'recht',
                'titel': 'Die Rechtsgrundlage: § 45 StVO und die Zeichen 283 und 286',
                'absaetze': [
                    'Nach § 45 Absatz 1 StVO können die '
                    'Straßenverkehrsbehörden die Benutzung bestimmter Straßen '
                    'oder Straßenstrecken aus Gründen der Sicherheit oder '
                    'Ordnung des Verkehrs beschränken. Absatz 3 legt fest, '
                    'dass sie bestimmen, wo und welche Verkehrszeichen '
                    'anzubringen sind. Eine Halteverbotszone ist deshalb keine '
                    'Privatsache, sondern eine Anordnung der Behörde.',
                    'Die Zeichen selbst stehen in Anlage 2 der StVO. '
                    'Zeichen 283 ist das absolute Haltverbot: Das Halten auf '
                    'der Fahrbahn ist verboten. Zeichen 286 ist das '
                    'eingeschränkte Haltverbot: Länger als drei Minuten darf '
                    'dort nur halten, wer ein- oder aussteigt oder be- oder '
                    'entlädt. Beide gelten nur '
                    'auf der Straßenseite, auf der sie stehen, und nach '
                    'Anlage 2 heben mobile, vorübergehend angeordnete '
                    'Haltverbote Verkehrszeichen auf, die das Parken '
                    'erlauben. Welches Zeichen in welcher Länge vor einem Haus '
                    'steht, legt die Anordnung der Stadt fest.',
                ],
            },
            {
                'id': 'antrag',
                'titel': 'Wer zuständig ist und wie viel Vorlauf die Städte verlangen',
                'absaetze': [
                    'Zuständig ist die Straßenverkehrsbehörde der Stadt, in der '
                    'das Haus steht; der Name der Stelle ist je Stadt '
                    'verschieden. Alle vier verlangen einen schriftlichen '
                    'Antrag mit Ort, Zeitraum und einem Verkehrszeichenplan, '
                    'der zeigt, wo welche Schilder stehen sollen.',
                    'In Halle (Saale) ist es das Team Sperrungen, Am Stadion 5. '
                    'Der Antrag auf verkehrsrechtliche Anordnung und '
                    'Sondernutzung geht per E-Mail oder persönlich ein, auch '
                    'über eine beauftragte Fachfirma mit Vollmacht. Gebraucht '
                    'wird ein Lage- und Verkehrszeichenplan im Maßstab 1:500, '
                    'den Verkehrssicherungsfirmen erstellen; einige übernehmen '
                    'laut Stadt die gesamte Beantragung. Beim Vorlauf nennt das '
                    'Serviceportal zwei Werte: Die vollständigen Unterlagen '
                    'müssen sieben Werktage vor dem Umzug vorliegen, an anderer '
                    'Stelle heißt es, der Antrag müsse mindestens 14 Tage '
                    'vorher eingereicht werden. Wer sich nach der längeren '
                    'Frist richtet, ist auf der sicheren Seite.',
                    'In Magdeburg ist es die Straßenverkehrsbehörde, An der '
                    'Steinkuhle 6. Den Verkehrszeichenplan darf man selbst '
                    'zeichnen oder mit einem Kartendienst erstellen; dazu '
                    'kommen Ort, Zeitraum, Datum sowie alte und neue '
                    'Wohnanschrift. Die Unterlagen können per Post gehen, '
                    'beantragt wird mindestens 14 Tage vorher.',
                    'In Dresden ist es das Straßen- und Tiefbauamt, Sachgebiet '
                    'Verkehrsregelung Arbeits- und Baustellen. Dort heißt das '
                    'Formular „Antrag auf Ausnahmegenehmigung für Umzug und '
                    'Anlieferung“; stellen können ihn Privatpersonen wie '
                    'Unternehmen, nach Möglichkeit mindestens 14 Tage vor dem '
                    'Termin.',
                    'In Leipzig ist es das Mobilitäts- und Tiefbauamt, '
                    'Sachgebiet Temporäre Verkehrsregelung, im Technischen '
                    'Rathaus an der Prager Straße. Der unterschriebene Antrag '
                    'geht per Post, E-Mail oder Fax ein, der '
                    'Verkehrszeichenplan fünffach. Er muss den '
                    'Straßenabschnitt mit den Breiten von Fahrbahn, Gehweg, '
                    'Radweg und Parktaschen zeigen, die vorhandenen '
                    'Verkehrszeichen, die Länge und Breite der Fläche und die '
                    'nötigen Schilder. Nach dem Formular muss der Antrag '
                    'spätestens 14 behördliche Arbeitstage vor dem Termin '
                    'eingegangen sein; das ist spürbar länger als zwei '
                    'Kalenderwochen.',
                ],
                'vergleich': {
                    'anker': 'halteverbot-tabelle',
                    'titel': 'Halteverbot für Umzug und Räumung in vier Städten',
                    'kopf': ['Stadt', 'Zuständig', 'Antrag spätestens',
                             'Schilder stehen', 'Gebühr der Stadt'],
                    'zeilen': [
                        ['Halle (Saale)', 'Team Sperrungen',
                         '14 Tage vorher (an anderer Stelle sieben Werktage)',
                         'drei volle Tage vorher, Aufstelltag zählt nicht',
                         '21,00 Euro, mit Möbellift mehr'],
                        ['Leipzig', 'Mobilitäts- und Tiefbauamt',
                         '14 behördliche Arbeitstage vorher',
                         'mindestens vier Tage vorher',
                         'ab 32,00 Euro'],
                        ['Magdeburg', 'Straßenverkehrsbehörde',
                         '14 Tage vorher',
                         'mindestens zweiundsiebzig Stunden vor dem Umzugstag',
                         '16 Euro'],
                        ['Dresden', 'Straßen- und Tiefbauamt',
                         'nach Möglichkeit 14 Tage vorher',
                         'mindestens vier Tage vorher',
                         'nach Kostenbescheid (GebOSt)'],
                    ],
                    'fazit_frage': 'Wie früh muss ein Halteverbot beantragt werden?',
                    'fazit': (
                        'In allen vier Städten rund zwei Wochen vor dem '
                        'Termin, in Leipzig 14 behördliche Arbeitstage. Die '
                        'Schilder müssen drei bis vier Tage vorher stehen, '
                        'aufgestellt vom Antragsteller oder einer '
                        'beauftragten Firma.'
                    ),
                },
            },
            {
                'id': 'schilder',
                'titel': 'Schilder aufstellen, Fahrzeuge erfassen, Fristen einhalten',
                'absaetze': [
                    'Die Genehmigung ist noch kein Schild. Leipzig schreibt '
                    'ausdrücklich, dass die Behörde selbst keine Verkehrszeichen '
                    'aufstellt; das tun der Antragsteller oder eine beauftragte '
                    'Firma. In Magdeburg muss eine Absperrfirma damit '
                    'beauftragt werden. In Dresden stellt der Antragsteller oder '
                    'ein beauftragter Verkehrssicherer die Schilder auf, die '
                    'sich bei einer Verkehrssicherungsfirma leihen lassen.',
                    'Die Vorlaufzeit für die Schilder gibt anderen die '
                    'Gelegenheit, ihr Fahrzeug wegzufahren. Halle verlangt '
                    'drei volle Tage vor dem Umzug, der Tag des Aufstellens '
                    'zählt nicht mit, und aufgestellt werden darf erst nach '
                    'Erhalt der Genehmigung. Magdeburg nennt mindestens '
                    'zweiundsiebzig Stunden vor dem Umzugstag, Leipzig und '
                    'Dresden mindestens vier Tage.',
                    'Wichtig ist der Nachweis. In Halle wird die Aufstellung in '
                    'einem Aufstellungsprotokoll mit Zeitpunkt und genauem Ort '
                    'festgehalten; in Leipzig müssen beim Aufstellen die dort '
                    'parkenden Fahrzeuge erfasst werden. Halle weist außerdem '
                    'darauf hin, dass Einzugs- und Auszugsort jeweils eine '
                    'eigene Anordnung brauchen und die Schilder nach dem Ende '
                    'unwirksam zu machen sind.',
                    'Steht am Tag selbst trotzdem ein fremdes Auto in der Zone, '
                    'lässt es sich nach Angaben der Stadt Halle entfernen. '
                    'Leipzig verweist dafür auf die Einsatzstelle des '
                    'Ordnungsamts, betont aber, dass kein Rechtsanspruch auf '
                    'Freimachung der Zone besteht.',
                ],
            },
            {
                'id': 'kosten',
                'titel': 'Was die Genehmigung kostet und was nicht darin steckt',
                'absaetze': [
                    'Die Städte nennen nur die eigene Verwaltungsgebühr. In '
                    'Halle kostet das Stellen eines Haltverbots 21,00 Euro, mit '
                    'Möbellift auf dem Gehweg 34,00 Euro, mit Möbellift auf der '
                    'Fahrbahn oder als Vollsperrung einer engen Straße 41,00 '
                    'Euro. Magdeburg nennt eine Gebühr von 16 Euro, Leipzig '
                    'eine Verwaltungsgebühr ab 32,00 Euro. Dresden nennt keinen '
                    'Betrag, sondern stellt einen Kostenbescheid nach der '
                    'Gebührenordnung für Maßnahmen im Straßenverkehr aus; für '
                    'einen Möbellift oder Schrägaufzug kommt dort eine '
                    'Sondernutzungsgebühr mit eigenem Bescheid hinzu. Alle '
                    'Beträge haben den Stand vom 02.10.2026 und sollten vor dem '
                    'Antrag auf der Seite der Stadt geprüft werden.',
                    'Nicht enthalten ist das Aufstellen der Schilder. Halle '
                    'schreibt, die Gebühr beinhalte nicht die Kosten der '
                    'Verkehrssicherung, und verweist dafür auf die Firmen; '
                    'Leipzig sagt, zu Preisen und Ablauf des Aufstellens '
                    'könnten nur die Dienstleister Auskunft geben.',
                ],
            },
            {
                'id': 'raeumung',
                'titel': 'Was das für eine Entrümpelung oder Haushaltsauflösung heißt',
                'absaetze': [
                    'Die Städte führen das Verfahren unter dem Stichwort Umzug. '
                    'Halle nennt ausdrücklich auch das Be- und Entladen, Leipzig '
                    'die Sperrung einer Fläche zum Be- oder Entladen und '
                    'Dresden die Anlieferung. Ob eine Räumung unter dasselbe '
                    'Formular fällt, beantwortet im Zweifel die zuständige '
                    'Stelle. Soll statt eines Fahrzeugs ein Container auf der '
                    'Straße stehen, braucht es laut Halle gegebenenfalls '
                    'zusätzlich eine Sondernutzungserlaubnis.',
                    'Ob für Ihren Termin ein Halteverbot nötig ist, hängt von '
                    'der Straße ab: von Hof oder Einfahrt, von der Parklage am '
                    'Vormittag und davon, ob ein Möbellift gebraucht wird. Das '
                    'und wer sich um Antrag und Schilder kümmert, sprechen wir '
                    'bei der Besichtigung ab; danach steht der Festpreis für '
                    'die <a href="/haushaltsaufloesung/">Haushaltsauflösung</a> '
                    'oder <a href="/wohnungsaufloesung/">Wohnungsauflösung</a> '
                    'fest. Für einen sicheren Termin lohnt es sich, das Thema '
                    'gleich beim ersten Gespräch anzusprechen, weil die Fristen '
                    'der Städte sonst den Räumtag bestimmen.',
                ],
            },
        ],

        'faq': [
            ('Wo beantrage ich ein Halteverbot in Halle (Saale)?',
             'Beim Team Sperrungen der Stadt Halle (Saale), Am Stadion 5. Der '
             'Antrag auf verkehrsrechtliche Anordnung und Sondernutzung geht '
             'per E-Mail oder persönlich ein, mit einem Lage- und '
             'Verkehrszeichenplan im Maßstab 1:500.'),
            ('Wie lange vorher müssen die Halteverbotsschilder stehen?',
             'In Halle drei volle Tage vor dem Umzug, ohne den Tag des '
             'Aufstellens; in Magdeburg mindestens zweiundsiebzig Stunden vor '
             'dem Umzugstag; in Leipzig und Dresden mindestens vier Tage vor '
             'dem Termin.'),
            ('Stellt die Stadt die Schilder auf?',
             'Nein. Die Genehmigung erlaubt das Aufstellen, die Schilder '
             'stellt der Antragsteller oder eine beauftragte Firma; in '
             'Magdeburg muss es eine Absperrfirma sein. Die Kosten dafür sind '
             'in der Gebühr der Stadt nicht enthalten.'),
            ('Darf ich den Platz mit Stühlen oder Absperrband freihalten?',
             'Nein. Halle rät ausdrücklich davon ab, andere dürfen solche '
             'Hindernisse wegräumen, und häufig folgt ein Verwarn- oder '
             'Bußgeld. Leipzig lässt eine Sperrung nur mit Verkehrszeichen '
             'nach der StVO zu.'),
            ('Was passiert, wenn trotzdem ein Auto in der Zone steht?',
             'Nach Angaben der Stadt Halle lassen sich fremde Fahrzeuge '
             'entfernen. Leipzig verweist auf das Ordnungsamt, ein '
             'Rechtsanspruch auf Freimachung besteht dort aber nicht. Das '
             'Aufstellungsprotokoll bzw. die Liste der beim Aufstellen '
             'parkenden Fahrzeuge ist dann der Nachweis.'),
        ],

        'leistungen': ['haushaltsaufloesung', 'wohnungsaufloesung'],
        'staedte': ['halle', 'leipzig', 'magdeburg', 'dresden'],
    },
}
