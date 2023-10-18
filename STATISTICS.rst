Using Statistics
================

There are two ways that statistics can be used: Statistics blocks, and in template-enabled text fields.
Statistics are described as consisting of a desired dataset and one or more space-separated params.

On statistics blocks, dataset and params are separate fields. For example, you might enter:

    Dataset
        num_incidents
    Params
        date_lower="2017-01-01"


In a template, the dataset is the first item in the template tag, and the remaining items are the params. For example:

.. code:: jinja

    Incidents since 1/1/17: {% num_incidents date_lower="2017-01-01" %}

The params will have the same format whether you are using statistics blocks or template tags.

Incident filter datasets
========================

Available datasets
------------------

num_incidents
+++++++++++++
Count of all incidents matching the given filter parameters.

.. code:: jinja

    {% num_incidents date_lower="2017-01-01" date_upper="2017-12-31" %}

num_journalist_targets
++++++++++++++++++++++
Count of all unique journalist targets affected by incidents matching the given filter parameters.

.. code:: jinja

    {% num_journalist_targets date_lower="2017-01-01" date_upper="2017-12-31" %}

num_institution_targets
++++++++++++++++++++++
Count of all unique institution targets affected by incidents matching the given filter parameters.

.. code:: jinja

    {% num_institution_targets date_lower="2017-01-01" date_upper="2017-12-31" %}

num_targets
+++++++++++
Combined count of num_institution_targets and num_journalist_targets, with the same filter parameters applied to both.

.. code:: jinja

    {% num_targets date_lower="2017-01-01" date_upper="2017-12-31" %}

Filter parameters
-----------------

Incident filter datasets accept the following parameters to filter the incidents used to calculate their values.
The options in this section correspond exactly to the options in the incident filtering interface on the website.
All filter parameters are optional.
If no filter parameters are provided, a dataset will calculate its value based on all the incidents in the database.

.. note::

    Some filter parameters are only available if a category that lists the parameter as one of its incident filters is also being filtered on.
    To filter on a category, use the ``categories`` filter as described in `Many relation filters`_.


Text filters
++++++++++++

Text filters check whether an incident has an exact value for a given field.

.. code:: jinja

    {% num_incidents city="Albuquerque" %}

Available filters:

- border_point
- city
- lawsuit_name
- target_us_citizenship_status
- third_party_in_possession_of_communications


Date filters
++++++++++++

Dates can be filtered by lower and upper bounds by adding ``_lower`` and ``_upper`` suffixes to the filter name.
Dates must be provided in YYYY-MM-DD format and quotated.
For example, to add lower and upper bounds to the ``date`` filter:

.. code:: jinja

    {% num_incidents date_lower="2017-01-01" date_upper="2017-12-31" %}

Available filters:

- date
- detention_date
- release_date

.. note:: ``date`` uses fuzzy filtering, which means that incidents whose exact date is not known will match any incident filter that overlaps with the month in which the incident occurred.

Boolean filters
+++++++++++++++

Boolean values can be filtered using 'True' or 'False':

.. code:: jinja

    {% num_incidents categories="4" unnecessary_use_of_force="True" %}

Available filters:

- charged_under_espionage_act
- denial_of_entry
- is_search_warrant_obtained
- stopped_previously
- unnecessary_use_of_force

Choice filters
++++++++++++++

Choice fields can be filtered by providing one or more choice options.
Choice options will vary from filter to filter.
Valid choices can be found in `incident/models/choices.py <https://github.com/freedomofpress/pressfreedomtracker.us/blob/develop/incident/models/choices.py>`_.

.. code:: jinja

    {% num_incidents categories="6" third_party_business="ISP,TRAVEL" %}

Available filter:

- actor
- arrest_status
- assailant
- detention_status
- legal_order_type
- status_of_charges
- status_of_prior_restraint
- status_of_seized_equipment
- subpoena_statuses
- subpoena_type
- third_party_business

Boolean "maybe" filters are a special case of choice filters that accept the values "Yes", "No", and "Maybe" as their choices.

- did_authorities_ask_about_work
- did_authorities_ask_for_device_access
- did_authorities_ask_for_social_media_pass
- did_authorities_ask_for_social_media_user
- held_in_contempt
- was_journalist_targeted
- were_devices_searched_or_seized

Relation filters
++++++++++++++++

Relation filters represent a database connection to another data model.
Params should use the id of the related object to refer to it.

.. code:: jinja

    {% num_incidents state=1 %}

You can get an object's id by opening it for editing in the admin and looking at the URL bar.

- state

Many relation filters
+++++++++++++++++++++

Many relation filters represent a database connection to multiple instances of a model.
Params should use a comma-separated list of ids for the desired objects.

.. code:: jinja

    {% num_incidents categories="1,2,3,4" %}

All incidents related to `any` of the given objects will be included in this filter.
You can get an object's id by opening it for editing in the admin and looking at the URL bar.

