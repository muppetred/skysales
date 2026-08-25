#!/usr/bin/env python3
"""
Controle qualite d'un sales deck socialsky avant export.

Deux niveaux, volontairement separes :

  BLOQUANT   - jamais legitime, quelle que soit la demande du client.
               Typiquement un residu de copier-coller. On ne sort pas le deck.

  A CONFIRMER - peut etre un choix delibere du client ou du commercial.
               On alerte, on ne bloque pas. C'est le lead qui tranche.

Cette separation vient d'une remarque de le lead (20/08/2026) : une incoherence
n'est pas forcement une erreur, elle peut venir de la demande du client.

Usage :
    python3 qa_deck.py <dump.json> --client "Nom Client" [--langue fr|en]

Le dump est la sortie de `read-design` (MCP Canva) sur le design complet,
sauvegardee sur disque. Sortie : rapport lisible + code retour 1 si bloquant.
"""

import argparse
import json
import re
import sys
from collections import defaultdict

# Clients du portefeuille socialsky. Leur presence dans un deck destine a un
# AUTRE client est le signe n1 d'un deck recycle non reecrit (cas un deck recyclé :
# 0 occurrence du client, 16 de marque A, 11 de marque B, 4 de marque C).
# Les case studies legitimes sont en P1 : voir PAGES_REFERENCE.
PORTEFEUILLE = [
    # À REMPLIR : les clients de votre portefeuille. Leur présence dans un deck
    # destiné à un AUTRE client est le signe n°1 d'un deck recyclé non réécrit.
    # Les case studies légitimes sont en P1 : voir PAGES_REFERENCE.
    "Client A", "Client B",
]

# Pages ou citer un autre client est normal (case studies, mur de logos, portfolio).
# Index 1-based, aligne sur la numerotation des slides Canva.
PAGES_REFERENCE = set(range(1, 24))  # toute la P1

# Jetons qui ne doivent jamais survivre a la production d'un deck.
RESIDUS = [
    (r"\(tbd\)", "(tbd) affiche a l'ecran"),
    (r"\bTBD\b", "TBD affiche a l'ecran"),
    (r"\[DRAFT\]", "[DRAFT] affiche a l'ecran"),
    (r"\blorem\b", "faux texte lorem ipsum"),
    (r"XX\s?%", "statistique non remplie (XX%)"),
    (r"X[,\.]XXX\s?€", "montant non rempli (X,XXX €)"),
    (r"\bXXXX\b", "libelle non rempli (XXXX)"),
]

# Placeholders du master : entre crochets. Ex : [LOGO], [Prospect], [Pillar 1 name]
PLACEHOLDER_RE = re.compile(r"\[[A-Za-z][^\]]{1,150}\]")

# Zones du template masquees par une carte blanche au lieu d'etre supprimees.
# Retrouvees dans la couche texte de 5 decks de le commercial.
FANTOMES = ["WHO SEES IT", "AUDIENCE"]

RESIDUS_FR_DANS_EN = [
    (r"\b\d+([,\.]\d+)?\s+ans\b", "'ans' dans un deck anglais"),
    (r"\bDur[ée]e\b", "'Duree' dans un deck anglais"),
    (r"\bmois\b", "'mois' dans un deck anglais"),
]

# Pages d'echafaudage du gabarit : consignes de montage laissees dans le master.
# Trouvees le 20/08/2026 en page 1 du deck le prospect — donc en premiere slide de
# TOUS les decks issus du master <DESIGN_ID>, et de tous ceux deja envoyes.
# Le texte ne ressemble ni a du francais ni a de l'anglais : c'est une note interne.
ECHAFAUDAGE = [
    (r"^\s*instruction\s*$", "page d'instructions du gabarit"),
    (r"\bSlide\s+xx\b", "consigne de montage 'Slide xx'"),
    (r"\bSlide\s+\d+\s*:\s*(Logo|Titre|Photo)", "consigne de montage 'Slide N : ...'"),
    (r"\bA REMPLACER\b", "consigne 'A REMPLACER'"),
    (r"\bNE PAS TOUCHER\b", "consigne 'NE PAS TOUCHER'"),
]


