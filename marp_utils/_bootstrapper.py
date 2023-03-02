import yaml

LINE_SKIP = "\n"
SECTION_SEP = "---"
NEXT_SECTION_SEP = LINE_SKIP * 2 + SECTION_SEP + LINE_SKIP * 2


def comment(name, **kwargs):
    return "".join(
        ("<!-- ", f"{name} ", " ".join(f'{k}="{v}"' for k, v in kwargs.items()), " -->")
    )


class Bootstrapper:
    def __init__(
        self,
        title,
        subtitle=None,
        date=None,
        event=None,
        sections=None,
        variables={},
        options=None,
    ):
        if options is None:
            options = []

        if sections is None:
            sections = []

        self.title = title
        self.subtitle = subtitle
        self.date = date
        self.event = event
        self.sections = sections
        self._variables = variables
        self.options = options

    variable_fields = ["title", "subtitle", "date", "event"]

    @property
    def header_text(self):
        return "'[*${title}*](#1)'"

    @property
    def footer_text(self):
        out = ""

        if self.event is not None:
            out += "*${event}* "

        if self.date is not None:
            out += "${date}"

        if out:
            out = f"'{out}'"
        return out

    @property
    def variables(self):
        out = self._variables

        for field in self.variable_fields:
            data = getattr(self, field)
            if getattr(self, field):
                out[field] = data

        return out

    @property
    def frontmatter(self):
        return yaml.dump(
            {"marp": True, "theme": "mfi-base", "variables": self.variables}
        )[:-1]

    @property
    def first_slide(self):
        to_write = ["# ${title}"]

        if self.subtitle:
            to_write.append("## ${subtitle}")

        if self.footer_text:
            to_write.append(self.footer_text[1:-1])

        return "\n".join(to_write)

    @property
    def extra_directives(self):
        out = []

        if "header" in self.options:
            out.append(f"<!-- header: {self.header_text} -->")

        if "footer" in self.options:
            out.append(f"<!-- footer: {self.footer_text} -->")

        if "paginate" in self.options:
            out.append("<!-- paginate: true -->")

        if "img-center" in self.options:
            out.append(
                (
                    "<style>\n"
                    "img[alt~=center] {\n"
                    "    display: block;\n"
                    "    margin: 0 auto;\n"
                    "}\n"
                    "</style>"
                )
            )

        return "\n".join(out)

    def toc(self):
        return "# Table of contents\n" + comment(name="toc")

    def divider(self, id, title):
        return comment(name="divider", id=id, title=title)

    def blank_sections(self):
        out = []

        for section in self.sections:
            divider_tag = self.divider(
                id=section.lower().replace(" ", "-"), title=section
            )

            content = f"## {section} \n Start writing your content here!"
            out.append((divider_tag, content))

        return out

    def bootstrap(self, file_path, include_toc=True):
        to_write = []

        to_write.append(SECTION_SEP)
        to_write.append(LINE_SKIP)
        to_write.append(LINE_SKIP)
        to_write.append(self.frontmatter)
        to_write.append(NEXT_SECTION_SEP)
        to_write.append(self.first_slide)
        to_write.append(NEXT_SECTION_SEP)
        to_write.append(self.extra_directives)

        if self.extra_directives:
            to_write.append(LINE_SKIP)
            to_write.append(LINE_SKIP)

        if include_toc:
            to_write.append(self.toc())
            to_write.append(NEXT_SECTION_SEP)

        for divider, content in self.blank_sections():
            to_write.append(divider)
            to_write.append(NEXT_SECTION_SEP)
            to_write.append(content)
            to_write.append(NEXT_SECTION_SEP)

        with open(file_path, "w", encoding="utf-8") as fp:
            fp.write("".join(to_write))
