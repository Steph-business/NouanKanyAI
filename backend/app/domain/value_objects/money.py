"""Montant monétaire précis exprimé en FCFA par défaut."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """Montant métier non négatif utilisant Decimal pour éviter les erreurs binaires."""

    amount: Decimal
    currency: str = "FCFA"

    def __post_init__(self) -> None:
        amount = Decimal(str(self.amount))
        if not amount.is_finite() or amount < 0:
            raise ValueError("Le montant doit être fini et positif ou nul")
        if not self.currency.strip():
            raise ValueError("La devise ne peut pas être vide")
        object.__setattr__(self, "amount", amount)
        object.__setattr__(self, "currency", self.currency.strip().upper())

    def __add__(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Un montant ne peut pas devenir négatif")
        return Money(result, self.currency)

    def _ensure_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError("Les devises doivent être identiques")
