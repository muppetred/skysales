# Pricing : construire le prix du deck depuis le scope R1

Méthode portée depuis l'agent de pricing interne de l'agence (déployé sur Dust).
Elle remplace l'ancienne doctrine « le prix est une donnée fournie par le lead ».
Le prix se **calcule** à partir du scope convenu au R1. Le commercial garde la main
sur le geste final.

Ce fichier décrit la méthode et le format attendu de la grille tarifaire. La grille
elle-même (taux horaires, temps par livrable, seuils, forfaits) n'est pas publiée :
elle se paramètre.

---

## 1. Le principe

- **Interne** : time-based, `heures × taux horaire`. **Jamais visible par le client.**
- **Externe** : package-based, un volume de livrables et deux montants. C'est ce que voit le client.

Appliquer la marge indiquée dans la grille. Si elle vaut 1, les taux horaires sont
directement des taux de facturation : ne pas remultiplier.

---

## 2. La source : lue à chaque run, sans exception

**Grille tarifaire de l'agence** : `<GRILLE_TARIFAIRE>` (un tableur, lu par le connecteur
Google Drive).

| Onglet | Ce qu'il contient |
|---|---|
| `Admin_Rates` | Taux horaire par profil, et marge. Les seules valeurs qui font foi. |
| `DB_Livrables` | Chaque livrable : temps par profil (minutes), taille S/M/L, tag, unité, fréquence, business units concernées, commentaire de calcul |
| `COMPLEXITY COEFF` | Critères, poids et bornes du coefficient de complexité |
| `IMAGE RIGHTS` | Critères, poids et bornes du coefficient droits à l'image |
| `LOGIC_EXAMPLE_*` | Des calculs complets de bout en bout, un par type d'offre, à lire en cas de doute |

> **Règle dure :** ne jamais utiliser un temps, un taux ou un poids mémorisé. Les valeurs
> changent. Aucune n'est recopiée dans ce fichier, exprès : il est impossible de calculer
> sans avoir lu la grille.

La colonne `Comment` de `DB_Livrables` porte la règle de multiplication de chaque ligne
(par profil, par vidéo, par action, par langue). Elle prime sur toute intuition.

---

## 3. Ce qu'il faut avoir avant de calculer

À récupérer du compte rendu R1, ou à chercher en Phase 2 si absent.

**Commun** : type d'offre (community management, Studio, podcast, influence, upsell, Ads),
client nouveau ou existant (onboarding inclus ou non), nombre de langues.

**Community management** : volume par plateforme (vidéos et statiques), nombre de
community managers et de social media managers, services spécifiques (modération active,
créative, reporting, réunions supplémentaires, media buying), critères de complexité,
critères de droits à l'image.

**Studio** : volume de vidéos, nombre de content producers, add-on stratégie oui ou non,
reporting oui ou non, critères de complexité, critères de droits.

**Ads** : budget media mensuel, nombre de channels, Lead Gen ou eCom, coût de tracking
(refacturé au coût exact), setup des accès oui ou non.

**Critères de complexité à faire trancher** (poids dans la grille) : contexte client,
distance des shootings, type de vidéos, qualité attendue, autonomie attendue, short notice
fréquent, nombre de langues. Les shootings hors heures de bureau ne touchent pas le
coefficient : ils majorent le taux horaire sur ces seules heures.

**Critères de droits à l'image** : talent face-cam fourni par l'agence, réutilisation en
paid, sur d'autres réseaux, sur le site web, ailleurs (TV, affichage), durée des droits,
exclusivité sectorielle **ou** totale (mutuellement exclusives).

---

## 4. La méthode

### 4.1 Taille client, avant tout calcul

Trois tailles, S, M et L. Pour les offres de contenu, on compte les livrables équivalents
par mois (1 vidéo = 1, 1 statique = 0,5). Pour les Ads, on regarde le budget media mensuel.

```
≤ <SEUIL_S>  → S
≤ <SEUIL_M>  → M
au-delà      → L
```

### 4.2 Coefficients

`Complexité = 1 + Σ poids` et `Droits = 1 + Σ %`, chacun borné selon la grille.
Les Ads ont leur propre grille (channels et type de campagne) et **pas** de coefficient droits.

