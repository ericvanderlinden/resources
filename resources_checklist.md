---
header-includes: |-
    <style>
    body {font-family:"Merriweather";font-size:12pt;line-height: 23px;width:21cm;}
    p, ul {width:16cm;}
    h1 {margin-top: 14px;margin-bottom: 20px;line-height: 40px;font-size:21pt;}
    h2 {margin-top: 18px;margin-bottom: 4px;line-height: 25px;font-size:18pt;}
    h3 {margin-top: 14px;margin-bottom: 4px;line-height: 23px;font-size:16pt;text-decoration: underline;}
    h4, h5, h6 {margin-top: 8px;margin-bottom: 0px;line-height: 23px;font-size:14pt;}
    ul li {line-height: 23px;}
    @media print {h2 {page-break-before: always;}}
    </style>
---

# Aanpak resources
De meeste resources zijn boeken of collecties brieven. Sommige resources zijn al datasets en hebben een iets andere behandeling nodig.  
Biografische woordenboeken zijn boeken met een bijzondere indeling, de biografie is de belangrijkste eenheid.

De resources bevatten veel teksten en scans die niet los van de applicatie page browser bestaan, die in Databases en XML zitten en door zelf gebouwde interfaces worden ontsloten.  
Het doel van het project is alle content van de resources om te zetten naar downloadbare datasets. In eerste instantie in CSV.  
(CSV (TSV) is het meest eenvoudige en meest overzichtelijke formaat om data te verzamelen en te verwerken.)

Voor de meeste resources komen de volgende stappen aan de orde:  
Verzamel (content, media, beschrijvingen)  
Verrijk (beschikbare meta data toevoegen.)  
Verbeter (OCR / HTR tekst als string)  
Ontsluit (maak een uri/url van alle onderdelen)  
Converteer (Biedt datasets aan in meerdere formaten)  

## Boeken (1)
Onder boeken verstaan we drukwerken die zijn gedigitaliseerd en waarvan OCR is gemaakt. Deze bevatten in grote lijnen:

- Biografieën
- Brieven collecties
- Dagboeken
- Bronnen publicaties
- Congresbundel
- Inventarisaties van bronnenmateriaal

### Verzamel (Basis 1)(M)   
#### Per pagina
In eerste instantie van alle resources

- Scan (link naar een scan van de pagina of brief)
- Tekst (Een link naar het tekst bestand met de tekst per pagina of brief)
- Tekst (de tekst als string)
- Indeling (de wijze waarop het document is gestructureerd.) (Meestal uit bijgevoegde documenten als ToC)  
Bijvoorbeeld:
    - Deel (Boek) -> Inleiding -> Hoofdstuk -> pagina -> Column -> paragraaf
    - Deel (Boek) -> Inleiding -> Brief - Commentaar

### Verzamel (Basis 2)(M)   
#### Per hoofdstuk (Chapter)
Een chapter is de kleinste mogelijke onderdeel van een resource. In een collectie brieven is dat een brief, in een biografisch woordenboek een biografie, in een dagboek een dagboek aantekening.  
Vanuit de CSV die is opgeleverd in Verzamel (Basis 1), waar dat van toepassing is.

