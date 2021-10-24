import parsing
import sys
import os
import threading
import requests
import q3rcon.q3rcon
import random
import math

from datetime import datetime

from config import *

import flask

from flask import (
    Flask, 
    make_response, 
    request, 
    redirect, 
    Response, 
    send_file
)

app = Flask(__name__, static_folder = "static/", static_url_path = "/static/")


# An excellent source for map images. 
map_image_url = "https://www.urbanterror.info/files/static/images/levels/wide/{map_name}.jpg"


os.chdir(os.path.dirname(os.path.realpath(__file__)))

# A list of currently cached images.
# The 'None' key refers to a map that cannot be found.
# We have to do this to avoid CORS. 
map_imgs = {
    None: open("static/map-404.png", "rb").read()
}



def archive_round(p, players):
    # Do not archive an empty round.
    if (players == []):
        return

    # Write to log file.
    log_file = datetime.now().strftime(log_format) + ".html"
    with open(f"static/archives/{log_file}", "w+") as fp:
        fp.write(
            requests.get(f"http://localhost:{host_port}").text
        )


p = parsing.UrTParser()

if (logging):
    p.on_newround = archive_round


# When a line from stdin is received, parse!
# You are supposed to feed the stdout/stderr of the ioUrTQuake3dedx86_64 program into here, where
# it parses on-the-fly.

def update_stats():
    for line in sys.stdin:
        p.parse_line(line)


# "Threading is bad!"
# But it works
threading._start_new_thread(update_stats, ())


html = """
<html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
    </head>

    <body>
        <title>Urban Terror Server Statistics</title>
        <h1>Urban Terror Server Statistics</h1>

        <div>
            <h2>Rcon Password: </h2>
            <br>
            <form action="/login/" method="POST">
                <input type="password" name="password">
                <br>
                <br>
                <input type="submit" value="Login" class="submit">
            </form>
        </div>

        <br>

        <div id="stats">
            <h2>{servername}</h2>
            <h3>{password_protected}</h3>
            <h4>{version}</h4>

            <h3>Players online: {count}</h3>

            <center>
                <h3>Map: {mapname}</h3>
                <img src="/map/{mapname}" width="33%">
                <br>
                <br>

                <table width=100%>
                    <tr>
                        <th> </th>
                        <th>Gear</th>
                        <th>Player Name</th>
                        <th>Kills</th>
                        <th>Deaths</th>
                        <th>Kick</th>
                    </tr>

                    {data}
                </table>
            </center>
        </div>
    </body>
</html>
"""

entry = """
<tr>
    <td><img src="{image}"></td>
    <td>
        {gear_img}
        <br>
        <b>{gear}</b>
    </td>
    
    <td>{name}</td>
    <td>{kills}</td>
    <td>{deaths}</td>
    <td>
        <form action="/kick/{player}" method="POST">
            Reason:
            <br>
            <input type="text" name="reason" class="admin-input">
            <br>
            <br>
            <input type="submit" value="Kick" class="admin-button">
        </form>
    </td>
</tr>
"""

@app.route("/")
def display_urt():
    data = ""
    online_players = []

    version = ""
    try:
        version = p.server["version"]
    except KeyError:
        return "<h2>Please wait for the server to initialize and come back! (Are you parsing any logs?)</h2>"


    for player in p.players:
        if (player == None):
            continue

        online_players.append(player)


    number = len(online_players)


    for player in online_players:
        sex_img = ""

        # There is no efficient way to determine the character's sex later on in development
        # of this program. Therefore, the avatar displayed on the website shall be of a random
        # sex.
        player.sex = random.choice([parsing.UrTSex.Male, parsing.UrTSex.Female])
        sex_img = ["/static/female.png", "/static/male.png"][player.sex]

        medic = parsing.UrTGear.Medkit in player.gear

        data += entry.format(
            name = player.name,
            gear_img = (" ".join([f"<img src='/static/gear/{x}.png' height='45'>" if x != parsing.UrTGear.Null else "" 
                            for x in player.gear])) if show_gear else "",

            gear = " ".join([x if x != parsing.UrTGear.Null else "" for x in player.gear]),
            image = sex_img,
            kills = player.kills,
            deaths = player.deaths,
            player = player.name
        )
    
    resp = make_response(html.format(
        servername = p.server["sv_hostname"],
        password_protected = "<i style='color: red;'>Password protected</i>" if p.server["g_needpass"] != "0" 
                                                    else "Not password protected",
        version = p.server["version"],
        count = number, 
        data = data,
        mapname = p.server["mapname"]
    ))

    
    return resp


