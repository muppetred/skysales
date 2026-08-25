> ⚠️ **CE DOCUMENT EST PÉRIMÉ — il ne fait plus autorité (constaté le 18/08/2026).**
>
> Il décrit le master `<DESIGN_ID>`, qui est **mort** : `read-design` renvoie `permission_denied`.
> Aucun design vivant ne correspond à cette carte, et son compte de pages (42) ne correspond
> à aucun des candidats survivants (43 pages).
>
> **Ne jamais résoudre une zone depuis ce fichier.** Le skill dérive sa carte du master
> effectivement lu à chaque run (voir `SKILL.md`, section MÉCANIQUE CANVA).
>
> Ce qui reste utile ici : la **structure de P2**, le **vocabulaire des zones** et les
> **budgets caractères**. C'est la meilleure base pour rédiger les placeholders d'un futur
> master neutre — pas pour piloter un run.

# Carte des zones P2 (résolution par placeholder)

Spec sémantique de la partie client (P2) du master Canva. Le skill ne s'appuie plus sur des `element_id` figés (fragiles : ils changent à chaque nouvelle version du template). Il résout chaque zone au runtime par son texte placeholder.

## Principe de résolution (runtime)

Le master est neutralisé : chaque zone éditable porte un placeholder explicite entre crochets, ex `[Diagnostic point 1: one observable fact, kept to two short lines]`. Tout le reste (rail de navigation, numéros `01`-`04`, libellés `Starts from` / `Feeling` / `Where`, titres de phases du Social OS™, timeline kick-off, équipe) est fixe et n'est jamais touché.

Au push, sur la copie fraîche du master :

1. `start-editing-transaction` retourne chaque élément avec son `element_id` et son texte.
2. Pour chaque zone de cette carte, trouver l'élément dont le texte égale le placeholder, et éditer par son `element_id`.
3. Zones sans texte (médias) ou à texte identique (les 4 `XX%`) : départager par position (voir colonne `résolution`).

Avantage : aucune dépendance à des IDs. Le skill marche sur n'importe quelle copie du master, et ne casse pas quand le template est re-versionné, tant que les placeholders restent.

## Master

- Design ID : `<DESIGN_ID>`
- Titre : « SK - Slide Deck Automatisé - Template »
- Lien : https://canva.link/eis3spbw8aedlsj
- 42 pages. P1 (pages 1-22) : boilerplate agence, jamais touché. P2 (pages 23-41) : ci-dessous. Page 42 : outro statique.
- Tout master qui porte ces mêmes placeholders fonctionne. Un template dont les placeholders auraient été renommés demande de mettre à jour cette carte (les textes), pas des IDs.

## Colonnes

