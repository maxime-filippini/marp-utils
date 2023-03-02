class Tag:
    ...


class Divider(Tag):
    id = "divider"

    def expand(self, id, title):
        directives = [
            f'<!-- _header: <div id="{id}"></div> -->',
            f"<!-- _class: divider -->",
        ]

        if title:
            directives.append(f"# {title}")

        return "\n".join(directives)
