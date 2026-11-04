from checkout_commerce.checkout.checkout_request import CheckoutRequest
from checkout_commerce.checkout.checkout_model import Checkout, CheckoutStatus
from checkout_commerce.infra.database import get_db
from fastapi import Depends, HTTPException


from checkout_commerce.infra.client.payment_client import PaymentClient, get_payment_client
from checkout_commerce.infra.client.inventory_client import InventoryClient, get_inventory_client
from checkout_commerce.infra.client.order_client import OrderClient, get_order_client


async def checkout_process(
    checkout_request: CheckoutRequest,
    db=Depends(get_db),
    inventory_client: InventoryClient = Depends(get_inventory_client),
    payment_client: PaymentClient = Depends(get_payment_client),
    order_client: OrderClient = Depends(get_order_client),
):
    checkout = Checkout(
        customer_email=checkout_request.customer_email,
        total_amount=checkout_request.total_amount,
        status=CheckoutStatus.PENDING.value,
    )

    db.add(checkout)
    await db.commit()
    await db.refresh(checkout)


    payment_response = await payment_client.process_payment(
        total_amount=checkout_request.total_amount,
        payment_method=checkout_request.payment_method,
        customer_email=checkout_request.customer_email,
    )


    if payment_response["error"]:
        checkout.status = CheckoutStatus.FAILED.value
        checkout.error = payment_response["error"]
        await db.commit()
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Payment processing failed",
                "message": payment_response["error"],
                "checkout_id": checkout.id,
            }
        )



    checkout.payment_id = payment_response["transaction_id"]


    inventory_response = await inventory_client.deduct(
        items=checkout_request.items,
    )


    if inventory_response["error"]:
        checkout.status = CheckoutStatus.FAILED.value
        checkout.error = inventory_response["error"]
        await db.commit()
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Inventory deduction failed",
                "message": inventory_response["error"],
                "checkout_id": checkout.id,
            }
        )


    order_response = await order_client.create(
        checkout_id=str(checkout.id),
        customer_email=checkout_request.customer_email,
        shipping_address=checkout_request.shipping_address,
        items=checkout_request.items,
    )


    if order_response["error"]:
        checkout.status = CheckoutStatus.FAILED.value
        checkout.error = order_response["error"]
        await db.commit()
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Order creation failed",
                "message": order_response["error"],
                "checkout_id": checkout.id,
            }
        )



    checkout.order_id = order_response["order_id"]
    checkout.status = CheckoutStatus.SUCCESS.value
    await db.commit()


    return {
        "checkout_id": checkout.id,
        "error": None,
    }

    

