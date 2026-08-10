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
    "2026-08-10/TEST_ATTRIBUTE_CHANGED"
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

    # Find the first div and change its class.
    old = '<div class="'

    position = html.find(old)

    if position == -1:
        raise RuntimeError(
            "No div with a class attribute found."
        )

    class_start = position + len(old)
    class_end = html.find(
        '"',
        class_start,
    )

    old_class = html[
        class_start:class_end
    ]

    new_class = "TEST_CHANGED_CLASS"

    html = (
        html[:class_start]
        + new_class
        + html[class_end:]
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
        "TEST_ATTRIBUTE_CHANGED"
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
    print("ATTRIBUTE CHANGE TEST CREATED")
    print("=" * 60)
    print(f"Old class: {old_class}")
    print(f"New class: {new_class}")
    print(f"Snapshot:  {TARGET}")


if __name__ == "__main__":
    main()