import uuid

from yookassa import Configuration, Payment


class YooKassaHelper:

    def __init__(self, account_id: str, secret_key: str):
        self.account_id = account_id
        self.secret_key = secret_key
        Configuration.account_id = self.account_id
        Configuration.secret_key = self.secret_key

    @staticmethod
    async def create_payment(telegram_user_id: int, amount: float, payment_id):
        payment = Payment.create({
            "amount": {
                "value": f"{amount}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://www.google.com/"
            },
            "capture": True,
            "description": f"Заказ пользователя {telegram_user_id}"
        }, payment_id)

        return payment