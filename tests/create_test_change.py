import hashlib
import json
from pathlib import Path
import shutil


SOURCE = Path(
    "snapshots/coffeyville_kansas/"
    "2026-08-10/20260810_054940"
)

TARGET = Path(
    "snapshots/coffeyville_kansas/"
    "2026-08-10/TEST_CHANGED"
)

def sha256(content: str) -> str:
    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

def main():
    if TARGET.exists():
        shutil.rmtree(TARGET)

    shutil.copytree(SOURCE, TARGET)

    normalized_file = TARGET / "normalized.html"
    metadata_file = TARGET / "metadata.json"

    html = normalized_file.read_text(
        encoding="utf-8"
    )

    # Simulate a website structure change.
    html = html.replace(
        "</body>",
        """
        <div class="test-change">
            NEW TEST ELEMENT
        </div>
        </body>
        """,
        1,
    )

    normalized_file.write_text(
        html,
        encoding="utf-8",
    )
    
    metadata = json.loads(
        metadata_file.read_text(
            encoding="utf-8"
        )
    )
    
    metadata["snapshot_id"] = "TEST_CHANGED"
    metadata["normalized_html_sha256"] = sha256(
        html
    )

    metadata_file.write_text(
        json.dumps(
            metadata,
            indent=4,
        ),
        encoding="utf-8",
    )
    

    print("=" * 60)
    print("TEST SNAPSHOT CREATED")
    print("=" * 60)
    print(f"Original: {SOURCE}")
    print(f"Modified: {TARGET}")
    print()
    print(
        "Added test element:"
        '<div class="test-change">'
    )


if __name__ == "__main__":
    main()