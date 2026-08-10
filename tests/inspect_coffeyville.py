from pathlib import Path

from bs4 import BeautifulSoup


HTML_FILE = Path(
    "snapshots/coffeyville_kansas/"
    "2026-08-10/20260810_054940/normalized.html"
)


def main():

    html = HTML_FILE.read_text(
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    print("=" * 70)
    print("COFFEYVILLE INPUTS")
    print("=" * 70)

    inputs = soup.find_all("input")

    print(f"Total inputs: {len(inputs)}")
    print()

    for index, element in enumerate(inputs, 1):

        print(f"[{index}]")
        print(f"  tag:         {element.name}")
        print(f"  id:          {element.get('id')}")
        print(f"  name:        {element.get('name')}")
        print(f"  type:        {element.get('type')}")
        print(f"  class:       {element.get('class')}")
        print(f"  placeholder: {element.get('placeholder')}")
        print()


    print("=" * 70)
    print("COFFEYVILLE LINKS")
    print("=" * 70)

    links = soup.find_all("a")

    print(f"Total links: {len(links)}")
    print()

    for index, element in enumerate(links, 1):

        text = element.get_text(
            " ",
            strip=True,
        )

        print(f"[{index}]")
        print(f"  text:  {text[:100]}")
        print(f"  href:  {element.get('href')}")
        print(f"  id:    {element.get('id')}")
        print(f"  class: {element.get('class')}")
        print()


if __name__ == "__main__":
    main()