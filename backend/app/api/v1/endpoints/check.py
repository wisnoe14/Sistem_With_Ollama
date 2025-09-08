from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.model.customer import Customer

router = APIRouter()

@router.get("/check/{customer_id}")
def check_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {
        "valid": True,
        "customer_id": customer.customer_id,
        "name": customer.name
    }