import re


class Filter:
    def __init__(self, settings: list[dict], all_match: bool) -> None:
        self._settings = settings
        self._all_match = all_match

    @staticmethod
    def _match_setting(setting: dict, line: str) -> bool:
        if setting["reg"]:
            # Regex match
            pattern = re.compile(setting["keyword"])
            return bool(pattern.search(line))
        else:
            # Simple substring match
            return setting["keyword"] in line

    def match(self, line) -> bool:
        return (all if self._all_match else any)(Filter._match_setting(setting, line) for setting in self._settings)
