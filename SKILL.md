---
name: skysales
description: "Produire la partie client (P2) d'un deck de vente socialsky dans Canva, à partir des documents du client. Se déclenche quand l'utilisateur dit « Go Skysales! » (ou « deck sales [client] », « présentation sales socialsky », « P2 socialsky [client] »). À l'activation, le skill explique son fonctionnement, énonce les étapes, vérifie qu'un dossier de travail est sélectionné, que les ressources client y sont et sur quel master Canva travailler, puis propose de lancer l'interview de cadrage. Le skill remplit les zones sur-mesure du template master en copiant le deck et en injectant le texte par leurs placeholders ; P1 (présentation agence) n'est pas réécrite, mais elle est traduite : un deck a une seule langue et toutes ses slides la parlent. Filtre anti-AI intégré sur tout texte visible."
---

# skysales

Produire un deck de vente socialsky dans Canva, partie client (P2) seulement, à partir des documents du client.

Le livrable final est un **document Canva**, copie du template master, dont seules les zones de P2 sont rédigées. Le contenu de P1 n'est jamais réécrit — mais il est traduit dans la langue du deck (règle 8 bis).

État : carte des zones P2 (pages 23 à 41) en spec sémantique, résolution par placeholder (le master neutre porte un placeholder par zone). Phases de contenu rédigées. Le deck se construit par morceaux (chunks de ~5 pages édités en place), assemblés ensuite en un deck complet (voir Phase 5).

> **Révision du 27/07/2026.** Le connecteur Canva a évolué depuis la v1 de juin. Le re-thèmage couleur, jusqu'ici hors scope, est désormais faisable : voir la section Thématisation couleur. La v1 de un contributeur précédent est conservée dans une sauvegarde locale. L'assemblage automatique d'un deck complet reste bloqué (non re-testé à ce jour).
>
> **Révision du 18/08/2026 — correction bloquante.** Le master par défaut `<DESIGN_ID>` était **mort** (`permission_denied`), et `references/template-map.md` décrivait ce master disparu. Le skill ne pouvait donc pas démarrer correctement : il substituait un master en silence et travaillait sur une carte fausse. Trois corrections : (1) plus aucun master par défaut, il est demandé et validé par un **préflight** en trois contrôles ; (2) la carte des zones est **dérivée du master lu** à chaque run, plus jamais transportée ; (3) `template-map.md` est marqué périmé. **Un master neutre reste à construire** — aucun des candidats vivants n'est un vrai gabarit.

---

## À LIRE AVANT TOUT : ce que le lead attend

Ce skill a été corrigé une cinquantaine de fois par le lead entre juin et août 2026. En relisant toutes ces corrections d'un bloc, elles disent **une seule et même chose**, et elle ne porte jamais sur la technique :

> **Un livrable se termine avant d'être montré. Ce n'est pas au lead de trouver ce qui manque.**

Le défaut récurrent n'a jamais été l'incompétence — c'est la **livraison prématurée avec le trou laissé au lead** : un deck annoncé fini avec vingt `[LOGO]` en place du logo, un master déclaré « 0 résidu » après n'avoir vérifié que le texte, une slide en anglais au milieu d'un deck français, une phrase ambiguë laissée telle quelle, une recherche abandonnée sur une contrainte supposée. À chaque fois, la même mécanique : **s'arrêter au bord du travail et présenter ça comme un résultat.**

Les quatre réflexes qui découlent de ce constat, à appliquer sans qu'on les demande :

1. **Ce qui manque, on va le chercher.** Un logo se trouve sur le site du client en deux minutes. Des vidéos se scrapent chez ses concurrents. Un nom propre se vérifie en trente secondes. « Je n'ai pas l'information » n'est presque jamais vrai — c'est une recherche qui n'a pas été faite. Réclamer une donnée au lead est le dernier recours, pas le premier.
2. **On dit l'état réel, pas l'état espéré.** « 40 pages sur 43, il reste ceci » vaut infiniment mieux que « c'est prêt » suivi d'un démenti. Le lead peut travailler avec un état honnête ; il ne peut rien faire d'une annonce fausse.
3. **Une correction vaut pour toute sa classe.** Elle s'applique partout dans le deck, se corrige dans le master, et s'écrit ici. Voir règle 13.
4. **On regarde le résultat.** L'API confirme qu'elle a écrit, pas que c'est lisible. Voir règle 18.

Le reste de ce document — les règles, les pièges Canva, les phases — n'est que la déclinaison de ces quatre réflexes sur un cas particulier.

---

## ACTIVATION : « Go Skysales! »

Quand l'utilisateur dit « Go Skysales! » (ou déclenche le skill autrement), produire d'abord le texte d'intro ci-dessous, puis exécuter les trois vérifications bloquantes avant toute autre chose. Ne PAS lancer l'interview tant que le dossier, les ressources et le master ne sont pas confirmés.

Texte d'intro à sortir :

> **Skysales** prépare la partie sur-mesure (P2) d'un deck de vente socialsky dans Canva, à partir du compte rendu du R1. Le contenu de la partie agence (P1) n'est jamais réécrit — il est seulement traduit dans la langue du deck. Le livrable final est une copie Canva du template master, dont seules les zones client sont rédigées.
>
> Comment ça marche, en 6 étapes :
> 1. **Extraction** : je lis les docs du client (compte-rendu de meeting, infos brand et commerciales).
> 2. **Interview de cadrage** : je te pose les questions qui manquent (langue, nom du client, données chiffrées, cardinalités).
> 3. **Remplissage** : j'écris le texte de chaque zone, dans la langue choisie, au budget, passé au filtre anti-AI.
> 4. **Validation** : je te montre un mapping zone par zone, tu valides ou corriges.
> 5. **Push Canva** : copie du master, injection du texte par lots, aperçus, commit après ton OK.
> 6. **Revue anti-AI finale**.
>
> Trois vérifs avant de commencer :
> - Un dossier de travail est-il sélectionné ? J'y lirai les docs client et j'y écrirai les drafts.
> - Les ressources du client (meeting minutes, infos brand) sont-elles dans ce dossier ? Si oui, dis-moi où ; sinon, dépose-les d'abord.
> - De quel rendez-vous s'agit-il, R1 ou R2 ? Le master est déjà fixé (Digest pour un R1, MASTER P1+P2 pour un R2) : je le vérifie au préflight, tu n'as pas à me le donner.
> - Dans quelle langue ? Elle vaudra pour les 43 pages, sans exception.
>
> Quand c'est bon, on lance l'interview de cadrage. Prêt ?

### Vérification 1 : dossier sélectionné (bloquant)
Si aucun dossier de travail n'est sélectionné, demander à l'utilisateur d'en sélectionner un. Ne pas continuer sans dossier : c'est là que vivent les docs client et les drafts de validation.

### Vérification 2 : ressources client présentes (bloquant)
Demander où sont les documents du client dans le dossier sélectionné (compte-rendu de meeting, infos brand et commerciales, précisions). Les ressources vivent dans le dossier de travail, pas dans le skill. Si elles manquent, demander à l'utilisateur de les déposer avant de lancer l'interview.

### Vérification 3 : master (bloquant, avec préflight)

### Architecture Canva : d'où on part, où on livre

Tout se passe dans l'espace **`Automation - Sales Desk`** (`<ESPACE_SALES>`), organisé en deux dossiers :

**📁 `Template` (`<DOSSIER_TEMPLATE>`) — on lit ici, on n'écrit jamais dedans.**

