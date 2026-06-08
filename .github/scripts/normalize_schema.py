#!/usr/bin/env python3
import re
import sys
from pathlib import Path

TARGET = Path("src/r2mm/ecosystem/EcosystemSchema.ts")

INJECTION = """\
function ensureOtherDistribution(distributions: R2Modman["distributions"]): R2Modman["distributions"] {
    if (!Array.isArray(distributions)) {
        return distributions;
    }
    const hasSteam = distributions.some(d => d.platform === Platform.STEAM);
    const hasOther = distributions.some(d => d.platform === Platform.OTHER);
    if (hasSteam && !hasOther) {
        const steamIndex = distributions.findIndex(d => d.platform === Platform.STEAM);
        const result = [...distributions];
        result.splice(steamIndex + 1, 0, {platform: Platform.OTHER, identifier: undefined});
        return result;
    }
    return distributions;
}

"""


def normalize(src: str) -> str:
    if "ensureOtherDistribution" in src:
        return src

    src = re.sub(
        r'(import\s*\{[^}]*EcosystemSupportedGames)(\s*\}\s*from\s*["\'][^"\']*ThunderstoreSchema["\'];?)',
        r'\1, Platform\2',
        src,
        count=1,
    )

    src = re.sub(
        r'(?=async function internalUpdateEcosystemReactives)',
        INJECTION,
        src,
        count=1,
    )

    src = re.sub(
        r'(\n\s+)(result\.push\(\[identifier, entry\]\);)',
        r'\1entry.distributions = ensureOtherDistribution(entry.distributions);\1\2',
        src,
        count=1,
    )

    return src


def main() -> None:
    if not TARGET.exists():
        print(f"ERROR: {TARGET} not found.", file=sys.stderr)
        sys.exit(2)

    original = TARGET.read_text(encoding="utf-8")
    result = normalize(original)

    if result == original:
        print(f"No changes needed for {TARGET}")
    else:
        TARGET.write_text(result, encoding="utf-8")
        print(f"Updated {TARGET}")


if __name__ == "__main__":
    main()
