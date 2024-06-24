# -*- coding: utf-8 -*-
import re
import json
import zipfile
import argparse
from typing import List
from xml.etree import ElementTree as ET


class XMindLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_content(self):
        with zipfile.ZipFile(self.file_path) as zf:
            namelist = zf.namelist()
            if "content.json" in namelist:
                content_json = zf.read("content.json").decode("utf-8")
                return json.loads(content_json), "json"
            elif "content.xml" in namelist:
                content_xml = zf.read("content.xml").decode("utf-8")
                content_xml = re.sub(r'\sxmlns(:\w+)?="[^"]+"', "", content_xml)
                content_xml = re.sub(r'\b\w+:(\w+)=("[^"]*")', r"\1=\2", content_xml)
                root = ET.fromstring(content_xml)
                return root, "xml"
            else:
                raise FileNotFoundError(
                    "XMind file must contain content.json or content.xml"
                )

    @staticmethod
    def topic2md_json(topic: dict, is_root: bool = False, depth: int = -1) -> str:
        title = topic["title"].replace("\r", "").replace("\n", " ")
        if is_root:
            md = "# " + title + "\n\n"
        else:
            md = depth * "  " + "- " + title + "\n"
        if "children" in topic:
            for child in topic["children"]["attached"]:
                md += XMindLoader.topic2md_json(child, depth=depth + 1)
        return md

    @staticmethod
    def topic2md_xml(topic: ET.Element, is_root: bool = False, depth: int = -1) -> str:
        title = topic.find("title").text.replace("\r", "").replace("\n", " ")
        if is_root:
            md = "# " + title + "\n\n"
        else:
            md = depth * "  " + "- " + title + "\n"
        for child in topic.findall("children/topics[@type='attached']/topic"):
            md += XMindLoader.topic2md_xml(child, depth=depth + 1)
        return md

    def load(self) -> list[str]:
        content, format = self.get_content()

        docs: List[str] = []
        if format == "json":
            content: List[dict]
            for sheet in content:
                docs.append(
                    XMindLoader.topic2md_json(sheet["rootTopic"], is_root=True).strip(),
                )

        elif format == "xml":
            content: ET.Element
            for sheet in content.findall("sheet"):
                docs.append(
                    XMindLoader.topic2md_xml(sheet.find("topic"), is_root=True).strip(),
                )

        else:
            raise ValueError("Invalid format")

        return docs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="XMind file")
    parser.add_argument(
        "-o",
        "--output",
        help="markdown file. If not provided, use the same filename of XMind file",
        required=False,
    )

    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    loader = XMindLoader(input_file)
    docs = loader.load()
    content = "\n\n".join(docs)

    if output_file is None:
        print(content)
    else:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)


if __name__ == "__main__":
    main()
