# Chart Pregenerator

A simple service for generating charts and maps into static assets.

## Endpoints

| path                 |
|----------------------|
| `/bar-chart.svg`     |
| `/bar-chart.png`     |
| `/treemap-chart.svg` |
| `/treemap-chart.png` |
| `/bubble-map.svg`    |
| `/bubble-map.png`    |

## Query Parameters

All query parameters are passed in via an urlencoded json string under the `options` parameter, for instance:

`http://localhost:3000/treemap-chart.png?options={%22filterCategories%22:[%22Assault%22]}`

Below are settings that can be specified in the options parameter:

| key                | type     | example                                           | default        |
|--------------------|----------|---------------------------------------------------|----------------|
| `filterTags`       | string[] | `['wombat']`                                      | null           |
| `filterCategories` | string[] | `['Assault']`                                     | null           |
| `dateRange`        | string[] | `['01-01-2020', '03-01-2020']`                    | `[null, null]` |
| `timePeriod`       | string   | `months`                                          | `months`       |
| `branchFieldName`  | string   | `categories`                                      | `null`         |
| `branches`         | object   | `{ type: "url", value: "/api/edge/categories/" }` | `null`         |
| `width`            | integer  | 1190                                              | 1190           |
| `height`           | integer  | 800                                               | 800            |
| `mini`             | boolean  | `false`                                           | `false`        |