La complexité multiplie les **heures** : elle impacte le prix et le capacity management.
Les droits multiplient le **prix total**, jamais une tâche isolée, et ne touchent pas aux heures.

Le coefficient de complexité ne s'applique qu'aux tâches listées dans l'onglet
`COMPLEXITY COEFF`. Pour Studio il s'applique à toutes les tâches, sauf le forfait fixe de
l'add-on stratégie, qui s'ajoute tel quel.

### 4.3 Prix

```
Coût tâche          = (Σ temps profil × taux horaire × coef_complexité si applicable) / 60
Contenu et Studio   : Prix = Σ Coûts × coef_droits
Ads                 : Prix = Σ Coûts   (tracking et frais sur budget media ajoutés hors coef)
```

Arrondir les heures de capacity vers le haut, à la demi-heure (10,2 h donne 10 h 30).
Media buying : forfait proportionnel au budget, sans coefficient.
Shooting événementiel : compter le temps réel (2 personnes sur 4 h font 8 h), pas la formule par vidéo.

### 4.4 Vérifications avant de sortir un chiffre

Taille calculée avec le bon critère. Temps issus de la grille lue pendant ce run.
Coefficient justifiable en une phrase. Modération active comptée par langue. One-shot et
récurrent distingués. Forfait de l'add-on stratégie hors coefficient. Ads : tracking et
frais sur budget hors coefficients.

---

## 5. Où ça atterrit dans le deck

Le calcul produit **un one-shot et un récurrent** : c'est la structure des deux dernières
pages de P2.

| Sortie du calcul | Page | Zone |
|---|---|---|
| One-shot | Prix | Mise en place, et son montant |
| Récurrent mensuel | Prix | Pack mensuel, et son montant par mois |
| Livrables retenus | Scope | La liste des inclus |
| Livrables écartés faute de budget | Scope | La colonne des options |

La page scope et la page prix décrivent **le même périmètre**. Un livrable facturé absent
du scope, ou un livrable au scope absent du calcul, est une incohérence bloquante : c'est
le premier endroit où un prospect attentif attrape une offre bâclée.

**Toute ligne ajoutée au scope en cours de run repasse par le calcul.** Cas typique : le
commercial demande exceptionnellement de raccourcir un deck, et du contenu d'une slide
retirée est rapatrié dans le scope. Le squelette du master reste la norme ; ce retrait est
une demande ponctuelle, jamais un défaut. Une simple mention de disponibilité
(« conversations 5/7 ») peut déclencher une tâche forfaitaire et faire passer le mensuel
annoncé sous le plancher de la grille.

Arrondir les lignes visibles au client au 50 € le plus proche. Le **total** reste le prix
exact calculé, jamais la somme des lignes arrondies.

---

## 6. Garde-fous

❌ **Jamais dans le deck client** : taux horaires, heures, capacity par profil,
coefficients, libellés internes des tâches de la grille. Le client voit des livrables et
deux montants.

❌ **Jamais de prix au doigt mouillé.** Trois cas :
- tous les paramètres sont là : calcul complet ;
- des critères manquent (complexité, droits, nombre de profils) : calculer un **plancher**
  en prenant chaque critère manquant à sa valeur la plus basse, marquer **Tarif de départ**,
  et lister les hypothèses dans le rapport de livraison ;
- le type d'offre ou les volumes manquent : le calcul est impossible, le montant reste
  `X,XXX €` avec un `TODO` explicite, comme toute autre donnée absente (règle 3).

❌ **Jamais de durée d'engagement chiffrée dans le deck** (position du lead). Le prix
mensuel est l'unité de vente. Annoncer soi-même le total annualisé transforme une dépense
mensuelle qu'un dirigeant arbitre seul en un investissement qui demande réflexion. La
mention des droits d'usage « pour la durée du contrat » est neutre et se garde.

✅ **Un ajustement commercial reste possible** sur le prix final. Le calcul donne le
plancher rentable et la structure ; le commercial garde la main sur le geste.

---

## 7. Vocabulaire

`P1 = R1` (premier rendez-vous, découverte, où le scope se discute) ;
`P2 = R2` (deuxième rendez-vous, où l'offre chiffrée se présente).
Le scope qui alimente ce calcul vient du **R1**.
