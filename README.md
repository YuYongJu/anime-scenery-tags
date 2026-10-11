# Anime Scenery Tags

Tag and metadata records for 19,652 anime scenery illustrations that contain no people, with a derived
`atmosphere` label (day, night, sunset, rain, snow, fog). Built for a supervised classification project.

The file holds text tags and numeric metadata only. It contains no images.

## File

`anime_scenery_tags.csv`: 19,652 rows, 31 columns, one row per illustration.

## Source

Extracted from the `sfw` split of [isek-ai/danbooru-tags-2024](https://huggingface.co/datasets/isek-ai/danbooru-tags-2024)
on Hugging Face (license CC0 1.0), which is a public export of the tags that volunteers write for illustrations
on the Danbooru image board. That split has 2,420,985 rows, all rated "general".

A row is kept when:

1. its tags include at least one of `scenery`, `landscape`, `cityscape`, `nature`, and
2. its tags include `no humans`, and
3. none of its general, character, copyright or meta tags is on the content blocklist in `build_dataset.py`.

Step 3 removed 151 rows. The source `artist` column is left out because artist handles are free-form
usernames that cannot be screened. `build_dataset.py` reproduces the file from the source parquet files.

## Columns

| Column | Type | Meaning |
|---|---|---|
| id | int | Post id |
| created_at, updated_at | timestamp | When the post was created and last edited |
| score, up_score, down_score | int | Community votes |
| fav_count | int | Number of users who favorited the post |
| rating | string | Content rating, always `g` (general) |
| image_width, image_height | int | Image size in pixels |
| tag_count | int | Total number of tags |
| tag_count_general, tag_count_artist, tag_count_character, tag_count_copyright, tag_count_meta | int | Tag counts by tag type |
| parent_id | int | Id of the parent post, blank if none |
| has_children, has_active_children, has_visible_children | bool | Whether the post has child posts |
| file_ext | string | Image file type |
| is_pending, is_flagged, is_deleted, is_banned | bool | Moderation status |
| bit_flags | int | Internal flags |
| general | string | Comma-separated descriptive tags (setting, objects, weather, composition, color) |
| character | string | Comma-separated character tags |
| copyright | string | Comma-separated series or franchise tags |
| meta | string | Comma-separated tags about the file itself |
| atmosphere | string | Derived target, blank when no single class applies |

## Target: `atmosphere`

Each class has a fixed list of tags. A row gets a class only when its `general` tags match exactly one class.
Rows that match no class, or more than one, are left blank.

| Class | Tags | Rows |
|---|---|---|
| day | day, blue sky, sunlight, sun | 8,144 |
| night | night, night sky, starry sky, moon, full moon, crescent moon | 2,086 |
| sunset | sunset, twilight, evening, dusk, orange sky, sunrise, dawn | 922 |
| snow | snow, snowing, winter | 236 |
| rain | rain, storm, lightning | 234 |
| fog | fog, mist | 159 |
| (blank) | no class or more than one | 7,871 |

Labeled rows: 11,781.

The tags listed above are still present in the `general` column. Remove them from the features before training,
otherwise the model reads the answer directly.

## License

CC0 1.0, same as the source.
