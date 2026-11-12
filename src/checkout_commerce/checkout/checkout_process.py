from checkout_commerce.checkout.checkout_request import CheckoutRequest
from checkout_commerce.checkout.checkout_model import Checkout, CheckoutStatus
from checkout_commerce.infra.database import get_db
from fastapi import Depends, HTTPException


from sqlalchemy.ext.asyncio import AsyncSession

from checkout_commerce.infra.kafka_client import KafkaClient, get_kafka_client

async def checkout_process(
    checkout_request: CheckoutRequest,
    db: AsyncSession=Depends(get_db),
    producer: KafkaClient = Depends(get_kafka_client)
):

    total_amount = sum(item.price for item in checkout_request.items)
    checkout = Checkout(
        customer_email=checkout_request.customer_email,
        total_amount=total_amount,
        status=CheckoutStatus.PENDING.value,
    )

    db.add(checkout)
    await db.commit()
    await db.refresh(checkout)


    body = {
        "checkout_id": checkout.id,
        "customer_email": checkout.customer_email,
        "payment_method": checkout_request.payment_method.model_dump()
    }

    await producer.publish(
        topic="checkout.created",
        value=body,
        key=str(checkout.id)
    )



    
    return {
        "checkout_id": checkout.id,
        "status": checkout.status,
    }

    

