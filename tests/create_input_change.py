from pathlib import Path
import hashlib
import json
import shutil


SOURCE = Path(
    "snapshots/coffeyville_kansas/"
    "2026-08-10/20260810_054940"
)

TARGET = Path(
    "snapshots/coffeyville_kansas/"
    "2026-08-10/TEST_INPUT_CHANGED"
)


def sha256(content: str) -> str:
    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def main():

    if TARGET.exists():
        shutil.rmtree(TARGET)

    shutil.copytree(SOURCE, TARGET)

    html_file = TARGET / "normalized.html"
    metadata_file = TARGET / "metadata.json"

    html = html_file.read_text(
        encoding="utf-8"
    )

    old = 'name="search"'

    if old not in html:
        raise RuntimeError(
            'Could not find name="search"'
        )

    html = html.replace(
        old,
        'name="keyword"',
        1,
    )

    html_file.write_text(
        html,
        encoding="utf-8",
    )

    metadata = json.loads(
        metadata_file.read_text(
            encoding="utf-8"
        )
    )

    metadata["snapshot_id"] = (
        "TEST_INPUT_CHANGED"
    )

    metadata["normalized_html_sha256"] = (
        sha256(html)
    )

    metadata_file.write_text(
        json.dumps(
            metadata,
            indent=4,
        ),
        encoding="utf-8",
    )

    print("=" * 60)
    print("INPUT CHANGE TEST CREATED")
    print("=" * 60)
    print(
        'Changed: name="search"'
    )
    print(
        'To:      name="keyword"'
    )
    print(f"Snapshot: {TARGET}")


if __name__ == "__main__":
    main()