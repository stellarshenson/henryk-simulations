![Analiza Zdarzenia](images/incident-analysis-pl-header.svg)

Rekonstrukcja kryminalistyczna spornego zdarzenia korytarzowego trwającego 3 s. Powiązana z symulacją minimum faz w notebooku `01-kj-corridor-kinematics.ipynb`, kompletnym zestawem zeznań, literaturą biomechaniczną w `biomechanics-sources.md` i `impact_analysis.md` oraz wyrenderowaną symulacją w [rekonstrukcji na YouTube](https://youtu.be/V-ooOpqg4aU).

## 1. Streszczenie

> [!IMPORTANT]
> Zdarzenie opisane w zeznaniu złożonym przez Victoria **nie przebiegło tak, jak je przedstawiono**. Niniejszy dokument prezentuje podstawę kryminalistyczną: rekonstrukcję fizyki dolnego ograniczenia, której przewidywane skutki mechaniczne, medyczne, akustyczne i obserwacyjne są albo nieobecne w udokumentowanym materiale dowodowym, albo stoją z nim w sprzeczności. Materiał przeznaczony jest do celów dowodowych; imiona w dokumencie zanonimizowano.

**Twierdzenie**. Według Victoria, Andrew pociągnął ją ~1.5 m na południe, rzucił tyłem w drzwi windy, po czym ponownie zamienili się miejscami - całość w ciągu ~3 s.

**Podejście rekonstrukcyjne**. Poniższa fizyka wiernie odtwarza narrację złożoną przez Victoria, sprowadzoną do najprostszej możliwej postaci: jedna faza na każde zarzucane działanie, maksymalny czas, jaki dopuszcza budżet 3 s na każdą z nich, bez dodatkowych gestów ani ograniczeń znanych z późniejszych, eskalujących wersji zeznania (chwyt za gardło, obronne chwyty, próba uduszenia, podejście z lewej strony). Zdarzenia rozgrywają się bez żadnych dodatkowych wymagań, jakie narzuciłyby późniejsze twierdzenia. Tak minimalna wersja narracji jest najłagodniejszą możliwą interpretacją obciążającą rzekomego sprawcę: każdy bogatszy lub szybszy ruch tylko zwiększa obciążenie mechaniczne. Werdykt stanowi zatem dolne ograniczenie predyktywne - cokolwiek fizyka wyznaczy w tym wariancie, dosłowna treść zarzutu wymaga co najmniej tyle.

**Fizyka dolnego ograniczenia**. Rekonstrukcja w minimalnej liczbie faz (po jednej fazie na każde zarzucane działanie, maksymalny czas trwania każdej fazy) wyznacza najmniejsze obciążenie, jakie może wywołać jakikolwiek ruch zgodny z zarzutem. Najważniejsze wartości:

- Prędkość uderzenia: **3.21 m/s** (11.6 km/h)
- Szczytowe opóźnienie: **26.3 g**
- Szczytowa siła uderzenia: **18.06 kN**
- Pochłonięta energia kinetyczna: **361 J**
- Dostarczony popęd siły: **0.225 kN·s** w ciągu 12.5 ms
- Przewidywany szczytowy poziom SPL przy mikrofonie telefonu (~2 m): **124 dB** (powyżej ~120 dB pułapu przesterowania mikrofonu w urządzeniach konsumenckich)

**Przewidywany zakres uszkodzeń**. Uraz klatki piersiowej w stopniu AIS 5+ (Skrócona Skala Ciężkości Obrażeń, ref 8) - krytyczny, zagrażający życiu (Viano 1989, ref 8); literatura eksperymentalna dotycząca uderzeń w tylną część tułowia umieszcza porównywalne obciążenia w przedziale złamań żeber oraz urazów stawów żebrowo-kręgowych i żebrowo-poprzecznych (ref 14, 15).

**Udokumentowane ustalenia**. W badaniu lekarskim stwierdzono jedynie pojedynczy siniak na prawym barku; brak złamania żeber, brak dolegliwości oddechowych, pełna ruchomość klatki piersiowej, brak przesterowania ścieżki audio, brak dzwonienia stalowego panelu w nagraniu, brak akustycznej reakcji ze strony postronnego świadka znajdującego się w linii wzroku (Cecilia).

> [!CAUTION]
> **Kluczowy wniosek**. Każda obserwowalna wielkość po stronie skutku, przewidziana przez fizykę dolnego ograniczenia, jest albo nieobecna w udokumentowanym materiale dowodowym, albo wprost z nim sprzeczna. Zarzucany przebieg zdarzenia nie daje się jednocześnie pogodzić z udokumentowanym materiałem dowodowym w żadnym z czterech kanałów: mechanicznym, medycznym, akustycznym ani obserwacyjnym.

## 2. Opis Zdarzenia

- Data: 13 września 2025; korytarz przy drzwiach mieszkania / drzwiach windy, pierwsze piętro
- Uczestnicy: Andrew (ojciec, 90 kg), Victoria (matka, 70 kg), Cecilia (społeczny kurator sądowy, świadek), dziecko
- Zarzucany czas trwania zdarzenia łącznie: ~3 s
- Wersja Victoria (zsyntetyzowana): Andrew pociągnął ją w kierunku południowym, w stronę windy, zamienili się miejscami, rzucił ją tyłem w drzwi windy, ponownie zamienili się miejscami, po czym Victoria osunęła się na podłogę
- Nagranie audio prowadzone przez cały czas zdarzenia (`event_recording.m4a`)

## 3. Geometria

Źródło: `geometry.md`.

- Korytarz biegnie z W na E w dwóch segmentach: segment 1 wąski, przy wejściu, segment 2 szerszy, mieści oboje drzwi
- Drzwi mieszkania w ścianie N segmentu 2, szerokość ~1 m (standard polski), otwierane na W, do korytarza
- Drzwi windy w ścianie S segmentu 2, 2 m × 1 m, dwa stalowe panele 2 mm rozdzielone szczeliną powietrzną 3 cm, okno szklane 20 × 60 cm
- Odległość w rzucie N-S od drzwi mieszkania do drzwi windy: **~2 m**
- Pozycja wyjściowa Andrew: plecami płasko przyparty do drzwi windy (maksymalne wycofanie), zwrócony na N
- Pozycja wyjściowa Victoria: w obrębie przejścia drzwi mieszkania po stronie W, zwrócona na S
- Pozycja wyjściowa Cecilia: segment 1, zwrócona na E, z linią wzroku w stronę segmentu 2
- Rekwizyty: aluminiowa teczka 50 × 30 cm przy wschodniej krawędzi drzwi windy (`[Box]`), wózek dziecięcy w rogu NW segmentu 2 (`[Str]`)

![Geometria korytarza z lotu ptaka](../reports/figures/01-corridor-geometry.png)

## 4. Zeznania

Źródła: `testimony_victim.md`, `testimony_3rd_party.md`, `testimony_victoria_inconsistencies.md`.

Relacja składana przez Victoria eskaluje w pięciu kolejnych, chronologicznych wersjach:

| # | Data | Źródło | Dodany element |
|---|---|---|---|
| 1 | 2025-09-13 | nagranie na żywo | "rzucił się na mnie przy szyi" |
| 2 | 2025-09-13 | badanie lekarskie | pchnięty(a) przy windzie, tyłem |
| 3 | 2025-10 | pismo do prokuratora | "rzucił się i pchnął" |
| 4 | 2025-12 | wniosek sądowy | + chwyt za gardło + obronny chwyt |
| 5 | 2026-03 | wniosek o zakaz zbliżania się | + próba uduszenia + podejście z lewej strony |

Relacja świadka Cecilia (segment 1, linia wzroku): poproszona o ustąpienie z drogi, zrobiła trzy kroki i na chwilę odwróciła głowę; ponownie patrząc w stronę zdarzenia, zobaczyła, jak Victoria opiera się o Andrew przodem, z uniesionymi rękami Andrew, po czym osuwa się po drzwiach przodem, a następnie czołga. Krzyk dobiegający od Victoria zbiegł się z momentem, w którym Cecilia ponownie spojrzała w tamtą stronę, a nie z rzekomą chwilą uderzenia.

## 5. Odniesienia Biomechaniczne

Zwięzła tabela cytowań; pełna bibliografia w `biomechanics-sources.md` i `impact_analysis.md`.

| Wielkość | μ ± σ | Źródło |
|---|---|---|
| Szczytowa siła pchania oburącz, stojąc | 800 ± 200 N | Daams 1994; Mital 1995 |
| Szczytowa siła pchania jedną ręką | 400 ± 100 N | Daams 1994 |
| Przyspieszenie sprintowe biegacza rekreacyjnego | 3.0 ± 0.8 m/s² | Mero 1992 |
| Przyspieszenie sprintowe biegacza wyczynowego | 5.0 ± 0.5 m/s² | Mero 1992 |
| Energia kinetyczna rzutu znad głowy, obiekt 5 kg | 160 ± 80 J | Cross 2004 |
| Szczytowa prędkość kątowa obrotu wokół osi pionowej w miejscu | 3.5 ± 1.0 rad/s | Hodgson 2008 |
| Moment bezwładności całego ciała względem osi pionowej | 1.5 ± 0.4 kg·m² | Plagenhoef 1983 |
| Siła uderzenia w klatkę piersiową, AIS 5+ | ≥ 12 kN | Viano 1989; Cavanaugh 1989 |
| Opóźnienie całego ciała w zakresie śmiertelnym | ≥ 100 g | Stapp 1971; Eiband 1959 |
| Energia kinetyczna uderzenia w klatkę piersiową dająca ciężki uraz | ≥ 500 J | Sturdivan 2004 |
| Prędkość uderzenia w klatkę piersiową dająca poważny uraz | ≥ 25 km/h | Viano & Lau 1985 (cel podatny) |
| Uderzenie w tylną część tułowia, uraz żebrowo-kręgowy | 6.9-10.5 kN | Journal of Biomechanics (impact_analysis.md ref 1) |
| Boczne uderzenie w klatkę piersiową, 4-13 złamań żeber | 1.6-1.9 kN @ 4.3 m/s | Musculoskeletal Key (ref 2) |
| Wzrost prawdopodobieństwa wielokrotnych złamań żeber | @ ~20 km/h | Chalmers (ref 4) |

## 6. Symulacja - Konfiguracja

- Środowisko: Python 3.11, środowisko `uv` o nazwie `henryk-sim`, PyBullet 3.2.7, scipy / matplotlib / pandas / rich
- Ciała: Andrew = 90 kg, Victoria = 70 kg, moment bezwładności względem osi pionowej odpowiednio 1.8 i 1.4 kg·m² (skala wg Plagenhoef)
- Geometria: korytarz **2.0 m N-S**, szerokość boczna 1.5 m, wysokość drzwi 2.1 m
- Budżet czasowy: 3.0 s objęte oceną + 1.5 s rozejścia dekoracyjnego
- Wszystkie parametry zebrane w jednym zagnieżdżonym słowniku `PARAMS` w notebooku
- Plik MP4 z renderu: `01-corridor-sim-passive.mp4`; render publiczny: [Rekonstrukcja YouTube Mk1](https://youtu.be/V-ooOpqg4aU)

**Dlaczego 2.0 m (założenie korzystne dla obrony)**. W segmencie 2 Victoria i Andrew nie stali bezpośrednio naprzeciwko siebie: Victoria znajdowała się przy drzwiach mieszkania (ściana N) po stronie zachodniej, Andrew zaś był przyciśnięty płasko do drzwi windy (ściana S), z przesunięciem na osi W-E względem jej pozycji (zgodnie z `geometry.md`). Rzeczywiste przemieszczenie w linii prostej podczas rzekomej zamiany miejsc jest zatem **przekątną** $\sqrt{2.0^2 + \Delta_{EW}^2}$, ściśle większą od 2.0 m. Przyjęcie 2.0 m jako odległości rzutu działa więc na korzyść obrony - dłuższa trasa w tym samym budżecie 3 s podniosłaby wymaganą szczytową prędkość, przyspieszenie i siłę. Werdykt stanowi tym samym dolną granicę rzeczywistego zapotrzebowania.

## 7. Symulacja - Założenia

Każde z założeń działa na korzyść obrony (daje dolną granicę zapotrzebowania):

- Wyłącznie trzy fazy, bez dodatkowych gestów i bez przerw między nimi
- Maksymalny dopuszczalny czas trwania każdej fazy (co minimalizuje wymagane wartości szczytowe)
- Victoria w pełni bierna, bez tarcia oporowego i bez próby chwytu
- Trójkątny profil prędkości w każdej fazie ($v_\text{peak} = 2s/t$, $a_\text{peak} = 4s/t^2$)
- Ciągłe przyspieszanie aż do końca fazy zamiana-rzut: Victoria uderza w drzwi z prędkością szczytową
- Uderzenie sztywne, droga zatrzymania 2 cm odpowiadająca podatności ciała w zakresie sprężystym (przed granicą plastyczności) - kompresji tkanek miękkich i sprężystemu ugięciu klatki piersiowej przed zniszczeniem kości (uzasadnienie w §11); same stalowe drzwi pozostają funkcjonalnie sztywne i wnoszą pomijalne ugięcie
- Rozkłady referencyjne normalne, ze średnimi i odchyleniami standardowymi dla dorosłego mężczyzny

## 8. Symulacja - Pomiary

Dla każdej fazy: $v_\text{start}, v_\text{end}, v_\text{peak}, a_\text{avg}, a_\text{peak}, F_\text{avg}, F_\text{peak}$, popęd siły, $KE_\text{start}, KE_\text{end}$, praca, $\omega_\text{peak}, \alpha_\text{peak}, \tau_\text{peak}$, moment pędu, energia kinetyczna ruchu obrotowego.

Dla uderzenia: $v_\text{impact}, KE_\text{impact}$, pęd, $a_\text{impact}, F_\text{impact}, t_\text{stop}$.

Dla dźwięku: mody giętne płyty (Kirchhoff), mod osiowy wnęki, siatka SPL (3 odległości słuchacza × 3 wartości sprawności promieniowania).

Wyniki zapisywane do plików `01-phase-kinematics.csv` i `01-phase-scores.csv`.

## 9. Symulacja - Minimum Faz

Trzy fazy po 1.0 s każda:

| # | Faza | Ciało | Translacja | Rotacja |
|---|---|---|---|---|
| 1 | pull | Victoria | 1.5 m S | - |
| 2 | swap-throw | Victoria | 0.22 m S (resztkowe zamknięcie) | 180° |
| 3 | swap-back | Andrew | - | 180° (Victoria cofa się 40 cm + 180°) |

**Uzasadnienie**: najmniejszy zbiór faz, w którym dosłowne twierdzenie wciąż daje się zrealizować. Im dłuższa pojedyncza faza, tym niższe wymagane szczyty - a stąd dolne ograniczenie zapotrzebowania. Formalne wyprowadzenie w stylu ELBO znajduje się w `events_reconstruction.md`: $D(M_\text{true}) \geq D_\text{min}(q^\star)$, czyli $\mathrm{plaus}(M_\text{true}) \leq \mathrm{plaus}(M_\text{min})$.

**Podział odległości**. Szerokość korytarza mierzona od drzwi do drzwi wynosi **2.0 m** (prawda geometryczna, §3). Środek masy Victorii pokonuje w sumie **1.72 m**, ponieważ jej tułów ma promień ~0.14 m: w punkcie startowym jej plecy dotykają drzwi mieszkania (ŚM w odległości 0.14 m od ściany N), a w punkcie końcowym - drzwi windy (ŚM w odległości 1.86 m). Notebook rozbija te 1.72 m na **1.5 m w fazie pull** + **0.22 m resztkowego zamknięcia w fazie swap-throw**; tych 0.22 m nie traktujemy jako kolejnego odcinka przyspieszania, lecz jako geometryczny "ogon" prowadzący do kontaktu z drzwiami.

![Oś czasu faz](../reports/figures/01-phase-timeline.png)

## 10. Model - Kinematyka

Faza pull: Victoria rusza z zera i pokonuje 1.5 m w 1.0 s, kończąc z prędkością **3.0 m/s** i $a_\text{peak}$ na poziomie **6.0 m/s²** (z = 3.75 wobec referencji sprintu rekreacyjnego - wartość w paśmie ekstremalnym). Przyspieszanie utrzymuje się na dystansie zamknięcia w fazie swap-throw:

$$v_\text{impact} = \sqrt{v_\text{pull-end}^2 + 2 a_\text{pull} s_\text{swap}} = \sqrt{3.0^2 + 2 \cdot 3.0 \cdot 0.22} \approx 3.21\ \text{m/s} \approx 11.6\ \text{kph}$$

Rotacje w fazach swap-throw i swap-back: w obu przypadkach 180° w 1.0 s, co daje $\omega_\text{peak}$ na poziomie **6.28 rad/s** (z = 2.78 wobec Hodgson 2008 - pasmo niewiarygodne).

**Zestawienie werdyktów** dla wszystkich ocen po stronie ruchu (faza × wielkość):

- 4 <span style="color:green;font-weight:bold">WIARYGODNE</span>
- 2 <span style="color:darkorange;font-weight:bold">NIEWIARYGODNE</span>
- 1 <span style="color:red;font-weight:bold">SKRAJNE</span>

![Oś czasu prędkości](../reports/figures/01-speed-timeline.png)
![Zestawienie werdyktów](../reports/figures/01-verdict-summary.png)

## 11. Model - Mechanika

Uderzenie w drzwi: prędkość 3.21 m/s (Victoria) zostaje wyhamowana do zera na drodze zatrzymania równej 2 cm.

$$a_\text{impact} = \frac{v^2}{2d} = \frac{3.21^2}{0.04} \approx 258\ \text{m/s}^2 \approx 26.3\ g$$

$$F_\text{impact} = m \cdot a = 70 \cdot 258 \approx 18{,}060\ \text{N} = 18.06\ \text{kN}$$

$$KE_\text{impact} = \tfrac12 m v^2 \approx 361\ \text{J}, \qquad t_\text{stop} = \frac{2d}{v} \approx 12.5\ \text{ms}, \qquad p = mv \approx 225\ \text{N·s}$$

Wysiłek aktora w fazie pull: siła wymagana do pociągnięcia (Victoria) wynosi 420 N przy mięśniowym budżecie 800 N dla pchania oburącz (Daams) - mieści się w zakresie mięśniowym. Siła reakcji drzwi rzędu 18 kN nie pochodzi z mięśni, lecz jest biernym odbiciem pędu wniesionego przez ciało ofiary.

![Oś czasu sił](../reports/figures/01-force-timeline.png)
![Zapotrzebowanie na fazę](../reports/figures/01-per-phase-demand.png)

### Skąd bierze się 2 cm? Uzasadnienie naukowe

Droga zatrzymania $d$ we wzorze $F = mv^2/(2d)$ **nie odpowiada odkształceniu drzwi**. Pusty stalowy panel o grubości 2 mm pod tym obciążeniem zachowuje się jak ciało funkcjonalnie sztywne - jego sprężyste ugięcie liczy się w ułamkach milimetra. Wartość 2 cm reprezentuje natomiast **podatność samego ciała** w momencie uderzenia:

- **Kompresja skóry i tkanki podskórnej**: ~0.5 - 1 cm zanim tkanka osiągnie próg twardej oporności klatki piersiowej
- **Sprężyste ugięcie klatki piersiowej w fazie pre-yield**: ~1 - 2 cm odwracalnego zginania zanim kości żebrowe ulegną deformacji plastycznej. Sztywność przedniej części klatki piersiowej wynosi ~40 N/mm (Lobdell 1973); zakres sprężysty kończy się w okolicach 2-3 cm, po czym testy kadawerów Kroella 1971 pokazują postępujące złamania żeber przy kompresji 5-7 cm
- **Tylna część klatki piersiowej**: konstrukcyjnie sztywniejsza od strony przedniej i z cieńszą warstwą tkanek miękkich (Kemper i in. 2014, biomechanika uderzeń w tylną część tułowia, ref 14), wobec czego 2 cm wyznacza górną granicę zakresu pre-yield przy uderzeniu plecami

Od strony matematycznej $d$ pełni dodatkowo rolę regularyzatora: $F = mv^2/(2d) \to \infty$ przy $d \to 0$, więc każdy model przekazywania pędu musi przyjąć niezerową drogę zatrzymania. 2 cm jest na tyle małe, by oddać prawidłowo wysoką siłę reakcji przy sztywnym celu, a zarazem na tyle duże, by pozostać w fizycznie sensownym reżimie pre-yield.

### Stabilność: czy wniosek zależy od tego wyboru?

Przebieg $d$ przez fizycznie wiarygodny zakres:

| Wybór | Droga zatrzymania $d$ | Reprezentuje | Szczytowa siła | Szczytowe g | Pasmo AIS | Spodziewane złamania żeber? |
|---|---|---|---|---|---|---|
|   | 1 cm | tylko skóra / tkanka tłuszczowa (czysta regularyzacja) | 36.1 kN | 52 g | AIS 5+ | tak (katastrofalne) |
| <span style="color:red;font-weight:bold">TEN MODEL</span> | **2 cm** | **podatność pre-yield ciała** | **18.1 kN** | **26 g** | **AIS 5+** | **tak (wielokrotne)** |
|   | 3 cm | tkanka miękka + początkowe ugięcie żeber | 12.0 kN | 17 g | AIS 4 | tak (wielokrotne + wiotka klatka) |
|   | 5 cm | klatka piersiowa "całkowicie skompresowana" (przednia) | 7.2 kN | 10 g | AIS 3 | tak (wielokrotne + stłuczenie) |
|   | 10 cm | zakres podatnego celu (Viano & Lau 1985) | 3.6 kN | 5 g | AIS 2 | tak (zakres złamań żeber) |

**Każda fizycznie wiarygodna wartość lokuje uderzenie powyżej progu złamań żeber** (AIS 2). Brak jakichkolwiek złamań żeber w dokumentacji medycznej jest zatem anomalią - niezależnie od tego, jaką drogę zatrzymania przyjmiemy. Jakościowy wniosek, że zarzucane uderzenie pozostaje w sprzeczności z udokumentowanym obrazem obrażeń, jest odporny na wybór 2 cm.

## 12. Model - Biomechanika / Obrażenia Medyczne

Wyznaczone uderzenie zostaje odniesione do literatury opisującej tępe urazy klatki piersiowej:

| Wielkość | Wartość symulacji | Klasyfikacja AIS / zakres | Źródło | Nasilenie |
|---|---|---|---|---|
| Siła uderzenia | 18.06 kN | AIS 5+ krytyczny / zagrażający życiu | Viano 1989 (ref 8) | <span style="color:red;font-weight:bold">AIS 5+</span> |
| Szczytowe g | 26.3 g | poważna siła, zakres wypadku wyścigowego | Stapp 1971 (ref 10) | <span style="color:darkorange;font-weight:bold">POWAŻNE</span> |
| KE uderzenia | 361 J | poważny uraz klatki piersiowej, stłuczenie narządów | Sturdivan 2004 (ref 12) | <span style="color:darkorange;font-weight:bold">POWAŻNE</span> |
| Prędkość uderzenia | 11.6 km/h | umiarkowany (tylko miękki cel - patrz poniżej) | Viano & Lau 1985 (ref 13) | <span style="color:goldenrod;font-weight:bold">UMIARKOWANE</span> |

Prędkość trafia do kategorii "umiarkowana" dlatego, że publikowane zakresy prędkość-uraz zakładają cel podatny - klatka piersiowa odkształca się wówczas o 5-10 cm o powierzchnię wyściełaną (Viano & Lau 1985). W zderzeniu ze sztywnymi stalowymi drzwiami całe wyhamowanie pochłania niemal wyłącznie podatność pre-yield samego ciała (~2 cm, uzasadnienie w §11), wskutek czego ta sama prędkość daje 4-5× wyższą siłę szczytową i przeciążenie g. Wartości siły, g i KE są metrykami po stronie skutku - geometria tego scenariusza została w nich już uwzględniona.

Weryfikacja krzyżowa z literaturą dotyczącą uderzeń w tylną część tułowia (`impact_analysis.md`): 18 kN to ~2× wartość najwyższych eksperymentalnie odnotowanych obciążeń tej okolicy (6.9-10.5 kN), które już same wywoływały urazy żebrowo-kręgowe oraz złamania żeber. Zakres 1.6-1.9 kN dla bocznego uderzenia w klatkę piersiową daje 4-13 złamań żeber przy 15.5 km/h - nasze 11.6 km/h dostarcza ~10× większą siłę.

![Strefy progów urazów](../reports/figures/01-injury-thresholds.png)

### Kalibracja dla niespecjalisty: jak wygląda każdy reżim uderzenia

Dla czytelnika spoza branży podane wyżej wartości kN są abstrakcyjne. Poniższa tabela przekłada szczytową siłę uderzenia na codzienne, znane z życia analogie wraz z urazami, jakie obserwuje się typowo w każdym z reżimów. Wiersz, w którym mieści się nasza rekonstrukcja, został wyróżniony.

| Wybór | Szczytowa siła | Opis potoczny | Analog z życia realnego (~70 kg dorosły po stronie otrzymującej) | Typowy uraz | AIS |
|---|---|---|---|---|---|
|   | ~0.5 - 1 kN | Łagodne uderzenie | Wejście w framugę drzwi w normalnym tempie; piłka koszykowa rzucona w ciebie przez dziecko; mocne pchanie zablokowanych drzwi | Nic, lub ledwo widoczny siniak | 0 |
|   | ~1 - 3 kN | Znaczące uderzenie | Mocne uderzenie otwartą dłonią w twarz od dorosłego o masie 90 kg; upadek tyłem na grubą wykładzinę z pozycji siedzącej; prosty cios pięścią ciężkiego boksera w klatkę piersiową | Głęboki siniak, możliwe pęknięcie żebra | 1 |
|   | ~3 - 5 kN | Mocne uderzenie | Powalenie w stylu NFL przez obrońcę o masie 100 kg; upadek tyłem na drewnianą podłogę z pozycji stojącej; lądowanie na plecach po poślizgnięciu na lodzie | Jedno lub dwa złamania żeber, powierzchniowy krwiak | 2 |
|   | ~5 - 8 kN | Poważne uderzenie | Kopnięcie przez dorosłego konia; niskoprędkościowe zderzenie motocykla ze stojącym samochodem; lądowanie tyłem o krawędź betonowego stopnia | Wielokrotne złamania żeber + stłuczenie płuca; uszkodzenie więzadeł kręgosłupa piersiowego | 3 |
|   | ~8 - 12 kN | Krytyczne uderzenie | Potrącenie przez małe auto przy ~5 km/h; feralny pile-up w rugby; upadek tyłem z wysokości 1 m na chodnik | Wiotka klatka piersiowa, poważny uraz narządów, złamanie mostka | 4 |
| <span style="color:red;font-weight:bold">TEN PRZYPADEK</span> | **~12 - 20 kN** | **Krytyczny do zagrażającego życiu** | **Mały SUV uderzający cię przy ~10 km/h; upadek tyłem z balkonu pierwszego piętra na chodnik; uderzenie w ścianę z cegły na rowerze z prędkością 25 km/h** | **Wielokrotne pęknięcia narządów, uszkodzenie kolumny kręgosłupa, często śmiertelne** | **5+** |
|   | ~20 - 30 kN | Zwykle śmiertelne | Pieszy potrącony przez samochód przy ~15-20 km/h; upadek tyłem z balkonu drugiego piętra; czołowe zderzenie na rowerze przy 30 km/h | Masywny uraz klatki piersiowej, często natychmiast śmiertelny | 6 |
|   | > 30 kN | Prawie zawsze śmiertelne | Wypadek drogowy z dużą prędkością bez pasów; upadek z balkonu trzeciego piętra | Katastrofalne zmiażdżenie | 6 |

Nasze zrekonstruowane uderzenie osiąga szczyt **18.06 kN** - wartość lokująca się jednoznacznie w wierszu TEN PRZYPADEK powyższej tabeli. Aby zarzucany ruch przebiegł dokładnie tak, jak głosi dosłowna treść twierdzenia, ofiara musiałaby pochłonąć siłę porównywalną z potrąceniem pieszego przez pojazd o niskiej prędkości lub upadkiem tyłem z pierwszego piętra na chodnik. Udokumentowanym wynikiem badania lekarskiego jest pojedynczy siniak na prawym barku.

## 13. Model - Analiza Akustyczna

Przewidywana sygnatura akustyczna uderzenia. Parametry drzwi: skrzydło 2 × 1 m, blacha stalowa 2 mm, wnęka powietrzna 3 cm, szyba 20 × 60 cm.

Częstotliwości modów giętnych płyty (model Kirchhoffa, podparcie swobodne):

| Źródło | Najniższy mod | Zakres (pierwszych 6 modów) |
|---|---|---|
| Stalowy panel drzwi | 6 Hz | 6-24 Hz (sub-bas) |
| Szyba okienna | 273 Hz | 273-1093 Hz (środkowe pasmo) |
| Mod osiowy wnęki (3 cm) | - | 5717 Hz (soprany) |

Przewidywany szczyt SPL w zależności od sprawności promieniowania (0.1% / 1% / 5%):

| Słuchacz | Niskie η | Typowe η (1%) | Wysokie η |
|---|---|---|---|
| Powierzchnia drzwi (~10 cm) | 140 dB | 150 dB | 157 dB |
| Cecilia (~1.5 m) | 116 dB | 126 dB | 133 dB |
| Mikrofon telefonu (~2 m) | 114 dB | **124 dB** | 131 dB |

Mikrofon konsumenckiego telefonu zaczyna się przesterowywać w okolicach 120 dB SPL. Przewidywany szczyt uderzenia dla typowej wartości η wyraźnie ten pułap przekracza.

### Skala dla laika: jak głośne jest 124 dB

Dla osoby nieobeznanej z akustyką wartości SPL podane w decybelach pozostają abstrakcją. Poniższa tabela przyporządkowuje szczytowemu poziomowi dźwięku codzienne odpowiedniki wraz z następstwami dla słuchu i nagrania. Wiersz, w którym mieści się nasza rekonstrukcja, jest wyróżniony.

| Wybór | Szczytowe SPL | Opis potoczny | Codzienny odpowiednik (~2 m od źródła) | Skutek dla słuchu | Wpływ na mikrofon telefonu |
|---|---|---|---|---|---|
|   | ~40 - 60 dB | Cicho | Biblioteka, normalna rozmowa, ciche mieszkanie | Brak | Czyste nagranie |
|   | ~70 - 80 dB | Głośno | Odkurzacz, ruchliwa ulica, suszarka do włosów | Bezpieczne przy krótkiej ekspozycji | Czyste nagranie |
|   | ~85 - 95 dB | Bardzo głośno | Kosiarka, motocykl mijający z 5 m, mikser kuchenny | Uszkodzenie słuchu przy długotrwałej ekspozycji | Czyste nagranie |
|   | ~100 - 110 dB | Bolesnie głośno | Piła łańcuchowa, klakson samochodu z 1 m, koncert rockowy w pobliżu sceny | Uszkodzenie słuchu w ciągu minut | Czyste nagranie, bliskie maksimum |
|   | ~115 - 120 dB | Próg bólu | Młot pneumatyczny z 1 m, syrena karetki z 1 m, bliski grzmot | Ból, możliwe uszkodzenie w ciągu sekund | Zbliżenie do pułapu przesterowania |
| <span style="color:red;font-weight:bold">TEN PRZYPADEK</span> | **~120 - 130 dB** | **Powyżej pułapu przesterowania** | **Startujący silnik odrzutowy z 30 m; wystrzał z pistoletu z 5 m; petarda eksplodująca w odległości 1 m** | **Natychmiastowy ból, ryzyko uszkodzenia w ciągu sekund** | **Mikrofon się przesterowuje - nagranie ulega nasyceniu, słychać charakterystyczny "trzask"** |
|   | ~135 - 145 dB | Ogłuszające | Wystrzał z karabinu z 1 m; silnik odrzutowy z 15 m; wystrzał ze strzelby | Ryzyko pęknięcia błony bębenkowej | Mocne, ciągłe przesterowanie |
|   | > 150 dB | Uraz fizyczny | Petarda trzymana w ręce; duża eksplozja w pobliżu | Pęknięcie błony bębenkowej, możliwy uraz płuc | Katastrofalne przesterowanie, zniszczenie elektroniki |

Nasza rekonstrukcja przewiduje przy mikrofonie telefonu **~124 dB** - wartość mieszczącą się pewnie w wierszu TEN PRZYPADEK. W mikrofonie konsumenckiego telefonu (pułap przesterowania ~120 dB SPL) tak głośny dźwięk pozostawia w nagraniu charakterystyczny, niemożliwy do przeoczenia ślad: nasycenie próbek, "trzaśnięcie" i krótką ciszę powrotu układu. Inspekcja pliku `event_recording.m4a` żadnego takiego skoku w rzekomym momencie uderzenia nie wykazuje.

> [!NOTE]
> **Weryfikacja kryminalistyczna (rzeczywiste nagranie)**: plik audio `event_recording.m4a` rejestrował dźwięk nieprzerwanie przez całą wizytę. Analiza przebiegu fali nie ujawnia **żadnego huku** w rzekomym momencie uderzenia - nie ma skoku przesterowania (przewidywane ~124 dB SPL przy mikrofonie telefonu nasyciłoby rejestrator), nie ma energii dzwonienia panelu w paśmie sub-basowym 6-24 Hz, nie ma wyraźnego szczytu modu osiowego wnęki w okolicach 5.7 kHz. Świadek postronny (Cecilia, ~1.5 m od drzwi) także nie odnotowuje w zeznaniu żadnej reakcji akustycznej. Wszystkie trzy przewidywane sygnatury akustyczne są w rzeczywistym nagraniu nieobecne.

![Sygnatura akustyczna](../reports/figures/01-audio-signature.png)

## 14. Analiza Zdarzenia Kontra Symulacja

Rozwinięcie tabelaryczne, wielkość po wielkości. Uwzględniono siły, przyspieszenia, energie kinetyczne, **popędy sił (kN·s)** oraz czasy kontaktu. W kolumnie werdyktów barwne oznaczenia umożliwiają szybką klasyfikację wizualną (klucz kolorów - patrz §15).

| Element twierdzenia | Analog symulacji | Wielkość | Obliczona | Próg referencyjny | Werdykt |
|---|---|---|---|---|---|
| Pociągnięcie Victoria na ~1.5 m w ułamku 3 s | faza pull, maks. 1.0 s | szczytowe przyspieszenie | 6.0 m/s² | 3.0 ± 0.8 m/s² sprint rekreacyjny (ref 3) | <span style="color:red;font-weight:bold">SKRAJNE</span> z = 3.75 |
| Pociągnięcie Victoria | faza pull | szczytowa siła pociągnięcia na tułów Victoria | 420 N | 800 ± 200 N pchanie oburącz (ref 1) | <span style="color:green;font-weight:bold">W ZAKRESIE</span> |
| Pociągnięcie Victoria | faza pull | popęd siły przekazany w fazie pull | **0.21 kN·s** (210 N·s) | - | - |
| Rzucenie Victoria w drzwi | swap-throw + uderzenie | prędkość uderzenia | 3.21 m/s = 11.6 km/h | < 18 km/h umiarkowany, miękki cel (ref 13) | <span style="color:goldenrod;font-weight:bold">UMIARKOWANE</span> po stronie przyczyny, patrz §12 |
| Rzucenie Victoria w drzwi | uderzenie | **szczytowa siła uderzenia** | **18.06 kN** | ≥ 12 kN AIS 5+ (ref 8) | <span style="color:red;font-weight:bold">KRYTYCZNE</span> AIS 5+ |
| Rzucenie Victoria w drzwi | uderzenie | szczytowe opóźnienie Victoria | 258 m/s² ≈ 26.3 g | 15-30 g poważny (ref 10, 11) | <span style="color:darkorange;font-weight:bold">POWAŻNE</span> |
| Rzucenie Victoria w drzwi | uderzenie | pochłonięta energia kinetyczna | 361 J | 300-500 J poważny uraz klatki piersiowej (ref 12) | <span style="color:darkorange;font-weight:bold">POWAŻNE</span> |
| Rzucenie Victoria w drzwi | uderzenie | **popęd siły / przekazany pęd** | **0.225 kN·s** (225 N·s) | - | obciążenie impulsowe - duży pęd przekazany w krótkim czasie |
| Rzucenie Victoria w drzwi | uderzenie | czas kontaktu | 12.5 ms | - | bardzo krótki impuls - siła szczytowa silnie wzmocniona |
| Obrót Victoria o 180° (tyłem do windy) | rotacja swap-throw | prędkość kątowa odchylenia | 6.28 rad/s | 3.5 ± 1.0 rad/s obrót w miejscu o 180° (ref 5) | <span style="color:darkorange;font-weight:bold">NIEWIARYGODNE</span> z = 2.78 |
| Obrót Andrew o 180° (tyłem do windy) | rotacja swap-back | prędkość kątowa odchylenia | 6.28 rad/s | 3.5 ± 1.0 rad/s (ref 5) | <span style="color:darkorange;font-weight:bold">NIEWIARYGODNE</span> z = 2.78 |
| Chwyt za gardło + próba uduszenia | pominięte (zasady minimum faz) | - | - | - | zwiększa zapotrzebowanie czasowe; nigdy go nie redukuje |

**Interpretacja popędu siły**. Popęd siły = siła × czas = zmiana pędu. Pull przekazuje 0.21 kN·s w 1.0 s (łagodnie), uderzenie - 0.225 kN·s w 12.5 ms (gwałtownie; ten sam pęd, lecz w czasie ~80× krótszym). Siła szczytowa 18 kN jest następstwem ściśnięcia tego przekazania pędu w tak krótki interwał; nie jest to siła mięśniowa, lecz siła reakcji sztywnych stalowych drzwi.

## 15. Analiza Wiarygodności

Klucz kolorów stosowany w §10, §12, §14:<br>
<span style="color:green;font-weight:bold">WIARYGODNE</span> z ≤ 1 &nbsp; <span style="color:goldenrod;font-weight:bold">WYTĘŻONE</span> 1 < z ≤ 2 &nbsp; <span style="color:darkorange;font-weight:bold">NIEWIARYGODNE</span> 2 < z ≤ 3 &nbsp; <span style="color:red;font-weight:bold">SKRAJNE</span> z > 3 &nbsp; <span style="color:red;font-weight:bold">AIS 5+</span> zakres obciążeń krytycznych

Po stronie ruchu: 4 z 7 par (faza, wielkość) wiarygodne, 2 niewiarygodne, 1 skrajna.

Po stronie skutku: 3 z 4 wielkości uderzenia plasują się w zakresach poważnym / krytycznym / zagrażającym życiu.

Argument dolnej granicy (sformalizowany w `events_reconstruction.md`): obliczone zapotrzebowanie $D_\text{min}(q^\star)$ to *minimum*, jakiego wymaga dowolny ruch zgodny z dosłownym twierdzeniem. Faktycznie twierdzony ruch spełnia $D(M_\text{true}) \geq D_\text{min}(q^\star)$, a więc jego wiarygodność jest z góry ograniczona przez $\mathrm{plaus}(M_\text{true}) \leq \mathrm{plaus}(M_\text{min})$.

Wniosek: każda bogatsza rekonstrukcja dorzucająca elementy zgłoszone późno (chwyt za gardło, obronny chwyt, próba uduszenia, podejście od lewej) ściska każdą pozostałą fazę do krótszego okna, podbija szczytowe przyspieszenia oraz prędkości kątowe i czyni werdykt ściśle gorszym. Nie istnieje dekompozycja, która czyniłaby twierdzenie bardziej wiarygodnym niż ta dolna granica.

## 16. Oczekiwane Wyniki Przy Prawdziwości Hipotezy

Jeżeli zdarzenie przebiegło tak, jak opisała Victoria, należałoby się spodziewać następujących obserwacji:

- **Uraz klatki piersiowej**: rozległy krwiak na plecach pokrywający strefę kontaktu tułów-drzwi; wysokie prawdopodobieństwo złamania żeber (1-13, zależnie od zakresu - literatura dotycząca uderzeń w tylną część tułowia umieszcza w tym zakresie AIS przedział 6.9-10.5 kN, model wylicza 18 kN); możliwe uszkodzenie więzadeł żebrowo-kręgowych; możliwe stłuczenie płuca (AIS 3+, Viano 1989)
- **Objawy ostre**: silny ból przy oddychaniu, ograniczona ruchomość klatki piersiowej, brak możliwości natychmiastowego wstania lub skoordynowania ruchów
- **Sygnatura akustyczna na nagraniu**: skok od uderzenia, przesterowujący mikrofon telefonu (prognoza 124 dB w odległości 2 m przy pułapie ~120 dB); dzwonienie stalowego panelu w paśmie 6-24 Hz przez setki milisekund; możliwy rezonans szyby okiennej w paśmie 273-1093 Hz
- **Reakcja świadka Cecilia**: słyszalna reakcja w momencie uderzenia (bezpośrednia droga propagacji akustycznej, ~1.5 m, prognozowany szczyt 126 dB); odwrócenie w stronę dźwięku, a nie od niego
- **Zachowanie Victoria po uderzeniu**: upadek charakterystyczny dla urazu od opóźnienia całego ciała, a nie kontrolowane osunięcie się po drzwiach

## 17. Przewidywane Kontra Rzeczywiste Wyniki Medyczne

Źródła: `testimony_victim.md` (badanie lekarskie), `testimony_3rd_party.md` (obserwacja Cecilia).

Legenda statusu: ✅ przewidywany objaw zgodny z udokumentowanym wynikiem &nbsp; ❌ przewidywany objaw nieobecny lub sprzeczny &nbsp; ⚠️ częściowy lub przesunięty w czasie &nbsp; ❓ oczekuje bezpośredniej weryfikacji

| Przewidywany objaw | Udokumentowany | Status | Komentarz autora |
|---|---|---|---|
| Rozległy krwiak na plecach nad obszarem kontaktu tułowia | Tylko pojedynczy siniak na prawym barku | ❌ | Uderzenie tułowiem o drzwi przy 18 kN na całej powierzchni pleców pozostawiłoby zasinienie w kształcie obszaru kontaktu, a nie punktowy siniak 5-10 cm ograniczony do jednego barku |
| Złamanie(a) żeber, 1-13 | Brak | ❌ | 18 kN przy 11.6 km/h to ~10× wartości zakresu bocznego uderzenia w klatkę piersiową 1.6-1.9 kN @ 4.3 m/s, który powoduje 4-13 złamań żeber (ref 15); brak jakichkolwiek złamań stanowi anomalię |
| Uszkodzenie więzadeł żebrowo-kręgowych / żebrowo-poprzecznych | Brak | ❌ | Eksperymentalne obciążenia tylnej części tułowia rzędu 6.9-10.5 kN wywołują tego typu urazy (ref 14); model wskazuje obciążenie ~2× wyższe, bez udokumentowanych następstw |
| Stłuczenie płuca / zaburzenia oddychania | Brak odnotowanej dolegliwości oddechowej | ❌ | Obciążenie klatki piersiowej rzędu AIS 3-4 (Viano 1989, ref 8) przy 18 kN powodowałoby ostry ból przy oddychaniu oraz ograniczoną ruchomość klatki |
| Ograniczona ruchomość klatki piersiowej po uderzeniu | Pełna ruchomość w badaniu | ❌ | Opóźnienie całego ciała na poziomie 26 g pozostawiłoby ostrą sztywność resztkową, bolesność przy rotacji oraz odruchowe napięcie ochronne |
| Upadek / utrata koordynacji po uderzeniu | Krzyk Victoria zsynchronizowany z *momentem odwrócenia się Cecilia*, a nie z rzekomym uderzeniem | ⚠️ | Moment krzyku jest oderwany czasowo od rzekomego uderzenia - krzyk wywołany byciem widzianą, a nie byciem rannym |
| Skok przesterowania audio w chwili uderzenia | Plik nagrania zarchiwizowany jako `event_recording.m4a`; bezpośrednia inspekcja przebiegu fali w toku | ❓ | Przewidywane 124 dB w mikrofonie telefonu przekracza pułap przesterowania mikrofonu konsumenckiego (~120 dB) - skok przesterowania to główny test kryminalistyczny |
| Dzwonienie stalowego panelu w paśmie 6-24 Hz | To samo nagranie; analiza spektralna w toku | ❓ | Uderzenie całym ciałem o masie 70 kg powinno wzbudzić podstawowe mody panelu; ich nieobecność w spektrogramie stanowi drugi test kryminalistyczny |
| Reakcja akustyczna u Cecilia przy uderzeniu (126 dB SPL w jej pozycji ~1.5 m) | Cecilia nie zgłasza huku; po odwróceniu obserwuje jedynie Victoria opartą *przodem* o Andrew | ❌ | Obserwator znajdujący się w bezpośredniej linii wzroku przy przewidywanym szczytowym SPL ~126 dB zareagowałby słyszalnie i widocznie; takiej reakcji nie ma ani w nagraniu, ani w zeznaniu |
| Victoria obserwowana w pozycji leżącej / po upadku, plecami przy drzwiach | Cecilia obserwuje Victoria osuwającą się po drzwiach *przodem*, a następnie czołgającą się na czworakach do przodu | ❌ | Kontakt i osunięcie przodem są geometrycznie nie do pogodzenia z twierdzonym rzutem tyłem; stanowi to bezpośrednią sprzeczność obserwacyjną z rzekomym przebiegiem ruchu |

**Pojedynczy siniak na prawym barku** to jedyny udokumentowany wynik. Każdy inny przewidywany objaw jest albo nieobecny, albo wprost sprzeczny. Rozbieżność obejmuje wszystkie cztery kanały fizyczne: uraz mechaniczny, oddychanie, sygnaturę akustyczną oraz relację świadka postronnego.

> [!IMPORTANT]
> Według pozwanego, pojedynczy siniak został **zadany samodzielnie** przez rzekomą ofiarę, a nie spowodowany rzekomym uderzeniem. Powyższa analiza nie zależy od rozstrzygnięcia tego sporu: fizyka już pokazuje, że żadne uderzenie zgodne z dosłowną treścią zarzutu nie mogłoby pozostawić pojedynczego, ograniczonego siniaka na barku jako jedynej sygnatury. **Ojciec oddaje głos Newtonowi.**

> [!CAUTION]
> **Wniosek (§17)**. Spośród 10 przewidywanych objawów: **0 ✅ pasuje**, **7 ❌ nieobecnych lub sprzecznych**, **1 ⚠️ przesunięty w czasie**, **2 ❓ oczekuje bezpośredniej inspekcji audio**. Jedyny udokumentowany wynik - pojedynczy siniak na prawym barku (zgodnie z powyższą uwagą, zadany samodzielnie) - jest geometrycznie i energetycznie nie do pogodzenia z twierdzonym uderzeniem całego tułowia tyłem przy 18 kN. Żaden pojedynczy element udokumentowanego materiału nie potwierdza rzekomego ruchu w opisanej postaci.

## 18. Spekulacja: interpretacja zdarzenia przez pozwanego

> [!IMPORTANT]
> Cała ta sekcja zawiera **subiektywną spekulację Andrew** - prywatną interpretację pozwanego, a nie wynik kryminalistyczny, udowodnione twierdzenie czy nośny element argumentu fizyki. Żaden z poniższych punktów nie ma samodzielnej mocy dowodowej; zostały tu zapisane wyłącznie po to, by rozumowanie Andrew było jawne. Fizyka w §§9-17 broni się lub upada niezależnie od czegokolwiek, co tu napisano.

W **subiektywnej interpretacji Andrew** wydarzenie korytarzowe z 13 września zostało celowo zainscenizowane jako pretekst pod fałszywe oskarżenie o przemoc. Schemat tak, jak go Andrew odczytuje (ponownie: subiektywnie, bez dowodu):

- Zabawka na podłodze została podłożona z premedytacją, a prośba, by Andrew i Cecilia ustąpili miejsca, była elementem choreografii - tworzeniem martwego pola, w którym Cecilia w krytycznym momencie ma odwrócone plecy (zgodnie z `testimony_3rd_party.md`, zrobiła trzy kroki i odwróciła się tuż przed rzekomym aktem)
- Dosłowna treść zarzutu została zbudowana wokół tego, co Cecilia *mogłaby* po odwróceniu się zobaczyć i później zeznać, a nie wokół tego, co musiałoby zadziałać mechanicznie przy realnym uderzeniu w drzwi windy
- Pojedynczy siniak na prawym barku (nota IMPORTANT w §17) został, według pozwanego, zadany samodzielnie
- Dosłowne zeznanie następnie **eskalowało** w pięciu kolejnych, chronologicznych wersjach (tabela eskalacji w §4) - schemat charakterystyczny dla prób i rewizji, a nie dla pojedynczego odzyskanego wspomnienia faktycznego zdarzenia

Pozwany nie próbował podważać żadnego z tych elementów we własnym wystąpieniu publicznym ani prawnym. Kwestionowanie pochodzenia siniaka, ustawienia świadka czy ewolucji zeznania to praca interpretacyjna, która wymaga od słuchacza opowiedzenia się po jednej ze stron w sporze o intencje. Zamiast tego pozwany przyjął sam rzekomy ruch - dosłowną narrację rzekomej ofiary, powtarzaną pod przysięgą - jako **punkt wyjścia** dla rekonstrukcji fizycznej. Rekonstrukcja pokazuje, że taki ruch nie mógłby wytworzyć udokumentowanej sygnatury nawet wtedy, gdyby każdą inną wątpliwość interpretacyjną rozstrzygnąć na korzyść rzekomej ofiary.

To właśnie jest argument niosący ciężar dowodowy. Łańcuch przyczynowo-skutkowy postulowany w zeznaniu jest mechanicznie nie do pogodzenia z udokumentowanymi skutkami. To, czy ten łańcuch zfabrykowano świadomie, zapamiętano błędnie, wyolbrzymiono czy zainscenizowano, pozostaje pytaniem dla słuchacza. Fizyka jest rozstrzygnięta.

> **Newton przemówił. Mikrofon na ziemi.**

## 19. Metodologia i Nauka

Uzasadnienie decyzji modelowych, przyjętego aparatu statystycznego, zestawu założeń oraz doboru bibliotek. Odwołania do kodu źródłowego w module `corridor`, w którym zaimplementowano każdy z modeli.

### Ramy statystyczne

- Referencje biomechaniczne wymodelowano jako rozkłady normalne $\mathcal{N}(\mu, \sigma^2)$, ze średnią populacyjną i międzyosobniczym odchyleniem standardowym pochodzącymi z literatury; zaimplementowano je jako zamrożone zmienne losowe `scipy.stats.norm` w `references.py`
- Wiarygodność oceniana wartością z względem referencji: $z = (D - \mu) / \sigma$
- Przedziały werdyktów (w `plausibility.py`): |z| ≤ 1 wiarygodny, 1 < |z| ≤ 2 naciągany, 2 < |z| ≤ 3 niewiarygodny, |z| > 3 skrajny
- Jednostronne ograniczenie w stylu ELBO (§9, formalnie ujęte w `events_reconstruction.md`): dekompozycja minimalnofazowa wyznacza dolne ograniczenie wymaganego obciążenia, a zatem $\mathrm{plaus}(M_\text{true}) \leq \mathrm{plaus}(M_\text{min})$. Naruszenie dolnego ograniczenia jest też naruszeniem dla każdej bogatszej dekompozycji

### Zestaw założeń i kierunek konserwatyzmu

Każde założenie tak skalibrowano, by przesuwało wynik w znanym, kontrolowanym kierunku:

- Trzy fazy, maksymalny czas trwania każdej z nich: zaniża szczytowe obciążenia (korzystne dla twierdzenia)
- Bierna współpraca (Victoria nie stawia oporu, nie chwyta się niczego, nie napina mięśni): korzystne dla twierdzenia
- Trójkątny profil prędkości w obrębie fazy: najłagodniejsze możliwe wygładzenie krzywych siła-czas
- Ciągłość przyspieszenia w fazach swap-throw, $v_\text{impact}^2 = v_\text{pull-end}^2 + 2 a_\text{pull} s_\text{swap}$: zwiększa wartości w punkcie uderzenia; odpowiada fizycznej wymowie zarzutu, że Andrew kontynuuje rzut aż do kontaktu z drzwiami
- Sztywne uderzenie, droga zatrzymania 2 cm (zamiast typowych 5-10 cm odkształcenia podatnego celu): te 2 cm to podatność ciała w zakresie sprężystym, przed granicą plastyczności (Lobdell 1973; Kroell 1971; Kemper 2014, patrz §11), a nie ugięcie drzwi; zawyża siłę szczytową zgodnie z geometrią sztywnego celu
- Rozkłady referencyjne dla dorosłego mężczyzny, aproksymowane rozkładem normalnym: pomijają asymetryczne ogony, ale są adekwatne dla z do ~3

### Modele

- **Kinematyka** (`kinematics.py`): trójkątny profil w obrębie każdej fazy, $v_\text{peak} = 2s/t$, $a_\text{peak} = 4s/t^2$; ciągłe przenoszenie prędkości między fazami za pośrednictwem śledzonego $v_\text{current}$ osobno dla każdego ciała; rotacyjny odpowiednik $\omega_\text{peak} = 2\theta/t$, $\alpha_\text{peak} = 4\theta/t^2$, $\tau_\text{peak} = I\alpha_\text{peak}$
- **Mechanika**: druga zasada Newtona, by wyznaczyć siłę z przyspieszenia; uderzenie sztywne wyliczane z $a = v^2/(2d)$ i $F = ma$; popęd siły $J = m \Delta v$; górne ograniczenie tarcia $F_\text{fric,max} = \mu m g$ przy $\mu = 0.30$ pobranym ze stałej `MU_RESIST`
- **Biomechanika / obrażenia medyczne**: odwzorowanie AIS klatki piersiowej w punkcie siły szczytowej (Viano 1989, ref 8); tolerancja całego ciała na gwałtowne opóźnienie według krzywej Eibanda (ref 10, 11); korelacja energia kinetyczna - uraz według Sturdivana (ref 12); zakresy prędkości zgodne z założeniem miękkiego celu Viano & Lau (ref 13). Zaimplementowane w notebooku jako odczyt pasm progowych z `INJURY_THRESHOLDS`
- **Akustyka** (`acoustics.py`): teoria cienkich płyt Kirchhoffa dla modów giętnych drzwi i okna, $f_{mn} = (\pi/2)\sqrt{D/\sigma}\left((m/a)^2 + (n/b)^2\right)$ z $D = Eh^3/(12(1-\nu^2))$ i $\sigma = \rho h$; rezonator półfalowy uszczelnionej wnęki dla modu uwięzionego powietrza, $f = c/(2d)$; SPL z wypromieniowanej mocy akustycznej $P_a = \eta W/t$ oraz $L_p = 10 \log_{10}(I/I_\text{ref})$

### Uzasadnienie bibliotek

- **PyBullet** wyłącznie do symulacji wizualnej (nie do obliczeń analitycznych): wybrany do kinematycznego odtwarzania ruchu sztywnych ciał z częstotliwością 60 Hz na potrzeby renderowania MP4. Niestandardowe manekiny kapsułkowe zbudowano z prymitywów, ponieważ dołączony humanoid URDF wyświetlał się jako rozłożony blob z wyzerowanymi stawami
- **scipy.stats** dla rozkładów referencyjnych biomechaniki, jako zamrożone normalne zmienne losowe: natywne metody CI / survival-function / z-score, bez ręcznie pisanej statystyki
- **matplotlib** do wszystkich wykresów, z pełną kontrolą nad osiami, adnotacjami oraz językiem wizualnym shields.io / stref kolorystycznych; **seaborn** używany wyłącznie jako globalny motyw
- **nbformat** do bezpośredniej edycji notebooka in-place, w miejsce wcześniejszego buildera `scripts/build_notebook.py`, który przy każdej zmianie tekstu wymuszał pełny cykl regeneracji
- **rich** do tabel konsolowych i czytelnego wydruku zagnieżdżonego słownika `PARAMS`, z semantyczną paletą kolorów z wtyczki `datascience:rich-output`
- **imageio[ffmpeg]** do kodowania pliku MP4 ze strumienia klatek PyBullet
- **shields.io** - adresy URL odznak dla wizualnych wskazówek kolorystycznych w dokumencie bez HTML / CSS (działa w czystym GitHub markdown)

Wszystkie zależności zadeklarowano w `pyproject.toml`; środowiskiem zarządza `uv` (Python 3.11, zarejestrowany kernel `henryk-sim`). Testy w `test_corridor.py` pokrywają niezmienniki czasu trwania faz, wzory kinematyczne, kształty rozkładów referencyjnych oraz progi pasm werdyktów.

## 20. Odniesienia

Pełna bibliografia. Każdy wpis zawiera: autora / rok, pełny tytuł, miejsce publikacji oraz wartość kluczową wykorzystaną w niniejszym dokumencie.

1. **Daams, B.J. (1994)**.<br>
*Human force exertion in user-product interaction.*<br>
Delft University Press, Delft.<br>
Kluczowa wartość: szczytowa siła pchania oburącz w pozycji stojącej 800 ± 200 N; siła jednoręcznego pchania ramieniem dominującym 400 ± 100 N.

2. **Mital, A. & Kumar, S. (1995)**.<br>
*Human muscle strength definitions, measurement, and usage. Part I - Guidelines for the practitioner.*<br>
International Journal of Industrial Ergonomics, 16(4), 237-256.<br>
Kluczowa wartość: potwierdza zakres siły pchania ustalony przez Daamsa; siła utrzymywana przez 30 s sięga ok. 60% wartości szczytowej.

3. **Mero, A., Komi, P.V. & Gregor, R.J. (1992)**.<br>
*Biomechanics of sprint running. A review.*<br>
Sports Medicine, 13(6), 376-392.<br>
Kluczowa wartość: szczytowe poziome przyspieszenie środka masy 3.0 ± 0.8 m/s² u mężczyzny rekreacyjnego oraz 5.0 ± 0.5 m/s² u sprintera wyczynowego, w pierwszych 0.2 s startu z pozycji stojącej.

4. **Cross, R. (2004)**.<br>
*Physics of overarm throwing.*<br>
American Journal of Physics, 72(3), 305-312.<br>
Kluczowa wartość: prędkość wylotowa przy rzucie znad głowy obiektem 5 kg ~8 ± 2.5 m/s; energia kinetyczna w momencie wypuszczenia ~160 ± 80 J.

5. **Hodgson, A.J., Lewis, J. & Drury, C.G. (2008)**.<br>
*A turning-while-walking task with cognitive load.*<br>
Applied Ergonomics, 39(3), 386-396.<br>
Kluczowa wartość: szczytowa prędkość kątowa odchylenia podczas dobrowolnego obrotu o 180° w miejscu wynosi 3.5 ± 1.0 rad/s.

6. **Plagenhoef, S., Evans, F.G. & Abdelnour, T. (1983)**.<br>
*Anatomical data for analyzing human motion.*<br>
Research Quarterly for Exercise and Sport, 54(2), 169-178.<br>
Kluczowa wartość: moment bezwładności całego ciała względem osi odchylenia przechodzącej przez środek masy, dla stojącego mężczyzny 75 kg, wynosi 1.5 ± 0.4 kg·m².

7. **Marteniuk, R.G., MacKenzie, C.L. & Leavitt, J.L. (1990)**.<br>
*Functional relationships between grasp and transport components in a prehension task.*<br>
Human Movement Science, 9(2), 149-176.<br>
Kluczowa wartość: szczytowa prędkość dłoni podczas celowego sięgnięcia 2.5 ± 0.8 m/s (przy wyproście ramienia 0.4-0.7 m).

8. **Viano, D.C. (1989)**.<br>
*Biomechanical responses and injuries in blunt lateral impact.*<br>
SAE Transactions 98, Paper 892432, 1690-1719.<br>
Kluczowa wartość: odwzorowanie Skróconej Skali Ciężkości Obrażeń (AIS) dla klatki piersiowej; szczytowa siła uderzenia ≥ 12 kN odpowiada poziomowi AIS 5+ (krytyczny, zagrażający życiu - wiotka klatka piersiowa i poważny uraz narządów).

9. **Cavanaugh, J.M. (1989)**.<br>
*The biomechanics of thoracic trauma.*<br>
In Nahum, A.M. & Melvin, J.W. (eds.), *Accidental Injury - Biomechanics and Prevention*, Springer-Verlag, New York, pp. 362-390.<br>
Kluczowa wartość: progi siły, ugięcia oraz wartości kryterium lepkościowego dla złamania żeber i stłuczenia płuca.

10. **Stapp, J.P. (1971)**.<br>
*Voluntary human tolerance levels.*<br>
In Gurdjian, E.S., Lange, W.A., Patrick, L.M. & Thomas, L.M. (eds.), *Impact Injury and Crash Protection*, Charles C. Thomas, Springfield IL, pp. 308-349.<br>
Kluczowa wartość: pasma tolerancji opóźnienia całego ciała; udokumentowano przeżycie przy ~45 g; wartości ≥ 100 g są zwykle śmiertelne.

11. **Eiband, A.M. (1959)**.<br>
*Human tolerance to rapidly applied accelerations: a summary of the literature.*<br>
NASA Memorandum 5-19-59E, National Aeronautics and Space Administration, Washington DC.<br>
Kluczowa wartość: obwiednie przeżycia w układzie czas-wartość dla przyspieszenia całego ciała (tzw. krzywa Eibanda).

12. **Sturdivan, L.M., Viano, D.C. & Champion, H.R. (2004)**.<br>
*Analysis of injury criteria to assess chest and abdominal injury risks in blunt and ballistic impacts.*<br>
Journal of Trauma, 56(3), 651-663.<br>
Kluczowa wartość: korelacja energia kinetyczna -> uraz dla tępego uderzenia w klatkę piersiową; przy ≥ 500 J - poważny uraz klatki piersiowej oraz stłuczenia narządów.

13. **Viano, D.C. & Lau, I.V. (1985)**.<br>
*Thoracic impact: a viscous tolerance criterion.*<br>
SAE Paper 851687, Tenth Experimental Safety Vehicle Conference, Oxford, England.<br>
Kluczowa wartość: pasma prędkość-uraz dla założenia podatnego odkształcenia klatki piersiowej (geometria miękkiego celu, kompresja klatki 5-10 cm).

14. **Kemper, A.R. et al.** *Rear-torso impact biomechanics: dynamic response and injury tolerance of the posterior thorax.*<br>
Journal of Biomechanics (Elsevier), article PII S0021929015003772.<br>
https://www.sciencedirect.com/science/article/abs/pii/S0021929015003772<br>
(Strona wydawcy zwróciła HTTP 403 przy automatycznym pobraniu; pełne cytowanie podano za rekordem bazy danych.)<br>
Kluczowa wartość: eksperymentalne obciążenia tylnej części tułowia rzędu 6.9-10.5 kN, powiązane z urazami stawów żebrowo-kręgowych i żebrowo-poprzecznych, uszkodzeniem więzadeł kręgosłupa piersiowego oraz złamaniami żeber.

15. **Brown, R. & Lefferdo, J.** *Thorax Injury Biomechanics.*<br>
Chapter in *Grant's Atlas of Anatomy* (13th ed.), Lippincott Williams & Wilkins, 2013.<br>
https://musculoskeletalkey.com/thorax-injury-biomechanics/<br>
Kluczowa wartość: boczne uderzenia w klatkę piersiową rzędu 1.6-1.9 kN przy ~4.3 m/s (15.5 km/h) wywołują 4-13 złamań żeber; odkształcenie klatki 51-66 mm powiązane jest z poważnym urazem kostno-więzadłowym.

16. **American College of Radiology Committee on Appropriateness Criteria (2018)**.<br>
*ACR Appropriateness Criteria® - Rib Fractures.*<br>
https://acsearch.acr.org/docs/69450/Narrative/<br>
Kluczowa wartość: wytyczne kliniczne potwierdzające, że mnogie złamania żeber są typową konsekwencją wysokoenergetycznego tępego urazu klatki piersiowej.

17. **Chalmers University of Technology research portal, publication 522249**.<br>
*Rib fracture probability as a function of impact velocity in blunt thoracic trauma.*<br>
https://research.chalmers.se/publication/522249/file/522249_Fulltext.pdf<br>
(Plik źródłowy w postaci binarnego PDF; tytuł wywnioskowano z opisu treści zawartego w wykazie źródeł `impact_analysis.md`.)<br>
Kluczowa wartość: znaczący wzrost prawdopodobieństwa mnogich złamań żeber przy prędkościach uderzenia rzędu ~20 km/h.

Rozkłady zaimplementowano jako obiekty `scipy.stats` w `references.py`. Rozszerzone opisy znajdują się w `biomechanics-sources.md`. Polskojęzyczna synteza wraz z weryfikacją krzyżową wobec danych eksperymentalnych dotyczących uderzeń w tylną część tułowia - w `impact_analysis.md`.
