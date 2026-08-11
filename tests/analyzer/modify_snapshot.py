from pathlib import Path


SOURCE = Path(
    "snapshots/beaconbid/2026-08-11/20260811_042013/normalized.html"
)

TARGET = Path(
    "snapshots/beaconbid/2026-08-11/test_modified.html"
)


def main():

    html = SOURCE.read_text(
        encoding="utf-8"
    )

    original = html

    # --------------------------------------------------
    # 1. HREF change
    # --------------------------------------------------

    html = html.replace(
        'href="bids.aspx?bidID=287"',
        'href="/procurement/bid/287"',
    )

    # --------------------------------------------------
    # 2. CLASS change
    # --------------------------------------------------

    html = html.replace(
        'class="bid-list"',
        'class="procurement-list"',
    )

    # --------------------------------------------------
    # 3. ID change
    # --------------------------------------------------

    html = html.replace(
        'id="bid-container"',
        'id="procurement-container"',
    )

    # --------------------------------------------------
    # 4. Visible text change
    # --------------------------------------------------

    html = html.replace(
        "View Bid",
        "Bid Details",
    )

    # --------------------------------------------------
    # 5. Add a scraper-relevant element
    # --------------------------------------------------

    marker = "</body>"

    if marker in html:

        html = html.replace(
            marker,
            """
<button class="download-bid">
    Download Bid
</button>
</body>
""",
            1,
        )

    # --------------------------------------------------
    # Safety check
    # --------------------------------------------------

    if html == original:
        raise RuntimeError(
            "No changes were made. "
            "The expected HTML patterns were not found."
        )

    TARGET.write_text(
        html,
        encoding="utf-8",
    )

    print("=" * 70)
    print("MODIFIED SNAPSHOT CREATED")
    print("=" * 70)
    print(f"Source : {SOURCE}")
    print(f"Target : {TARGET}")
    print(
        f"Original size : {len(original):,}"
    )
    print(
        f"Modified size : {len(html):,}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()