# --- COHERENCE DE LANGUE (regle 8 bis) -----------------------------------
# Un deck a UNE langue et toutes ses slides la parlent, P1 comprise.
# Le lexique de marque reste en anglais dans les deux langues : ce sont des
# noms, pas des mots. On le retire du texte AVANT de detecter la langue,
# sinon chaque page du Social OS ressort comme "anglaise".
LEXIQUE_MARQUE = [
    "Social OS\u2122", "Social OS", "socialsky", "social-first", "social-os",
    "CULTURAL SIGNALS", "PLATFORM INTELLIGENCE", "NATIVE CREATION",
    "CONTINUOUS PRESENCE", "AMPLIFICATION",
    "STRATEGY", "Studio", "Community", "Influence", "social ads",
    "always-on", "playbook", "paid", "organic", "feed", "UGC", "vox pop",
    "motion design", "packshot", "community management", "drive-to-store",
    "way of working", "kick-off", "no bullshit", "native by design", "ownership",
    "TikTok", "Meta", "Instagram", "Facebook", "YouTube", "LinkedIn",
    "Pinterest", "Google Ads", "Meta Ads", "TikTok Ads", "Social Commerce",
    "Reels", "Stories", "e-shop", "IAB Mixx Awards", "Top Employers",
]

# Mots-outils SANS ambiguite : aucun n'est un mot francais, aucun n'appartient
# au lexique de marque. Volontairement conservateur — mieux vaut manquer une
# page que crier au loup sur "on", "a", "as", "son", "par", "or", "an", "note",
# qui existent dans les deux langues.
MOTS_ANGLAIS_SURS = re.compile(
    r"\b(the|and|with|your|our|from|into|that|this|what|when|where|which|while|"
    r"are|is|of|to|we|you|they|their|there|its|it's|every|more|than|been|being|"
    r"have|has|had|does|did|will|would|could|should|must|about|across|after|"
    r"before|between|during|over|under|without|within|through|because|however|"
    r"only|just|very|many|such|same|still|even|back|out|up|off|again|why|how|"
    r"week|weeks|month|months|year|years|day|days|team|goals|content|brand|"
    r"launch|operate|delivered|setup|briefing|workshop|benchmark|shooting|"
    r"editing|validation|scheduling|calendar|check|challenge|deployed|impact|"
    r"reach|growth|awareness|study|case)\b",
    re.I,
)

# Marqueurs francais surs : accents + articles/prepositions sans equivalent anglais.
MOTS_FRANCAIS_SURS = re.compile(
    r"[\u00e0\u00e2\u00e7\u00e9\u00e8\u00ea\u00eb\u00ee\u00ef\u00f4\u00fb\u00f9\u00fc\u0153]|"
    r"\b(le|la|les|des|du|une|nos|vos|votre|notre|qui|que|dans|pour|avec|sur|"
    r"est|sont|tout|toute|toutes|cette|leur|leurs|aux|pas|ne|se|ses|mais|"
    r"chez|entre|depuis|vers|sans|sous|apr\u00e8s|avant|ainsi|donc|alors)\b",
    re.I,
)


def langue_de_page(morceaux):
    """Rend 'fr', 'en' ou None (indecidable) pour une page.

    Retire d'abord le lexique de marque, puis compte les marqueurs surs.
    None = la page ne porte que des noms propres, des chiffres ou du lexique :
    elle est neutre et ne peut pas etre incoherente.
    """
    txt = " ".join(morceaux)
    for terme in LEXIQUE_MARQUE:
        txt = re.sub(re.escape(terme), " ", txt, flags=re.I)
    en = len(MOTS_ANGLAIS_SURS.findall(txt))
    fr = len(MOTS_FRANCAIS_SURS.findall(txt))
    if en == 0 and fr == 0:
        return None
    if en >= fr * 2 and en >= 2:
        return "en"
    if fr >= en * 2 and fr >= 2:
        return "fr"
    return None


CONVENTIONS = [
    (r"\bSocialsky\b", "socialsky doit s'ecrire en minuscules dans le corps de texte"),
    (r"\bSOCIAL OS\b(?!™)", "Social OS doit porter le glyphe ™ et sa casse (S + OS)"),
]

# Mentions obligatoires sous toute grille de prix (invariant releve dans les 7 templates).
MENTIONS_PRIX = [
    (("STARTING AT", "TARIF DE D\u00c9PART", "\u00c0 PARTIR DE"),
     "l'ancrage 'FEE STARTING AT' / 'Tarif de depart' : un prix ne s'affiche jamais ferme"),
    (("RIGHTS OF USE", "DROITS D'USAGE"),
     "la mention sur les droits d'usage pour la duree du contrat"),
]
MOTS_PRIX = re.compile(r"(setup|onboarding|monthly|pack|€)", re.I)


