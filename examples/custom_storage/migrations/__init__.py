from migrate_anything import configure


class CustomStorage(object):
    def __init__(self, file):
        self.file = file

    def save_migration(self, name, code):
        with open(self.file, "a", encoding="utf-8") as file:
            file.write("{},{}\n".format(name, code))

    def list_migrations(self):
        try:
            with open(self.file, encoding="utf-8") as file:
                return [
                    line.split(",")
                    for line in file.readlines()
                    if line.strip()  # Skip empty lines
                ]
        except FileNotFoundError:
            return []

    def remove_migration(self, name):
        migrations = [
            migration for migration in self.list_migrations() if migration[0] != name
        ]

        with open(self.file, "w", encoding="utf-8") as file:
            for row in migrations:
                file.write("{},{}\n".format(*row))


configure(storage=CustomStorage("test.txt"))
