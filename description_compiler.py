import json


class DescCompiler:
    def __init__(self):
        with open("assets/description.json", "r") as f:
            data = json.load(f)
        self.description_json = data

    def get_compiled_text(self,level,kind,stats):
        temp = []
        if kind not in self.description_json.get(str(level), {}):
            raise KeyError(f"Invalid kind={kind!r} for level={level}")
        for line in self.description_json[str(level)][kind]["description"][0]:
            if line is self.description_json[str(level)][kind]["description"][0][-1]:
                temp.append(f"{line} {stats}")
            else:
                temp.append(line)
        for line in self.description_json[str(level)][kind]["description"][1]:
            temp.append(line)
        return [[self.description_json[str(level)][kind]["title"]],temp]
