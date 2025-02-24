from website.models import BonusTransaction, User
from website.extensions import db

class BonusService:
    @staticmethod
    def add_bonus(user_id, amount, transaction_type):
        user = User.query.get(user_id)
        if not user:
            return None, "Пользователь не найден"
        if transaction_type == 'debit' and user.bonus_balance < amount:
            return None, "Недостаточно бонусов"
        bonus_transaction = BonusTransaction(user_id=user_id, amount=amount, type=transaction_type)
        db.session.add(bonus_transaction)
        user.bonus_balance += amount if transaction_type == 'credit' else -amount
        db.session.commit()
        return bonus_transaction, None