| Colonne | Sens |
|---|---|
| `label` | Identifiant sémantique (repère humain) |
| `page` | Numéro de page (1-based) |
| `placeholder` | Texte exact à retrouver dans la copie (l'ancre) |
| `type` | titre / corps / cellule / stat / prix / nom+role / media |
| `budget` | Budget caractères + lignes (mesuré sur le cadre) |
| `cardinalité` | `fixe` / `optionnel` (supprimable) / `repete-N` |
| `donnée` | `oui` si stat ou prix (jamais inventé) |
| `résolution` | Note de départage si pas d'ancre texte unique |

---

## P2

### Page 23 : séparateur (médias optionnels, pas de texte)

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_sep_logo | 23 | (aucun) | media | n/a | optionnel | non | élément image, zone logo |
| p2_sep_visuel | 23 | (aucun) | media | n/a | optionnel | non | élément image/vidéo, visuel principal |

### Page 24 : diagnostic, introduction

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_diag_eyebrow | 24 | `[Diagnosis: the real problem]` | titre | ≈25 car / 1 ligne | fixe | non | ancre texte |
| p2_diag_titre | 24 | `[The real problem, in one short line]` | titre | ≈40 car / 2 lignes | fixe | non | ancre texte |
| p2_diag_point_1 | 24 | `[Diagnostic point 1: one observable fact,kept to two short lines]` | corps | ≈85 car / 2 lignes | repete-4 | non | ancre texte |
| p2_diag_point_2 | 24 | `[Diagnostic point 2: one observable fact,kept to two short lines]` | corps | ≈100 car / 2 lignes | repete-4 | non | ancre texte |
| p2_diag_point_3 | 24 | `[Diagnostic point 3: one observable fact,kept to two short lines]` | corps | ≈90 car / 2 lignes | optionnel | non | ancre texte |
| p2_diag_point_4 | 24 | `[Diagnostic point 4: one observable fact,kept to two short lines]` | corps | ≈85 car / 2 lignes | optionnel | non | ancre texte |
| p2_diag_logo | 24 | (aucun) | media | n/a | optionnel | non | image, zone logo |
| p2_diag_creative | 24 | (aucun) | media | n/a | optionnel | non | vidéo verticale |

Suppression d'un point non utilisé : supprimer l'élément texte + son numéro (`01`-`04`) + sa forme de fond, repérés par position dans le même groupe.

### Page 25 : diagnostic, sector signals (DONNÉES)

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_signals_titre | 25 | `[Sector signals headline]` | titre | ≈45 car / 2 lignes | fixe | non | ancre texte |
| p2_signals_stat_1 | 25 | `XX%` | stat | ≈5 car | fixe | oui | le `XX%` apparié à caption_1 (même quadrant) |
| p2_signals_stat_2 | 25 | `XX%` | stat | ≈5 car | fixe | oui | quadrant de caption_2 |
| p2_signals_stat_3 | 25 | `XX%` | stat | ≈5 car | fixe | oui | quadrant de caption_3 |
| p2_signals_stat_4 | 25 | `XX%` | stat | ≈5 car | optionnel | oui | quadrant de caption_4 |
| p2_signals_caption_1 | 25 | `[Stat 1 caption,sourced]` | corps | ≈60 car / 3 lignes | fixe | oui | ancre texte |
| p2_signals_caption_2 | 25 | `[Stat 2 caption,sourced]` | corps | ≈65 car / 3 lignes | fixe | oui | ancre texte |
| p2_signals_caption_3 | 25 | `[Stat 3 caption,sourced]` | corps | ≈70 car / 3 lignes | fixe | oui | ancre texte |
| p2_signals_caption_4 | 25 | `[Stat 4 caption,sourced]` | corps | ≈75 car / 3 lignes | optionnel | oui | ancre texte |

Les 4 `XX%` ont le même texte : les départager par position, chacun apparié à la légende de son quadrant. Moins de 4 signaux : supprimer le couple stat + caption.

### Page 26 : diagnostic, current state

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_currentstate_titre | 26 | `[Current stateheadline]` | titre | ≈21 car / 2 lignes | fixe | non | ancre texte |
| p2_currentstate_audience | 26 | `[Audience: where the prospect stands today]` | corps | ≈92 car / 3 lignes | fixe | non | ancre texte |
| p2_currentstate_strengths | 26 | `[Strengths: what the prospect already has]` | corps | ≈90 car / 3 lignes | fixe | non | ancre texte |
| p2_currentstate_friction | 26 | `[Friction: what holds the brand back]` | corps | ≈85 car / 3 lignes | fixe | non | ancre texte |
| p2_currentstate_positioning | 26 | `[Positioning: the brand asset, underused]` | corps | ≈96 car / 3 lignes | fixe | non | ancre texte |

Libellés `Audience` / `STRENGTHS` / `Friction` / `POSITIONING` : fixes, non touchés.

### Page 27 : diagnostic, priorities

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_priorities_titre | 27 | `[Three prioritiesto address]` | titre | ≈25 car / 2 lignes | fixe | non | ancre texte |
| p2_priorities_1_titre | 27 | `[Priority 1]` | titre | ≈12 car / 1 ligne | repete-3 | non | colonne gauche |
| p2_priorities_2_titre | 27 | `[Priority 2]` | titre | ≈22 car / 2 lignes | repete-3 | non | colonne centre |
| p2_priorities_3_titre | 27 | `[Priority 3]` | titre | ≈20 car / 2 lignes | repete-3 | non | colonne droite |
| p2_priorities_1_corps | 27 | `[Priority 1:why it matters for the prospect]` | corps | ≈97 car / 5 lignes | repete-3 | non | ancre texte |
| p2_priorities_2_corps | 27 | `[Priority 2:why it matters for the prospect]` | corps | ≈98 car / 6 lignes | repete-3 | non | ancre texte |
| p2_priorities_3_corps | 27 | `[Priority 3:why it matters for the prospect]` | corps | ≈100 car / 6 lignes | repete-3 | non | ancre texte |

### Page 28 : North Star

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_northstar_titre | 28 | `[North Star:turn X into Y]` | titre | ≈20 car / 2 lignes | fixe | non | ancre texte |
| p2_northstar_gap | 28 | `[The gap, in one short line]` | corps | ≈60 car / 1 ligne | fixe | non | ancre texte |
| p2_northstar_from_1 | 28 | `[From: audience voice today]` | corps | ≈22 car | repete-3 | non | 1er `[From...]` (haut) |
| p2_northstar_to_1 | 28 | `[To: audience voice after]` | corps | ≈42 car | repete-3 | non | 1er `[To...]` (haut) |
| p2_northstar_from_2 | 28 | `[From: audience voice today]` | corps | ≈30 car | repete-3 | non | 2e `[From...]` (milieu) |
| p2_northstar_to_2 | 28 | `[To: audience voice after]` | corps | ≈46 car | repete-3 | non | 2e `[To...]` (milieu) |
| p2_northstar_from_3 | 28 | `[From: audience voice today]` | corps | ≈43 car / 2 lignes | repete-3 | non | 3e `[From...]` (bas) |
| p2_northstar_to_3 | 28 | `[To: audience voice after]` | corps | ≈64 car / 2 lignes | repete-3 | non | 3e `[To...]` (bas) |

Les 3 `[From...]` ont le même texte (idem `[To...]`) : départager par position verticale (haut / milieu / bas). Échelle `AWARENESS → RECURRENCE → RELEVANCE → PREFERENCE` : fixe.

### Pages 29-30 : approche, cultural layer (5 phases sur 2 pages)

Titres de phases (`CULTURAL SIGNALS`, `PLATFORM INTELLIGENCE`, `NATIVE CREATION`, `CONTINUOUS PRESENCE`, `AMPLIFICATION`) : FIXES. Seules les descriptions sont éditées.

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_cl_1_corps | 29 | `[Cultural signals: what we listen to]` | corps | ≈56 car / 1 ligne | repete-5 | non | ancre texte |
| p2_cl_2_corps | 29 | `[Platform intelligence approach]` | corps | ≈48 car / 1 ligne | repete-5 | non | ancre texte |
| p2_cl_3_corps | 29 | `[Native creation approach]` | corps | ≈56 car / 1 ligne | repete-5 | non | ancre texte |
| p2_cl_4_corps | 30 | `[Continuous presence approach]` | corps | ≈45 car / 1 ligne | repete-5 | non | ancre texte |
| p2_cl_5_corps | 30 | `[Amplification approach]` | corps | ≈52 car / 1 ligne | repete-5 | non | ancre texte |
| p2_cl_applied_29 | 29 | `applied to [Prospect].` | corps | ≈18 car | fixe | non | remplacer `[Prospect]` par le nom client |
| p2_cl_applied_30 | 30 | `applied to [Prospect].` | corps | ≈18 car | fixe | non | remplacer `[Prospect]` par le nom client |
| p2_cl_mascotte_29 | 29 | (aucun) | media | n/a | optionnel | non | image/mascotte |
| p2_cl_mascotte_30 | 30 | (aucun) | media | n/a | optionnel | non | image/mascotte |

`applied to [Prospect].` apparaît sur les 2 pages : remplacer `[Prospect]` (via `find_and_replace_text`) par le nom client. `What we activate first` : fixe.

### Page 31 : approche, platform roles (TikTok vs Meta)

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_pr_titre | 31 | `[Different platforms Different rules]` | titre | ≈35 car / 2 lignes | fixe | non | ancre texte |
| p2_pr_soustitre | 31 | `[TikTok role. Meta role.]` | corps | ≈53 car / 1 ligne | fixe | non | ancre texte |
| p2_pr_tiktok_audience | 31 | `[TikTok: audience]` | cellule | ≈15 car | repete-6 | non | ancre texte |
| p2_pr_tiktok_whosees | 31 | `[TikTok: who sees it]` | cellule | ≈49 car / 2 lignes | repete-6 | non | ancre texte |
| p2_pr_tiktok_style | 31 | `[TikTok: content style]` | cellule | ≈38 car | repete-6 | non | ancre texte |
| p2_pr_tiktok_service | 31 | `[TikTok: service content]` | cellule | ≈45 car / 2 lignes | repete-6 | non | ancre texte |
| p2_pr_tiktok_origin | 31 | `[TikTok: content origin]` | cellule | ≈21 car | repete-6 | non | ancre texte |
| p2_pr_tiktok_metrics | 31 | `[TikTok: key metrics]` | cellule | ≈45 car / 2 lignes | repete-6 | non | ancre texte |
| p2_pr_meta_audience | 31 | `[Meta: audience]` | cellule | ≈26 car | repete-6 | non | ancre texte |
| p2_pr_meta_whosees | 31 | `[Meta: who sees it]` | cellule | ≈41 car / 2 lignes | repete-6 | non | ancre texte |
| p2_pr_meta_style | 31 | `[Meta: content style]` | cellule | ≈40 car | repete-6 | non | ancre texte |
| p2_pr_meta_service | 31 | `[Meta: service content]` | cellule | ≈61 car / 2 lignes | repete-6 | non | ancre texte |
| p2_pr_meta_origin | 31 | `[Meta: content origin]` | cellule | ≈48 car / 2 lignes | repete-6 | non | ancre texte |
| p2_pr_meta_metrics | 31 | `[Meta: key metrics]` | cellule | ≈43 car | repete-6 | non | ancre texte |

En-têtes `Tiktok` / `Meta (Instagram + Facebook)` et libellés de lignes (`audience`, `Who sees it`, etc.) : fixes.

### Page 32 : approche, same country different cultures (FR vs NL)

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_cult_titre | 32 | `[same countrydifferent cultures]` | titre | ≈31 car / 2 lignes | fixe | non | ancre texte |
| p2_cult_soustitre | 32 | `[FR and NL are two audiences, not translations.]` | corps | ≈53 car / 1 ligne | fixe | non | ancre texte |
| p2_cult_reference | 32 | `[Reference: example brand]` | titre | ≈21 car | fixe | non | ancre texte |
| p2_cult_reference_corps | 32 | `[One BE account.Same brand idea.Two humor executions.]` | corps | ≈70 car / 3 lignes | fixe | non | ancre texte |
| p2_cult_fr_label | 32 | `[Be FR]` | titre | ≈5 car | repete-2 | non | ancre texte |
| p2_cult_nl_label | 32 | `[BE NL]` | titre | ≈5 car | repete-2 | non | ancre texte |
| p2_cult_fr_corps | 32 | `[FR humour execution: tone, format, why it lands.]` | corps | ≈89 car / 3 lignes | repete-2 | non | ancre texte |
| p2_cult_nl_corps | 32 | `[NL humour execution: tone, format, caption choice and why it lands.]` | corps | ≈106 car / 3 lignes | repete-2 | non | ancre texte |
| p2_cult_video_1 | 32 | (aucun) | media | n/a | optionnel | non | vidéo gauche |
| p2_cult_video_2 | 32 | (aucun) | media | n/a | optionnel | non | vidéo droite |

### Page 33 : three pillars (vue d'ensemble)

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_pillars_titre | 33 | `[Three pillarsOne voice, Platform-native]` | titre | ≈40 car / 2 lignes | fixe | non | ancre texte |
| p2_pillars_1_nom | 33 | `[Pillar 1name]` | titre | ≈21 car / 2 lignes | repete-3 | non | colonne 1, page 33 |
| p2_pillars_2_nom | 33 | `[Pillar 2name]` | titre | ≈12 car / 2 lignes | repete-3 | non | colonne 2, page 33 |
| p2_pillars_3_nom | 33 | `[Pillar 3name]` | titre | ≈16 car / 2 lignes | repete-3 | non | colonne 3, page 33 |
| p2_pillars_1_start | 33 | `[Pillar 1 start]` | corps | ≈23 car | repete-3 | non | ancre texte |
| p2_pillars_2_start | 33 | `[Pillar 2start]` | corps | ≈28 car | repete-3 | non | ancre texte |
| p2_pillars_3_start | 33 | `[Pillar 3 start]` | corps | ≈16 car | repete-3 | non | ancre texte |
| p2_pillars_1_feeling | 33 | `[P1 feeling]` | corps | ≈12 car | repete-3 | non | ancre texte |
| p2_pillars_2_feeling | 33 | `[P2 feeling]` | corps | ≈19 car | repete-3 | non | ancre texte |
| p2_pillars_3_feeling | 33 | `[P3 feeling]` | corps | ≈21 car | repete-3 | non | ancre texte |
| p2_pillars_mascotte | 33 | (aucun) | media | n/a | optionnel | non | image/mascotte |

Libellés `Starts from` / `Feeling` : fixes.

### Pages 34-36 : content strategy, détail par pilier

`[Pillar Nname]` apparaît aussi en titre de la page détail : départager par page. Les exemples sont un seul bloc multi-lignes.

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_pillar1_titre | 34 | `[Pillar 1name]` | titre | ≈21 car / 2 lignes | fixe | non | page 34 |
| p2_pillar1_startsfrom | 34 | `[Starts from: what it builds on]` | corps | ≈42 car / 2 lignes | fixe | non | page 34 (cf p36, départager par page) |
| p2_pillar1_examples | 34 | `[Example content idea 1 for this pillar]` (bloc, 4 idées) | corps | ≈300 car / 8 lignes | fixe | non | bloc d'exemples, page 34 |
| p2_pillar1_feeling | 34 | `[Feeling]` | corps | ≈13 car | fixe | non | page 34 |
| p2_pillar1_where | 34 | `[Where it lives and how it is produced]` | corps | ≈71 car / 3 lignes | fixe | non | page 34 |
| p2_pillar1_media | 34 | (aucun) | media | n/a | repete-2 | non | vidéos |
| p2_pillar2_titre | 35 | `[Pillar 2name]` | titre | ≈12 car / 2 lignes | fixe | non | page 35 |
| p2_pillar2_startsfrom | 35 | `[Starts from: what it builds on here]` | corps | ≈61 car / 2 lignes | fixe | non | page 35 (texte unique : `here`) |
| p2_pillar2_examples | 35 | `[Example content idea 1 for this pillar]` (bloc, 5 idées) | corps | ≈430 car / 8 lignes | fixe | non | bloc d'exemples, page 35 |
| p2_pillar2_feeling | 35 | `[Feeling]` | corps | ≈19 car | fixe | non | page 35 |
| p2_pillar2_where | 35 | `[Where it lives and how it is produced]` | corps | ≈48 car / 2 lignes | fixe | non | page 35 |
| p2_pillar2_media | 35 | (aucun) | media | n/a | repete-2 | non | logo + vidéos |
| p2_pillar3_titre | 36 | `[Pillar 3name]` | titre | ≈15 car / 2 lignes | fixe | non | page 36 |
| p2_pillar3_startsfrom | 36 | `[Starts from: what it builds on]` | corps | ≈30 car | fixe | non | page 36 (cf p34, départager par page) |
| p2_pillar3_examples | 36 | `[Example content idea 1 for this pillar]` (bloc, 4 idées) | corps | ≈300 car / 8 lignes | fixe | non | bloc d'exemples, page 36 |
| p2_pillar3_feeling | 36 | `[Feeling, in a few words]` | corps | ≈34 car / 2 lignes | fixe | non | ancre texte |
| p2_pillar3_where | 36 | `[Where it lives and how it is produced]` | corps | ≈73 car / 3 lignes | fixe | non | page 36 |
| p2_pillar3_media | 36 | (aucun) | media | n/a | repete-3 | non | vidéos |

`[Starts from: what it builds on]` et `[Where it lives and how it is produced]` se répètent à l'identique sur p34/p36 (et `[Feeling]` sur p34/p35) : toujours départager par page. Le bloc d'exemples est un seul élément texte multi-lignes (les idées 1 à 4/5 sont dans le même cadre, séparées par des sauts de ligne).

### Page 37 : way of working, kick-off (FIXE)

Aucune zone éditable. Timeline 6 semaines (`w -6` à `w -1`) et libellés : standard process socialsky. Ajuster seulement sur demande explicite (langue, planning différent).

### Page 38 : way of working, always-on (FIXE)

Aucune zone éditable. Forme de semaine standard.

### Page 39 : way of working, team (FIXE par défaut)

Équipe dédiée standard (5 membres nom + rôle). Éditer seulement si l'équipe diffère : chaque membre est un élément texte unique (nom + rôle après un saut de ligne), à retrouver par le nom. Photos : médias optionnels.

### Page 40 : scope

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_scope_titre | 40 | `[whats includedin the scope]` | titre | ≈26 car / 2 lignes | fixe | non | ancre texte |
| p2_scope_items | 40 | `[Deliverable 1 included in the scope]` (bloc, 9 lignes) | corps | ≈360 car / 9 lignes | fixe | non | bloc multi-lignes des livrables |
| p2_scope_addon_1 | 40 | `[Add-on 1]` | corps | ≈10 car | optionnel | non | ancre texte |
| p2_scope_addon_2 | 40 | `[Add-on 2]` | corps | ≈10 car | optionnel | non | ancre texte |
| p2_scope_addon_3 | 40 | `[Add-on 3]` | corps | ≈10 car | optionnel | non | ancre texte |

Les 9 `[Deliverable N included in the scope]` sont dans un seul élément texte (un par ligne). `Available add-ons` / `Included` : fixes.

### Page 41 : pricing (DONNÉES)

| label | page | placeholder | type | budget | cardinalité | donnée | résolution |
|---|---|---|---|---|---|---|---|
| p2_pricing_titre | 41 | `[Setup+ monthly pack]` | titre | ≈20 car / 2 lignes | fixe | oui | ancre texte |
| p2_pricing_setup_label | 41 | `[Setup label]` | titre | ≈16 car | fixe | oui | ancre texte |
| p2_pricing_setup_desc_1 | 41 | `[What the setupincludes, line 1]` | corps | ≈30 car / 2 lignes | fixe | oui | ancre texte |
| p2_pricing_setup_desc_2 | 41 | `[What the setup includes, line 2]` | corps | ≈30 car / 2 lignes | fixe | oui | ancre texte |
| p2_pricing_setup_montant | 41 | `X,XXX €` | prix | ≈7 car | fixe | oui | montant proche de `[Setup label]` |
| p2_pricing_monthly_label | 41 | `[Monthly pack label]` | titre | ≈28 car | fixe | oui | ancre texte |
| p2_pricing_monthly_desc_1 | 41 | `[What the monthly pack includes: channel 1 volume and details]` | corps | ≈150 car | fixe | oui | ancre texte |
| p2_pricing_monthly_desc_2 | 41 | `[What the monthly pack includes: channel 2 volume and details]` | corps | ≈150 car | fixe | oui | ancre texte |
| p2_pricing_monthly_montant | 41 | `X,XXX €/month` | prix | ≈14 car / 2 lignes | fixe | oui | suffixe `/month` distingue du montant setup |

Les deux montants : `X,XXX €` (setup) et `X,XXX €/month` (monthly) sont distincts par le suffixe `/month`. Jamais inventés (fournis ou TODO).

---

## Page 42 : outro (statique)

Wordmark + baseline. Rien à éditer.
