# Storyboard — « Routes de France : pourquoi la route ne tue pas moins depuis 10 ans »

## Cadrage

| | |
|---|---|
| **Public** | Décideurs locaux : élus et services des conseils départementaux, préfectures, communes. Ce sont eux qui gèrent les routes départementales et peuvent agir (aménagements, contrôles, éclairage, pistes cyclables). |
| **Question principale** | Après une forte baisse, la mortalité routière stagne depuis 2013 : **où, quand et pour qui la route tue-t-elle encore ?** |
| **Message à retenir** | Le danger se concentre sur **les routes de campagne, la nuit et les usagers vulnérables** (cyclistes, seniors). C'est là que les leviers d'action locaux se trouvent. |
| **Types de récit** (consigne) | Avant / après dans le temps · Comparaison de territoires avec une carte · Classements et répartitions |
| **Données** | Bases annuelles des accidents corporels 2005-2024 (ONISR, data.gouv.fr, Licence Ouverte). Métropole par défaut. |
| **Indicateurs** | **Tués** (seul indicateur de gravité comparable sur 20 ans) · **Létalité** = tués pour 100 accidents (comparable entre territoires, sans données de population) |

## Filtres de la barre latérale

Chaque filtre sert l'histoire du public visé :

| Filtre | Pourquoi |
|---|---|
| **Période** (curseur d'années, 2005-2024) | comparer avant et après le plateau de 2013 |
| **Département** (« France métropolitaine » par défaut) | un décideur local veut voir **son** territoire, comparé à la moyenne nationale |
| **Mode de déplacement** (tous, voiture, deux-roues, vélo, piéton…) | se concentrer sur un type d'usager |

## Les sections

### 1. Accroche — « La route tue encore près de 9 personnes par jour »
- **Constat** : 3 193 tués en 2024 en métropole. −40 % depuis 2005, mais **plus aucune baisse depuis 2013** (3 268).
- **Visuel** : bandeau d'indicateurs (tués, accidents, létalité, évolution par rapport au début de la période), qui réagit aux filtres.
- **Visuel** : courbe des tués 2005-2024, avec des **annotations** : « plateau depuis 2013 », « juillet 2018 : 80 km/h », « 2020 : confinements ».
- **Contexte** : la gravité d'un accident n'a pas changé en 20 ans (≈ 6 tués pour 100 accidents) ; la baisse vient du nombre d'accidents.

### 2. Où ? — « Un tiers des accidents, deux tiers des morts : le danger est à la campagne »
- **Constats** : hors agglomération, 36 % des accidents mais **68 % des tués** ; les **routes départementales** concentrent **61 % des tués** ; un accident est **22 fois plus meurtrier dans le Jura qu'à Paris**.
- **Visuel** : **carte de France par département**, colorée selon la létalité (ou le nombre de tués, au choix), avec le département sélectionné mis en évidence.
- **Visuel** : barres « part des accidents » / « part des tués », en et hors agglomération, puis par type de route.
- **Interaction** : survol d'un département → accidents, tués, létalité, comparaison avec la moyenne nationale.

### 3. Quand ? — « La nuit et le week-end, chaque accident pèse plus lourd »
- **Constats** : la nuit (22 h - 6 h) compte 13 % des accidents mais **22 % des tués** ; un accident est près de 3 fois plus grave à 4 h qu'à 8 h ; week-end : 26 % des accidents, 32 % des tués.
- **Visuel** : **carte de chaleur heure × jour de la semaine** (létalité ou nombre d'accidents, au choix).
- **Visuel** : barres par condition d'éclairage, avec une ligne de référence à la létalité moyenne.

### 4. Qui ? — « Les automobilistes ont le plus gagné ; cyclistes et seniors sont restés sur le bord de la route »
- **Constats** : tués en voiture −50 %, à vélo **+24 %** ; 18-24 ans −57 %, 65 ans et plus −5 à −13 % ; les 65 ans et plus représentent **29 %** des tués (19 % en 2005) ; 77 % des tués sont des hommes.
- **Visuel** : **petits multiples** — un mini-graphique par mode de déplacement, évolution 2005-2024 (base 100 en 2005).
- **Visuel** : barres par classe d'âge, 2005 comparé à la dernière année de la période.

### 5. Qualité des données et limites
- **Visuel** : tableau des contrôles par année (doublons, cohérence entre tables, valeurs manquantes).
- **Visuel** : part des accidents géolocalisés par année (0 % en 2009, 100 % depuis 2019).
- **Visuel** : la rupture de 2018 sur les blessés hospitalisés.
- **Texte** : les limites (pas de données de trafic ni de population, âge à un an près, catégories apparues en cours de période, corrélation ≠ causalité) et la validation avec les chiffres officiels de l'ONISR 2024.

### 6. Conclusions et pistes d'action
- **Ce qui ressort** : le plateau se joue hors des villes, la nuit, et chez les usagers vulnérables.
- **Pistes pour un décideur local** : cibler les routes départementales (aménagements, séparateurs, contrôles), les trajets de nuit et du week-end, les infrastructures cyclables et la sécurité des seniors.
- **Pour aller plus loin** : croiser avec les populations INSEE (risque par habitant) et les données de trafic (risque par kilomètre), évaluer localement les mesures (80 km/h, 30 km/h en ville).

## Correspondance avec les exigences de la consigne

| Exigence | Où |
|---|---|
| Filtres dans la barre latérale | période, département, mode |
| Au moins 3 graphiques interactifs avec survol | courbe, carte, carte de chaleur, barres, petits multiples |
| Au moins une carte | carte des départements (section 2) |
| Indicateurs liés aux filtres | bandeau de la section 1 |
| Section qualité des données | section 5 |
| Accroche, contexte, constats, conséquences | sections 1, 1, 2-4, 6 |
