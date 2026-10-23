# Storyboard — "Roads of France: why road deaths have not fallen in 10 years"

## Framing

| | |
|---|---|
| **Audience** | Local decision-makers: elected officials and staff of departmental councils, prefectures, municipalities. They manage departmental roads and can act on them (road layout, enforcement, lighting, cycle lanes). |
| **Main question** | After a sharp fall, road deaths have stalled since 2013: **where, when and among whom do people still die on the roads?** |
| **Key message** | The danger is concentrated on **rural roads, at night and among vulnerable road users** (cyclists, older people). That is where local levers lie. |
| **Narrative patterns** | Before/after over time · Comparing territories with a map · Rankings and distributions |
| **Data** | Annual injury accident databases 2005-2024 (ONISR, data.gouv.fr, Licence Ouverte). Metropolitan France. |
| **Indicators** | **Deaths** (the only severity measure comparable over 20 years) · **Lethality** = deaths per 100 crashes (comparable between territories without population data) |

Figures below are for 2019-2024 unless stated otherwise; in the dashboard they follow the filters.

## Sidebar filters

Each filter serves the audience's story:

| Filter | Why |
|---|---|
| **Period** (year slider, 2005-2024) | compare before and after the 2013 plateau |
| **Department** ("Metropolitan France" by default) | a local decision-maker wants to see **their** territory, compared with the national average |
| **Travel mode** (all, car, motorised two-wheeler, bicycle, pedestrian...) | focus on one type of road user |

## Sections

### 1. Hook — "Road crashes still kill nearly 9 people a day"
- **Finding**: 3,193 deaths in 2024 in metropolitan France. -40% since 2005, but **no further fall since 2013** (3,268).
- **Visual**: key figures (deaths, deaths per day, crashes, lethality, change since the start of the period), following the filters.
- **Visual**: road deaths 2005-2024, with **annotations** ("start of the plateau", "80 km/h on secondary roads", "lockdowns") and a dashed reference line at the 2013 level.
- **Context**: crash severity has not changed in 20 years (about 6 deaths per 100 crashes); the fall comes from fewer crashes.

### 2. Where? — "A third of crashes, two thirds of deaths: the danger is in the countryside"
- **Findings**: outside built-up areas, 36% of crashes but **68% of deaths**; **departmental roads** account for **61% of deaths**; a crash is **22 times deadlier in the Jura than in Paris**.
- **Visual**: bars "share of crashes" / "share of deaths", inside and outside built-up areas, then by road type.
- **Visual**: **map of France by department**, colored by lethality (or number of deaths), with the selected department outlined.
- **Interaction**: hovering over a department shows its crashes, deaths and lethality; a sentence gives its rank and the national average.

### 3. When? — "At night and at weekends, every crash takes a heavier toll"
- **Findings**: nights (10 pm - 6 am) account for 13% of crashes but **22% of deaths**; a crash at 4 am is nearly 3 times deadlier than at 8 am; weekends: 26% of crashes, 32% of deaths.
- **Visual**: **hour × weekday heatmap** (lethality or number of crashes).
- **Visual**: bars by light conditions, with a reference line at the average lethality.

### 4. Who? — "Car occupants gained the most; cyclists and older people were left behind"
- **Findings** (2005 → 2024): car deaths -50%, cyclist deaths **+24%**; ages 18-24 -57%, 65 and over -5 to -13%; people aged 65+ make up **29%** of deaths (19% in 2005); 77% of those killed are men.
- **Visual**: **small multiples** — one chart per travel mode, each with its own scale, to compare trends.
- **Visual**: bars by age group, first year against last year of the period.

### 5. Data quality and limitations
- **Visual**: four checks at a glance (duplicate crashes, orphan records, fixed duplicate vehicles, gap with the ONISR 2024 figure).
- **Visual**: share of geolocated crashes per year (0% in 2009, 100% since 2019).
- **Visual**: the 2018 break in hospitalized casualties.
- **Text**: fixes applied, and limitations (no traffic or population data, age accurate to one year, categories added over time, correlation ≠ causation).

### 6. Conclusions and possible actions
- **Key findings**: the plateau is played out outside towns, at night and among vulnerable road users (figures follow the filters).
- **Actions for local decision-makers**: target departmental roads (layout, separation, enforcement), night and weekend trips, cycling infrastructure and older people's safety.
- **Going further**: relate to INSEE population (risk per inhabitant) and traffic data (risk per kilometre), evaluate local measures (80 km/h, 30 km/h in towns).

## Mapping to the assignment requirements

| Requirement | Where |
|---|---|
| Sidebar filters | period, department, travel mode |
| At least 3 interactive charts with hover | line, bars, map, heatmap, small multiples |
| At least one map | department map (section 2) |
| Key figures tied to filters | section 1 |
| Data quality section | section 5 |
| Hook, context, key insights, implications | sections 1, 1, 2-4, 6 |