def texte_des_pages(dump):
    """Rend {index_slide_1based: [chaines de texte]} depuis un dump read-design."""
    pages = dump.get("design_content", {}).get("pages", [])
    out = {}
    for i, page in enumerate(pages, start=1):
        morceaux = []
        for el in page.get("elements", []):
            if el.get("type") != "text":
                continue
            for region in el.get("textRegions", []):
                c = region.get("characters")
                if c:
                    morceaux.append(c)
        out[i] = morceaux
    return out


def analyser(dump, client, langue, reference=None, gabarit='allin'):
    pages = texte_des_pages(dump)
    bloquant, confirmer = [], []

    tout = " \n".join(t for m in pages.values() for t in m)
    client_l = client.lower()

    # --- BLOQUANT 1 : le client est-il seulement nomme ?
    # Depend du gabarit. Un Digest est un deck de credentials SANS partie client :
    # l'absence du nom y est normale (Estee Lauder, Cytoderm, Fanny's Wigs, AS24,
    # Group-F sont dans ce cas). Sur un All-in, la meme absence est fatale
    # (un deck recyclé). Ne pas distinguer les deux fait sur-bloquer l'outil.
    attend_nom = gabarit in ("proposition", "allin", "pitch")
    occurrences = tout.lower().count(client_l)
    if occurrences == 0:
        msg = (f"Le nom du client ne figure NULLE PART dans le deck "
               f"(0 occurrence de « {client} »).")
        if attend_nom:
            bloquant.append(msg + " Sur un gabarit "
                            f"« {gabarit} », c'est un deck recycle et non reecrit.")
        else:
            confirmer.append(msg + f" Normal sur un gabarit « {gabarit} » "
                             "(credentials sans partie client) — a verifier tout de meme.")
    elif occurrences < 3 and attend_nom:
        confirmer.append(
            f"Le nom du client n'apparait que {occurrences} fois. "
            f"Verifier que la personnalisation est reelle."
        )

    # --- BLOQUANT 2 : un autre client du portefeuille hors pages de reference
    # La marque de reference du bloc FR/NL (page 33) est citee volontairement :
    # elle se declare avec --reference et sort du perimetre de blocage.
    refs = {r.strip().lower() for r in (reference or "").split(",") if r.strip()}
    intrus = defaultdict(list)
    for idx, morceaux in pages.items():
        if idx in PAGES_REFERENCE:
            continue
        txt = " ".join(morceaux).lower()
        for marque in PORTEFEUILLE:
            if marque.lower() == client_l or marque.lower() in refs:
                continue
            if marque.lower() in txt:
                intrus[marque].append(idx)
    for marque, idxs in sorted(intrus.items(), key=lambda kv: -len(kv[1])):
        bloquant.append(
            f"« {marque} » apparait sur {len(idxs)} slide(s) hors P1 "
            f"(slides {', '.join(map(str, idxs[:8]))}). Residu d'un autre deck."
        )

    # --- BLOQUANT 3 : jetons residuels
    for idx, morceaux in pages.items():
        txt = " ".join(morceaux)
        for motif, libelle in RESIDUS:
            if re.search(motif, txt, re.I):
                bloquant.append(f"Slide {idx} : {libelle}.")
        for ph in PLACEHOLDER_RE.findall(txt):
            bloquant.append(f"Slide {idx} : placeholder non remplace « {ph} ».")
    # --- A CONFIRMER : zones de template masquees au lieu d'etre supprimees.
    # Attention : « AUDIENCE » et « WHO SEES IT » sont des libelles LEGITIMES des
    # tableaux current-state et platform-roles. Le vrai bug de le commercial les faisait
    # apparaitre sur des pages de PRIX, ou ils n'ont rien a faire. On ne teste donc
    # que la. (Corrige un faux positif constate au premier essai.)

    # --- BLOQUANT 4 : slides dupliquees
    signatures = defaultdict(list)
    for idx, morceaux in pages.items():
        sig = " ".join(morceaux).strip()
        if len(sig) > 120:
            signatures[sig].append(idx)
    for sig, idxs in signatures.items():
        if len(idxs) > 1:
            bloquant.append(
                f"Slides {', '.join(map(str, idxs))} : contenu texte strictement identique."
            )

    # --- BLOQUANT : pages d'echafaudage du gabarit
    for idx, morceaux in sorted(pages.items()):
        for m in morceaux:
            for motif, libelle in ECHAFAUDAGE:
                if re.search(motif, m.strip(), re.I | re.M):
                    bloquant.append(
                        f"Slide {idx} : {libelle} — une note de montage est restee visible dans le deck client."
                    )
                    break
            else:
                continue
            break

    # --- BLOQUANT : coherence de langue (regle 8 bis)
    # Le balayage porte sur TOUT le deck, P1 comprise. C'est le point qui a
    # laisse passer 23 pages anglaises dans le deck FR de le prospect le 20/08/2026 :
    # l'ancien controle ne regardait que les residus FR dans un deck EN, et
    # seulement sur les zones remplies.
    intruses = []
    for idx, morceaux in sorted(pages.items()):
        detectee = langue_de_page(morceaux)
        if detectee is not None and detectee != langue:
            intruses.append((idx, detectee))
    if intruses:
        idxs = ", ".join(str(i) for i, _ in intruses)
        autre = intruses[0][1].upper()
        bloquant.append(
            f"Deck annonce en {langue.upper()} mais {len(intruses)} slide(s) sont en {autre} : {idxs}. "
            f"Un deck a une seule langue, toutes ses slides la parlent (regle 8 bis). "
            f"Le lexique de marque (Social OS\u2122, always-on, les cinq phases...) ne compte pas : "
            f"il est retire avant detection."
        )

    # --- A CONFIRMER : residus lexicaux d'une langue dans l'autre
    if langue == "en":
        for idx, morceaux in pages.items():
            txt = " ".join(morceaux)
            for motif, libelle in RESIDUS_FR_DANS_EN:
                if re.search(motif, txt):
                    confirmer.append(f"Slide {idx} : {libelle}.")

    # --- A CONFIRMER : conventions de marque (P2 seulement, P1 est fige et verrouille)
    for idx, morceaux in pages.items():
        if idx in PAGES_REFERENCE:
            continue
        txt = " ".join(morceaux)
        for motif, libelle in CONVENTIONS:
            if re.search(motif, txt):
                confirmer.append(f"Slide {idx} : {libelle}.")

    # --- A CONFIRMER : mentions obligatoires sur la page prix, et zones fantomes
    pages_prix = [i for i, m in pages.items()
                  if i not in PAGES_REFERENCE and len(MOTS_PRIX.findall(" ".join(m))) >= 3]
    for idx in pages_prix:
        txt = " ".join(pages[idx]).upper()
        for cles, libelle in MENTIONS_PRIX:
            if not any(c in txt for c in cles):
                confirmer.append(f"Slide {idx} (page prix) : il manque {libelle}.")
        for f in FANTOMES:
            if f in txt:
                confirmer.append(
                    f"Slide {idx} (page prix) : zone de template « {f} » dans la couche texte. "
                    f"Probablement masquee par une carte blanche au lieu d'etre supprimee."
                )

    # Un meme defaut peut declencher deux regles (ex : « [DRAFT] » est a la fois
    # un jeton residuel et un placeholder). On dedoublonne en gardant l'ordre.
    def unique(seq):
        vus, out = set(), []
        for x in seq:
            if x not in vus:
                vus.add(x)
                out.append(x)
        return out

    return unique(bloquant), unique(confirmer), len(pages)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dump", help="dump JSON de read-design")
    p.add_argument("--client", required=True)
    p.add_argument("--langue", default="fr", choices=["fr", "en"])
    p.add_argument("--gabarit", default="allin",
                   choices=["digest", "offerte", "proposition", "allin", "pitch"],
                   help="famille de deck : digest et offerte n'ont pas de partie client")
    p.add_argument("--reference", default="",
                   help="marque(s) du portefeuille citees volontairement (bloc FR/NL, case study), separees par des virgules")
    a = p.parse_args()

    with open(a.dump) as f:
        dump = json.load(f)

    bloquant, confirmer, n = analyser(dump, a.client, a.langue, a.reference, a.gabarit)

    print(f"\nQA deck — « {a.client} », gabarit {a.gabarit}, {n} slides, langue {a.langue.upper()}\n")

    if bloquant:
        print(f"BLOQUANT ({len(bloquant)}) — le deck ne doit pas sortir en l'etat")
        for b in bloquant:
            print(f"  x {b}")
        print()
    else:
        print("BLOQUANT (0) — rien qui interdise la sortie\n")

    if confirmer:
        print(f"A CONFIRMER ({len(confirmer)}) — peut etre un choix delibere, a toi de voir")
        for c in confirmer:
            print(f"  ? {c}")
        print()
    else:
        print("A CONFIRMER (0)\n")

    print("Rappel : ce controle attrape ce qui est mecaniquement verifiable.")
    print("Une relecture en mode presentation reste necessaire — une slide aux")
    print("couleurs d'une autre marque, par exemple, ne se detecte qu'a l'oeil.\n")

    sys.exit(1 if bloquant else 0)


if __name__ == "__main__":
    main()
