import logging
import random
import string
from datetime import datetime, timezone

import requests
from flask import Blueprint, render_template, request, current_app
from flask_mail import Message


from mc_whitelist_form.db import get_db
from mc_whitelist_form import mailsender

bp = Blueprint('main', __name__)


@bp.get("/admin")
def list_requests():
    if request.args.get("secret") != current_app.config["ADMIN_SECRET"]:
        return render_template("error.html", error="Authentifizierung fehlgeschlagen.")

    def convert_date(epoch: int):
        if epoch is not None:
            return datetime.fromtimestamp(epoch).strftime('%d.%m.%Y %H:%M:%S UTC')
        return None

    db = get_db()
    dbc = db.cursor()

    reqs = []
    dbc.execute('SELECT * FROM requests')
    for r in dbc.fetchall():
        r = dict(r)
        r["request_date"] = convert_date(r["request_date"])
        r["accept_date"] = convert_date(r["accept_date"])
        reqs.append(r)

    return render_template("list.html", reqs=reqs)


@bp.get("/")
def serve_form():
    return render_template("form.html")

@bp.post("/")
def parse_form():
    mail = request.form.get('mail')
    user = request.form.get('user')
    if not (mail and user):
        return render_template("form.html", error="Bitte fülle das Formular vollständig aus.")
    if not any([mail.endswith(s) for s in current_app.config['ALLOWED_MAIL_SUFFIXES']]):
        return render_template("form.html", error="Bitte nutze deine Nordakademie-Mailadresse.")
    resp = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{user}")
    if resp.status_code != 200:
        return render_template("form.html", error="Der angegebene Spielername existiert nicht.")

    user = resp.json().get("name")  # get the correct username (incl. capitalization)

    db = get_db()
    dbc = db.cursor()

    dbc.execute('SELECT 1 FROM requests WHERE username = ? AND accept_date IS NOT NULL', (user, ))
    if dbc.fetchone():
        return render_template("form.html", error=f"{user} wurde bereits zur Whitelist hinzugefügt.")

    now = int(datetime.now(timezone.utc).timestamp())
    secret = "".join(random.choices(string.ascii_letters+string.digits, k=32))
    dbc.execute('INSERT INTO requests (username, mail, secret, request_date) VALUES (?, ?, ?, ?)', (user, mail, secret, now))
    db.commit()

    _send_confirmation_mail(mail, user, secret)
    return render_template("form.html", success="Wir haben deine Anfrage erhalten. Bitte überprüfe deine E-Mails.")

@bp.route("/verify", methods=["GET", "POST"])
def verify():
    user = request.form.get("user") or request.args.get("user")
    secret = request.form.get("secret") or request.args.get("secret")
    confirm = request.form.get("confirm")
    if not (user and secret):
        return render_template("error.html", error="Fehlende URL-Parameter")

    db = get_db()
    dbc = db.cursor()
    dbc.execute("SELECT 1 FROM requests WHERE username = ? AND secret = ? and accept_date IS NULL", (user, secret))
    if not dbc.fetchone():
        return render_template("error.html", error="Die übermittelten Parameter sind ungültig oder der Spieler wurde bereits zur Whitelist hinzugefügt.")

    if confirm != "yes":
        return render_template("confirm.html", user=user, secret=secret)

    added = _add_to_whitelist(user)
    if not added:
        return render_template("error.html", error="Ein Fehler beim Hinzufügen zur Whitelist ist aufgetreten. Sollte der Fehler mehrfach auftreten, wende dich bitte an die Fachschaft Informatik.")

    now = int(datetime.now(timezone.utc).timestamp())
    dbc.execute("UPDATE requests SET accept_date = ? WHERE username = ? AND secret = ? AND accept_date IS NULL", (now, user, secret))
    db.commit()

    return render_template("success.html", success=f'Spieler "{user}" wurde erfolgreich zur Whitelist hinzugefügt. Viel Spaß beim Spielen.')


def _send_confirmation_mail(mail: str, user: str, secret: str):
    url = f'{current_app.config["BASE_URL"]}/verify?user={user}&secret={secret}'

    msg = Message(
        subject="Deine Registrierung für den NAK-INF Minecraft Server",
        recipients=[mail],
        body=f'''Guten Tag, 

Uns ist eine Anfrage eingegangen, den Minecraft-Spieler "{user}" zur Whitelist des Fachschaftsservers hinzuzufügen.
Sollte diese Anfrage nicht von dir persönlich gestellt worden sein, lösche bitte diese E-Mail und tue nichts weiter.
Um die Anfrage zu bestätigen, klicke auf folgenden Link oder kopiere ihn in die URL-Leiste deines Webbrowsers: {url}

Beste Grüße
die Fachschaft Informatik der Nordakademie
''',
        html=f'''Guten Tag, <br>
<br>
Uns ist eine Anfrage eingegangen, den Minecraft-Spieler "{user}" zur Whitelist des Fachschaftsservers hinzuzufügen.<br>
Sollte diese Anfrage nicht von dir persönlich gestellt worden sein, lösche bitte diese E-Mail und tue nichts weiter.<br>
Um die Anfrage zu bestätigen, klicke auf folgenden Link: <a href="{url}">{url}</a><br>
<br>
Beste Grüße<br>
die Fachschaft Informatik der Nordakademie
'''
    )
    mailsender.send(msg)


def _add_to_whitelist(user: str) -> bool:
    resp = requests.put(
        url=f'https://api.exaroton.com/v1/servers/{current_app.config["EXAROTON_SERVER_ID"]}/playerlists/whitelist/',
        data='{"entries": ["%s"]}' % user,
        headers={"Authorization": f'Bearer {current_app.config["EXAROTON_API_TOKEN"]}', "Content-Type": "application/json"}
    )

    if resp.json().get("success", False):
        return True
    else:
        logging.error("Got non-positive response from Exaroton: %s" % resp.content)
        return False