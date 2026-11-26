# ADR-2: Wybór modelu produkcyjnego

- **Status:** proponowany
- **Sprint:** S3
- **Autor:** Michał Sadrzak
- **Recenzent:** Mateusz Głowacki

## Kontekst

Wybór modelu predykcyjnego z pośród 3 trenowanych modeli.

## Rozważone opcje
|Model|f1|Czas predykcji 1 wiersza|Rozmiar|Pamięć potrzebna po wczytaniu|
|-----|--|--------------|-------|-----------------------------|
|LogisticRegression (Baseline)|0.0636|4.059 ms|0.006 MB|3.9 MB|
|WeightedEnsemble_L2 (Autogluon Medium)|0.3777|59.238 ms|89.9 MB|137.6 MB|
|LightGBMXT_BAG_L1_FULL (Autogluon Good)|0.3893|6.626 ms|2.18 MB|24.9 MB|

## Decyzja

Jako model produkcyjny wybieramy LightGBMXT_BAG_L1_FULL z Autogluon Good, ponieważ przeważa na każdym polu ponad modelem WeightedEnsemble_L2 z Autogluon Medium oraz ma znacząco większą miarę docelową f1 (0.3893) od Baseline (0.0636).

## Odrzucone alternatywy

**Baseline (LogisticRegression)**
Odrzucamy go z powodu bardzo niskiej jakości predykcji:
F1 = 0.064 wobec 0.389 dla wybranego modelu.
Recall wynosi zaledwie 0.034,
czyli model wykrywa ok. 3% klientów, którzy faktycznie dokonują zakupu, więc nie spełnia swojej roli dla użytkownika systemu. Jego przewaga w czasie predykcji (4.1 ms wobec 6.6 ms) i rozmiarze (0.006 MB wobec 2.18 MB) jest w praktyce pomijalna. Uwaga: baseline działa z domyślnym progiem 0.5, a modele AutoGluona z progiem dobranym pod F1 (0.179 i 0.194), co odpowiada za część różnicy w F1.

**AutoGluon Medium (WeightedEnsemble_L2)**
Odrzucamy go, ponieważ jest gorszy od AutoGluon Good w każdym kryterium. Jest to ensemble trzech modeli (LightGBMXT, CatBoost, ExtraTreesEntr), więc każda predykcja wymaga uruchomienia wszystkich trzech. W efekcie, w porównaniu z AutoGluon Good:
- F1 jest niższe: 0.378 wobec 0.389,
- czas predykcji jest ok. 9× dłuższy: 59.2 ms wobec 6.6 ms,
- rozmiar jest ok. 40× większy: 89.9 MB wobec 2.18 MB,
- pamięć po wczytaniu jest ok. 5,5× większa: 137.6 MB wobec 24.9 MB.

## Konsekwencje

- mały (2.18 mb) i szybki (6.6 ms vs 59 ms) model, łatwy do wdrożenia w API

## Historia

| Data | Zmiana |
|---|---|
|17.11.2026 | utworzenie |
|25.11.2026 | potwierdzenie |
