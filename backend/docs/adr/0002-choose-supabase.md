# ADR 0002 : Conserver Supabase comme adaptateur de persistance

## Statut

Accepté — 2026-09-30

## Contexte

Le backend existant utilise déjà Supabase pour les organisations, sites, machines, mesures, factures et journaux. Remplacer le stockage pendant le refactoring augmenterait le risque de régression et imposerait une migration des données sans bénéfice immédiat pour les contrats clients.

## Décision

Conserver Supabase comme fournisseur concret derrière les dépôts `MachineRepository` et `ReadingRepository`. La création du client se fait dans le container à partir de la configuration centralisée. Les environnements locaux sans identifiants utilisent les dépôts de démonstration.

## Conséquences

- ✅ Les schémas de persistance et données existants restent en place.
- ✅ Les use cases peuvent être testés via de faux dépôts.
- ⚠️ Le SDK Python est synchrone; les adaptateurs déplacent ses appels hors de la boucle asynchrone.
- ⚠️ Les tables et colonnes restent couplées à l'adaptateur jusqu'à la conversion vers les entités métier.
- 📝 Vérifier les correspondances de clés et les schémas Supabase en intégration réelle.
