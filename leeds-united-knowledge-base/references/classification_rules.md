# Leeds Classification Rules (extracted-authoritative)

Use these for rows sourced from `leeds_fans_1919_2009.csv` where `competition` is often blank and the actual contest is encoded in `opponent` and `notes`.

## 1) European competitions first

Match on any of:

- full name variants: `champions league`, `europa league`, `uefa cup`, `cup winners' cup`, `inter-cities fairs cup`, `inter cities`, `texaco cup`, `anglo-scottish cup`, `icfc`, `european`
- abbreviated round markers: `(CL1-`, `(CL2-`, `...`, `(UCR`, `(UI`
- club names *only* when used as European opponents: `Besiktas`, `Real Madrid`, `Lazio`, `Anderlecht`, `Troyes`

## 2) FA Cup

- `fa cup`, `facq`, `facr`

## 3) League Cup / EFL Cup family

- `league cup`, `efl cup`, `carabao`, `carling`, `coca-cola`, `milk cup`, `littlewoods`, `rumbelows`, `worthington`, `johnstone`, `trophy`, `lcr`, `lcq`
- round markers like `LCR1`, `LCR2`, ...

## 4) Friendlies and specials

- `friendly`, `testimonial`, `charity`, `benevolent`, `benefit`
- year-summer opponent strings that are known touring clubs (`Lysekil`, `Jonkoping`, `Sparta Rotterdam`, `Preston North End (friendly)`, etc.)

## 5) Everything else with venue `H`/`A` = League default

## 6) Wartime and non-league seasons (label mapping)

Force the `classification` and the outer JSON key to `wartime_or_non_league` when season label is:

- `1919-20`
- `1939-39`
- `1939-40`
- `1940-41`
- `1941-41`
- `1941-42`
- `1942-42`
- `1942-43`
- `1943-43`
- `1943-44`
- `1944-44`
- `1944-45`
- `1945-46`

Otherwise the season is `league` and the JSON label is `Football League`.