- 1 of meerdere Scans (link naar de scan of scans van het chapter afhankelijk of het chapter op 1 of op meerdere pagina's staat.) 
- Tekst (Een link naar het tekst bestand met de tekst per chapter. Wordt vanuit de dataset gegenereerd.)
- Tekst (de tekst als string)
- Indeling (de wijze waarop het document is gestructureerd.) aangepast aan boek per hoofdstuk, dus bijvoorbeeld meerdere paginanummers of kolomnummers als dat van toepassing is. 

### Verrijk (Basis 1)(M)
#### Per boek, collectie
- Beschikbare gegevens uit bijgevoegde documenten en bibliografische gegevens. Daarbij ook de inleidingen en dergelijke die door onderzoekers tijdens het digitaliseringsproject zijn toegevoegd.

#### Per pagina
- Beschikbare gegevens uit bijgevoegde documenten die betrekking hebben op de inhoud zoals verzender en ontvanger van een brief, de persoon in een mini biografie, etc.  
- Gegevens die eenvoudig uit een tekst gehaald kunnen worden zoals de schrijver van een geheel of deel van het boek, de voetnoten, titels, datums relevant voor het boek of de pagina, voetnoten.

### Verrijk (Basis 2)(M)
#### per chapter
- De gegevens die per pagina zijn geordend moeten per chapter worden geordend.

### Verbeter (Tekst behandeling) (Basis)(M)
De tekst is soms beschikbaar als transcriptie van zeer goede kwaliteit gecodeerd in TEI (NNBW, VDAA), Er is OCR van goede kwaliteit en OCR van matige kwaliteit.  
Hoewel het einddoel is om de teksten in TEI op te coderen zal het in de eerste fase grotendeels HTML blijven.

#### Algemeen
- OCR bevat rudimentaire html, meestal alleen linebreaks (\<br />) die moet worden ingebed in een beperkte TEI of HTML met een header. De header zou beperkte metadata kunnen bevatten zoals paginanummer.
- De tekst moet ingebed worden een HTML pre tag (\<pre>\</pre>) omdat dan de structuur die vaak wel in de HTML zit met name door veelvuldig gebruik van spaties in een browser zichtbaar wordt.
- Ontwikkel een aantal zoek/vervang strategieën met gebruik van regex om de OCR te verbeteren. Denk bijvoorbeeld aan het verwijderen van spaties in woorden als k i n d e r e n -> kinderen. Mogelijk opvallende OCR fouten als Û -> ò.
- Als tekst uit een omgeving komt waarin de karakterset Latin1 (ISO/IEC 8859-1) (8-bit single-byte coded) wordt gebruikt zoals in oudere databases en die tekst was aangeboden als Unicode of UTF8 dan worden karakters die niet in de latin1 set zitten met twee karakters geschreven. Deze moeten vervangen worden door de UTF8 karakters. In het algemeen moet tekst netjes UTF8 worden. 

### Ontsluit (niveau 1)
Ontsluiten in een beperkte website, resulteert in een link per resource en een link per resource onderdeel als een pagina, paragraaf, brief of biografie. 
- Maak een index pagina per resource 
    - met alle links naar alle onderdelen van de resource die ontsloten worden. 
    - met links naar (indien aanwezig) de inleiding van de schrijver en de onderzoekers.
- directory met:
    - 1 pagina waarop de scans van het onderdeel worden ontsloten
    - 1 pagina waarop de tekst van het onderdeel wordt ontsloten
    - 1 pagina waarop de bibliografische en andere belangrijke gegevens worden ontsloten in YAML.



### Verrijk (uitgebreid)
Valt buiten het project maar denk bijvoorbeeld aan:
- NER


### Verbeter (Tekst behandeling) (uitgebreid)
Valt buiten het project maar denk bijvoorbeeld aan:
- Tekst volledig in correcte TEI. verwijder HTML.

## Datasets (2)
#### Digital born
Sommige resources zijn databases of xml die worden ontsloten met zelf gemaakte applicaties. Deze resources zou je "digital born" kunnen noemen omdat er nooit een papieren versie aan vooraf is gegaan of dat ze een papieren versie letterlijk digitaliseren.
#### Archief materiaal
Andere databases ontsluiten archief materiaal als de brieven van Willem van oranje. De database bevat meta data en links naar gedigitaliseerde fysieke objecten.

### Verzamel
- Om de data vrij te maken van applicaties wordt de data omgezet naar CSV Relationeel (met behoud van de relationele aspecten als Foreign Key).
- Het kan voldoende zijn om bij de XML een beschrijving van de relatie tussen de verschillende onderdelen te maken.

### Ontsluit (niveau 1)
Zie boven.
### Converteer
Zie beneden

## Extra (3)
### Converteer
#### Wat en waarom 
Conversie heeft betrekking op de data die is opgeleverd in CSV of TSV.  
Conversie heeft waarschijnlijk met name betrekking op de resources die geen boeken zijn. Bij boeken is omzetten naar XML (TEI) wel relevant. De conversie van alle resource is wel relevant voor ontsluiting. Zie hieronder Ontsluit (uitgebreid).
- Onderzoek of een generieke conversie van CSV naar json mogelijk is.
    - Moet er aan de CSV een json-ld file toegevoegd worden met de definities van kolommen en de onderlinge relaties.
    - zijn er bestaande oplossingen
    - moet er zelf iets gemaakt worden
- Hetzelfde voor json-ld, turtle, xml.
- De datasets die al "database" zijn omzetten in json of json-ld.

### Ontsluit (niveau 2)
Het tweede niveau van ontsluiting is het doorzoekbaar maken van de resources. 
Op enig moment zullen resources gestructureerd zijn opgeslagen met alle relevante links (scan, tekst), de tekst als string en andere beschikbare metadata. Verwerkte resources kunnen geschikt gemaakt worden voor indexering door Elastic.
- Maak een opzet voor JSON die geschikt is voor het indexeren van de resources. Liefst uniform.
- Indexeer resources.
- Maakt zoek interface.