| Design | Titre | Pages | Rôle |
|---|---|---|---|
| `<DIGEST>` | Digest - socialsky - EN (To Duplicate) | 23 | **R1 — premier rendez-vous.** Présentation de la boîte uniquement. Pas de partie client, pas de diagnostic, pas de prix. |
| `<MASTER_EN>` | **MASTER SD Sales P1+P2 - NEUTRE (skysales)** | 43 | **R2 en anglais.** Le deck complet, construit sur les insights récoltés au R1. |
| `<MASTER_FR>` | **MASTER SD Sales P1+P2 - NEUTRE FR (skysales)** | 43 | **R2 en français.** Même gabarit, P1 et navigation intégralement traduites (20/08/2026). **C'est lui qu'on copie pour un deck FR.** |
| `<DESIGN_ID>` | FINAL Socialsky - SD Sales Template P1+P2 EN ((To Duplicate) | 42 | Ancien template EN de l'agence, **non neutralisé**. Référence historique, à ne pas utiliser comme master. |

**📁 `Sales Desk - Finaux` (`<DOSSIER_SORTIE>`) — on écrit ici.** Tout deck client terminé y est déplacé. C'est la sortie du processus.

> **Deux templates P1+P2 cohabitent.** Le nôtre porte **`MASTER … NEUTRE (skysales)`** dans son titre : c'est le seul discriminant fiable. Vérifier le titre, jamais la longueur — c'est la confusion qui avait cassé le skill au départ.

### Le processus, en une phrase

Activer le skill → **copier** le template depuis `Template` → remplir → contrôler (Phase 5 bis) → **déplacer la copie dans `Sales Desk - Finaux`** → livrer le lien d'édition.

Le master reste vierge et n'est jamais rempli. Toute correction structurelle (mise à jour de P1, nouvelle page, changement de grille) se fait **sur le master lui-même**, dans `Template` — c'est un template vivant, pas un fichier figé.

### Vocabulaire : P1 = R1, P2 = R2

Ce sont les mêmes choses nommées de deux façons — par la partie du deck, ou par le rendez-vous auquel elle sert. Ne jamais les traiter comme quatre notions.

| | Rendez-vous | Ce qu'on y fait | Support |
|---|---|---|---|
| **P1 = R1** | Premier | On présente la boîte, **et surtout on récolte toutes les informations** | Le **Digest** (23 p) |
| **P2 = R2** | Deuxième | On apporte de l'insight — marché, concurrents — **à partir exactement de ce qui a été dit au R1** | Le **MASTER P1+P2** (43 p) : on rejoue la partie agence, puis on déroule la partie client |

**Conséquence directe : l'entrée du P2 n'est pas un dossier de documents, c'est le compte rendu du R1.** Ce que le prospect a dit à ce rendez-vous est la matière première du diagnostic, des priorités et du North Star. S'il n'y a pas de compte rendu de R1, il n'y a pas de P2 à écrire — le demander avant toute chose.

**Quel template copier :** R1 → le Digest ; R2 → le MASTER P1+P2. Si le lead ne précise pas, demander de quel rendez-vous il s'agit : c'est la première question du brief, avant même la langue.

**Renommer un design est possible par API** (constaté le 20/08/2026) : opération `update_title` dans `edit-design`, avec un `page_index` quelconque. Le paramètre `title` de `copy-design`, lui, reste ignoré — d'où la confusion antérieure. Renommer chaque copie dès sa création : « Socialsky - SD Sales - [Client] ».

**Piège de propriété :** un design appartenant à un autre membre de l'équipe ne peut pas être déplacé dans un dossier personnel (Canva renvoie « Shared designs are not allowed in the root folder »). Il faut en faire une copie, qui devient la propriété du compte courant. C'est pour cela que les templates de `Template` sont des copies et non les originaux de `SALES_TEMPLATES`. Exécuter le préflight ci-dessous à chaque run. Ne jamais substituer un master de son propre chef : c'est ce qui a produit un run silencieusement faux le 18/08/2026.

> **Historique.** L'ancien défaut `<DESIGN_ID>` (« SK - Slide Deck Automatisé - Template », 42 pages) est **mort** : `read-design` renvoie `permission_denied`. La carte `references/template-map.md` décrit ce master disparu et ne correspond donc plus à aucun design vivant.

**Préflight du master — les trois contrôles, dans l'ordre :**

1. **Vivant ?** `read-design` sur l'ID fourni. Si `permission_denied` ou introuvable → **STOP**. Dire lequel a été tenté et demander un autre ID. Ne pas chercher un remplaçant tout seul.
2. **Porteur de placeholders ?** Chercher dans le contenu des marqueurs de zone à remplir (`[...]`, `XX%`, `X,XXX €`). Annoncer le compte trouvé.
   - Beaucoup de placeholders → **mode placeholder** (nominal).
   - Peu ou aucun, et du contenu d'un vrai client à la place → **mode remplacement**. Le dire explicitement au lead : « ce master est un deck rempli, pas un gabarit ; je vais devoir remplacer zone par zone et le risque de résidu est réel. » Puis demander confirmation avant de continuer.
3. **Cohérent ?** Si le contenu mélange plusieurs clients (ex : diagnostic d'une marque et piliers d'une autre), **le signaler et s'arrêter**. Un master hybride produit un deck hybride.

Garder l'ID pour tout le run. Consigner le mode retenu (placeholder ou remplacement) : il change ce qui est promis au lead en Phase 4.

**Candidats vivants connus au 18/08/2026** (aucun n'est un vrai gabarit neutre — à traiter en mode remplacement) :

| ID | Pages | État |
|---|---|---|
| `<DESIGN_ID>` | 43 | Le plus propre : contenu un client précédent **cohérent** de bout en bout, `XX%` conservés sur les signaux secteur. Meilleur point de départ. |
| `<DESIGN_ID>` | 43 | **À éviter** : hybride un autre client (diagnostic, pilier 01) + un client précédent (piliers 02-03), chiffres en dur à la place des `XX%`. |
| `<DESIGN_ID>` | 42 | Nommé « FINAL ». Non inspecté. |
| `<MASTER_EN>` | 43 | ✅ **MASTER NEUTRE — utiliser celui-ci.** Neutralisation terminée le 18/08/2026 : **92 placeholders**, **0 résidu un client précédent**, **0 résidu un autre client**, accents passés en `#f50c45` sur P1 et P2 (y compris les 3 bandes ex-verrouillées p32/p41/p42 et les 5 lignes de la p32, déverrouillées puis recolorées le 19/08/2026). Placeholders **tous uniques** (pas de désambiguïsation par position ni par page). Les 20 slots logo client ont été remplacés par un placeholder neutre carte blanche + texte `[LOGO]`/`[CLIENT LOGO]` (voir « Slot logo client » ci-dessous — ce n'est plus un slot média unique, ça change la mécanique de remplissage). Renommé « MASTER SD Sales P1+P2 - NEUTRE (skysales) » et rangé dans `Template` le 20/08/2026. Reste en résidu orange, non adressable par API : les pastilles TikTok/Meta (p33) et les pastilles prix (p42-43) — ce sont des fonds de texte (*highlight*), invisibles dans le dump (voir tableau de limitations ci-dessous). |

Une fois les trois vérifs OK, enchaîner sur la Phase 1 (extraction) puis la Phase 2 (interview).

---

## RÈGLES NON NÉGOCIABLES

1. **Sortie Canva obligatoire.** Le but de l'exercice est un deck Canva, pas un doc texte. Le texte structuré n'est qu'une étape intermédiaire de validation.
2. **P1 intacte, sauf pour la langue.** Le skill ne touche qu'aux zones listées dans la carte (toutes dans P2) : le contenu de P1 est du boilerplate agence, jamais réécrit. **Une seule exception, et elle est impérative : la langue** (voir règle 8 bis). Traduire P1 n'est pas la réécrire — c'est le même discours dans la langue du deck.
3. **Jamais de donnée inventée.** Stats secteur (`XX %`), prix (`X XXX €`), durées, volumes : le lead ou les docs fournissent. Si une donnée manque, ne pas s'arrêter pour la réclamer : laisser un marqueur `TODO` explicite dans le deck, continuer le run, et lister le manque dans le rapport de livraison. Jamais de chiffre plausible inventé.
4. **Jamais de constat inventé.** Diagnostic, frictions, priorités : viennent des docs client ou du lead. Pas de constat déduit du seul nom de l'entreprise.
5. **Filtre anti-AI** sur tout le texte visible. Voir Phase 6 et `references/writing-filter.md`. Tout texte destiné au lecteur final passe par ce filtre avant validation.
6. **Committer sans demander, livrer pour faire valider.** Committer n'est pas livrer : la copie reste privée tant que son lien n'a pas été donné. `commit-editing-transaction` part dès qu'un lot est écrit — un run interrompu sur une transaction ouverte perd tout son travail. La validation du lead porte sur le deck fini qu'on lui remet, jamais sur l'autorisation d'écrire dedans. **Le run va de l'intake à la livraison sans s'arrêter** : les seuls arrêts légitimes sont un master mort, un master pollué par le contenu d'un vrai client, ou l'absence de compte rendu du premier rendez-vous. Tout le reste — logo introuvable, vidéo manquante, chiffre absent, couleur non recolorable — se tranche, s'applique, et se remonte en hypothèse dans le rapport de livraison. Une hypothèse écrite se corrige en trente secondes ; le temps passé à attendre une réponse ne se récupère pas.
7. **Budget caractères et sauts de ligne.** Les pages sont fixes (`is_responsive: false`), le texte ne reflue pas. Chaque zone a un budget mesuré sur le texte d'origine. Écrire avec des sauts de ligne `\n` explicites : certains cadres débordent derrière un média (ex : points du diagnostic intro sous la vidéo), et sans `\n` l'auto-wrap fait passer le texte sous le média. Respecter un budget PAR LIGNE, pas seulement total.
8. **Langue selon le client** (EN / FR). Demander avant de remplir. Ponctuation française si FR (espaces avant `: ; ! ?`, guillemets « »). Pas de tiret cadratin. Le filtre anti-AI couvre EN et FR (voir `references/writing-filter.md`).
8 bis. **Un deck a UNE langue, et toutes ses slides la parlent.** Deck en français → les 43 pages sont en français, P1 comprise. Deck en anglais → les 43 pages sont en anglais. Il n'existe pas de deck moitié-moitié. Un prospect francophone qui tourne la page et tombe sur « 6 weeks to launch » voit un template, pas une proposition écrite pour lui — et c'est exactement l'inverse de ce que le P2 essaie de démontrer.

   **Ce que ça implique concrètement :**
   - Le contrôle de langue porte sur **tout le deck**, pas sur les seules zones remplies. Le balayage se fait sur les 392 blocs de texte, pas sur les 90 placeholders.
   - **Le lexique de marque n'est pas une exception à la règle, c'en est le complément.** `Social OS™`, les cinq phases (`CULTURAL SIGNALS`, `PLATFORM INTELLIGENCE`, `NATIVE CREATION`, `CONTINUOUS PRESENCE`, `AMPLIFICATION`), les cinq composants (`STRATEGY`, `Studio`, `Community`, `Influence`, `social ads`), `always-on`, `social-first`, `playbook`, `paid`, `organic`, `feed`, `UGC`, `vox pop`, `motion design`, `packshot` restent en anglais dans les deux langues — ce sont des noms, pas des mots. La frontière est simple : **un terme du vocabulaire maison reste ; une phrase se traduit.** « Content check + calendar validation » est une phrase. `CONTINUOUS PRESENCE` est un nom.
   - Les **labels de navigation** de la barre latérale se traduisent aussi, et **de la même façon d'une page à l'autre**. C'est là que l'incohérence se glisse le plus facilement : sur un run récent, la page 40 disait déjà `équipe` pendant que les pages 38 et 39 disaient encore `team`, dans le même deck.

   **Pourquoi c'est une règle et pas une préférence :** le lead l'a posée le 20/08/2026 en une phrase — « si tu fais une présentation tout en français, alors toutes les slides sont en français ». Aucune marge d'interprétation.

9. **Conventions de marque socialsky** : socialsky en minuscules, le Social OS™ (casse S + OS majuscules, glyphe ™, jamais « SOCIAL OS » ni « (TM) »), concepts métier en anglais sans guillemets. Détail et voix dans `references/content-playbook.md`.
10. **Le master est fixé, mais jamais implicite.** Le master du skill dépend du rendez-vous **et de la langue** : R2 en français → `<MASTER_FR>` ; R2 en anglais → `<MASTER_EN>` ; R1 → `<DIGEST>` (le Digest). Tous dans le dossier `Template`. **Choisir le master de la bonne langue est le premier geste du run** — c'est ce qui rend la règle 8 bis gratuite au lieu de coûter 113 traductions par deck. **Ne pas redemander au lead quel master utiliser à chaque run** — il est écrit ici. Mais le préflight (Activation, Vérification 3) tourne quand même, à chaque fois : un master peut mourir entre deux runs, c'est déjà arrivé à `<DESIGN_ID>`. Si le préflight échoue, **le dire et s'arrêter** — jamais de substitution silencieuse, jamais de remplaçant improvisé.

11. **Le logo client se pose nu, jamais sur une carte blanche, et toujours sur la couverture.** Dès qu'un logo client est fourni : (a) le poser sur **toutes** les pages qui portent un slot logo, **couverture (page 2) comprise** — elle n'est jamais oubliée ; (b) **supprimer la carte blanche** de fond en même temps que le texte `[LOGO]` / `[CLIENT LOGO]` — cette carte n'existait que pour porter le placeholder, la garder derrière un vrai logo n'a aucun sens visuel ; (c) le poser **plus grand** que le placeholder, pour qu'il se voie. Ne jamais attendre que le lead le redemande : c'est le comportement par défaut du skill. Détail des dimensions dans « Slot logo client ».

11 bis. **Le logo et les vidéos ne sont pas optionnels. Ils font partie du scope, toujours.** Un deck livré sans le logo du client et sans vidéos réelles n'est pas un deck fini, c'est un brouillon. Ces deux éléments se produisent **d'office**, sans que le lead ait à les demander, et **sans jamais s'arrêter pour réclamer un fichier**.

- **Le logo se cherche, il ne se demande pas.** Aller le prendre sur le site du client (favicon, en-tête, page presse, `og:image`), sur sa page LinkedIn, sur son e-shop. `upload-asset-from-url` avale n'importe quelle URL publique : le logo d'une entreprise qui a un site EST une URL publique. Ne demander au lead que si la recherche a réellement échoué, et le dire alors explicitement. **« Je n'ai pas d'URL » n'est pas une raison de livrer sans logo — c'est une recherche qui n'a pas été faite.**
- **Les vidéos se scrapent, elles ne s'attendent pas.** Les treize slots vidéo se remplissent avec du contenu réel : le prospect sur la page 25, la marque de référence sur la page 33, **les concurrents directs de sa niche sur les pages piliers**. La chaîne est établie et testée (Apify → `downloadedVideo` → `upload-asset-from-url` → `update_fill`). Laisser les vidéos du template en place revient à montrer au prospect le contenu d'une autre marque en prétendant que c'est sa stratégie.
- **Corollaire sur la carte blanche** : dès que le vrai logo est posé, la forme blanche de fond ET le texte `[LOGO]` / `[CLIENT LOGO]` disparaissent tous les deux. Voir la règle 11.

> **Erreur commise le 20/08/2026 sur un run récent, à ne pas répéter.** Deck livré avec vingt placeholders `[LOGO]` intacts et les vidéos du template, en annonçant au lead qu'il « suffirait » de fournir une URL. Le logo était sur prospect.be, et les comptes Instagram à scraper avaient déjà été identifiés et confirmés dans le même run. Rien ne manquait sauf la décision d'aller les chercher.

12. **La carte des zones se dérive du master, elle ne se transporte pas.** À chaque run, lire le master et construire la carte des zones à partir de ce qu'il contient réellement. `references/template-map.md` n'est plus qu'un document de référence historique : il décrit un master mort et ne fait autorité sur rien. En cas de désaccord entre la carte et le master lu, **le master gagne, toujours**.

13. **Une correction du lead n'est pas un patch, c'est une règle.** Quand le lead signale un défaut, il ne signale jamais *cette occurrence-là* : il signale une classe de défauts. Trois gestes, dans le même mouvement, sans qu'on les redemande :
   - **(a) l'appliquer partout dans le deck en cours**, pas seulement à l'endroit montré ;
   - **(b) le corriger à la source** — le master vit dans `Template`, c'est un template vivant : un défaut trouvé dans une copie existe aussi dans le master et dans tous les decks à venir ;
   - **(c) écrire la règle ici**, avec le verbatim et la date.

   *Verbatim du 20/08/2026 :* « **tout ce que je viens de te dire, des trucs qui n'allaient pas, soient bien mis dans les skills pour que ça ne se reproduise plus et que la prochaine fois que je te le montre, ce soit encore mieux.** » Et, sur le logo : « on doit remplir **toujours** la slide 2 avec le logo. Il faut bien faire attention à **toujours** enlever l'élément blanc. » Les deux « toujours » sont le sujet de la phrase.

   Corriger uniquement l'endroit montré, c'est garantir que le lead retrouvera le même défaut deux slides plus loin. Il le retrouvera.

14. **Chaque ligne visible doit se comprendre seule, sans personne pour l'expliquer.** le commercial présente ce deck sans nous dans la pièce. Une phrase qui a besoin d'une phrase de contexte est une phrase ratée. Test avant validation : lire chaque ligne à voix haute **en se mettant à la place du prospect qui la découvre**. Si elle appelle un « c'est-à-dire… », la réécrire.

   *Le cas du 20/08/2026 :* la slide 30 portait « Ce que un concurrent du prospect fait déjà, et où. » le lead a répondu « **Ça veut dire quoi, ça ?** » — remplacé par « Où votre patientèle est vraiment, pas où on l'imagine. »

   **Corollaire : une question du lead sur le contenu n'est presque jamais une question.** C'est un défaut qui se signale poliment. « C'est quoi Alliage ? », « Ça veut dire quoi, ça ? », « Pourquoi il y a des carrés orange ? » : traiter chacune comme un bloquant, pas comme une demande d'éclaircissement.

15. **« Prêt », « fini », « livré » sont des mots qui se méritent.** Ne jamais annoncer un master, un skill ou un deck comme prêt sans avoir **réellement lancé** le test de bout en bout. Ne jamais annoncer un deck comme livré tant qu'il reste un bloquant au contrôle qualité **ou** que le scope obligatoire est incomplet — logo, vidéos, langue, couleur (règles 8 bis, 11, 11 bis).

   *Le cas du 20/08/2026 :* deck le prospect annoncé terminé avec 20 placeholders `[LOGO]` et les vidéos du template. Réponse du lead : « **là, c'est trop, c'est pas bon, quoi.** » Le deck n'était pas fini, il était fini *de mon point de vue*.

   Formuler l'état réel plutôt que l'état espéré : « 40 des 43 pages sont faites, il reste X, Y, Z » vaut mieux que « c'est prêt » suivi d'un démenti.

16. **Une action que le lead doit faire à la main se donne clé en main.** Certaines choses sont hors de portée de l'API (fonds de texte, cartes de recoloration d'images, formes verrouillées, suppression de page). Écrire « à traiter à la main » et s'arrêter là fait porter au lead un travail d'enquête qui nous revient. Toujours fournir : **la page, l'élément décrit comme il le voit à l'écran, le geste exact, et la valeur exacte à copier-coller.**

   Corollaire de vocabulaire : parler à le lead dans les termes de ce qu'il voit dans Canva — « le bandeau à gauche de la slide 30 », « la pastille orange derrière 59 % » — jamais en `locator_id`. Les identifiants sont notre plomberie, pas son interface.

17. **Ne jamais s'arrêter sur une contrainte supposée.** Crédits, quotas, coût, droits, limites d'API : **vérifier avant d'affirmer**. Une contrainte annoncée sans avoir été constatée fait perdre un aller-retour au lead et le met en position de nous autoriser quelque chose qui n'avait pas besoin de l'être.

   *Verbatim :* « **il y a des crédits donc fait le ?** » — j'avais renoncé à un scraping en supposant un problème de quota.

   Si la contrainte est réelle, dire trois choses et pas une : ce qui est bloqué, ce que ça coûterait de le débloquer, et **ce qui reste faisable sans**. Puis faire ce qui reste faisable.

18. **Ce qui compte, c'est ce qui s'affiche.** `edit_operation_results` renvoie `applied` pour une opération qui déborde du cadre, pour un texte blanc posé sur une pastille blanche, pour un disque rouge qui ressort d'un fond qu'on vient de repeindre. L'API confirme qu'elle a écrit, pas que c'est lisible. **Après chaque lot : regarder la miniature rendue.** Et quand on annonce un état (« 0 résidu », « tout est recoloré »), vérifier la chose annoncée sur les quatre porteurs de couleur, pas sur le seul texte — c'est comme ça que quatre illustrations un client précédent ont survécu quatre mois à un master déclaré neutre.

---

## ARCHITECTURE

Deux temps : une carte établie une fois, puis un run par client.

### La carte (une fois)

Le master neutre porte un placeholder par zone éditable de P2. La carte (`references/template-map.md`) enregistre, pour chaque zone : page, placeholder (texte d'ancre), label, type, budget caractères, cardinalité. Pas d'`element_id` figé, ils sont résolus au runtime. Voir ce fichier pour la mécanique et le format.

### Run (par client)

1. Master fixé par la règle 10, validé par le préflight. Entrée : le compte rendu du R1.
2. Interview de complétion (AskUserQuestion) pour les trous.
3. Remplissage des zones selon la carte, langue choisie, filtre anti-AI.
4. Validation intermédiaire : mapping zone vers contenu proposé, le lead valide.
5. Push Canva : copie du master, résolution des zones par placeholder, édition, aperçus, commit après OK.
6. Revue anti-AI finale.

---

## MÉCANIQUE CANVA (vérifiée)

Master à copier : **fixé par la règle 10** (`<MASTER_EN>` pour un R2, `<DIGEST>` pour un R1) et validé par le préflight à chaque run.

**Résolution par placeholder (pas d'ID figé), avec carte dérivée à l'exécution.** Le skill ne stocke ni `element_id` ni carte figée : il lit le master et construit sa carte à chaque run.

1. `copy-design` du master (par chunks de ~5 pages, voir Phase 5).
2. Ouvrir une transaction d'édition sur la copie : chaque élément revient avec son `element_id` (préfixe propre à la copie) et son texte.
3. **Construire la carte des zones à partir de ce qui a été lu**, pas d'un fichier. Repérer les zones à remplir par leurs marqueurs (`[...]`, `XX%`, `X,XXX €`) et, en mode remplacement, par le contenu client à écraser.
4. Éditer chaque zone par son `element_id` fraîchement résolu.

Pourquoi dériver plutôt que transporter : une carte stockée à côté du master survit à sa disparition et devient un mensonge silencieux. C'est exactement ce qui s'est produit avec `<DESIGN_ID>`. La résolution par placeholder rendait le skill robuste au **re-versionnage** du master ; la carte dérivée le rend robuste à son **remplacement**.
4. Zones sans texte (médias) ou à texte identique (les 4 `XX%`, les `[From...]` / `[To...]`) : départager par position (colonne `résolution` de la carte).

Conséquence : l'`element_id` peut changer d'un fichier à l'autre, ça n'a aucune importance. Tant que les placeholders sont là, la résolution tient, et un re-versioning du template ne casse rien.

**Opérations** (via `perform-editing-operations`) :

- `replace_text` (element_id, text) : remplacer tout le texte d'une zone.
- `find_and_replace_text` (element_id, find, replace) : remplacer une sous-chaîne (utile pour les `XX %` dans un bloc).
- `delete_element` (element_id) : supprimer un slot optionnel non utilisé.
- `recolor_element` (element_id, color hex) : recolorer une **forme vectorielle**. Vérifié le 27/07/2026.
- `format_text` (element_id, formatting.color) : recolorer un **texte**.
- `update_stroke_properties` (element_id, color, weight) : contours.
- Pages fixes : `position_element`, `resize_element` disponibles si besoin de réajuster après suppression.

Le connecteur expose aujourd'hui **27 opérations** (liste confirmée en direct le 19/08/2026 via une erreur de validation intentionnelle, qui renvoie toujours l'énumération exacte du schéma — technique fiable pour re-vérifier sans devoir lire une doc externe). Parmi les ajouts utiles depuis juin : `recolor_element`, `update_stroke_properties`, `insert_shape`, `insert_fill` (insertion d'image/vidéo, voir « Slot logo client »), `replace_shape`, `update_opacity`, `layer_element`, `group_elements` / `ungroup_elements`, `reorder_page`, `replace_speaker_notes`, `update_autofill_field`.

**Canva ne publie pas de patch notes pour son MCP.** La liste des opérations est donc à re-vérifier périodiquement : c'est ainsi qu'on a découvert `recolor_element`. Relire la liste `operations` du schéma `edit-design` avant de conclure qu'une chose est impossible.

**`element_id` attend le `locator_id` complet, pas l'id nu.** Le dump donne les deux : `id` (ex. `LBmH7HYk7FKtFgwq`) et `locator_id` (ex. `PB4vLShQQcPTSTfg-LBmH7HYk7FKtFgwq`, soit `PAGE-ELEMENT`). Passer l'id nu échoue avec `invalid_request` / « Page ID did not match the expected pattern » — message trompeur, puisque le problème est dans `element_id` et pas dans un paramètre `page_id`. Toujours transporter le `locator_id`.

Effet de bord utile : **une opération qui échoue renvoie quand même le `document` complet de la page**. Quand on n'a plus en mémoire que les ids nus (après une reprise de contexte, par exemple), envoyer l'opération avec l'id nu sert de sonde : elle échoue proprement, sans rien modifier, et rend la page avec tous ses `locator_id`. Un appel au lieu de deux.

**Flux d'édition** : `start-editing-transaction` (garder le `transaction_id`) → `perform-editing-operations` (en lot) → montrer les aperçus → OK du lead → `commit-editing-transaction`. Sans commit, rien n'est sauvé. Pour abandonner : `cancel-editing-transaction`.

### Slot logo client (changé le 19/08/2026)

Sur le master `<MASTER_EN>`, les 20 slots logo client ne sont **plus** un élément image unique (`RECT` avec `fill.media`, `isMediaReplaceable: true`) qu'on remplaçait par `update_fill`. Ils portaient encore le logo un client précédent en dur ; ils ont été remplacés par une **carte neutre à deux éléments** :
1. une forme (`shape`, rectangle blanc arrondi) aux mêmes position/taille que l'ancien slot,
2. un texte `[LOGO]` (petits slots, 18 occurrences) ou `[CLIENT LOGO]` (2 grands slots : couverture p2, séparateur p24) par-dessus, gras, centré.

Conséquence pour un run client : il n'y a plus de `update_fill` à faire ici. Pour poser le vrai logo du client, il faut soit (a) insérer un élément image par-dessus la carte puis supprimer le texte `[LOGO]`, soit (b) laisser le placeholder tel quel si le lead n'a pas fourni de logo.

**Résolu le 19/08/2026 — l'opération existe : `insert_fill`.** Absente des 29 opérations recensées le 27/07 (encore un cas « pas de patch notes »), elle a été découverte en testant en aveugle sur un `discriminator` invalide, qui a renvoyé la liste à jour (27 types). Testée et validée en conditions réelles (upload d'un vrai logo via URL fournie par le lead, insertion sur le master neutre) :

1. `upload-asset-from-url` (`url`, `name`) → renvoie un `asset.id` (`MAH...`).
2. `insert_fill` (`page_id`, `asset_id`, `asset_type: "image"` ou `"video"`, `alt_text`, `top`, `left`, `width`, `height`) → insère un élément `rect` avec `fill.media` pointant sur l'asset, positionné/dimensionné librement. Centrer dans la carte blanche existante (mêmes `top`/`left`/`width`/`height` que la forme, ou une version réduite avec marge).
3. `delete_element` sur le texte `[LOGO]`/`[CLIENT LOGO]` maintenant recouvert.

**Règle de traitement du logo (posée par le lead le 20/08/2026, non négociable).** Quand un vrai logo client est fourni, on **supprime la carte blanche** de fond en même temps que le texte `[LOGO]` — les trois éléments (forme + texte + ancien média) disparaissent, il ne reste que le logo. La carte blanche n'existait que pour porter le placeholder ; la garder derrière un vrai logo n'a pas de sens visuel. Et on pose le logo **plus grand** que le placeholder qu'il remplace, pour qu'il se voie : environ 215 × 87 px pour les 18 slots d'en-tête (contre 110 × 45 avant), environ 620 × 252 px pour la couverture p2 et le séparateur p24. Cadrage : coin haut-gauche à `top: 108, left: 108` pour les petits slots ; centré horizontalement pour les deux grands.

**Vérifier le fond du fichier logo avant de poser.** Un PNG à fond opaque (typiquement un logo « fond noir ») se fond parfaitement sur les pages à fond noir, mais dessine un rectangle visible sur les pages à dégradé rouge (p2, p24, p29, p41). Réclamer un **PNG à fond transparent** au lead quand c'est le cas ; à défaut, le signaler plutôt que de laisser passer.

Contrainte amont inchangée : `upload-asset-from-url` prend une URL, pas un fichier local. Si le lead colle une image dans la conversation sans URL, il faut soit qu'il l'uploade lui-même dans Canva, soit qu'il fournisse un lien où l'image est déjà hébergée (site, Drive public...) — jamais publier son fichier sur un hébergeur tiers à sa place pour lui fabriquer une URL.

---

### Médias clients scrapés sur les réseaux (dans le scope depuis le 20/08/2026)

**Pourquoi.** Un deck qui montre les vrais contenus du prospect prouve qu'on est allé voir ses réseaux. C'est un argument de vente en soi : le lead voit qu'on s'est renseigné, et les visuels parlent son branding au lieu de montrer des vidéos stock. Demande explicite du lead.

**Chaîne complète, testée de bout en bout le 20/08/2026** (compte Instagram réel, reel posé dans le deck) :

1. **Scraper** via Apify. Acteurs vérifiés :
   - Instagram reels : `apify/instagram-reel-scraper` — `{username: ["handle"], resultsLimit: N, includeDownloadedVideo: true}`
   - Instagram profil / posts : `apify/instagram-profile-scraper`, `apify/instagram-post-scraper`
   - TikTok : `clockworks/tiktok-profile-scraper` — `shouldDownloadVideos`, `shouldDownloadCovers`, `shouldDownloadSlideshowImages`
   - Recherche de compte quand le handle est incertain : `apify/instagram-scraper` avec `{search: "nom", searchType: "user"}`
2. **Récupérer** les résultats : `get-dataset-items` sur le `datasetId` du run. Le champ **`downloadedVideo`** contient une URL `api.apify.com/v2/key-value-stores/…` directement exploitable. `displayUrl` donne la cover, utile en repli.
3. **Importer** dans Canva : `upload-asset-from-url` accepte **les vidéos comme les images** (vérifié : mp4 vertical 540×960 importé, renvoie un `asset.id` en `VAH…` et `type: "video"`).
4. **Poser** : `update_fill` (`element_id`, `asset_id`, `asset_type: "video"`, **`alt_text` obligatoire**) sur un slot vidéo existant, ou `insert_fill` pour créer un nouvel élément.

**Repli quand le compte n'a pas de vidéo** : prendre les images de carrousel ou les covers (`displayUrl`), même chaîne avec `asset_type: "image"`.

**Coût** : ~0,002-0,003 $ par résultat, +0,001 $ par téléchargement vidéo. Une passe sur un compte client coûte quelques centimes.

**Vérifier que le compte existe avant de conclure.** Un handle inexistant renvoie `error: "not_found"` / `"Post does not exist"` dans le dataset, avec un run en `SUCCEEDED` — l'échec est donc **silencieux au niveau du run**. Toujours lire les items, jamais se fier au seul statut. Si le handle donné par le lead est faux, chercher le bon compte et **faire arbitrer** plutôt que de scraper un homonyme de son propre chef.

### Carte des slots vidéo du master (relevée le 20/08/2026)

Le master `<MASTER_EN>` contient **13 slots vidéo**, tous `isMediaReplaceable: true`. Dix sont en P2 et se remplissent ; **trois sont en P1 et ne se touchent jamais** (règle 2).

| Page | Slots | Format | Ce que le slot doit montrer |
|---|---|---|---|
| 25 — diagnostic intro | 1 (423×752) | portrait large | **Un contenu du prospect lui-même.** C'est la preuve qu'on est allé voir ses réseaux. |
| 33 — same country, different cultures | 2 (313×556) | portrait | **Les deux exécutions de la marque de référence citée sur la page** : une FR, une NL. Voir la règle ci-dessous. |
| 35 — pilier 1 | 2 (289×427 et 271×427) | portrait | Deux exemples illustrant le pilier 1 |
| 36 — pilier 2 | 2 (288×459) | portrait | Deux exemples illustrant le pilier 2 |
| 37 — pilier 3 | 3 (264×425, 239×425, 239×425) | portrait | Trois exemples illustrant le pilier 3 |
| 11, 19, 21 — P1 agence | 3 (1920×1080) | plein écran | **P1. Ne jamais toucher.** |

Tous les slots P2 sont au format **portrait vertical** : ne poser que des reels ou des TikTok, jamais du paysage.

**La référence se prend dans le portefeuille socialsky — et la proximité sectorielle passe avant tout le reste.** Citer un client qu'on a réellement accompagné vaut mieux qu'un exemple générique. Mais **le critère n°1 est que le prospect s'y reconnaisse** : une référence alimentaire face à une marque de luminaires ne démontre rien, même si c'est un beau case avec de beaux chiffres. Ordre de choix : (1) client socialsky du **même secteur ou d'un secteur adjacent** ; (2) à défaut, le plus proche possible en modèle économique (retail-produit → retail-produit). Ne jamais privilégier un client au seul motif qu'il possède la bonne caractéristique structurelle (bilingue, gros volume, award) si son secteur est étranger à celui du prospect.

> **Erreur type, à ne pas répéter.** Sur un prospect du secteur luminaires et décoration, la référence retenue pour la page 33 était un retailer alimentaire — choisi parce qu'il était le cas le mieux documenté et le plus bilingue du portefeuille. Le lead a corrigé : l'alimentaire n'a rien à voir avec la lumière, la démonstration tombe à plat. Un retailer d'équipement de la maison, également au portefeuille, était le bon choix et avait été identifié — le mauvais critère l'a emporté. **Tenir à jour la liste des clients et de leur secteur, et la vérifier à chaque run** : elle bouge.

**Règle de la page 33 : la vidéo suit la référence, pas l'inverse.** La page nomme une marque de référence (zone `[Reference: example brand]`) et montre deux exécutions, FR et NL. Les deux vidéos doivent venir **du compte de cette marque-là**, une en français et une en néerlandais — sinon la démonstration ne tient pas. La référence **change à chaque client** : elle se choisit dans le secteur du prospect, et c'est elle qui détermine quel compte scraper. Ordre des opérations : choisir la référence avec le lead → scraper son compte → poser ses deux vidéos → seulement alors écrire le texte des deux exécutions à partir de ce qu'on voit vraiment dans ces vidéos.

### D'où viennent les vidéos : l'ordre de priorité

**1. Le prospect lui-même.** Prouve qu'on est allé voir ses réseaux. Obligatoire sur la page 25.

**2. Ses concurrents directs. C'est la source principale pour les piliers.** Un deck qui montre ce que font les concurrents du prospect a une valeur commerciale que n'aura jamais une vidéo de niche anonyme : le lead se reconnaît, voit le terrain, et comprend ce qu'il rate. Méthode :
   - Établir la liste des concurrents **avec le lead** ou depuis les docs client. Ne pas l'inventer.
   - Pour chacun, trouver le compte Instagram et TikTok. Vérifier qu'il existe (`apify/instagram-profile-scraper` en lot sur plusieurs handles candidats — voir le piège `not_found` plus haut).
   - Vérifier qu'il publie des reels et à quelle fréquence : c'est déjà un constat pour le diagnostic (« vos trois concurrents publient X fois par semaine, vous zéro »).
   - Récupérer les reels via `apify/instagram-reel-scraper` et les répartir par pilier selon ce qu'ils montrent.
   - Bénéfice secondaire : le scraping concurrentiel nourrit **aussi** les pages diagnostic et sector signals, pas seulement les slots vidéo.

**3. La recherche par sujet dans la niche.** Dernier recours, quand le prospect n'a pas de contenu et que les concurrents non plus. Le résultat est plus générique et le tri plus long.

### Trouver des vidéos par niche (et pas seulement par compte)

Quand ni le prospect ni ses concurrents ne fournissent — pilier que personne ne produit encore, ou comptes vides — chercher **par sujet** dans sa niche. Vérifié le 20/08/2026 (hashtag déco → 3 vidéos pertinentes téléchargées) :

- **TikTok par hashtag ou par recherche** : `clockworks/tiktok-scraper` — `{hashtags: ["..."], resultsPerPage: N, shouldDownloadVideos: true, shouldDownloadCovers: true}`. Accepte aussi `searchQueries` pour une recherche en langage naturel, et `videoSearchSorting` / `videoSearchDateFilter` pour trier.
- **Instagram par hashtag** : `apify/instagram-hashtag-scraper`.

**⚠️ Passer par Instagram pour tout ce qui doit finir dans Canva. Le circuit TikTok ne fonctionne pas pour l'import** (constaté le 20/08/2026) :
- `clockworks/tiktok-scraper` avec `shouldDownloadVideos: true` écrit dans un key-value store **privé** : l'URL renvoyée par `mediaUrls` / `downloadAddr` répond **403** à Canva. Vérifiable en une commande : `curl -o /dev/null -w "%{http_code}" <url>`.
- Sans `shouldDownloadVideos`, l'actor ne renvoie **plus aucune URL vidéo** — le champ `downloadAddr` disparaît du schéma. Il n'y a donc pas de repli côté TikTok.
- `apify/instagram-reel-scraper` avec `includeDownloadedVideo: true` écrit dans un store **public** : l'URL du champ `downloadedVideo` répond 200 et s'importe sans problème. C'est le seul circuit fiable, vérifié quatre fois.

TikTok reste utile en **repérage** (sa recherche par sujet est meilleure) : on y identifie les comptes et les thèmes, puis on récupère les vidéos via Instagram. `apify/instagram-hashtag-scraper` sert à trouver des comptes par hashtag, mais **ne télécharge pas de vidéo** — il ne remplace pas le reel-scraper.

**Ce qu'il faut vraiment en entrée : une URL de fichier, pas une URL de page.** `upload-asset-from-url` sait avaler un `.mp4` accessible publiquement ; il ne sait pas extraire une vidéo d'une page `tiktok.com/@x/video/123` ou `instagram.com/p/xxx`. Tout l'étage scraping ne sert qu'à convertir la seconde en la première. Conséquence pratique : si le lead fournit des liens de posts ou un handle, on gagne énormément de temps — on lance le reel-scraper directement sur ces posts au lieu de chercher.

**Trier avant de poser — les résultats bruts d'un hashtag sont un panier mélangé.** Le test a rendu, sur un même hashtag déco, une vidéo espagnole, une américaine et une togolaise. Filtrer sur :
1. **La langue et le marché** — `textLanguage` et le contenu de `text` (la légende). Pour un client belge, écarter ce qui ne parle ni FR ni NL.
2. **La traction** — `playCount`, `diggCount`, `authorMeta.fans`. Une vidéo à 300 vues n'illustre pas un pilier qui marche.
3. **Le format** — `videoMeta.width`/`height` : ne garder que le vertical (hauteur > largeur).
4. **Le fond** — lire `text` pour vérifier que la vidéo montre bien ce que le pilier annonce. Une vidéo déco n'est pas forcément une vidéo *de fabrication*.

Ne jamais poser une vidéo sans avoir lu sa légende : le deck affirme quelque chose, la vidéo doit le prouver.

---

### Neutraliser un master, ce n'est pas seulement neutraliser son texte

Le master `<MASTER_EN>` était déclaré « 0 résidu un client précédent » depuis le 18/08/2026. C'était vrai **du texte seul**. Quatre **illustrations** de l'ancien client y ont survécu quatre mois, invisibles pour tous les contrôles, parce que le contrôle qualité lit des chaînes de caractères et que personne n'avait ouvert le deck en mode présentation.

> **Retirées le 20/08/2026** (signalées par le lead à l'œil) : personnages 3D sur fond orange un client précédent, `MAHE9l0HhIU` (p24), `MAHE95QB-aA` (p30 et p31), `MAHE9zxw7tU` (p34). Contenu : clés de voiture, vase cassé, valise de voyage — de l'imagerie de sinistres d'assureur, sans aucun rapport avec un client de socialsky.

**La méthode pour vérifier un master, ou pour purger une copie :** lire le design, lister **tous** les `rect` porteurs d'un `fill.media`, et soustraire les assets socialsky légitimes. Ce qui reste est suspect par défaut.

```
Assets socialsky à conserver (relevé du 20/08/2026)
  MAG-iHdEW5I   le « s » socialsky          MAHAdcsVaqE   logo Social OS™
  MAG-iHxzyuw   wordmark SOCIALSKY          MAHFkHaE7sw  MAHFkFdb_YU   icônes TikTok / Instagram
  MAG-iO_fASs   baseline                    MAHHn…        photos de l'équipe (p40)
```

**Le préfixe est un indice fort mais pas une preuve** : les assets un client précédent commencent par `MAHE9…`, les socialsky par `MAG-…`, `MAHA…`, `MAHF…`, `MAHHn…`. Vérifier au thumbnail avant de supprimer.

**Reste non corrigeable par API** : les icônes TikTok et Instagram des pages 35 à 37 portent une carte de recoloration `{"#000000": "#ff6f0d"}` — l'orange un client précédent. `recolor_element` renvoie `not_permitted` sur une image à carte de recoloration (limitation documentée). À reprendre à la main dans Canva.

### Un transcript automatique invente des noms propres

**Vérifier chaque nom de marque, de personne et de lieu avant de le mettre sur une slide.** Les transcripts d'appel sont produits par reconnaissance vocale : sur un nom qu'elle ne connaît pas, elle ne laisse pas un blanc, elle **fabrique un mot plausible** — et le répète ensuite de façon cohérente, ce qui le rend crédible.

> **Cas le prospect, 20/08/2026.** Le transcript nommait quatre fois « Alliage » l'enseigne rachetée par le prospect. Elle s'appelle **Santis** : reprise annoncée le 28/05/2024, dix pharmacies en région liégeoise, réseau porté à 57 officines. Aucune trace publique d'« Alliage » nulle part. Le nom inventé est parti sur **quatre slides** du deck avant d'être corrigé. Le même transcript écrivait « Averdé » pour le prospect et « Mehdi Marquet » pour un concurrent du prospect — mêmes symptômes, mais ceux-là étaient repérables.

**Le test :** tout nom propre issu d'un transcript doit exister quelque part ailleurs — site du client, presse, registre d'entreprises. **Une recherche web de trente secondes par nom.** S'il n'existe nulle part, ce n'est pas une marque discrète, c'est une hallucination de la reconnaissance vocale. Les faits qui l'entourent (dates, volumes, lieux) sont généralement corrects et suffisent à retrouver le vrai nom.

### Le français déborde : leçons du run récent (20/08/2026)

Le master a été dimensionné sur des libellés anglais. **Le français est plus long de 15 à 20 %**, et chaque zone remplie en français a de bonnes chances de déborder. C'est le défaut le plus répété du premier run FR : sept corrections de largeur sur treize pages.

**Le correctif standard : `resize_element` avec `width` seul.** Sur un élément `text`, ne jamais passer `height` (le schéma l'interdit, la hauteur se recalcule). Élargir le cadre plutôt que raccourcir le texte, tant que rien ne se trouve à droite. Cas rencontrés :

| Symptôme | Cause | Correctif |
|---|---|---|
| « Avant » rendu « Avan / t » | cadre calibré sur « From » (4 car.) | `width` 114 → 190 |
| « Ressenti » rendu « Resse / nti », chevauche la ligne suivante | cadre calibré sur « Feeling » (7 car.) | `width` 146 → 240 |
| « Options disponibles » coupé | cadre calibré sur « Available add-ons » | raccourcir en « En option » |
| `XX%` → « 58,9 % » qui dépasse | cadre calibré sur 3 caractères | `width` 171 → 240 |

**Vérifier au thumbnail après chaque lot, pas à la fin.** Un débordement ne remonte dans aucun `edit_operation_results` : le statut est `applied_unverified` même quand le rendu est cassé. Seul l'aperçu le montre.

### Zones du master qui ne sont PAS neutralisées (relevé le 20/08/2026)

Trois angles morts, à traiter en mode remplacement et non par placeholder :

1. **La navigation latérale est en dur en anglais** — `diagnosis`, `sector signals`, `current state`, `priorities`, `strategic approach`, `platform roles`, `Cultural layer`, `content strategy`, `Pillar 01/02/03`, `team`. Environ 40 éléments sur une quinzaine de pages. Sur un deck français, les laisser produit un document bâtard. Les traduire à mesure, dans le lot de chaque page. **Exceptions à garder en anglais** (règle 9) : `social-os`, `way of working`, `always-on`, `kick-off`, `scope`, les cinq phases du Social OS™ et l'échelle `AWARENESS → RECURRENCE → RELEVANCE → PREFERENCE`.
2. **La page 40 (équipe) porte de vrais noms socialsky** avec des rôles FR et NL. Pour un client monolingue, la moitié de l'équipe affichée ne parle pas sa langue. Ne jamais réaffecter les personnes soi-même — c'est un constat inventé. Documenter la question en note de présentateur et faire trancher.
3. **La page 42 (prix) a perdu les mentions obligatoires** relevées comme invariantes dans les 7 templates : pas de `FEE STARTING AT`, pas de `RIGHTS OF USE`. Les rajouter avec `add_text`. **Piège :** `add_text` crée le texte en **noir par défaut** ; sur un fond noir il est invisible. Enchaîner avec `format_text` (`color`) dans le lot suivant.

### Les notes de présentateur sont le bon endroit pour les sources

`replace_speaker_notes` (5 000 caractères par page) résout le conflit entre « citer ses sources » et « ne pas surcharger la slide ». Sur un run récent : les quatre sources des signaux secteur, l'origine exacte du prix avec la citation verbatim du commercial, la précaution méthodologique sur les chiffres scrapés, et les arbitrages laissés au lead. Le deck reste lisible, le commercial a tout sous la main en mode présentation.

---

## THÉMATISATION COULEUR (dans le scope depuis le 27/07/2026)

**Cette section a été réécrite. Le connecteur Canva a évolué et le re-thèmage est désormais faisable.** L'ancienne version disait le contraire : elle reste dans une sauvegarde locale.

État vérifié le 27/07/2026 (test sur une copie du deck un autre client, 5 opérations sur 5 réussies) :

- **Texte** : `format_text` (champ `color`) recolore un élément texte par `element_id`. Recolorable. *(inchangé)*
- **Images / vidéos** : `update_fill` remplace l'asset. Logo et creative swappables. *(inchangé)*
- **Formes vectorielles** : **recolorables** via `recolor_element` (`element_id` + `color` hex). L'ancien échec venait de l'emploi d'`update_fill`, qui n'est pas la bonne opération pour une forme et renvoie « The shape does not contain an editable fill ». `recolor_element` n'existait pas en juin 2026.
- **L'API renvoie désormais la couleur des éléments.** Chaque `SHAPE` expose `path[0]: ... fill=#rrggbb`, chaque région de `TEXT` expose `color=#rrggbb`. Plus besoin de repérer les accents à l'œil sur le thumbnail.
- **Le flag `replaceable=false`** sur le fill d'une forme **ne bloque pas** `recolor_element` : il concerne le remplacement d'asset, pas la recoloration.
- **Contours** : `update_stroke_properties` (`color`, `weight`).

### Mécanique de re-thèmage
Il n'existe pas d'opération native « remplace toutes les couleurs X par Y ». On l'obtient en trois temps, côté skill :

1. **Lire** le deck (`read-design`, `design_content`) et collecter, par page, chaque `element_id` avec sa couleur.
2. **Filtrer** sur le hex source à remplacer (couleur de la marque d'origine).
3. **Émettre** un `recolor_element` par forme et un `format_text` par texte, en lot dans la transaction de la page.

Une seule couleur source peut porter sur des types différents sur la même page (une forme + plusieurs textes) : il faut donc appliquer les deux opérations, pas une seule.

### Ce qui NE se recolore pas (vérifié sur 42 pages le 27/07/2026)

| Cas | Symptôme | Contournement |
|---|---|---|
| **Forme verrouillée** (`locked: true`) | `not_permitted` : « Selected entity cannot be recolored » | Déverrouiller à la main dans Canva, puis relancer. Le message d'erreur ne mentionne PAS le verrou : toujours lire le flag `locked` dans le dump avant de conclure. **Fait le 19/08/2026** sur les 3 dernières bandes du master `<MASTER_EN>` (p32/p41/p42) : geste manuel du lead dans Canva, `recolor_element` a ensuite fonctionné normalement une fois le flag à `false`. |
| **Ligne** (`LINE`) | Était `not_supported` : « Cannot update stroke on this entity » (constaté le 27/07/2026, `update_line_properties` n'exposait alors aucun champ couleur). | **Débloqué depuis, constaté le 19/08/2026** : `update_stroke_properties` (`element_id`, `color`, `weight`) fonctionne désormais sur les éléments `LINE`. Vérifié sur les 5 lignes de la p32 du master `<MASTER_EN>`, recolorées `#ff6f0d` → `#f50c45` sans erreur. Nouvel exemple du principe « pas de patch notes, revérifier périodiquement » de la section suivante. |
| **Fond de texte** (*highlight*) | Aucun symptôme : l'élément **n'apparaît nulle part** dans la liste. Vérifié p26 — 4 pastilles orange visibles au rendu, 17 éléments listés, aucun ne les porte. | Aucun. `format_text` n'expose pas de champ de fond. À traiter à la main. **Et la reconstruction ne sauve pas la mise** (vérifié le 24/08/2026) : supprimer le texte puis le refaire en forme + `add_text` fait retomber la police sur le défaut Canva `YACgEZ1cb1Q` au lieu de l'Oldschool Grotesk du deck (`YAHARS4rVeQ`), et `format_text` n'a aucun paramètre de police. Le remède est pire que le défaut — ne pas tenter, et corriger dans le master. |
| **Image à carte de recoloration** (`recoloring={#src:#dst}`) | `not_permitted` : « target.type="rect-element" Selected entity cannot be recolored » | Aucun. **Vérifié le 18/08/2026** sur les icônes réseaux sociaux (p35-37) et les logos recolorisés (p2, p43). À traiter à la main. |

**Piège de diagnostic** : c'est très probablement un de ces trois cas qui a fait conclure en juin que « les formes ne sont pas recolorables ». Un échec sur un élément verrouillé ressemble exactement à un échec de capacité. Toujours vérifier le flag `locked` avant de généraliser.

### `layer_element` casse le rendu d'une forme insérée par API (vérifié le 25/08/2026)

`insert_shape` pose une forme qui s'affiche correctement — **tant qu'elle reste au-dessus de tout**. Dès qu'on applique `layer_element`, la forme **disparaît du rendu** alors qu'elle reste présente dans le document, avec ses bonnes coordonnées, sa bonne taille et sa bonne couleur.

Reproduit dans les quatre configurations : `position: back` sur la forme, `position: front` sur le texte, les deux dans la même transaction, et les deux séparés par un commit. Constaté sur le rendu de transaction, sur le rendu après commit et dans l'éditeur rechargé — ce n'est pas un cache de miniature.

**Conséquence : on ne peut pas construire « forme derrière texte » par API.** Or c'est le seul montage qui rend une pastille recolorable par client (voir « Fond de texte » ci-dessus).

**Le partage de travail qui marche** : poser les formes **par API** — la géométrie est exacte du premier coup, calculée depuis la boîte du texte — puis les **reculer à la main** dans l'éditeur, où l'opération fonctionne normalement. Un geste par forme, et le gabarit devient re-thèmable pour toujours.

**Reculer la forme ne suffit pas : il faut aussi éteindre l'effet.** Une forme posée et reculée sous un texte qui porte encore son effet « Arrière-plan » coloré reste **totalement invisible** — l'effet la recouvre exactement, au pixel près, puisqu'il épouse la même boîte de texte. Le document rapporte alors la forme à la nouvelle couleur pendant que le rendu montre l'ancienne : rien n'a échoué, la couleur est simplement cachée dessous. Le geste manuel est donc **double, par pastille** : reculer la forme *et* passer l'effet « Arrière-plan » du texte sur **Aucun**. Tant que le second manque, la page ne se re-thème pas et la couleur du gabarit se propage à tous les decks clients.

### Le fond de page n'est pas modifiable par API

`edit-design` accepte exactement 27 types d'opérations, et **aucune ne touche au fond de page** : `update_title`, `replace_text`, `update_fill`, `insert_fill`, `delete_element`, `find_and_replace_text`, `position_element`, `resize_element`, `format_text`, `add_text`, `insert_shape`, `replace_shape`, `add_page`, `update_opacity`, `layer_element`, `recolor_element`, `rotate_element`, `group_elements`, `ungroup_elements`, `flip_media`, `crop_media`, `reorder_page`, `replace_speaker_notes`, `update_text_anchoring`, `update_stroke_properties`, `update_line_properties`, `update_autofill_field`.

Le fond apparaît pourtant en lecture, dégradé compris (`background.color.type: "linear_gradient"` avec ses `stops`) — **lisible, non modifiable**. Toute page dont le fond porte une couleur de marque garde donc celle du gabarit dans tous les decks clients.

**Conséquence pour le gabarit** : une page qui doit se re-thémer se construit sur un fond neutre (noir ou blanc), la couleur client étant portée par une **forme** posée dessus. Un fond coloré est un choix définitif, à réserver aux pages qui doivent rester aux couleurs de l'agence.

**Piège de vérification associé, et sa solution** : le service de miniatures sert des versions en cache, signalées par `fallbackstale=T` dans l'URL. Après une modification de couleur ou de calque, une miniature peut montrer l'état d'avant — et deux pages du même appel peuvent revenir l'une fraîche, l'autre périmée. Ne jamais confirmer un état sur une vignette marquée stale.

**La méthode fiable, c'est `export-design`** (constatée le 25/08/2026). Un export PNG avec `format.pages` sur les seules pages à contrôler force un rendu neuf, hors cache, et se télécharge en une commande. C'est la seule vérification qui fait autorité sans ouvrir l'éditeur — beaucoup plus rapide et plus sûr que de piloter le navigateur, qui se bat avec un filmstrip virtualisé et une vue grille capricieuse.

```
export-design  design_id, {type: "png", pages: [26, 32, 41, 42], width: 900}
→ curl les URLs renvoyées, puis regarder les images
```

### Ce que la lecture ne montre pas d'emblée
Le premier balayage doit couvrir **quatre** porteurs de couleur, pas deux :
1. `SHAPE` → `path[0]: ... fill=#rrggbb`
2. `TEXT` → `regions[n] ... color=#rrggbb`
3. `LINE` → `stroke: weight=N color=#rrggbb` (non modifiable, mais à compter dans la carte)
4. `RECT` avec fill IMAGE → `recoloring={#src:#dst}`

Oublier 3 et 4 donne une carte des couleurs incomplète et un deck qui reste partiellement à l'ancienne couleur après balayage.

### La couleur du client se déduit de son logo

Le lead ne fournit pas de charte. Le logo, lui, est déjà là (règle 11 bis : il se cherche, il ne se demande pas). Il porte la réponse.

**Méthode, sur un logo SVG** : parser les tracés, calculer l'aire couverte par chaque couleur, classer. La couleur dominante en surface est la primaire ; la seconde est l'accent. Sur un run récent (`https://www.prospect-connect.be/.../logo.svg`) :

| Couleur | Aire | Part | Tracés | Rôle |
|---|---|---|---|---|
| `#004079` | 6 213 px² | 54,0 % | 8 | primaire — le bleu marine |
| `#dddc15` | 5 289 px² | 46,0 % | 2 | accent — le jaune |

Ne pas se fier au coup d'œil : sur ce logo, le jaune saute aux yeux alors qu'il est minoritaire. L'aire tranche, l'œil non.

**Sur un logo bitmap**, la même logique s'applique par quantification des pixels, en excluant le blanc et le transparent. À défaut, demander au lead — mais après avoir essayé, jamais avant.

**Règle d'application** : la primaire porte les bandeaux latéraux, les numéros, les accents sur fond clair. **L'accent ne sert qu'aux endroits où la primaire deviendrait illisible** — typiquement un texte d'accent posé sur fond noir. Sur un run récent, deux cas seulement sur tout le deck (p30 « appliqué à le prospect. », p33 « une enseigne de référence »). Ne pas alterner les deux couleurs « pour faire joli » : ça se lit comme une hésitation.

**Contrôler le contraste après coup, pas avant.** Recolorer une forme change ce qui est lisible dessus. Deux conséquences vues sur un run récent :
- p42, la carte du pack mensuel passe en bleu marine → ses deux textes noirs deviennent illisibles, il faut les basculer en blanc dans le même lot.
- p25, les libellés de navigation passés en blanc **disparaissent** — ils sont posés sur des pastilles de fond de texte blanches. Retour à `#000000`. Corollaire utile : **la couleur du bandeau n'a aucun effet sur la lisibilité de la nav**, puisque celle-ci ne repose jamais directement dessus.

### Le fond de page n'est pas un élément — et ça se contourne

Les pages séparateurs et pleine couleur (North Star, équipe) ne portent pas de bandeau : leur couleur est le **fond de page**, un `linear_gradient` exposé en lecture sous `background.color` mais **absent de la liste des éléments**. Aucun `element_id`, donc ni `recolor_element` ni `update_fill`. Il n'existe pas d'opération `update_background` dans les 27.

**Contournement vérifié le 20/08/2026** (pages 29 et 40 du deck le prospect), en trois opérations et deux appels :

1. `insert_shape` — `page_id`, `path: "M0 0H64V64H0z"`, `view_box_width: 64`, `view_box_height: 64`, `top: 0`, `left: 0`, `width: 1920`, `height: 1080`.
2. `recolor_element` sur la forme qui vient d'être créée, à la couleur primaire du client.
3. `layer_element` — `element_id`, `position: "back"`.

Trois pièges, tous rencontrés :
- **`insert_shape` exige `path` + `view_box_width` + `view_box_height`.** Un simple `shape: "rectangle"` est rejeté. Reprendre le path des bandeaux existants (`M0 0H64V64H0z`) évite d'en inventer un.
- **`insert_shape` ignore `fill_color`.** La forme naît sans couleur, donc invisible : le rendu ne bouge pas et on croit à un échec. D'où l'étape 2, obligatoire — et d'où les deux appels, puisque l'`element_id` de la nouvelle forme n'est connu qu'au retour du premier.
- **`layer_element` prend `position: "front" | "back"`**, pas `action`.

Le dégradé d'origine reste sous l'aplat, intact. C'est réversible : supprimer la forme suffit.

**Ce que ce contournement révèle en dessous** : sur la page équipe, les photos portent un disque rouge socialsky cuit dans l'image (`MAHHn…`). Invisible sur fond rouge, il ressort dès que le fond devient bleu. À arbitrer avec le lead : ou on redécoupe les photos, ou on assume les pastilles rouges comme la signature de l'agence sur la couleur du client.

**Ce qu'on ne recolore PAS** : la page de fin (p43), qui porte le wordmark socialsky et la baseline. C'est la signature de l'agence, pas du client. Elle reste rouge.

### Prudence
Vérifier avec le lead **quelle** couleur remplacer avant de balayer : sur un deck client, un même orange peut être un résidu de la marque du deck d'origine **ou** la couleur légitime du client. L'API donne le hex, pas son intention. En cas de doute, sortir la carte des couleurs et faire arbitrer.

### Lire un deck de 42 pages sans saturer le contexte
`read-design` avec `open_transaction: true` et sans `page_indices` renvoie le CDF complet des 42 pages (~247 000 caractères). C'est le payload que la v1 jugeait « trop gros à relire ». Il n'est pas trop gros pour être **traité** : le laisser être écrit sur disque, puis le parser en script (découpe sur `# Page N`, extraction des hex par type d'élément). On obtient la carte complète des couleurs en un seul appel de lecture, au lieu de 42.

---

## PHASE 1 : ENTRÉE ET EXTRACTION

**L'entrée principale est le compte rendu du R1** — notes de réunion, transcript d'appel, enregistrement retranscrit. C'est là que se trouve tout ce qui rend le P2 juste : ce que le prospect a dit de ses problèmes, de ses objectifs, de ses contraintes, et le vocabulaire qu'il emploie lui-même. Les autres documents (infos brand, données commerciales) complètent, ils ne remplacent pas.

**Pas de compte rendu de R1 = pas de P2.** Le réclamer avant de commencer, plutôt que de produire un diagnostic déduit du nom de l'entreprise — c'est exactement ce que la règle 4 interdit.

Lire et extraire :

- Secteur, marque, audience cible, plateformes actuelles.
- Constats issus des échanges (problèmes de fit, frictions, ambition).
- Données chiffrées fournies (stats secteur, budgets, volumes, prix).
- Toute précision sur le scope, l'équipe, le planning.

Confirmer ce qui est compris, ne demander que ce qui manque.

---

## PHASE 2 : INTERVIEW DE COMPLÉTION

`AskUserQuestion` pour les blocs manquants. Ne pas produire tant que le minimum n'est pas réuni.

- **Langue du deck** : EN / FR.
- **Nom client** tel qu'il apparaîtra.
- **Données manquantes** : tout `XX %` ou `X XXX €` sans source. Réclamer ou marquer `TODO`.
- **Cardinalité** : 2 ou 3 priorités ? 3 piliers de contenu ? Combien de cases pertinents ?

---

## PHASE 3 : REMPLISSAGE DES ZONES

Pour chaque zone de la carte, produire le texte dans la langue choisie, dans le budget caractères (par ligne, avec sauts de ligne explicites), filtré anti-AI. Respecter la cardinalité (marquer les slots à supprimer). Jamais de donnée ni de constat inventé.

Guide par section (but, ce qu'il faut, patron d'écriture, propre au client vs fixe socialsky) : `references/content-playbook.md`. Distinction clé : les titres des 5 phases du Social OS™ et la structure way of working sont fixes ; le génératif porte sur diagnostic → North Star → piliers.

---

## PHASE 4 : TRACE, PAS BARRAGE

Sortir un mapping `label de zone` → `texte proposé`, avec pour chaque : budget vs longueur réelle, et alerte si donnée manquante (`TODO`). Format markdown, dans le dossier de travail sélectionné.

Ce mapping n'est **pas une étape de validation** : c'est une trace, et elle part **avec** le deck à la livraison, jamais avant. Le lead lit le deck fini et le mapping en même temps, puis corrige ce qu'il veut en une seule passe. Ne jamais suspendre le run pour le lui faire relire.

---

## PHASE 5 : PUSH CANVA

Mécanique prouvée sur une page (test page 24 : 6/6 `replace_text` en succès, aperçu draft conforme).

### Résolution des zones (par placeholder)
À l'ouverture d'une transaction, chaque élément a un `element_id` et son texte. Pour chaque zone de la carte, retrouver l'élément dont le texte égale le placeholder, puis éditer par cet `element_id`. Pour les zones sans ancre texte unique (médias, `XX%`, `[From...]` / `[To...]`), départager par position. Si un placeholder de la carte est introuvable sur la page attendue, le signaler (la carte ou le master a changé), ne pas deviner.

### Opérations
- `replace_text` (element_id, text) : texte, avec les `\n` voulus (budget par ligne, règle 7).
- `delete_element` : slots optionnels non utilisés (texte + numéro + forme du groupe de suppression).
- `update_fill` (image/video, asset_id) : médias, après `upload-asset-from-url` de l'asset client.
- `recolor_element` / `format_text` : re-thèmage couleur, si demandé (voir la section Thématisation couleur).
- Passer le `transaction_id`, le `page_index` et le tableau `pages` retournés par `start-editing-transaction`.

### Validation obligatoire après chaque lot
Le connecteur renvoie désormais `status: "edits_unverified"` et exige une vérification avant tout édit suivant : comparer le thumbnail **avant** (capturé via `read-design`, champ `thumbnails`) au thumbnail **après** retourné par l'édition, puis relire le `document` pour confirmer les nouvelles valeurs. Ne pas enchaîner sur la page suivante sans cette double vérification.

Édition et finalisation sont deux appels **séparés** : on ne peut pas combiner `operations` avec `finalize: "commit"` ou `"cancel"`. Commit et cancel se font avec `operations` vide.

**Piège du `transaction_id` (constaté le 18/08/2026).** L'ID de transaction est une chaîne de ~19 chiffres. Si l'environnement d'exécution convertit les chaînes numériques en nombres (JSON parse), l'ID **perd sa précision** (…768 devient …000) et la transaction devient inutilisable. Symptômes : `Expected string, received number` sur `transaction_id`, ou une alternance d'erreurs `Expected boolean/object, received string` sur les autres champs. Dans ce cas : (1) l'environnement se verrouille en mode dégradé après la première erreur de validation — **reconnecter le connecteur Canva** pour le réinitialiser ; (2) après reconnexion, passer le `transaction_id` **entouré de guillemets JSON littéraux** dès le premier appel, sans aucune erreur de validation avant lui.

### Construction par morceaux
On édite P2 par morceaux (chunks), puis on assemble.

- **Édition en place de chunks (testé)** : copier un chunk de ~5 pages P2 → `start-editing-transaction` reste INLINE et lisible → apparier chaque élément à son placeholder (carte) et `replace_text` en lot → commit. Validé sur les pages 24-28 (32 opérations sur 32). C'est le bloc de construction.
- **Pourquoi des morceaux** : une transaction sur les 42 pages renvoie un payload trop gros à relire ; un chunk de ~5 pages reste lisible. Donc éditer P2 en chunks de ~5 pages en place, jamais en une transaction sur tout le deck.
- **Assemblage** : une fois les chunks édités et validés, les assembler en un deck complet. En attendant, chaque chunk édité est livrable tel quel.

### Lien et livraison
1. Dès la copie créée (`copy-design`), la **renommer** (`update_title` → « Socialsky - SD Sales - [Client] ») et donner son lien d'édition au lead : il suit les édits en direct s'il le souhaite, sans que le run l'attende.
2. Après chaque lot, vérifier le **document renvoyé par l'API** — texte, largeur, hauteur, corps de police — et corriger par le calcul. Pas d'images à ce stade, pas de validation demandée au lead.
3. `commit-editing-transaction` dès que le lot est écrit et vérifié. `cancel-editing-transaction` seulement si le lot est raté et doit être refait.
4. **Contrôle qualité obligatoire** (Phase 5 bis). Ne pas livrer tant qu'il reste un bloquant.
5. **Déplacer la copie dans `Sales Desk - Finaux`** (`<DOSSIER_SORTIE>`) via `move-item-to-folder`. C'est la sortie du processus : un deck fini ne reste pas à la racine.
6. Livrer le **lien d'édition** (`edit_url`), pas le `view_url` ni un PDF — le commercial ajuste le deck avant et pendant le rendez-vous.

---

## PHASE 5 BIS : CONTRÔLE QUALITÉ AVANT SORTIE (obligatoire)

Avant de livrer le lien Canva au lead, faire passer le deck au contrôle :

```bash
python3 ~/.claude/skills/skysales/scripts/qa_deck.py <dump.json> \
  --client "Nom Client" --gabarit allin --langue fr --reference "Marque citée volontairement"
```

Le `dump.json` est la sortie de `read-design` sur le design complet, sauvegardée sur disque (elle l'est automatiquement quand elle dépasse la limite de tokens).

**Deux niveaux, à ne jamais confondre :**

- **BLOQUANT** — jamais légitime, quel que soit le brief. Nom d'un autre client du portefeuille hors P1, placeholder `[...]` non remplacé, `(tbd)` / `TBD` / `[DRAFT]`, `XX%`, `X,XXX €`, slides dupliquées. Le deck ne sort pas.
- **À CONFIRMER** — peut être un choix délibéré du client ou du commercial. Mélange de langues, mentions manquantes sur la page prix, conventions de marque. On alerte, le lead tranche.

**Cette distinction est une règle, pas un détail** (posée par le lead le 20/08/2026) : une incohérence n'est pas forcément une erreur, elle peut venir de la demande du client. Un outil qui bloque sur tout se fait désactiver.

**Le gabarit change ce qui est bloquant.** Sur un `digest` ou une `offerte` — decks de crédentials sans partie client — l'absence du nom du client est normale. Sur un `allin`, `proposition` ou `pitch`, c'est un deck recyclé non réécrit. Sans ce paramètre, l'outil sur-bloque : au premier essai il refusait 11 decks sur 13, dont 5 à tort.

**Déclarer les marques citées volontairement** avec `--reference` : la marque du bloc FR/NL est un client du portefeuille cité à dessein, elle n'est pas un résidu.

**Résultat sur les 13 decks réels de le commercial** (août 2026) : 6 bloqués, tous sur des défauts indiscutables — un deck recyclé (0 occurrence du client, marque A sur 9 slides, marque C sur 2), Domino's (Crazy Tiger résiduel + `(tbd)`), marque A, Brightplus (`[DRAFT]`), Easy Syndic, Takeaway (`[city]`). Les 7 autres passent.

**Ce que le contrôle ne voit pas.** Il lit du texte. Une slide aux couleurs d'une autre marque au milieu du deck, un visuel hors sujet, un ton qui sonne faux : invisibles pour lui. La relecture en mode présentation reste obligatoire — c'est ce qui a manqué sur un deck recyclé, dont la slide 36 était entièrement à la charte jaune marque C.

---

## PHASE 6 : REVUE ANTI-AI

Repasser tout le texte produit au filtre `references/writing-filter.md`. Mots et tournures bannis, EN et FR, patterns structurels, typographie FR : tout est dans ce fichier.

Test de spécificité : si on peut remplacer le nom du client par un concurrent sans que la phrase change de sens, elle est trop générique. Ajouter un fait ou couper.

---

## STRUCTURE P2 (inventaire des sections de P2)

Ordre observé dans le template. Chaque section devient un ou plusieurs blocs dans la carte :

1. `social media strategy` (séparateur)
2. Diagnostic, introduction : le constat central + 4 points (`01`-`04`)
3. Diagnostic, sector signals : « What's shifting » + 4 stats `XX %` (DONNÉES)
4. Diagnostic, current state : Audience / Strengths / Friction / Positioning
5. Diagnostic, priorities : 3 priorités (titre + paragraphe), cardinalité variable
6. North Star : phrase nord + échelle From → To (Awareness → Preference)
7. Approche, cultural layer : Social OS appliqué, 5 phases (2 slides)
8. Approche, platform roles : tableau TikTok vs Meta
9. Approche, same country different cultures : FR vs NL
10. Approche, three pillars : 3 piliers (titre + feeling)
11. Content strategy, intro + Pilier 01 / 02 / 03 (définition, exemples, feeling, where)
12. Way of working, kick-off : timeline 6 semaines (w-6 à w-1)
13. Way of working, always-on : forme de la semaine (mon → fri)
14. Way of working, team : 5 personnes (nom + rôle)
15. Scope : what's included
16. Pricing : Setup + Monthly pack (DONNÉES `X XXX €`)

Les blocs marqués DONNÉES ne sont jamais remplis sans source.

---

## NOMMAGE ET RANGEMENT

- Carte du template : `references/template-map.md`.
- Mapping de validation par client : dans le dossier de travail sélectionné, `salesdeck-[client]_[date].md` (ou la convention de nommage de l'équipe).
- Deck Canva final : copie nommée « Socialsky - SD Sales - [Client] ».
- Quand le lead valide : marquer le draft comme validé (suffixe `_OK` ou équivalent).

---

## CHECKLIST DE LIVRAISON

**Scope obligatoire — un « non » ici veut dire que le deck n'est pas livrable (règle 15).**

- [ ] **Langue** : une seule sur les 43 pages, P1 comprise, navigation latérale incluse (règle 8 bis) — `qa_deck.py` le vérifie
- [ ] **Logo client** posé sur les 20 slots, couverture (p2) comprise, carte blanche et texte `[LOGO]` supprimés (règles 11 et 11 bis)
- [ ] **Vidéos réelles** dans les 13 slots : prospect d'abord, concurrents de sa niche ensuite — aucune vidéo du template ne survit (règle 11 bis)
- [ ] **Couleur du client** dérivée de son logo et appliquée aux bandeaux et accents (section Thématisation couleur)
- [ ] **Aucune page d'échafaudage** du gabarit (note de montage, « Slide xx : ») — `qa_deck.py` le vérifie
- [ ] `qa_deck.py` **passé, zéro bloquant**, sortie montrée au lead telle quelle

**Contenu**

- [ ] Aucune donnée inventée (toute stat / prix sourcé ou TODO explicite)
- [ ] Aucun constat inventé
- [ ] Tout nom propre venu d'un transcript vérifié par recherche web (règle du transcript, cas « Alliage »)
- [ ] **Chaque ligne relue à voix haute** : aucune ne demande d'explication orale (règle 14)
- [ ] Filtre anti-AI passé
- [ ] Aucun résidu d'un autre client : texte **et** médias (règle 18)

**Forme**

- [ ] Budgets caractères respectés, vérifiés **sur les miniatures rendues** et pas dans le JSON (règle 18)
- [ ] Slots optionnels non utilisés supprimés (pas de placeholder résiduel)
- [ ] Contenu de P1 non réécrit (seule la langue a pu changer)

**Sortie**

- [ ] Aperçus validés par le lead avant commit
- [ ] Copie déplacée dans `Sales Desk - Finaux` (`<DOSSIER_SORTIE>`)
- [ ] Lien Canva **d'édition** fourni (jamais un PDF ni un export — le commercial édite avant et pendant le rendez-vous)
- [ ] Retouches manuelles restantes listées **clé en main** : page, élément tel qu'il le voit, geste, valeur exacte (règle 16)

---

## RÉFÉRENCES

- `references/content-playbook.md` : moteur de contenu, conventions de marque, voix, extraction, interview, guide par section. **Fait autorité.**
- `references/writing-filter.md` : filtre anti-AI (EN / FR) + principes d'écriture pour le texte court de deck. **Fait autorité.**
- `references/template-map.md` : ⚠️ **PÉRIMÉ, ne fait plus autorité.** Décrit le master `<DESIGN_ID>`, mort depuis. Conservé comme référence de la structure de P2 et du vocabulaire des zones, utile pour rédiger les placeholders d'un futur master neutre. La carte réelle se dérive du master lu à chaque run.
- *(Le journal des corrections du lead, qui documente l'origine de chaque règle, reste interne.)*
- `scripts/qa_deck.py` : le contrôle qualité. Bloquants = placeholders, résidus, page d'échafaudage, incohérence de langue, mentions de prix manquantes, autre client cité hors page de référence. À confirmer = ce qui demande un arbitrage humain.
- Master : **fixé par son ID et par la langue** — `<MASTER_FR>` (R2 FR), `<MASTER_EN>` (R2 EN), `<DIGEST>` (Digest R1), tous dans le dossier `Template` (`<DOSSIER_TEMPLATE>`). Ne pas le redemander au lead ; le valider par le préflight à chaque run (règle 10).
