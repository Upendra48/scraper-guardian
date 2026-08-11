from pathlib import Path

from bs4 import BeautifulSoup


SNAPSHOT = Path(
    "snapshots/coffeyville_kansas/2026-08-10/"
    "20260810_054940/normalized.html"
)


def get_element_path(element) -> str:
    """
    Generate an XPath-like path for a BeautifulSoup element.
    """

    path_parts = []

    current = element

    while current is not None:

        if not getattr(current, "name", None):
            break

        parent = current.parent

        if parent is None:
            break

        index = 1

        for sibling in parent.find_all(
            current.name,
            recursive=False,
        ):
            if sibling is current:
                break

            index += 1

        path_parts.append(
            f"{current.name}[{index}]"
        )

        current = parent

    path_parts.reverse()

    return "/" + "/".join(path_parts)


def main():

    html = SNAPSHOT.read_text(
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    links = soup.find_all("a")

    print("=" * 70)
    print("BID ELEMENT DETECTION")
    print("=" * 70)

    found = 0

    for link in links:

        text = link.get_text(
            " ",
            strip=True,
        )

        href = link.get(
            "href"
        )

        if not text:
            continue

        # Only show links that look like
        # procurement/bid links.
        text_lower = text.lower()

        href_lower = (
            href.lower()
            if href
            else ""
        )

        is_bid = (
            "bidid" in href_lower
            or "/bid/" in href_lower
            or "proposal" in text_lower
            or "project" in text_lower
            or "construction" in text_lower
            or "wastewater" in text_lower
        )

        if not is_bid:
            continue

        found += 1

        print()
        print(f"[BID {found}]")
        print("-" * 70)

        print(
            f"Text: {text}"
        )

        print(
            f"Href: {href}"
        )

        print(
            f"Path: {get_element_path(link)}"
        )

        print(
            f"Attributes: {dict(link.attrs)}"
        )

    print()
    print("=" * 70)
    print(
        f"Bid-like elements found: {found}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()