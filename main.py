import os
from database import init_database
from lures import create_lures

def main():
    if os.path.exists('LURE.db'):
        print("Load database...")
    else:
        print("Initializing database...")
        init_database()
    create_lures()


if __name__ == "__main__":
    main()
