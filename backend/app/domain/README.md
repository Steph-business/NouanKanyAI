# Couche Domain

## Rôle

Le domaine porte les règles métier stables de NouanKanyAI : machines, mesures, énergie, factures, tarifs et événements. Il reste indépendant des frameworks et des détails de stockage.

## Ce qu'on peut y mettre

- Entités immuables qui possèdent une identité et des invariants métier.
- Objets valeur validés et comparés par leur valeur.
- Événements métier et exceptions métier.
- Interfaces abstraites de dépôts dont les use cases ont besoin.
- Règles de calcul exprimées en types Python standard.

## Ce qu'on ne doit jamais y mettre

- Pydantic, FastAPI, SQLAlchemy ou Supabase.
- XGBoost, scikit-learn, clients HTTP ou accès au système de fichiers.
- Statuts HTTP, formats JSON d'API, variables d'environnement ou détails d'interface.
- Imports depuis `application`, `infrastructure` ou `presentation`.

## Exemples

### Vérifier une puissance admissible

```python
machine = Machine(MachineId("POMPE-01"), "Pompe", "Atelier A", 120.0)
assert machine.can_consume(90.0)
assert machine.is_overloaded(110.0)
```

### Utiliser les objets valeur

```python
energy = Kwh("125.5")
cost = Money("8540", "FCFA")
tier = TariffTier.for_consumption(energy.value)
```

### Dépendre d'un dépôt sans connaître son adaptateur

```python
class MachineRepository(ABC):
    async def get_by_id(self, machine_id: MachineId) -> Machine | None: ...
```

## Erreurs courantes

- Importer un schéma Pydantic directement dans une entité.
- Retourner un `HTTPException` depuis une règle métier.
- Mélanger un identifiant primitif et un `MachineId` dans les signatures.
- Représenter les montants financiers par `float` lorsque `Decimal` convient.
- Faire dépendre un dépôt abstrait d'un fournisseur concret de base de données.

## Contenu actuel

- `entities/` : `Machine`, `SensorReading`, `EnergyConsumption`, `Invoice`.
- `value_objects/` : `MachineId`, `Money`, `Kwh`, `TariffTier`.
- `events/` : `AnomalyDetected`, `ThresholdExceeded`.
- `exceptions/` : erreurs métier indépendantes du transport.
- `repositories/` : interfaces abstraites asynchrones machine et relevés.