log_view = """
<html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
    </head>

    <body>
        <h1>Log viewer</h1>

        {entries}
    </body>
</html>
"""

@app.route("/logs/")
def log_viewer():
    archives = os.listdir("static/archives/")
    archives.reverse()
    
    
    entries = ""
    if (len(archives) == 0):
        entries = "<h3>No logs found!</h3>"
    else:
        for archive in archives:
            entries += f"<a href='/static/archives/{archive}'>{archive}</a><br>"

    return log_view.format(
        entries = entries
    )


    
# This will login and store the password via a cookie.
# Not the best method, but it works for this--a program which is not going to be used.
@app.route("/login/", methods = ["POST"])
def save_password():
    try:
        password = request.form["password"]
    except IndexError:
        return "<h1>You did not provide the required fields.</h1>"

    resp = make_response(redirect("/"))

    if (password != rcon_password):
        return "<h1>Incorrect RCON Password!</h1>"

    resp.set_cookie("password", password)

    return resp


# This will obtain the current map image, by proxying urbanterror.info.
# It will also cache map images, to rate limit downloading from urbanterror.info.
@app.route("/map/<map_name>")
def get_map_image(map_name):
    # Return cached
    if (map_name in map_imgs):
        return Response(map_imgs[map_name], mimetype = "image/jpeg")

    download = requests.get(map_image_url.format(
        map_name = map_name
    ))

    # Map does not exist on urbanterror.info
    if (download.status_code == 404):
        return Response(map_imgs[None], mimetype = "image/png")

    # Cache it.
    map_imgs[map_name] = download.content

    return Response(download.content, mimetype = "image/jpeg")


# This will kick a user, but requires the RCON password stored as a cookie.
# You must also provide a reason (spaces make this harder).
@app.route("/kick/<user>", methods = ["POST"])
def kick_user(user):
    # Sanity check
    try:
        reason = request.form["reason"]
        password = request.cookies.get("password")
    except IndexError:
        return "<h1>Missing required fields--are you signed in?</h1>"

    # Password check
    if (password != rcon_password):
        return "<h1>Invalid password!</h1>"

    # User not found.
    if (user not in p.usernames):
        return "??? not supposed to happen (user was not found)"


    q3rcon.q3rcon.rcon_exec("127.0.0.1", rcon_password, f"kick {user} {reason}")
    print(f"kick {user} {reason}")
    index = p.usernames.index(user)
    
    # Delete the user from the list afterwards, since there is a bug, apparently, for some reason.
    p.usernames[index] = None
    p.players[index] = None

    return redirect("/")

    

def main():
    if (len(sys.argv) > 1):
        if (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
            menu = (
                "urt-stats - Generate a statistics page in real time for Urban Terror, with Python + Flask.\n"
                "USAGE:\n"
                "python urt-stats.py\n"
                "Server logging information must be piped into stdin.\n"
                "You may pipe the output of the dedicated server program to urt-stats.\n"
                "Example:\n"
                "./urt-ded-x86_64 | python urt-stats.py\n"
                "You may also, albeit less efficiently, parse the games.log file by piping it into this program.\n"
                "urt-stats will generate an HTML page containing the players and their characteristics, along with a moderation panel, accessible by the correct RCON password as specified in this program's config.\n"
            )

            print(menu)
    
        else:
            print("Error: urt-stats takes no arguments besides help (-h/--help)")
            return 1

        return 0

    app.run(host = '0.0.0.0', port = host_port)


if __name__ == "__main__":
    main()