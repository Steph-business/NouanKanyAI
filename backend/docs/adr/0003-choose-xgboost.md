# ADR 0003 : Préserver les modèles XGBoost et Isolation Forest

## Statut

Accepté — 2026-09-30

## Contexte

Les pipelines ML entraînés, leurs schémas de caractéristiques, manifestes et model cards sont déjà versionnés et utilisés par les routes d'inférence. Réentraîner ou remplacer les algorithmes au cours du refactoring rendrait les résultats difficiles à comparer et compromettrait l'auditabilité.

## Décision

Garder les artefacts et algorithmes en place. `XGBoostAdapter` et `IsolationForestAdapter` enveloppent le `ModelManager` existant et exposent les ports applicatifs; `CombinedMLAdapter` fournit le port ML commun. Les algorithmes ne sont modifiés que dans une décision distincte accompagnée d'une évaluation de modèle.

## Conséquences

- ✅ Les modèles et artefacts existants ne changent pas pendant le refactoring.
- ✅ Les use cases peuvent substituer un adaptateur ML simulé.
- ⚠️ Le modèle historique prévoit un pas horaire; l'horizon multi-heures est exécuté séquentiellement.
- ⚠️ Les bornes min/max d'une séquence ne constituent pas un intervalle de confiance calibré.
- 📝 Garder les endpoints d'administration et le format détaillé d'inférence sous compatibilité tant qu'ils ne sont pas migrés.
