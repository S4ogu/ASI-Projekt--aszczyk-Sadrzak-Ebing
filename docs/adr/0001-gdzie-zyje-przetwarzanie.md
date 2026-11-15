# ADR-1: Gdzie żyje przetwarzanie: input normalization, training-only filtering, model preprocessing

- **Status:** proponowany
- **Sprint:** S2
- **Autor:** Hubert Łaszczyk
- **Recenzent:** imię i nazwisko (inna osoba niż autor)

## Kontekst

Jaki problem rozwiązujemy? Jakie ograniczenia mamy (dane, kontrakt, czas, platforma)?

Tworzymy proces treningowy do Kedro, tak aby cały proces od danych do modelu i metryk można było odtworzyć jedną komendą. Ograniczeniem jest to, że część procesów trzeba wykonać na całym zbiorze, a inne na zbiorze treningowym.

## Rozważone opcje

1. Opcja A - Zmiana typów 4 kolumn z int64 na category, nie usuwanie dokładnych duplikatów. Input normalization w data_processing nodes.py, training-only filtring w data_processing nodes.py oraz model preprocessing w model.py
2. Opcja B - Usuwanie dokładnych duplikatów. Centralizacja czyszczenia i tranformacji w jednym, dużym węźle przygotowania przed podaniem ich do modelu.

## Decyzja

Którą opcję wybieramy i dlaczego. Co najmniej dwie liczby z naszego systemu, na których
opiera się decyzja:

Wybrano opcję A. Podział podział przetwarzania na osobne kroki.
Input normalization oraz training-only filtering są uniwersalne, a model preprocessing i inne elementy wymagające wyuczenia są częścią modelu. Podział na osobne kroki ułatwi przyszłą modyfikację konkretnych elementów w razie potrzeby zmiany.

| Wielkość | Wartość | Skąd pochodzi |
|---|---|---|
| Dokładne duplikaty wierszy | 125 | 01_eda.ipynb Training-only filtering|
| Zmodyfikowane typy kolumn | 4 | 01_eda.ipynb Input normalization|

## Odrzucone alternatywy

Co odrzuciliśmy i z jakiego powodu.

Odrzuciliśmy filtrowanie duplikatów sesji w training-only filtering, ponieważ nie możemy stwierdzić czy duplikaty to 2 niezależne sesje czy jedna zapisana dwa razy.


## Konsekwencje

Co ta decyzja ułatwia, co utrudnia i co trzeba będzie zrobić w kolejnych sprintach.

Podjęta decyzja ułatwia ponowne użycie utworzonego input normalization oraz training-only filtering. Utrudnia ona pracę wymagajac ścisłej dyscypliny aby nie umieszczać transformacji uczących się w proceesie czyszczenia, a poza nim np. wewnątrz modelu. W kolejnych sprintach będzie trzeba używać w ten sposób przygotowanych kroków input normalization oraz training-only filtering do dalszej pracy nad modelem i jego wzdrożeniem.

## Historia

| Data | Zmiana |
|---|---|
| 11.11.2026 | utworzenie |
