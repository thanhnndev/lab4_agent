"""Custom mock data for TravelBuddy tools."""

FLIGHTS_DB = {
    ("Ha Noi", "Da Nang"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1450000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1200000, "class": "economy"},
    ],
    ("Ha Noi", "Phu Quoc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2100000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1100000, "class": "economy"},
    ],
    ("Ho Chi Minh", "Da Nang"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1300000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780000, "class": "economy"},
    ],
}

HOTELS_DB = {
    "Da Nang": [
        {"name": "Muong Thanh Luxury", "stars": 5, "price_per_night": 1800000, "area": "My Khe", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1200000, "area": "My Khe", "rating": 4.3},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250000, "area": "Hai Chau", "rating": 4.6},
    ],
    "Phu Quoc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3500000, "area": "Bai Dai", "rating": 4.4},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800000, "area": "Duong Dong", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200000, "area": "Duong Dong", "rating": 4.5},
    ],
    "Ho Chi Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2800000, "area": "District 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1400000, "area": "District 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550000, "area": "District 3", "rating": 4.4},
    ],
}
