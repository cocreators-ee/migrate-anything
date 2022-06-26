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

    ap.add_argument('--down', action='store_true', help='Reverse last migration.')

    options = ap.parse_args()
    run(options.package, down=options.down)


if __name__ == "__main__":
    main()
