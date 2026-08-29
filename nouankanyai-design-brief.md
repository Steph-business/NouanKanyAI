# NouanKanyAI — Brief de design system pour Claude Design

À attacher avec `nouankanyai-landing.html` dans un nouveau projet Claude Design.
Premier message suggéré à coller dans Claude Design : voir tout en bas de ce document.

---

## 1. Contexte produit (ne pas inventer au-delà de ça)

NouanKanyAI est une plateforme logicielle (pas encore IoT) de prédiction et de maîtrise de
la consommation électrique, pour ménages, PME et industries en Côte d'Ivoire. MVP en
développement actif, zéro capteur physique déployé à ce jour, modèles ML entraînés sur
données synthétiques. Née du Global AI Hackathon 2026, équipe issue du programme
FORPRODE IA (Tech Talent Accelerator, GIZ).

Principe produit non négociable : **une donnée est mesurée, estimée, ou synthétique,
jamais inventée.** Toute nouvelle page ou composant doit respecter ce principe, y compris
dans le copywriting (pas de faux chiffres, pas de faux témoignages).

## 2. Design tokens

### Couleurs
| Rôle | Valeur | Usage |
|---|---|---|
| Fond | `#FAFAF9` | Fond général, froid, pas crème |
| Fond surélevé | `#F1F1EE` | Cartes secondaires, sections alternées |
| Texte principal | `#1C1F1B` | Anthracite chaud, jamais noir pur |
| Texte secondaire | `#55584f` | Sous-titres, légendes (contraste 6.95:1 sur fond, validé AA) |
| Ligne / bordure | `#E2E1DB` | Séparateurs, bordures de carte |
| Accent (coût/tarif) | `#E8590C` | Fonds décoratifs, icônes, jamais en texte sur fond clair |
| Accent texte (CTA) | `#7a2c05` | **Couleur réelle des boutons et rubans**, contraste 9.59:1 validé AA |
| Alerte | `#D6293E` | Réservé exclusivement aux vraies urgences, jamais décoratif |
| Confirmation / économies | `#1B7A43` | Validations, économies réalisées, badge "mesuré" |
| Badge "estimé" | `#7a5b0d` sur `#f7efd8` | Contraste 5.49:1, corrigé après audit (l'ambre initial échouait AA) |

Interdits explicites : fond crème + terracotta pastel, fond near-black + accent néon,
gradients décoratifs, blobs de fond.

### Typographie
- Titres : **Space Grotesk** (500/600/700)
- Corps de texte : **Inter** (400/500/600)
- Chiffres (FCFA, kWh, données tabulaires) : **IBM Plex Mono** (500/600), toujours en
  `font-variant-numeric: tabular-nums`

### Rayons de bordure
- Composants standards : `10px`
- Cartes segment/pricing (hiérarchie supérieure) : `14-16px`

### Correctifs d'accessibilité (déjà appliqués dans le HTML attaché, à ne pas régresser)
- Boutons et rubans : texte blanc sur `#7a2c05`, jamais sur `#E8590C` directement.
- Cibles tactiles boutons : padding vertical 13px minimum (hauteur réelle ~44px).
- Aucun `<img>` avec `src=""` vide : soit une vraie image, soit pas d'attribut `src`.

## 3. Signature visuelle (ce qui différencie ce produit)

1. **Barre de paliers tarifaires CIE** : segments heures creuses / heures pleines / heures
   de pointe, visualisés en barre horizontale colorée. Élément récurrent, pas décoratif.
2. **Badge de provenance de donnée** : `mesuré` (vert) / `estimé` (ambre) / `synthétique`
   (gris neutre), sur toute donnée affichée. C'est l'expression visuelle de l'honnêteté
   produit, à garder sur toutes les pages, y compris le futur dashboard.
3. **Sélecteur de niveau** (`débutant` / `amateur` / `technique`) : pills visibles sur les
   cartes de segment utilisateur, suggéré automatiquement selon le profil, modifiable
   manuellement.

## 4. Règles de copywriting

- Pas de tiret cadratin (—) dans le corps de texte. Phrases courtes, points, virgules.
- Pas de badge pilule arrondi au-dessus des titres (pattern template SaaS générique).
- Pas de promesse générique "IA / temps réel / rentabilité maximale" sans ancrage concret.
- Toute accroche doit décrire une action réelle du produit (ex : upload facture → OCR →
  prédiction → recommandation), pas une promesse abstraite.
- Pas de témoignages fabriqués : le produit n'a pas encore d'utilisateurs réels payants.
  Utiliser une section "bientôt disponible" / capture email à la place.

## 5. Photos réelles à intégrer (actuellement en placeholder dans le HTML)

Chercher chaque `<!-- PHOTO : ... -->` dans le fichier HTML attaché. Liste complète :

1. Main tenant un smartphone photographiant une facture CIE papier, gros plan
2. Compteur électrique CIE réel, cadrage serré, contexte ivoirien reconnaissable
3. Devanture ou intérieur de petit commerce à Abidjan (boulangerie, salon, boutique)
4. Intérieur de foyer ivoirien, salon ou cuisine, ambiance quotidienne
5. Gérant(e) de PME en activité dans son commerce
6. Technicien devant un tableau électrique industriel
7. Équipe fondatrice au travail, ou photo du hackathon FORPRODE

Aucune de ces photos ne doit être un stock générique (bureau open-space, poignée de main,
sourire face caméra) : privilégier du réel local, quitte à les prendre soi-même au
téléphone.

## 6. Structure de la page (ordre actuel, à challenger si besoin)

1. Nav (sticky, avec ancre vers chaque section)
2. Hero (accroche action réelle + carte de paliers tarifaires)
3. Preuve visuelle (3 photos)
4. Le constat (3 stats chiffrées du business plan)
5. Pour qui (3 cartes segment avec photo + sélecteur de niveau)
6. Qui sommes-nous
7. Notre engagement (badge de provenance expliqué)
8. Formules (pricing, 3 tiers, ruban sur le tier central)
9. Newsletter (capture email, pas de témoignages fabriqués)
10. Footer (Produit / Entreprise / Légal, CGU et politique de confidentialité en attente
    de rédaction juridique séparée)

---

## 7. Spécification du dashboard (à concevoir, aucune maquette existante)

Basé sur le Plan Opérationnel et la Vision Produit fournis, pas d'invention au-delà.

### 7.1 Principe transversal
Un seul design system pour les trois profils (ménage, PME, industrie) et l'admin.
Ce qui change entre profils : le contenu affiché et l'ordre de priorité, jamais les
composants ou les couleurs. Chaque profil a un niveau par défaut suggéré (débutant /
amateur / technique), modifiable par l'utilisateur à tout moment depuis le dashboard
(pas seulement à l'onboarding).

### 7.2 Hiérarchie de l'information (ordre non négociable)
1. **Alerte active** en premier, visuellement dominante. Ce n'est pas un badge discret
   en haut de page : c'est le pilier central du produit (confirmé par l'utilisateur).
   Distinction visuelle claire entre alerte nécessitant une action humaine (surchauffe,
   anomalie majeure) et action à faible risque déjà auto-exécutée (délestage préventif,
   journalisé). Ne jamais mélanger les deux registres visuellement.
2. **KPI de consommation/coût** ensuite (FCFA, kWh, tendance).
3. **Prédiction IA** en dernier, toujours accompagnée du badge de provenance
   (mesuré / estimé / synthétique).

### 7.3 Pages à concevoir

**Dashboard Ménage** (niveau par défaut : débutant)
- 1 seuil global de consommation, alerte simple si dépassement
- Prédiction hebdomadaire avec badge de provenance
- Conseils génériques classés par impact
- Historique 30 jours (formule Essentiel) ou quotidien (Intelligent)
- Assistant conversationnel accessible en widget (chat contextualisé par équipements)
- Upload facture CIE par photo (OCR) avec aperçu de l'extraction

**Dashboard PME** (niveau par défaut : amateur)
- Seuils par appareil, pas seulement global
- Rapport hebdomadaire exploitable sans expertise technique
- Conseils priorisés par impact sur la marge
- Vue équipements : catégorie, marque, modèle, site, priorité, statut opérationnel
- Upload facture + analyse média équipement (photo/vidéo d'une machine)

**Dashboard Industrie** (niveau par défaut : technique)
- Alertes multi-niveaux (avertissement 70 %, critique 90 %, urgence 100 %)
- Détection d'anomalie (Isolation Forest) avec score de sévérité affiché
- Métadonnées machine complètes : température, vibration, pression, statut, priorité
- Plan d'action mensuel chiffré
- Historisation des résolutions d'anomalies (ce qui a résolu une alerte passée)

**Portail Admin**
- Statut base de données, uptime processus, latence API moyenne (fenêtre glissante,
  avec compteur d'échantillons visible, jamais une moyenne seule)
- Métriques XGBoost réelles (R², MAE, MAPE) avec mention explicite `dataset: synthetic`
- Compteur d'anomalies détectées (Isolation Forest)
- Observabilité Gemini : appels réels, cache hits, saturations, mode mock
- Journal d'activité agrégé (connexions, uploads, analyses média, délestages, resets)
- Rendu "dégradé" explicite en cas de panne partielle : jamais un écran d'erreur global,
  chaque métrique indisponible affiche son propre état "indisponible"

### 7.4 Composants transverses à réutiliser partout
- Badge de provenance (déjà défini section 3)
- Carte alerte (avec les deux registres : action requise vs auto-exécutée)
- Sélecteur de niveau (pills débutant/amateur/technique)
- Widget assistant conversationnel (accessible depuis toutes les pages utilisateur)

### 7.5 Ce qu'il ne faut pas faire
- Ne pas présenter de données IoT temps réel comme si les capteurs étaient déjà
  déployés : ils ne le sont pas encore (voir section 1). Toute donnée doit porter son
  badge de provenance, y compris dans le dashboard.
- Ne pas fusionner les alertes "action requise" et "action déjà automatisée" dans la
  même liste sans distinction visuelle claire.
- Ne pas dupliquer un design différent par profil : un seul système, un contenu qui
  change.

---

## Premier message à coller dans Claude Design

```
Voici le design system et le brief de contenu d'un projet existant (NouanKanyAI), avec
le fichier HTML de la landing page en pièce jointe comme référence de style.

Étape 1 : reconstruis/itère la landing page à partir de cette base. Respecte les tokens
de couleur et typographie du brief à la lettre (les correctifs d'accessibilité sont déjà
appliqués dans le HTML, ne les régresse pas). Respecte les règles de copywriting en
section 4 (pas de tiret cadratin, pas de badge pilule, pas de témoignage fabriqué). Ne
change pas la signature visuelle (barre de paliers, badge de provenance, sélecteur de
niveau) sans me le signaler d'abord.

Étape 2 : conçois ensuite la maquette complète du dashboard, à partir de la section 7 du
brief (spécification dashboard). Quatre vues à produire : Ménage, PME, Industrie, Portail
Admin. Un seul design system pour les quatre, le contenu et l'ordre de priorité changent
selon le profil, jamais les composants. Respecte strictement la hiérarchie de l'information
en 7.2 : l'alerte active passe toujours avant les KPI, qui passent toujours avant la
prédiction IA. Chaque donnée affichée doit porter son badge de provenance
(mesuré/estimé/synthétique) : aucune donnée n'est présentée comme mesurée en temps réel
puisque les capteurs IoT ne sont pas encore déployés.

Montre-moi d'abord un plan des composants et de la hiérarchie de chaque vue avant de
passer au visuel détaillé, pour qu'on valide la structure ensemble en premier.
```

