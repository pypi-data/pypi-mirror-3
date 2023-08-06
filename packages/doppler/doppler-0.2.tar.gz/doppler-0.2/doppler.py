import os,argparse
from urlparse import urlparse

import psycopg2

parser = argparse.ArgumentParser(description='''Create and apply migrations for
    the python-storm database ORM.
    https://storm.canonical.com
    ''')
parser.add_argument("-f","--folder",default="migrations")
parser.add_argument("-db","--database",default=os.environ.get("DATABASE_URL"))

subparsers = parser.add_subparsers(help="sub-command help",dest="action")

generate_parser = subparsers.add_parser("generate")
generate_parser.add_argument("name")

migrate_parser = subparsers.add_parser("migrate")
migrate_parser.add_argument("direction",choices=["up","down"])


def find_migrations(folder="migrations"):
    for root,dirs,files in os.walk("./"):
        if folder in dirs:
            return (os.path.join(root,folder),
                filter(lambda filename: os.path.splitext(filename)[1]==".sql",
                os.listdir(os.path.join(root,folder))))

def install(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS _doppler_migration_count (migration_id INTEGER);")
    cursor.execute("SELECT migration_id from _doppler_migration_count LIMIT 1;")
    if cursor.fetchone() == None:
        cursor.execute("INSERT INTO _doppler_migration_count (migration_id) VALUES (0);")

def generate(name,folder,migrations):

    if len(migrations) == 0:
        migration_up = open(os.path.join(folder,"001.{0}.up.sql".format(name)),"a")
        migration_down = open(os.path.join(folder,"001.{0}.down.sql".format(name)),"a")
    else:   
        sorted_migrations = sorted(migrations)
        migration = migrations[-1]
        migration_number = (int(migration[0:3])+1)
        migration_up = open(os.path.join(folder,"%03i.%s.up.sql" % (migration_number,name)),"a")
        migration_down = open(os.path.join(folder,"%03i.%s.down.sql" % (migration_number,name)),"a")
    
    print "Created: {0}".format(migration_up.name)
    print "Created: {0}".format(migration_down.name)

    migration_up.close()
    migration_down.close()

def main():   
    args = parser.parse_args()
    migration_folder, migrations = find_migrations(args.folder)

    if args.action == "generate":
        generate(args.name,migration_folder,migrations)

    elif args.action == "migrate":
        db_params = urlparse(args.database)

        db_connection = psycopg2.connect(
            host=db_params.hostname,
            port=db_params.port,
            user=db_params.username,
            password=db_params.password,
            database=db_params.path[1:]
        )
        db_cursor = db_connection.cursor()

        install(db_cursor)
        db_connection.commit()

        ups = filter(lambda mig: os.path.splitext(os.path.splitext(mig)[0])[1]==".up",migrations)
        downs =  filter(lambda mig: os.path.splitext(os.path.splitext(mig)[0])[1]==".down",migrations)

        migrations = ups if args.direction=="up" else reversed(downs)

        db_cursor.execute("select migration_id from _doppler_migration_count LIMIT 1;")
        migration_id = db_cursor.fetchone()[0]

        for migration in migrations:
            count = int(migration[0:3])
            if ((args.direction == "up" and count <= migration_id) or
                (args.direction == "down" and count > migration_id)):
                continue

            try:
                with open(os.path.join(migration_folder,migration),"r") as mig:
                    db_cursor.execute(mig.read())
                db_cursor.execute("UPDATE _doppler_migration_count SET migration_id={0};".format(count))
            except Exception as e:
                print e
                print "Migration failed, rolling back..."
                db_connection.rollback()

            if count == 1 and args.direction == "down":
                db_cursor.execute("UPDATE _doppler_migration_count SET migration_id=0;")


        db_connection.commit()

        db_cursor.close()
        db_connection.close()


if __name__ == "__main__":
    main()

