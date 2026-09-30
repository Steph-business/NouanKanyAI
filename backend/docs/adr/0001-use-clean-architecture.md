# ADR 0001 : Adopter une architecture en couches

## Statut

Accepté — 2026-09-30

## Contexte

Le backend a grandi autour de `main.py`, des routeurs HTTP et de modules AI/ML transverses. Cette organisation mélangeait protocoles, règles métier, accès externes et configuration, ce qui rendait les composants difficiles à remplacer et à tester isolément. La compatibilité avec l'API et le frontend impose une migration progressive.

## Décision

Organiser les nouveaux composants selon quatre couches : `domain`, `application`, `infrastructure` et `presentation`. Les dépendances métier pointent vers l'intérieur : Presentation appelle Application, Infrastructure implémente ses ports, et Application dépend de Domain. Les contrats HTTP existants restent stables durant la migration.

Les routes historiques sont conservées temporairement dans `presentation/legacy_app.py`, et des modules de compatibilité gardent les anciens chemins d'import Python.

## Conséquences

- ✅ Les règles métier et use cases peuvent être testés sans FastAPI ni fournisseur externe.
- ✅ Les adaptateurs ML, LLM, Supabase et rapports ont des ports remplaçables.
- ⚠️ Le backend n'est pas entièrement migré : les handlers legacy gardent encore des accès directs.
- ⚠️ Des contrats et adaptateurs doivent être raccordés avant de retirer les chemins de compatibilité.
