from app import db
from app.models import *

def main():
    db.create_all()
    print("All tables created!")

if __name__ == "__main__":
    main() 