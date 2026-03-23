from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# -------------------------------
# Preloaded Data
# -------------------------------
cars = [
    {"id": 1, "name": "Swift", "brand": "Maruti", "price_per_day": 40, "available": True},
    {"id": 2, "name": "i20", "brand": "Hyundai", "price_per_day": 50, "available": True},
    {"id": 3, "name": "City", "brand": "Honda", "price_per_day": 70, "available": True},
    {"id": 4, "name": "Fortuner", "brand": "Toyota", "price_per_day": 120, "available": True},
    {"id": 5, "name": "XUV700", "brand": "Mahindra", "price_per_day": 100, "available": True},
    {"id": 6, "name": "Verna", "brand": "Hyundai", "price_per_day": 65, "available": True},
    {"id": 7, "name": "Baleno", "brand": "Maruti", "price_per_day": 45, "available": True}
]

customers = [
    {"id": 1, "name": "Rahul", "email": "rahul@gmail.com"},
    {"id": 2, "name": "Priya", "email": "priya@gmail.com"}
]

bookings = []

# -------------------------------
# Models
# -------------------------------
class Car(BaseModel):
    id: int
    name: str = Field(..., min_length=2)
    brand: str
    price_per_day: float
    available: bool = True

class Customer(BaseModel):
    id: int
    name: str
    email: str

class Booking(BaseModel):
    id: int
    car_id: int
    customer_id: int
    days: int = Field(..., gt=0)
    status: str = "booked"

# -------------------------------
# Helper Functions
# -------------------------------
def find_car(car_id: int):
    return next((car for car in cars if car["id"] == car_id), None)

def find_customer(customer_id: int):
    return next((c for c in customers if c["id"] == customer_id), None)

def find_booking(booking_id: int):
    return next((b for b in bookings if b["id"] == booking_id), None)

def calculate_total(price: float, days: int):
    return price * days

# -------------------------------
# Day 1 - GET APIs
# -------------------------------
@app.get("/")
def home():
    return {"message": "Car Rental API Running 🚗"}

@app.get("/cars")
def get_all_cars():
    return cars

@app.get("/cars/count")
def get_car_count():
    return {"total_cars": len(cars)}

@app.get("/cars/available")
def get_available_cars():
    return [car for car in cars if car["available"]]

# -------------------------------
# Day 6 - Advanced APIs (FIXED ORDER)
# -------------------------------
@app.get("/cars/search")
def search_cars(
    brand: Optional[str] = Query(None),
    max_price: Optional[float] = Query(None)
):
    results = cars

    if brand is not None:
        results = [c for c in results if c["brand"].lower() == brand.lower()]

    if max_price is not None:
        results = [c for c in results if c["price_per_day"] <= max_price]

    return results

@app.get("/cars/sort")
def sort_cars(order: str = Query("asc")):
    reverse = True if order == "desc" else False
    return sorted(cars, key=lambda x: x["price_per_day"], reverse=reverse)

@app.get("/cars/page")
def paginate_cars(limit: int = 5, skip: int = 0):
    return cars[skip: skip + limit]

@app.get("/cars/browse")
def browse_cars(
    brand: Optional[str] = None,
    max_price: Optional[float] = None,
    sort_order: Optional[str] = "asc",
    limit: int = 5,
    skip: int = 0
):
    results = cars

    if brand:
        results = [c for c in results if c["brand"].lower() == brand.lower()]

    if max_price:
        results = [c for c in results if c["price_per_day"] <= max_price]

    reverse = True if sort_order == "desc" else False
    results = sorted(results, key=lambda x: x["price_per_day"], reverse=reverse)

    return results[skip: skip + limit]

# -------------------------------
# Dynamic Route (MUST BE LAST)
# -------------------------------
@app.get("/cars/{car_id}")
def get_car_by_id(car_id: int):
    car = find_car(car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    return car

# -------------------------------
# Day 2 - POST + Validation
# -------------------------------
@app.post("/cars", status_code=201)
def add_car(car: Car):
    if find_car(car.id):
        raise HTTPException(400, "Car ID already exists")
    cars.append(car.dict())
    return car

@app.post("/customers", status_code=201)
def add_customer(customer: Customer):
    if find_customer(customer.id):
        raise HTTPException(400, "Customer already exists")
    customers.append(customer.dict())
    return customer

# -------------------------------
# Customer APIs
# -------------------------------
@app.get("/customers")
def get_customers():
    return customers

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    customer = find_customer(customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")
    return customer

# -------------------------------
# Day 4 - CRUD Operations
# -------------------------------
@app.put("/cars/{car_id}")
def update_car(car_id: int, updated_car: Car):
    car = find_car(car_id)
    if not car:
        raise HTTPException(404, "Car not found")

    car.update(updated_car.dict())
    return car

@app.delete("/cars/{car_id}")
def delete_car(car_id: int):
    car = find_car(car_id)
    if not car:
        raise HTTPException(404, "Car not found")

    cars.remove(car)
    return {"message": "Car deleted successfully"}

# -------------------------------
# Day 5 - Multi-Step Workflow
# -------------------------------
@app.post("/bookings", status_code=201)
def create_booking(booking: Booking):
    car = find_car(booking.car_id)
    customer = find_customer(booking.customer_id)

    if not car:
        raise HTTPException(404, "Car not found")
    if not customer:
        raise HTTPException(404, "Customer not found")
    if not car["available"]:
        raise HTTPException(400, "Car not available")

    car["available"] = False
    bookings.append(booking.dict())

    return {"message": "Booking created", "booking": booking}

@app.put("/bookings/{booking_id}/pickup")
def pickup_car(booking_id: int):
    booking = find_booking(booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")

    booking["status"] = "picked"
    return booking

@app.put("/bookings/{booking_id}/return")
def return_car(booking_id: int):
    booking = find_booking(booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")

    car = find_car(booking["car_id"])
    car["available"] = True
    booking["status"] = "returned"

    return {"message": "Car returned successfully"}

@app.get("/bookings")
def get_all_bookings():
    return bookings

@app.get("/bookings/{booking_id}/total")
def calculate_booking_total(booking_id: int):
    booking = find_booking(booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")

    car = find_car(booking["car_id"])
    total = calculate_total(car["price_per_day"], booking["days"])

    return {"total_cost": total}