# Minecraft Whitelist Form

Diese simple Webanwendung dient dazu, Spieler auf die Whitelist eines Minecraft Servers hinzuzufügen, nachdem diese
ihre Zugehörigkeit zur Nordakademie mittels E-Mail-Verifikation bewiesen haben.

## Setup

Es ist eine Flask App. Sie lässt sich durch gängige WSGI Tools wie `waitress` deployen.

```bash
pip install waitress
waitress-serve --call 'mc_whitelist_form:create_app'
```

## Config

Die Konfiguration ist über mehrere Ebenen möglich, die sich jeweils überschreiben.

1. Standardwerte im Code
2. Werte aus der `./instance/config.py` (muss manuell angelegt werden)
3. Umgebungsvariablen (Konfigurationsnamen müssen mit `MCWLF_` prefixed werden. Aus `BASE_URL` wird als z.B. `MCWLF_BASE_URL`)

Folgende Konfigurationen sind möglich:

- `DATABASE` (Pfad zur sqlite Datei)
- `ALLOWED_MAIL_SUFFIXES`
- `BASE_URL` (Von außen erreichbare URL der Webanwendung inkl. `http(s)://`)
- `EXAROTON_API_TOKEN` (User Access Token von Exaroton)
- `EXAROTON_SERVER_ID` (Unique Server ID; steht unter dem Servernamen; ohne #)
- `MAIL_SERVER` (SMTP Hostname)
- `MAIL_PORT` (SMTP Port)
- `MAIL_USE_TLS`
- `MAIL_USE_SSL`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_DEFAULT_SENDER` (Absenderadresse für E-Mails) 

