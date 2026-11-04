from fastapi import APIRouter

from checkout_commerce.checkout.checkout_process import checkout_process


router = APIRouter(prefix="/checkout", tags=["Checkout"])

router.add_api_route(
    "/process",
    endpoint=checkout_process,
    methods=["POST"],
)