# Model Card

> Scaffold for Sprint 3 — do not implement before this sprint.
> Minimalną Model Card wypełnia zespół w Sprincie 3, a aktualizuje w Sprincie 6.

## Model

- Typ modelu i jego wersja (alias `production` w W&B): typ modelu: Autogluon Tabular, wersja: `LightGBMXT_BAG_L1_FULL`
- Data utworzenia i autor runu: Hubert Łaszczyk

## Przeznaczenie

- Problem (binary classification) i klasa pozytywna: Przewidywanie czy sesja w sklepie zakończy się zakupem. Target: `Revenue`, klasa pozytywna: `1` (czyli `true`)
- Użytkownik systemu i decyzja, którą wspiera model: sklep będzie w stanie wykryć wachających się klientów i zachęcić ich do zakupu dodatkową promocją, darmową wysyłką, popupem. Dla sesji o wysokim zamiarze zakupu sklep ogranicza popupy i zachęcacze.
- Zastosowania, do których model nie jest przeznaczony: odpowiadanie na pytania: "Dlaczego dany projekt jest kupowany?", "Czy ta promocja zachęci użytkownika do zakupu?", przewidywanie rozmiaru koszyka albo popytu na produkt (brak danych o koszyku i produktach w datasecie)

## Dane

- Dataset (id z `docs/datasets.md`) i fingerprint danych: `online_shoppers` [link](https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset)
- Strategia splitu z kontraktu i liczebności zbiorów: `stratified_random`, `test_size=0.2`, `random_state=42`, klasa pozytywna stanowi 15,5% wszystkich sesji

## Metryki

- Metryka główna na zbiorze testowym, w porównaniu z DummyClassifier: F1=0.389
- Pozostałe metryki i macierz pomyłek: czas predykcji 1 wiersza 6.6 ms, rozmiar modelu 2.18 mb, pamięć po wczytaniu 24.9 mb, TODO: accuracy, macierz pomyłek

## Ograniczenia i ryzyka

Ograniczenia danych (z `docs/datasets.md`):
- Część cech to metryki analityczne, których użytkownik formularza nie zna. Realnym klientem
  API byłby system analityczny; formularz Streamlit pełni rolę symulatora sesji.
- Jedno źródło danych z okresu jednego roku więc sezonowość może się nie uogólnić

Znane błędy i sytuacje, w których model zawodzi:
- F1=0.39 oznacza że model często się myli bo klasa pozytywna jest rzadka (15.5% wszystkich sesji). 


## Wersje

- Wersje bibliotek modelu i git SHA treningu:
hash commitu gdzie wytrenowano model: `037358c84f92fb71afbcb2b0d426db339adbdf50`
