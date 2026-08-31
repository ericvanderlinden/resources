# -*- coding: utf-8 -*-
import sys, markdown, os, sys
# Configuration
#p = os.getcwd()
workspace = os.getenv("GITHUB_WORKSPACE", "../")
GROUP = "retro"
SERIES = "heinsius"
BOOK = "heinsius_01_GS158"
INPUT_FILE = os.path.join(workspace, "{}/{}/{}/readme.md".format(GROUP,SERIES,BOOK))
OUTPUT_FILE = os.path.join(workspace, "{}/{}/{}/index.html".format(GROUP,SERIES,BOOK))

TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="referrer" content="no-referrer" />
    <meta name="referrer" content="unsafe-url" />
    <meta name="referrer" content="origin" />
    <meta name="referrer" content="no-referrer-when-downgrade" />
    <meta name="referrer" content="origin-when-cross-origin" />
    <title>Page Title</title>
    <link rel="stylesheet" href="https://herwaarts.nl/resources/style/style.css" type="text/css" media="all">

</head>
<body>
<div class="container">
    <div id="primary">
        {{content}}
    </div>
</div>
</body>
</html>
"""



def get_paths(group, series, book, workspace=None):
    """
    Build (input, output) path pairs for the group, series, and book
    levels, each of which has its own readme.md / index.html.
    """
    workspace = workspace or os.getenv("GITHUB_WORKSPACE", "../")

    levels = {
        "group":  [group],
        "series": [group, series],
        "book":   [group, series, book],
    }

    paths = {}
    for level, parts in levels.items():
        dir_path = os.path.join(workspace, *parts)
        paths[level] = {
            "input": os.path.join(dir_path, "readme.md"),
            "output": os.path.join(dir_path, "index.html"),
        }

    return paths



def check_inputs_exist(paths):
    missing = [p["input"] for p in paths.values() if not os.path.exists(p["input"])]
    if missing:
        for path in missing:
            print(f"::error::Required file not found: {path}")
        raise FileNotFoundError(f"{len(missing)} required readme.md file(s) missing")


def main():
    paths = get_paths(GROUP, SERIES, BOOK)
    print(paths)
    check_inputs_exist(paths)  # raises with a clear message if anything's missing
    for level, p in paths.items():
        with open(p["input"], 'r') as f:
            md= f.read()
        extensions = ['extra', 'smarty']
        html = markdown.markdown(md, extensions=extensions, output_format='html5')
        doc = TEMPLATE.replace('{{content}}', html);
        with open(p["output"], 'w') as f:
            f.write(doc)

main()
# if __name__ == '__main__':
    # sys.exit(main())