========
Settings
========

'FK_REGISTRY' = {
   'grade': {
      'app.Model': 'gradelevel',
      'app.Model2': (
         'primary_grade',
         {'name': 'secondary_grade', 'related_name': 'secondary_grade',}
      )
   },
   '
}

ENABLE_<FOO>
============

**Default:** ``True``

**Description:** The settings ``ENABLE_GRADES``, ``ENABLE_SUBJECTS``, ``ENABLE_GEOLOGICTIME``, ``ENABLE_ALTTYPES``, and ``ENABLE_EDUCATEGORIES`` will show the model in the Django Admin. 

These settings allow for a cleaner admin if not all features are required. The model is created in the database, to make it easier to enable later.

FK_REGISTRY
===========

**Default:** ``{}``

**Description:** Dynamically add fields to other models. The value consists of several 

HISTORICAL_DATE_FIELDS
======================

**Default:** ``{}``

**Description:** Models which to dynamically add one or more :py:class:`HistoricalDateField`\ s. 

Registering one HistoricalDate field to model
---------------------------------------------

The simplest way is to specify the name of the field, such as:

.. code-block:: python
	
	EDUMETADATA_SETTINGS = {
	    'HISTORICAL_DATE_FIELDS': {
	        'app.AModel': 'event_data'
	    }
	}

This is equivalent to adding the following the ``AModel`` of ``app``\ :

.. code-block:: python
	
	event_date = HistoricalDateField()


If you want more control over the new field, you can use a dictionary and pass other field options. The ``name`` key is required:

.. code-block:: python
	
	EDUMETADATA_SETTINGS = {
	    'HISTORICAL_DATE_FIELDS': {
	        'app.AModel': {'name': 'event_date', 'blank': True}
	    }
	}

This is equivalent to adding the following the ``AModel`` of ``app``\ :

.. code-block:: python

	event_date = HistoricalDateField(blank=True)

Registering two or more HistoricalDate fields to a Model
--------------------------------------------------------

When you want more than one :py:class:`HistoricalDateField` to a model, you can pass multiple field configurations in a ``list`` or ``tuple``.

.. code-block:: python
	
	EDUMETADATA_SETTINGS = {
	    'HISTORICAL_DATE_FIELDS': {
	        'app.MyModel': (
	            'start_date', 
	            {'name': 'end_date', 'blank': True}, 
	         )
	    },

