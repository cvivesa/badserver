# BAD Server
The Blockchain for Allocation and Decentralization Group Website

## Usage
Start the containers with `docker-compose start`

Navigate to [127.0.0.1:8000](http://127.0.0.1:8000/)

Use ```docker-compose exec web python manage.py createsuperuser``` to create an admin account


Use ```docker-compose exec web python manage.py auction``` to auction all spots to highest bids (first admin functions as school)

## Installation
Requires Docker and docker-compose
```bash
git clone https://github.com/PhilipConte/badserver
cd badserver
echo "BAD_DEBUG=1
BAD_SECRET_KEY=super_secure_tm" > .env
docker-compose up -d
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## Shell
You can use ```docker-compose exec web python manage.py shell``` to experiment with queries
I recommend often importing the following
```python
from django.contrib.auth.models import User
from django.utils import timezone
from parking.models import *
```
