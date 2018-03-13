## Stworzenie indeksu
```
PUT judgments
{
  "settings": {
    "analysis": {
      "analyzer": {
        "std_pl": { 
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "morfologik_stem"
          ]
        }
      }
    }
  },
  "mappings": {
    "_doc": {
      "properties": {
        "content": {
          "type": "text",
          "analyzer": "std_pl"
        },
        "date": {
          "type": "date",
          "format": "yyyy-MM-dd"
        },
        "signature": {
          "type": "keyword"
        },
        "judges": {
          "type": "keyword"
        }
      }
    }
  }
}
```


## Orzeczenia, w których występuje słowo 'szkoda'
```
GET judgments/_search
{
  "size": 0,
  "query": {
    "match": {"content": "szkoda"}
  }
}
```

Wynik: 829


## Orzeczenia, w których występuje słowo 'trwały uszczerbek na zdrowiu'
```
GET judgments/_search
{
  "size": 0,
  "query": {
    "match_phrase": {
      "content": "trwały uszczerbek na zdrowiu"
    }
  }
}
```

Wynik: 9


## Jak wyżej, ale z uwzględnieniem możliwości wystąpienia maksymalnie 2 dodatkowych słów pomiędzy dowolnymi elementami frazy
```
GET judgments/_search
{
  "size": 0,
  "query": {
    "match_phrase": {
      "content": {
        "query": "trwały uszczerbek na zdrowiu",
        "slop": 2
      }
    }
  }
}
```

Wynik: 10


## 3 sędziów, którzy wydali największą liczbę orzeczeń w danym roku, wraz z liczbą wydanych orzeczeń
```
GET /judgments/_search
{
    "size" : 0,
    "aggs" : { 
        "judgments_per_judge" : { 
            "terms" : { 
              "field" : "judges",
              "size" : 300
            }
        }
    }
}
```

Wyniki:
```
{
  "key": "Dariusz Zawistowski",
  "doc_count": 227
},
{
  "key": "Teresa Bielska-Sobkowicz",
  "doc_count": 223
},
{
  "key": "Gerard Bieniek",
  "doc_count": 220
}
```


## Histogram liczby orzeczeń w zależności od miesiąca

```
GET judgments/_search
{
  "size": 0,
  "aggs": {
    "judgments_over_months": {
      "date_histogram": {
        "field": "date",
        "interval": "month"
      }
    }
  }
}
```

Histogram w pliku hist.png
