#!/usr/bin/env python3
import json
import sys
from pathlib import Path

FILE = Path("src/assets/data/ecosystem.json")

def add_other_platform(distributions):
    if not isinstance(distributions, list):
        return distributions
    for i, dist in enumerate(distributions):
        if dist.get("platform") == "steam":
            if not any(d.get("platform") == "other" for d in distributions):
                distributions.insert(i + 1, {"platform": "other", "identifier": None})
            break
    return distributions

def main():
    if not FILE.exists():
        print(f"ERROR: {FILE} not found.", file=sys.stderr)
        sys.exit(2)
    data = json.loads(FILE.read_text(encoding="utf-8"))
    changed = False
    changed_games = []
    games = data.get("games", {})
    for game_key, game in games.items():
        game_changed = False
        dists = game.get("distributions")
        if isinstance(dists, list):
            before = json.dumps(dists, sort_keys=True)
            add_other_platform(dists)
            after = json.dumps(dists, sort_keys=True)
            if before != after:
                changed = True
                game_changed = True
        r2list = game.get("r2modman")
        if isinstance(r2list, list):
            for entry in r2list:
                ed = entry.get("distributions")
                if isinstance(ed, list):
                    before = json.dumps(ed, sort_keys=True)
                    add_other_platform(ed)
                    after = json.dumps(ed, sort_keys=True)
                    if before != after:
                        changed = True
                        game_changed = True
        if game_changed:
            changed_games.append(game_key)
    if changed:
        FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Modified {FILE}")
        if changed_games:
            print(f"Modified games: {', '.join(changed_games)}")
    else:
        print("No changes needed")

if __name__ == "__main__":
    main()