# skysales

Skill Claude qui rédige la partie sur-mesure d'un deck de vente et la pose directement dans Canva.

Développé chez [socialsky](https://socialsky.eu), agence social media belge, et corrigé une cinquantaine de fois en production avant d'atteindre cette forme. Publié pour la mécanique Canva qu'il documente — celle-ci a coûté cher à établir et ne se trouve nulle part ailleurs.

---

## Le problème

Un deck de vente d'agence a deux parties. La première présente l'agence : c'est du boilerplate, identique d'un client à l'autre. La seconde est écrite sur mesure à partir de ce que le prospect a dit au premier rendez-vous — diagnostic, ambition, piliers de contenu, périmètre, prix.

Écrire cette seconde partie prend une journée. La recopier d'un client à l'autre en oubliant d'en changer un morceau coûte un rendez-vous.

Le skill produit cette partie sur-mesure : il copie un master Canva neutre, écrit chaque zone au budget de caractères de sa page, va chercher lui-même le logo du client et des vidéos réelles sur les réseaux sociaux, contrôle les 43 pages, et livre un lien Canva.

## Ce qu'il y a dans le dépôt

| Fichier | Rôle |
|---|---|
| `SKILL.md` | Le skill. Règles non négociables, mécanique Canva vérifiée, phases du run. |
| `DUST-AGENT.md` | Le même skill déployé comme agent [Dust](https://dust.tt), pour les commerciaux. Version condensée, alignée sur `SKILL.md` côté comportement. |
| `references/writing-filter.md` | Filtre anti-AI, FR et EN. Vocabulaire banni, patterns structurels, principes pour le texte court de deck. |
| `references/content-playbook.md` | Voix de marque et patrons de rédaction par section. |
| `references/template-map.md` | Carte historique d'un master disparu. Référence documentaire, ne fait plus autorité. |
| `scripts/qa_deck.py` | Contrôle qualité avant sortie. Sépare ce qui bloque de ce qui demande un arbitrage humain. |

## Installer

```bash
git clone https://github.com/muppetred/skysales.git ~/.claude/skills/skysales
```

Le skill a besoin du connecteur Canva. Apify sert au scraping des vidéos. Les identifiants de designs sont remplacés par des placeholders `<MASTER_FR>`, `<DIGEST>` — à renseigner avec les vôtres.

## Contrôler un deck avant de le sortir

```bash
python3 scripts/qa_deck.py dump.json --client "Nom Client" --langue fr
```

Le `dump.json` est la sortie de `read-design` sur le design complet. Le script sort en code 1 s'il reste un bloquant.

Il distingue deux niveaux, et la distinction est le cœur de l'outil : **bloquant** — un placeholder oublié, le nom d'un autre client, une slide dans la mauvaise langue : le deck ne sort pas. **À confirmer** — une incohérence qui peut être un choix délibéré : on alerte, on ne bloque pas. Un outil qui bloque sur tout finit par être ignoré.

---

## Ce que l'API Canva sait faire, et ce qu'elle ne sait pas

La partie la plus utile du dépôt. Tout est vérifié en production, pas déduit de la documentation.

| Objet | Recolorable par API | Mécanisme |
|---|---|---|
| Forme vectorielle | **oui** | `recolor_element` agit sur `paths[].fill` |
| Couleur d'un texte | **oui** | `format_text` |
| Trait (`line`) | **oui** | `update_stroke_properties` |
| **Fond de texte** | **non** | `not_permitted` sur `text-element` |
| **Couleur cuite dans une image** | **non** | `not_permitted` sur `rect-element` |
| **Fond de page** | **non** | aucune opération pour ça dans l'API |

### Le fond de texte n'est pas un élément

Le rectangle coloré derrière un texte — Canva l'appelle « Arrière-plan » — est un **effet**, pas un objet. Il n'apparaît nulle part dans le modèle exposé par l'API : ni dans la liste des éléments, ni dans le formatage du texte. On ne peut pas modifier ce qu'on ne peut pas voir.

Conséquence pour qui construit un gabarit réutilisable : **un élément qui doit porter la couleur du client se dessine comme une forme.** Un accent qui doit rester neutre peut être un effet « Arrière-plan », mais alors en noir ou en blanc, jamais dans une couleur de marque — sinon il se recopie de client en client sans que rien ne puisse le rattraper.

### `layer_element` casse le rendu d'une forme insérée par API

`insert_shape` pose une forme qui s'affiche correctement — tant qu'elle reste au-dessus de tout. Dès qu'on applique `layer_element`, la forme **disparaît du rendu** alors qu'elle reste présente dans le document, aux bonnes coordonnées et à la bonne couleur.

Reproduit dans les quatre configurations : `back` sur la forme, `front` sur le texte, les deux dans la même transaction, et les deux séparés par un commit.

Donc « forme derrière texte » ne se construit pas par API. Le partage qui fonctionne : **poser les formes par API** — la géométrie est exacte du premier coup, calculée depuis la boîte du texte — puis les **reculer à la main** dans l'éditeur, une fois, dans le gabarit.

### Reculer la forme ne suffit pas : il faut aussi éteindre l'effet

Une forme posée et reculée sous un texte qui porte encore son effet « Arrière-plan » coloré reste **totalement invisible** : l'effet la recouvre au pixel près, puisqu'il épouse la même boîte de texte. Le document rapporte la forme à la nouvelle couleur pendant que le rendu montre l'ancienne — rien n'a échoué, la couleur est cachée dessous.

Le geste manuel est donc double, par pastille : reculer la forme **et** passer l'effet « Arrière-plan » du texte sur *Aucun*.

### Le fond de page n'est pas modifiable par API

`edit-design` accepte 27 types d'opérations et aucune ne touche au fond de page. Le fond se lit pourtant, dégradé compris — lisible, non modifiable.

Donc : une page qui doit se re-thémer se construit sur un fond neutre, la couleur client étant portée par une forme posée dessus. Un fond coloré est un choix définitif.

### Ne jamais vérifier un rendu sur une vignette

Le service de miniatures sert des versions en cache, signalées par `fallbackstale=T` dans l'URL. Deux pages du même appel peuvent revenir l'une fraîche et l'autre périmée.

La méthode fiable est `export-design` avec `format.pages` limité aux pages à contrôler : un rendu neuf, hors cache, téléchargeable en une commande.

### `add_text` ne conserve pas la police du document

Un texte créé par API retombe sur une police Canva par défaut, et `format_text` n'expose aucun paramètre de police. Reconstruire un élément textuel par API coûte donc la typographie du gabarit — le remède est pire que le défaut.

---

## Ce qui n'est pas dans ce dépôt

Le skill d'origine cite nommément le portefeuille client de l'agence, des prospects en cours de négociation, et contient un journal de quarante-neuf corrections internes nominatives. Tout cela a été retiré ou anonymisé avant publication.

Ce qui reste est la méthode et la mécanique. Les identifiants de designs Canva sont remplacés par des placeholders : le skill n'est pas exécutable tel quel, il se paramètre.
