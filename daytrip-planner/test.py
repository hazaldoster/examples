from dotenv import load_dotenv
from location_validator import validate_city

load_dotenv()


if __name__ == "__main__":
    print(validate_city("Madrid"))
