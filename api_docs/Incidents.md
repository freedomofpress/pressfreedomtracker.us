# Incidents

Incidents are occurrences of violations of the freedom of the press committed by government authorities or private individuals.  The API contains information about when the incident took place, who was involved, and what kind of violation happened.

## Endpoints

```
GET incidents/
```

Gets a list of all incidents.

## Parameters

Parameters can be applied to the API request as part of the URL's query string.  All parameters are optional.

### Query parameters

These parameters can be used to customize the query and response that the API returns.



| Query string parameter | Type    | Description                                                                                                                                                                           |
|------------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`                | integer | The maximum number of results to return per page. If this parameter is not provided, it will default to 25.                                                                           |
| `fields`               | string  | A comma-separated list of field names. The incidents returned in the response will include only the ones given in this parameter. The set of available field names is detailed below. |
| `format`               | string  | Describes the format of the data in the response. Can be either `json` (the default) or `csv`.                                                                                        |


### Filtering parameters

These parameters can be used to filter which incidents are returned in the response.  Only incidents that match the values given will be included in the response.

TODO: fill in this section.

## Sample request

```
curl -X GET "https://pressfreedomtracker.us/api/edge/incidents/?limit=2&format=json"
```

## Sample response

Here is a sample response:

```
{
  "next": "http://localhost:8000/api/edge/incidents/?cursor=cD0yMDIxLTAyLTIwLTQ3Mzk%3D&format=json&limit=2",
  "previous": null,
  "results": [
    {
      "title": "Break this exactly I.",
      "url": "http://localhost:8000/all-incidents/break-this-exactly-i/",
      "first_published_at": "2021-04-17T04:45:30Z",
      "last_published_at": "2021-04-20T04:45:30Z",
      "latest_revision_created_at": "2021-04-22T04:45:30Z",
      "date": "2021-03-21",
      "exact_date_unknown": false,
      "city": "Carterstad",
      "body": "<div class=\"rich-text\"><p>Lorem ipsum dolor sit amet.</p></div>",
      "teaser": "<div class=\"rich-text\">Mind although win turn.</div>",
      "teaser_image": null,
      "primary_video": null,
      "image_caption": "<div class=\"rich-text\">Wait culture case western any size citizen.</div>",
      "arresting_authority": null,
      "arrest_status": null,
      "status_of_charges": null,
      "release_date": null,
      "detention_date": null,
      "unnecessary_use_of_force": false,
      "lawsuit_name": "Christopher Simpson v. Lisa Armstrong",
      "status_of_seized_equipment": null,
      "is_search_warrant_obtained": false,
      "actor": null,
      "border_point": null,
      "target_us_citizenship_status": null,
      "denial_of_entry": false,
      "stopped_previously": false,
      "did_authorities_ask_for_device_access": null,
      "did_authorities_ask_about_work": null,
      "assailant": null,
      "was_journalist_targeted": null,
      "charged_under_espionage_act": false,
      "subpoena_type": null,
      "held_in_contempt": null,
      "detention_status": null,
      "third_party_in_possession_of_communications": null,
      "third_party_business": null,
      "legal_order_type": null,
      "status_of_prior_restraint": null,
      "links": [],
      "equipment_seized": [],
      "equipment_broken": [],
      "state": {
        "name": "Texas",
        "abbreviation": "TX"
      },
      "updates": [],
      "venue": [
        "DarkRed Court of South Dakota",
        "LightSalmon Court of Louisiana"
      ],
      "workers_whose_communications_were_obtained": [
        "John A. Worker",
        "Tyler H. Worker"
      ],
      "target_nationality": [],
      "targeted_institutions": [
        "The Dennisville Tribune 4",
        "The Stevenburgh Tribune 5"
      ],
      "tags": [],
      "current_charges": [],
      "dropped_charges": [],
      "politicians_or_public_figures_involved": [],
      "authors": [
        "Diana Gomez",
        "Chase Mejia"
      ],
      "categories": [
        "Leak Case"
      ],
      "targeted_journalists": [
        "Ronald Castro (The North Andreastad Daily News 7)",
        "Megan Wright (The Adamsmouth Sun 6)"
      ],
      "subpoena_statuses": null
    },
    {
      "title": "Heavy everything every which activity husband head.",
      "url": "http://localhost:8000/all-incidents/heavy-everything-every-which-activity-husband-head/",
      "first_published_at": "2021-03-08T19:55:23Z",
      "last_published_at": null,
      "latest_revision_created_at": null,
      "date": "2021-02-20",
      "exact_date_unknown": false,
      "city": "Bairdview",
      "body": "<div class=\"rich-text\"><p>Lorem ipsum dolor sit amet.</p></div>",
      "teaser": "<div class=\"rich-text\">Memory himself never pass thing relate store.</div>",
      "teaser_image": null,
      "primary_video": null,
      "image_caption": "<div class=\"rich-text\">Over network rate act however seek.</div>",
      "arresting_authority": null,
      "arrest_status": null,
      "status_of_charges": null,
      "release_date": null,
      "detention_date": null,
      "unnecessary_use_of_force": false,
      "lawsuit_name": null,
      "status_of_seized_equipment": null,
      "is_search_warrant_obtained": false,
      "actor": null,
      "border_point": null,
      "target_us_citizenship_status": null,
      "denial_of_entry": false,
      "stopped_previously": false,
      "did_authorities_ask_for_device_access": null,
      "did_authorities_ask_about_work": null,
      "assailant": null,
      "was_journalist_targeted": null,
      "charged_under_espionage_act": false,
      "subpoena_type": null,
      "held_in_contempt": null,
      "detention_status": null,
      "third_party_in_possession_of_communications": null,
      "third_party_business": null,
      "legal_order_type": null,
      "status_of_prior_restraint": null,
      "links": [],
      "equipment_seized": [],
      "equipment_broken": [],
      "state": null,
      "updates": [],
      "venue": [],
      "workers_whose_communications_were_obtained": [],
      "target_nationality": [],
      "targeted_institutions": [
        "The Dianestad Post 1581",
        "The West Jonathon Tribune 1582"
      ],
      "tags": [],
      "current_charges": [],
      "dropped_charges": [],
      "politicians_or_public_figures_involved": [],
      "authors": [],
      "categories": [
        "Subpoena / Legal Order"
      ],
      "targeted_journalists": [
        "Leah Barnett (The Lake Chrisfurt Sun 1583)"
      ],
      "subpoena_statuses": null
    }
  ]
}
```

### Field descriptions

This table describes all the fields on the incident objects in the `results` object array.

| Field                                         | Description                                                                                                                                                                             | Data Type        |
|-----------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------|
| `title`                                       | Title of the incident                                                                                                                                                                   | string           |
| `url`                                         | URL linking to the article about this incident on the Press Freedom Tracker website                                                                                                     | string           |
| `first_published_at`                          | When the article about this incident was first published.                                                                                                                               | datetime         |
| `last_published_at`                           | When the article about this incident was most recently published.                                                                                                                       | datetime         |
| `latest_revision_created_at`                  | When the article about this incident was most recently updated.                                                                                                                         | datetime         |
| `date`                                        | When the incident happened.                                                                                                                                                             | date             |
| `exact_date_unknown`                          | This field will be set to `true` if the exact date of the incident is not known, meaning the `date` field is not a precise value.                                                       | boolean          |
| `city`                                        | The city the incident happened in.                                                                                                                                                      | string           |
| state                                         | The state the incident happened in.                                                                                                                                                     | object           |
| `body`                                        | The HTML content of the article about this incident on the Press Freedom Tracker website                                                                                                | string           |
| `teaser`                                      | A short description of the content of the article about this incident on the Press Freedom Tracker website                                                                              | string           |
| `teaser_image`                                | The URL of an image related to this incident.                                                                                                                                           | string           |
| `primary_video`                               | The URL of a video related to this incident.                                                                                                                                            | string           |
| `image_caption`                               | The caption of image from the `teaser_image` field.                                                                                                                                     | string           |
| `arresting_authority`                         | The name of the law-enforcement organization involve in an arrest incident.                                                                                                             | string           |
| `arrest_status`                               | The status of the arrest in an arrest incident. Can be one of: `UNKNOWN`, `DETAINED_NO_PROCESSING`, `DETAINED_CUSTODY`, `ARRESTED_CUSTODY`, or `ARRESTED_RELEASED`.                     | string           |
| `status_of_charges`                           | The status of the charges in the incident. Can be one of: `UNKNOWN`, `NOT_CHARGED`, `CHARGES_PENDING`, `CHARGES_DROPPED`, `CONVICTED`, `ACQUITTED`, or `PENDING_APPEAL`.                | string           |
| `release_date`                                | The date of release for an arrest incident.                                                                                                                                             | date             |
| `detention_date`                              | The date of detention for an arrest incident.                                                                                                                                           | date             |
| `unnecessary_use_of_force`                    | If unnecessary force was used in the incident.                                                                                                                                          | boolean          |
| `lawsuit_name`                                | The name of the lawsuit pertaining to the incident.                                                                                                                                     | string           |
| `status_of_seized_equipment`                  | The status of any equipment seized during the incident. Can be one of: `UNKNOWN`, `CUSTODY`, `RETURNED_FULL`, or `RETURNED_PART`.                                                       | string           |
| `is_search_warrant_obtained`                  | Whether or not a search warrant was obtained for this incident.                                                                                                                         | boolean          |
| `actor`                                       | A description of the principal actor involved in the incident. Can be one of: `UNKNOWN`, `LAW_ENFORCEMENT`, `PRIVATE_SECURITY`, `POLITICIAN`, `PUBLIC_FIGURE`, or `PRIVATE_INDIVIDUAL`. | string           |
| `border_point`                                | What border-crossing point a border-stop incident occurred at.                                                                                                                          | string           |
| `target_us_citizenship_status`                | The citizenship status of the target of the incident. Can be one of: `US_CITIZEN`, `PERMANENT_RESIDENT`, or `NON_RESIDENT`                                                              | string           |
| `denial_of_entry`                             | If the incident involved denying entry to the country.                                                                                                                                  | boolean          |
| `stopped_previously`                          | If the incident targeted someone who had been previously stopped at the border.                                                                                                         | boolean          |
| `did_authorities_ask_for_device_access`       | If authorities asked for access to the target's electronic devices during the incident. Can be one of: `NOTHING`, `JUST_TRUE`, `JUST_FALSE`.                                            | string           |
| `did_authorities_ask_about_work`              | If authorities asked about the target's work during the incident. Can be one of: `NOTHING`, `JUST_TRUE`, `JUST_FALSE`.                                                                  | string           |
| `assailant`                                   | The type of assailant in an assault incident. Can be one of: `UNKNOWN`, `LAW_ENFORCEMENT`, `PRIVATE_SECURITY`, `POLITICIAN`, `PUBLIC_FIGURE`, or `PRIVATE_INDIVIDUAL`.                  | string           |
| `was_journalist_targeted`                     | If a journalist was specifically targeted in the incident. Can be one of `NOTHING`, `JUST_TRUE`, `JUST_FALSE`.                                                                          | string           |
| `charged_under_espionage_act`                 | If someone was charged under the espionage act as part of the incident.                                                                                                                 | boolean          |
| `subpoena_type`                               | The type of subpoena used in a legal case incident. Can be one of `TESTIMONY_ABOUT_SOURCE`, `OTHER_TESTIMONY`, `JOURNALIST_COMMUNICATIONS`                                              | string           |
| `held_in_contempt`                            | If the target was held in contempt of court during the incident. Can be one of `NOTHING`, `JUST_TRUE`, `JUST_FALSE`.                                                                    | string           |
| `detention_status`                            | The status of the detainee. Can be one of `HELD_IN_CONTEMPT_NO_JAIL`, `IN_JAIL`, or `RELEASED`.                                                                                         | string           |
| `third_party_in_possession_of_communications` | A description of what third-party possess communications in an incident involving a legal order for a journalist's records.                                                             | string           |
| `third_party_business`                        | What type of business the above third-party is engaged in. Can be one of: `TELECOM`, `TECH_COMPANY`, `ISP`, `FINANCIAL`, `TRAVEL` or `OTHER`.                                           | string           |
| `legal_order_type`                            | What type of legal order was involved in the incident. Can be one of: `SUBPOENA`, `2703`, `WARRANT`, `NATIONAL_SECURITY_LETTER`, `FISA` or `OTHER`.                                     | string           |
| `status_of_prior_restraint`                   | Status of prior restraint related to the incident. Can be one of `PENDING`, `DROPPED`, `STRUCK_DOWN`, `UPHELD`, or `IGNORED`.                                                           | string           |
| `links`                                       | A collection of links pertaining to the incident.                                                                                                                                       | array of objects |
| `equipment_seized`                            | What equipment, and how much, was seized during the incident.                                                                                                                           | array of objects |
| `equipment_broken`                            | What equipment, and how much, was broken during the incident.                                                                                                                           | array of objects |
| `updates`                                     | Updates to the article on the Press Freedom Tracker after it was initially published.                                                                                                   | array of strings |
| `venue`                                       | Courts that are hearing or have heard the case related to the incident.                                                                                                                 | array of strings |
| `workers_whose_communications_were_obtained`  | Alleged recipient of leak incidents.                                                                                                             | array of strings |
| `target_nationality`                          | Nationalities of targets of the incident.                                                                                                                                               | array of strings |
| `target_institutions`                         | Institutions targeted during the incident.                                                                                                                                              | array of strings |
| `tags`                                        | Tags used to classify the incident.                                                                                                                                                     | array of strings |
| `current_charges`                             | Charges made in legal cases related to the incident.                                                                                                                                    | array of strings |
| `dropped_charges`                             | Charges made that were later dropped as part of the incident.                                                                                                                           | array of strings |
| `politicians_or_public_figures_involved`      | Politicians or public figures involved in the incident.                                                                                                                                 | array of strings |
| `authors`                                     | Authors of the article about the incident on the Press Freedom Tracker website.                                                                                                         | array of strings |
| `categories`                                  | Categories that the incident is filed-under on the Press Freedom Tracker website.                                                                                                       | array of strings |
| `targeted_journalists`                        | Journalists (and what institution they belonged to, if any) targeted during the incident.                                                                                               | array of strings |
| `subpoena_statuses`                           | Statuses of any subpoenas involved in the incident. For each subpoena, the status can be one of: `UNKNOWN`, `PENDING`, `DROPPED`, `QUASHED`, `UPHELD`, `CARRIED_OUT`, or `IGNORED`.     | array of strings |
