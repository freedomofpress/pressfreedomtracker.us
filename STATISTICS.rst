Statistics
==========

Summary
-------

The "statistics" app is a feature that allows administrators and authors to embed the output of statistics helper functions into posts and other site content.  The helper functions are Python functions that query the incident database and return either numbers or maps (i.e. a series of data pairs), though any code is possible.  They can be added to site content either by using special tags in text fields, or by taking advantage of the StatisticsBlock within a StreamField.

Statistics Functions
--------------------

There are many ways to analyze the IncidentPages in our database.  It is possible to expose some of querying capabilities directly to the people who edit content on the site via statistics functions.  Consider a simple statistics: the total number of incidents that happened in a given year.  To obtain this number, we might write a function like this:

.. code:: python

    def num_incidents(year):
        return IncidentPage.objects.filter(
            live=True,
            date__year=year,
        ).count()

This is a very simple function, and you can imagine writing many different ones like it to probe different aspects of the Incidents on file.  Right now these are stored in ``statistics/templatetags/statistics_tags.py``.


Embedding Statistics as Tags
----------------------------

To allow others to use your statistics functions in their content, you must register them as tags.  This is done using the plain-old Django tag registration process.  I recommend the ``simple_tag`` decorator (see `the documentation <https://docs.djangoproject.com/en/1.11/howto/custom-template-tags/#simple-tags>`_).  Adding it to our stat function declaration like this:

.. code:: python

   from django import template
   register = template.Library()

   @register.simple_tag
   def num_incidents(year):
       return [...]

Allows anyone editing, say, a blog post body to use the tag as follows:

.. code:: jinja

   The number of incidents in 2017 was {% num_incidents 2017 %}, compared with the number in 2016: {% num_incidents 2016 %}.

And, when the blog post is rendered, the appropriate numbers will be inserted.

As a side note: the fact that we have registered ``num_incidents`` as a plain-old Django tag means we can also use it in any template we like, not just in post content.  This may prove useful, eventually.

The ``render_as_template`` tag
------------------------------

The above process works because the blog page template (as well as several other templates) have been set up to process Django tags in their content when rendering.  We use a template tag called render_as_template (under the "common" app) that renders a variable containing a templated string using the Django template engine. This means if you can use registered template tags, context variables, etc. as the values of page fields and have them be dynamically populated with values when rendered.

I should note here that since this basically allows anyone with a login to the /admin/ part of the site to run python code, we wouldn't want to put this feature on the site unless we trust everyone with such access.

Here is how we use ``render_as_template`` to produce blog post bodies.  At the top of the page, we need

.. code:: jinja

    {% load render_as_template %}

And when rendering the field that will contain the template tags:

.. code:: jinja

    {% for block in page.body %}
        {% if block.block_type == 'rich_text' %}
            <section>{% render_as_template block.value %}</section>
        {% else %}
            <section>{% include_block block %}</section>
        {% endif %}
    {% endfor %}

I am including the full context for clarity, but the main action happens when we call ``render_as_template``.

Note: If adding new usage of render_as_template, be sure to add template validation to the relevant field(s), either by using ``common.validators.validate_template`` directly or using one of the Template blocks provided in ``common.blocks``.

StatisticsBlock: Maps, Numbers, and Visualizations
--------------------------------------------------

Maps
~~~~

It is possible to imagine another kind of data query that is not just a number but a series of numbers.  In our parlance these are referred to as maps, which we represent in Python as lists of pairs (i.e. 2-tuples).

Here is such a query:

.. code:: python

    def incidents_in_year_range_by_month(start_year, end_year):
        data = (
            IncidentPage.objects
            .filter(
                live=True,
                date__year__gte=start_year,
                date__year__lte=end_year,
            )
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(c=Count('*')).order_by('month')
        )
        return [(i['month'].strftime('%B %Y'), i['c']) for i in data]

This returns data of the form ``[('Jan 2010', 3), ('Feb 2010', 10)]``.  This is rich, delicious data but it is not optimized for embedding into page content as-is.  This is where we need ``StatisticsBlock``.  This is a type of wagtail block that can be added to any StreamField and consists of two main subfields a statistic (with optional parameters) and a visualization.

Statistics Decorators
~~~~~~~~~~~~~~~~~~~~~

A statistic is just one of our statistics functions (as seen above), but in order for the ``StatisticsBlock`` to be aware of it, we have to apply a decorator.  We supply two: one for numbers and one for maps.  Here is an example of their use:

.. code:: python

    from statistics.registry import Statistics
    statistics = Statistics()

    @statistics.number
    @register.simple_tag
    def num_incidents(year):
        return [...]

    @statistics.map
    def incidents_in_year_range_by_month(start_year, end_year):
        return [...]

While ``@register.simple_tag`` tells Django about the function for use as a tag, the ``@statistics`` decorators tell our own app about the function for use in ``StatisticsBlock`` (or other places we might want statistics).  Both are required if you want both pieces of functionality.

Visualizations
~~~~~~~~~~~~~~

The other piece of the ``StatisticsBlock`` puzzle are visualizations.  A visualization is a Django template that renders a map or a number.  Here is an example of a table-based visualization: fairly ordinary, but given extra importance by the large font size and credibility by the stately color blue:

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

In this case, we see that this visualization is suitable for rendering a map, or iterable series of data points, rather than a single-valued number.  Of note is the ``data`` context variable: this is the variable in which the data from the statistics function is stored at render time.

You can create as many visualizations as you desire.  Right now they're all stored in the directory ``statistics/templates``.  In order for the ``StatisticsBlock`` to be aware of them, they must be added (along with a descriptive name) to the ``get_visualization_choices`` function in ``statistics/blocks.py``.  All this bookkeeping is only slightly cumbersome but it does make everything run a lot more smoothly.

Number and Map Types
~~~~~~~~~~~~~~~~~~~~

I want to emphasize here that numbers and maps are, essentially, functions that can be used by non-programmers, such as authors who will incorporate them into the site content, and designers who will create visualizations for them.  So it is important that they not cause errors (as their users might not be able to debug what is happening), and they their return values match their indicated type of ``number`` or ``map``.  There are examples of testing the return values of these functions in the ``statistics/tests`` folder, and I encourage anyone writing new ones to add similar tests to their own additions.


Using StatisticsBlock
~~~~~~~~~~~~~~~~~~~~~

Once we are set up with at least one statistic and visualization, we are ready to add them to some of our page content.  The content field must be a wagtail ``StreamField`` and that field must offer ``StatisticsBlock`` (see ``BlogPage#body`` in ``blog/models.py`` for an example of how this is configured).

When adding a statistics block, there are dropdown lists of visualizations and statistics.  There is also a ``params`` field which is how you input what parameters should be passed to the underlying statistics function.  These should be input by the user as space-separated values, e.g. ``2014 2016`` for our earlier function ``incidents_in_year_range_by_month``.  This will send ``'2014'`` as the first argument and ``'2016'`` as the second argument, both strings.  Implementing other-typed arguments is left as an exercise for future readers.
