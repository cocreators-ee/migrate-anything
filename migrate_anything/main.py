from argparse import ArgumentParser

from migrate_anything.migrator import run


def main():
    ap = ArgumentParser(
        prog="migrate-anything",
        description="Helps manage migrations for databases and anything else",
        epilog="For more information check out https://github.com/cocreators-ee/migrate-anything",
    )

    ap.add_argument(
        "package", help="The Python package where your migrations are stored"
    )

    ap.add_argument(
        "--revert-latest",
        action="store_true",
        dest="revert",
        help="Reverts last migration applied using migration file rather than migration stored in DB",
    )

    options = ap.parse_args()
    run(options.package, revert=options.revert)


if __name__ == "__main__":
    main()
