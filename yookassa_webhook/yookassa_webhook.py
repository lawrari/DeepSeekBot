from fastapi import FastAPI, Request, HTTPException
from yookassa.domain.notification import WebhookNotification
from contextlib import asynccontextmanager
from services.database.database_utils import DatabaseUtils
from config.config import load_config
from services.database.repo.requests import RequestsRepo
import traceback


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config(".env")
    DatabaseUtils.initialize(config.db)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def my_webhook_handler(request: Request):
    try:
        event_json = await request.json()
        notification_object = WebhookNotification(event_json)
        payment = notification_object.object
        print(f"id of returned payment {payment.id}")
        
        # Example of using the database session
        if payment.status == 'succeeded':
            async with DatabaseUtils.get_session() as session:
                repo = RequestsRepo(session)
                db_payment = await repo.payments.change_status(
                    payment_id=payment.id,
                    status='succeeded'
                )
                await repo.profiles.add_requests(
                    profile_id=db_payment.payer.profile_id,
                    requests_amount=db_payment.subscription.requests_amount,
                    image_requests_amount=db_payment.subscription.image_requests_amount
                )
            
        print(db_payment.payment_id)
        return {"status": "success"}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))
    