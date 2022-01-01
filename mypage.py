html_start = """
<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" charset="utf-8"/>
        <style>
            .block {
                display: block;
                position: relative;
                clear: both;
                padding: 0.5vw;
            }
            .button {
                float: left;
                margin: 0.5vw;
            }
            .title {
                font-family: "Helvetica", sans-serif;
            }
            .heading {
                font-family: "Helvetica", sans-serif;
            }
            .result {
            	font-family: "Lucida Console", monospace;
            }
            .loaded {
            	font-family: "Helvetica", sans-serif;
            	color: black;
            }
            .queued {
            	font-family: "Helvetica", sans-serif;
            	color: darkgrey;
            }
            .playlist {
                font-family: "Helvetiva", sans-serif;
                font-size: 3.5vw
            }

            @media screen and (max-width: 800px) {
                h2 {font-size: 5vw}
                h3 {font-size: 4vw}
                p {font-size: 3vw}
                .block {width: 100%}
                input[type=text] {width: 81%}
                input[type=submit]{font-size:3vw}
            }

            wrap-collabsible {
            margin-bottom: 1.2rem 0;
            }

            input[type='checkbox'].toggle {
            display: none;
            }

            .lbl-toggle {
            display: block;

            font-weight: bold;
            font-family: monospace;
            font-size: 1.2rem;
            text-transform: uppercase;
            text-align: center;

            padding: 1rem;

            color: #000000;
            background: #aaaaaa;
            cursor: pointer;

            border-radius: 7px;
            transition: all 0.25s ease-out;
            }

            .lbl-toggle:hover {
            color: #444444;
            }

            .lbl-toggle::before {
            content: ' ';
            display: inline-block;

            border-top: 5px solid transparent;
            border-bottom: 5px solid transparent;
            border-left: 5px solid currentColor;
            vertical-align: middle;
            margin-right: 0.7rem;
            transform: translateY(-2px);

            transition: transform 0.2s ease-out;
            }

            .toggle:checked + .lbl-toggle::before {
            transform: rotate(90deg) translateX(-3px);
            }

            .collapsible-content {
            max-height: 0px;
            overflow: hidden;
            transition: max-height 0.25s ease-in-out;
            }

            .toggle:checked + .lbl-toggle + .collapsible-content {
            max-height: 100vh;
            }

            .toggle:checked + .lbl-toggle {
            border-bottom-right-radius: 0;
            border-bottom-left-radius: 0;
            }

            .collapsible-content .content-inner {
            background: rgba(50, 50, 50, 0.2);
            border-bottom: 1px solid rgba(0, 0, 0, 0.45);
            border-bottom-left-radius: 7px;
            border-bottom-right-radius: 7px;
            padding: 0.5rem 1rem;
            }
            </style>
        <title>home audio</title>
    </head>
    <body>
"""

base_page = """
        <h2 class="title">Home Audio</h2>

        <div class="block">
            <form action="" method="post">
                <input type="submit" name="control" value="play" class="button">
                <input type="submit" name="control" value="pause" class="button">
                <input type="submit" name="control" value="vor" class="button">
                <input type="submit" name="control" value="zurück" class="button">
            </form>
        </div>
        <div class="block">
            <form action="" method="post">
                <input type="text" id="ytlnk" name="ytlnk" placeholder="Link">
                <input type="submit" name="link_back" value="hinten anfügen">
                <input type="submit" name="link_front" value="jetzt abspielen">
            </form>
        </div>
"""

song_list = """
<h3 class="heading">Songliste</h3>
"""

playlist_spoiler_start = """
<div class="wrap-collabsible">
  <input id="collapsible" class="toggle" type="checkbox">
  <label for="collapsible" class="lbl-toggle">Playlists</label>
  <div class="collapsible-content">
    <div class="content-inner">"""

def build_list_element(title, id):
    string = "<div class\"block\"><form action=\"\" method=\"post\">"
    string = string + "<input type=\"hidden\" name=\"ytlnk\" value=\"%s\" class=\"button\">" % id
    string = string + "<input type=\"submit\" name=\"link_back\" value=\"hinten\" class=\"button\">"
    string = string + "<input type=\"submit\" name=\"link_front\" value=\"vorne\" class=\"button\">"
    string = string + "</form><p class=\"playlist\">%s</p></div>" % title
    return string

playlist_spoiler_end = """
    </div>
  </div>
</div>
"""


html_end = """
    </body>
</html>
"""
