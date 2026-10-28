# Architektura systemu

Ten dokument opisuje architekturę systemu zespołu. W Sprincie 1 powstaje diagram v0, który
będzie aktualizowany w kolejnych sprintach.

## Architektura docelowa (scaffold)

Tak wygląda system po sześciu sprintach — na poziomie warstw. To mapa odpowiedzialności,
a nie diagram do skopiowania: diagram v0 (niżej) rysujecie sami.

Relacje między warstwami (opis tekstowy, nie diagram):

- training: dane → pipeline Kedro → artefakt modelu
- serving: UI → API → model (artefakt wczytany przez API)
- state: API → persistence
- deployment: API + UI → Cloud Run

| Warstwa | Odpowiedzialność | Sprint | Miejsce w repozytorium |
|---|---|---|---|
| Dane i kontrakt | źródło danych, kontrakt, input normalization, training-only filtering | S1 | `data/01_raw/`, `src/asi_project/datasets.yaml`, `src/asi_project/data.py` |
| Pipeline | odtwarzalne przetwarzanie i trening od surowych danych | S2 | `conf/`, `src/asi_project/pipelines/` |
| Eksperymenty i artefakt | porównanie runów, wybór modelu, pakiet modelu ładowalny poza treningiem | S3 | W&B, pakiet modelu, `docs/model_card.md` |
| API | kontrakt usługi, walidacja na granicy, model wczytywany raz | S4 | `src/asi_project/api/`, `docker/` |
| Persistence | zapis predykcji poza procesem aplikacji (tryby `sql` / `disabled`) | S4 → S5 → S6 | repository w API, Postgres w compose |
| UI | formularz jako klient API | S5 | `ui/`, `docker/`, `docker-compose.yml` |
| Chmura | wdrożenie, sekret, logi, release | S6 | `deploy/`, Cloud Run, Secret Manager, Cloud Logging |

## Diagram v0 (Sprint 1)

Narysujcie, jak — według waszej obecnej wiedzy — będzie wyglądał system na koniec projektu.
Diagram v0 nie musi być poprawny w szczegółach; ma pokazać wasze rozumienie przepływu.
Sama lista warstw z sekcji wyżej nie wystarcza — diagram pokazuje wasz system i wasze decyzje.

Na diagramie zaznaczcie co najmniej:

- skąd pochodzą dane i gdzie żyje kontrakt danych;
- gdzie działa każdy z trzech typów przetwarzania: input normalization, training-only
  filtering, model preprocessing;
- gdzie powstaje model i jak trafia tam, gdzie wykonuje się predykcja;
- kto lub co wysyła żądanie predykcji i co dostaje w odpowiedzi;
- gdzie przechowywany jest stan (np. zapis predykcji);
- które elementy już istnieją po Sprincie 1, a które są planowane.

Diagram umieśćcie w bloku `mermaid` w sekcji poniżej (GitHub renderuje Mermaid w Markdown)
albo jako obraz w `docs/` z linkiem w tej sekcji. Usuńcie znaczniki TODO, gdy diagram będzie
gotowy — sprawdza to `python scripts/check_dod.py`.

<!-- DIAGRAM-V0:START -->
```mermaid
flowchart TB
    contract["Kontrakt danych<br/>datasets.yaml + project.yaml"]

    subgraph training["Trening modelu (S1)"]
        direction LR
        uci["Dane z UCI"] --> raw["Pełny CSV<br/>lub próbka CI"]
        raw --> norm["Input normalization"]
        norm --> filter["Training-only filtering<br/>usunięcie rekordów bez targetu"]
        filter --> split["Split train / test<br/>stratified_random"]
        split --> pipeline["sklearn Pipeline<br/>imputacja, skalowanie,<br/>OneHotEncoder + LogisticRegression"]
        pipeline --> metrics["Ocena<br/>DummyClassifier vs<br/>LogisticRegression"]
        pipeline -. "serializacja (S3)" .-> artifact["Artefakt modelu"]
    end

    contract -. "target, dozwolone cechy,<br/>typy, strategia splitu" .-> norm
    contract -.-> pipeline

    subgraph serving["Predykcja (planowane S4 i S5)"]
        direction LR
        employee["Pracownik sklepu"] --> ui["Formularz"]
        ui --> api["API<br/>walidacja + input normalization"]
        api --> model["Model z artefaktu"]
        model --> response["Wynik<br/>klasa + prawdopodobieństwo"]
        response --> ui
        api --> state["Persistence<br/>zapis wyniku"]
    end

    artifact -. "wdrożenie modelu" .-> model
    cloud["Cloud Run (S6)"] -. "wdrożenie" .-> api
    cloud -.-> ui

    classDef existing fill:#e6f4ea,stroke:#27864a,color:#163d24;
    classDef planned fill:#f3f4f6,stroke:#6b7280,stroke-dasharray:5 5,color:#374151;
    class uci,raw,norm,filter,split,pipeline,metrics,contract existing;
    class artifact,employee,ui,api,model,response,state,cloud planned;
```

W Sprincie 1 pobieramy dane z UCI, sprawdzamy je względem kontraktu, normalizujemy i usuwamy z danych treningowych rekordy bez targetu. Następnie dzielimy dane zgodnie ze strategią `stratified_random` i uczymy pipeline, w którym imputacja, skalowanie oraz kodowanie kategorii są dopasowywane razem z LogisticRegression. Obecny baseline porównujemy z DummyClassifier i oceniamy na zbiorze testowym. W kolejnych sprintach wytrenowany model będzie zapisywany jako artefakt i używany przez API wywoływane z formularza. API zwróci klasę i prawdopodobieństwo, a wynik będzie mógł zostać zapisany w persistence. Zielone elementy oznaczają zakres istniejący po Sprincie 1; szare i przerywane oznaczają elementy planowane.
<!-- DIAGRAM-V0:END -->

## Historia zmian architektury

| Sprint | Zmiana | Powiązany ADR |
|---|---|---|
| S1 | diagram v0 | — |
