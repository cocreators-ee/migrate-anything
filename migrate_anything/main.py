from argparse import ArgumentParser

from migrate_anything.migrator import run


def main():
    ap = ArgumentParser(
        prog="migrate-anything",
        description="Helps manage migrations for databases and anything else",
        epilog="For more information check out https://github.com/Lieturd/migrate-anything",
    )

    ap.add_argument(
        "package", help="The Python package where your migrations are stored"
    )

    options = ap.parse_args()
    run(options.package)


if __name__ == "__main__":
    main()
