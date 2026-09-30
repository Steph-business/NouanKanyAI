# Couche Application

## Rôle

Cette couche décrit les actions que la plateforme sait réaliser. Un use case valide une commande, charge les objets domaine nécessaires, appelle des ports et retourne un résultat indépendant du transport HTTP.

## Ce qu'on peut y mettre

- Use cases avec une méthode `execute(command)`.
- DTO immuables d'entrée et de sortie.
- Ports abstraits (ABC) pour ML, LLM, notification, rapports ou persistance.
- Services d'orchestration et de politique applicative.

## Ce qu'on ne doit jamais y mettre

- FastAPI, Pydantic, codes HTTP ou schémas OpenAPI.
- Clients Supabase, SDK Gemini, modèles XGBoost ou accès disque.
- Lecture de variables d'environnement.
- Dépendances vers `presentation/` ou `infrastructure/`.

## Exemples

### Prévoir une machine

```python
result = await use_case.execute(PredictConsumptionCommand("POMPE-01", 24))
print(result.model_version, result.predictions)
```

### Calculer une estimation tarifaire

```python
invoice = await CalculateInvoiceUseCase().execute(CalculateInvoiceCommand(Decimal("600")))
print(invoice.tariff.band, invoice.total.amount)
```

### Substituer le port ML en test

```python
class FakeMLService(MLService):
    @property
    def version(self) -> str:
        return "fake-1"

    async def forecast(self, machine_id: str, horizon_hours: int) -> ForecastResult:
        return ForecastResult([10.0] * horizon_hours, 9.0, 11.0)
```

## Erreurs courantes

- Laisser une route HTTP décider elle-même des règles tarifaires.
- Importer un adaptateur concret au lieu de dépendre d'un port.
- Retourner un objet Pydantic depuis un use case.
- Omettre les validations des bornes et des ressources absentes.
- Introduire un `Any` sans documenter la frontière dynamique concernée.

## Use cases et services actuels

- `PredictConsumptionUseCase` : charge et valide une machine avant la prévision.
- `DetectAnomalyUseCase` : charge les relevés puis délègue l'analyse ML.
- `CalculateInvoiceUseCase` : applique le tarif métier de la tranche.
- `GenerateReportUseCase` : valide les formats puis délègue au port de rapport.
- `EnergyOptimizationService` : produit une recommandation à partir d'une surcharge.
