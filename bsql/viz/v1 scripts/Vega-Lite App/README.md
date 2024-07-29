Flask app that embeds Vega interactive charts into HTML using the provided Vega-Lite JSON specification
Can be used for deployment

An input example:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.16.3.json",
  "config": {
    "view": {
      "continuousHeight": 300,
      "continuousWidth": 300
    }
  },
  "data": {
    "name": "data-0a4d72375f8bf383f29b604f6dc2cfb1"
  },
  "datasets": {
    "data-0a4d72375f8bf383f29b604f6dc2cfb1": [
      {
        "x": "A",
        "y": 5
      },
      {
        "x": "B",
        "y": 10
      },
      {
        "x": "C",
        "y": 15
      },
      {
        "x": "D",
        "y": 20
      },
      {
        "x": "E",
        "y": 25
      }
    ]
  },
  "encoding": {
    "x": {
      "field": "x",
      "type": "nominal"
    },
    "y": {
      "field": "y",
      "type": "quantitative"
    }
  },
  "height": 300,
  "mark": {
    "type": "bar"
  },
  "params": [
    {
      "bind": "scales",
      "name": "param_1",
      "select": {
        "encodings": [
          "x",
          "y"
        ],
        "type": "interval"
      }
    }
  ],
  "width": 800,
  "height": 600
}
```
