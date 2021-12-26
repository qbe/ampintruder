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

            @media screen and (max-width: 800px) {
                h2 {font-size: 5vw}
                h3 {font-size: 4vw}
                p {font-size: 3vw}
                .block {width: 100%}
                input[type=text] {width: 81%}
                input[type=submit]{font-size:3vw}
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
                <input type="submit" name="link" value="hinten anfügen">
                <input type="submit" name="link" value="jetzt abspielen">
            </form>
        </div>
"""
song_list = """
<h3 class="heading">Songliste</h3>
"""

html_end = """
    </body>
</html>
"""