- categories
- equipment_broken
- equipment_seized
- politicians_or_public_figures_involved
- related_incidents
- tags
- target_nationality
- targeted_journalists
- targeted_institutions
- workers_whose_communications_were_obtained
- venue


Charges
+++++++

The charges filter is like a many relation filter but will filter on both dropped and current charges.

.. code:: jinja

    {% num_incidents charges="1,2,3" %}

Circuits
++++++++

The circuits filter is like a choice filter but lets users enter a given circuit to automatically filter by the states in that circuit's jurisdiction.

.. code:: jinja

    {% num_incidents circuits="eleventh,tenth" %}

Search filter
+++++++++++++

The search filter takes a string value and performs a search of the items in the database using the same logic as for the incident filter.

.. code:: jinja

    {% num_incidents search="lorem ipsum" %}


Other Datasets
==============

incidents_in_year_range_by_month
--------------------------------

This dataset is intended to be used with one of the table templates.
It returns incident count data by month.
The year range includes the start and end years.

Parameters:

- start_year
- end_year

.. code:: jinja

    {% incidents_in_year_range_by_month start_year=2014 end_year=2016 %}


Developing New Statistics
=========================

Summary
-------

The "statistics" app is a feature that allows administrators and authors to embed the output of statistics helper functions into posts and other site content.
The helper functions are Python functions that query the incident database and return either numbers or maps (i.e. a series of data pairs), though any code is possible.
They can be added to site content either by using template tags or by taking advantage of the StatisticsBlock within a StreamField.

Statistics Functions
--------------------

There are many ways to analyze the IncidentPages in our database.
It is possible to expose some of querying capabilities directly to the people who edit content on the site via statistics functions.
Consider a simple statistics: the total number of incidents that happened in a given year.
To obtain this number, you might write a function like this:

.. code:: python

    from django import template
    register = template.Library()

    @statistics.number
    @register.simple_tag
    def num_incidents(year):
        return IncidentPage.objects.filter(
            live=True,
            date__year=year,
        ).count()

This is a very simple function, and you could write many different ones like it to probe different aspects of the Incidents on file.
Right now these are stored in ``statistics/templatetags/statistics_tags.py``.


Numbers vs Maps
---------------

Statistics functions can return two types of data: numbers and maps.
Number functions are expected to return integers.
Map functions are expected to return a list of tuples in the form of (header, value).
In order to make sure content editors can't cause 500 errors, statistics functions should always return values of the correct type and never raise errors.

Please include tests for any new statistics tags.


Embedding statistics in StreamFields and templates
--------------------------------------------------

There are two decorators we put on the statistics functions.
The first, ``@statistics.number`` (or ``@statistics.map``), marks the function as providing a dataset that can be used by StatisticsBlock.

The second, ``@register.simple_tag``, marks the function as usable inside Django templates as part of the ``statistics_tags`` template tag library:

.. code:: jinja

    {% load statistics_tags %}
    The number of incidents in 2017 was {% num_incidents date_lower="2017-01-01" date_upper="2017-12-31" %}, compared with the number in 2016: {% num_incidents date_lower="2016-01-01" date_upper="2017-12-31" %}.

We also expose the statistics_tags library automatically to content editors in certain StreamFields, for example in SimplePage.body.
This has two parts:

1. Adding a template block to the StreamField.
   There are two template blocks in the common app: ``common.blocks.RichTextTemplateBlock`` and ``common.blocks.StyledTextTemplateBlock``.
   These blocks handle validation of template content so that template editors can't save data that contains syntax errors.
   (You can also directly add ``common.validators.validate_template`` to any non-StreamField to add template validation.)
   Validation will also disallow tags that shouldn't be used in a dynamic content context.
2. Use the ``{% render_as_template %}`` tag to render the content as a template when rendering the page as a whole.
   This will not give the dynamic content access to outside context.
   The template blocks will already handle rendering template content by default.
   This tag should only be necessary when building new block templates or enabling template content on basic rich text fields.

For the latter part, it might look something like this:

.. code:: jinja

    {% load render_as_template %}

    {% render_as_template rich_text_value %}

Visualizations
--------------

StatisticsBlocks allow users to select visualizations.
Visualizations are developer-created templates for rendering a particular type of data in a particular block-based style.
Here is an example of a table-based visualization: fairly ordinary, but given extra importance by the large font size and credibility by the stately color blue:

.. code:: jinja

    <div style="font-size: 200%; color: blue !important">
        <table cellpadding="5">
            {% for line in data %}
                <tr>
                    <td>{{ line.0 }}</td>
                    <td>{{ line.1 }}</td>
                </tr>
            {% endfor %}
        </table>
    </div>

In this case, we see that this visualization is suitable for rendering a map, or iterable series of data points, rather than a single-valued number.
Of note is the ``data`` context variable: this is the variable in which the data from the statistics function is stored at render time.

You can create as many visualizations as you desire.
Right now they're all stored in the directory ``statistics/templates``.
In order for the ``StatisticsBlock`` to be aware of them, they must be added (along with a descriptive name) to the ``get_visualization_choices`` function in ``statistics/blocks.py``.
