"""Build anime_scenery_tags.csv from the SFW split of isek-ai/danbooru-tags-2024.

Usage:
    python build_dataset.py path/to/sfw/train-*.parquet

Keeps illustrations that are tagged as scenery and contain no people, drops any
row carrying a tag on the blocklist, and adds the derived `atmosphere` column.
"""
import collections
import csv
import sys

import pyarrow.parquet as pq

OUT = "anime_scenery_tags.csv"

SCENE_BASE = {"scenery", "landscape", "cityscape", "nature"}

ATMOSPHERE = {
    "day": {"day", "blue sky", "sunlight", "sun"},
    "night": {"night", "night sky", "starry sky", "moon", "full moon", "crescent moon"},
    "sunset": {"sunset", "twilight", "evening", "dusk", "orange sky", "sunrise", "dawn"},
    "rain": {"rain", "storm", "lightning"},
    "snow": {"snow", "snowing", "winter"},
    "fog": {"fog", "mist"},
}

# Rows carrying any of these are dropped. The source split is already rated
# "general", so this removes only a handful of rows.
BLOCKLIST = {
    "yuri", "yaoi", "hetero", "kiss", "nude", "completely nude", "topless", "nipples", "breasts",
    "large breasts", "small breasts", "medium breasts", "cleavage", "ass", "panties", "underwear", "bra",
    "lingerie", "swimsuit", "bikini", "blood", "death", "corpse", "guro", "sex", "vaginal", "cum",
}
BLOCK_SUBSTRINGS = ("breast", "nipple", "nude", "naked", "panties", "panty", "underwear", "lingerie", "sex",
                    "erotic", "pussy", "penis", "loli", "shota", "bikini", "thong", "crotch", "groin",
                    "pubic", "bdsm", "bondage", "fellatio", "futa", "tentacle", "blood", "corpse", "guro",
                    "suicide", "yuri", "yaoi", "nsfw", "pantsu", "pantyshot", "upskirt", "censor", "hentai",
                    "eroge", "ecchi", "porn", "raped")


# Artist handles are free-form usernames that cannot be screened, and they are not a usable feature.
DROP_COLUMNS = {"artist"}


def blocked(tags):
    if tags & BLOCKLIST:
        return True
    return any(sub in tag for tag in tags for sub in BLOCK_SUBSTRINGS)


def split_tags(value):
    return set(x.strip() for x in value.split(",")) if value else set()


def atmosphere_of(tags):
    hit = [name for name, members in ATMOSPHERE.items() if tags & members]
    return hit[0] if len(hit) == 1 else ""


def main(paths):
    kept = dropped = 0
    labels = collections.Counter()
    writer = None
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        for path in sorted(paths):
            pf = pq.ParquetFile(path)
            for i in range(pf.num_row_groups):
                table = pf.read_row_group(i)
                if writer is None:
                    writer = csv.writer(f)
                    names = [n for n in table.column_names if n not in DROP_COLUMNS]
                    writer.writerow(names + ["atmosphere"])
                for row in table.to_pylist():
                    tags = split_tags(row["general"])
                    if not tags & SCENE_BASE or "no humans" not in tags:
                        continue
                    every_tag = tags.union(*(split_tags(row[c]) for c in ("meta", "character", "copyright")))
                    if blocked(every_tag):
                        dropped += 1
                        continue
                    label = atmosphere_of(tags)
                    labels[label or "(unlabeled)"] += 1
                    writer.writerow(["" if row[n] is None else row[n] for n in names] + [label])
                    kept += 1
    print("rows written", kept, "rows dropped by blocklist", dropped)
    for name, count in labels.most_common():
        print(f"  {name:12s} {count}")


if __name__ == "__main__":
    main(sys.argv[1:])
