import json
import re

class DescCompiler:
    def __init__(self):
        with open("assets/description.json", "r") as f:
            self.description_json = json.load(f)

    def get_compiled_text(self, level, kind, stats):
        if kind not in self.description_json.get(str(level), {}):
            raise KeyError(f"Invalid kind={kind!r} for level={level}")

        desc_template = self.description_json[str(level)][kind]["description"]

        # replace @n with stats[n-1]
        def replacer(match):
            index = int(match.group(1)) - 1
            return str(stats[index]) if 0 <= index < len(stats) else match.group(0)

        compiled = re.sub(r'@(\d+)', replacer, desc_template)

        # split description into lines for text_display
        lines = compiled.split("\n")

        return [[self.description_json[str(level)][kind]["title"]], lines]
