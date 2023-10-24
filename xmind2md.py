# -*- coding: utf-8 -*-
import os
import argparse
import zipfile
import json


def get_content(xmind_file: str) -> dict:
    with zipfile.ZipFile(xmind_file) as zf:
        namelist = zf.namelist()
        assert "content.json" in namelist, FileNotFoundError(
            "XMind file doesn't contain content.json"
        )
        content_json = zf.read("content.json").decode("utf-8")
        return json.loads(content_json)


def topic2md(topic: dict, is_root: bool = False, depth: int = -1) -> str:
    if is_root:
        md = "# " + topic["title"] + "\n\n"
    else:
        md = depth * "  " + "- " + topic["title"] + "\n"
    if "children" in topic:
        for child in topic["children"]["attached"]:
            md += topic2md(child, depth=depth + 1)
    return md


def main(args):
    input_file = args.input
    content = get_content(input_file)

    results = ""
    for canvas in content:
        md = topic2md(canvas["rootTopic"], True)
        results += md + "\n"

    output_file = args.output
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + ".md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="XMind file")
    parser.add_argument(
        "-o",
        "--output",
        help="markdown file. If not provided, use the same filename of XMind file",
        required=False,
    )
    args = parser.parse_args()
    main(args)
