import yaml

import re
from pathlib import Path

from ._tags import Divider


class MarpProcessor:
    tag_dict = {"divider": Divider}

    def __init__(self):
        pass

    def _parse_frontmatter(self, section):
        frontmatter = yaml.safe_load(section)

        if "marp" not in frontmatter or not frontmatter.get("marp"):
            raise Exception("not marp")

        return frontmatter

    def _parse_section(self, section, var_dict):
        section_lines = section.splitlines()
        out = []
        for line in section_lines:
            for k, v in var_dict.items():
                line = line.replace(f"${{{k}}}", str(v))

            out.append(self._parse_comment(line))

        return "\n".join(out)

    def _parse_comment(self, line):
        rgx = re.compile("<!--(.+)-->")
        match = rgx.match(line)

        if not match:
            return line

        content = match.groups()[0].strip()
        id = content.split(" ").pop(0)

        if id not in self.tag_dict:
            return line

        tag_parser = self.tag_dict[id]()

        param_items = re.findall('(\w+)="([^"]+)"', content)
        params = {k: v for k, v in param_items}

        return tag_parser.expand(**params)

    def process_file(self, path, out_path):
        path = Path(path)

        with open(path, "r", encoding="utf-8") as fp:
            data = fp.read()

        sections = [section.strip() for section in data.split("---") if section]

        frontmatter = self._parse_frontmatter(sections[0])
        variable_dict = frontmatter["variables"]

        new_sections = []
        for section in sections:
            new_sections.append(self._parse_section(section, var_dict=variable_dict))

        out_path = Path(out_path)
        out_str = "---\n\n" + "\n\n---\n\n".join(new_sections)

        with open(out_path, "w", encoding="utf-8") as fp:
            fp.write(out_str)
