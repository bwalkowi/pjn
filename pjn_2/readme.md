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

## Orzeczenia, w których występuje słowo 'trwały uszczerbek na zdrowiu'
```GET judgments/_search
   {
     "size": 0,
     "query": {
       "match_phrase": {"content": "trwały uszczerbek na zdrowiu"}
     }
   }
```

## Jak wyżej, ale z uwzględnieniem możliwości wystąpienia maksymalnie 2 dodatkowych słów pomiędzy dowolnymi elementami frazy
TODO

## 3 sędziów, którzy wydali największą liczbę orzeczeń w danym roku, wraz z liczbą wydanych orzeczeń
TODO

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
