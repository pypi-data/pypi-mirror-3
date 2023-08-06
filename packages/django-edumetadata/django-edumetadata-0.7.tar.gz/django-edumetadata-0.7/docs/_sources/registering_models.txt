.. _registering_models:

==================
Registering Models
==================

.. contents::
   :local:

Registering models in settings.py
=================================

It is nice to not have to modify the code of applications to add a relation to metadata. You can therefore do all the registering in ``settings.py``\ . For example:


.. literalinclude:: code_examples/register_example.py
   :linenos:


The ``FK_REGISTRY`` and ``M2M_REGISTRY`` are dictionaries whose keys are any of the models in Django-Metadata. The values are a :ref:`relationshipdefinition`.

You only need to specify the specific relationship you need. If aren't using  :class:`EducationalGrade`, you don't need to include a ``education_grade`` key.

.. note::
   The default values for ``FK_REGISTRY`` and ``M2M_REGISTRY`` are really closer to:
   
   .. literalinclude:: code_examples/register1.py
   
   And your settings here will update those.


.. _relationshipdefinition:

Relationship Definition
-----------------------

Each model uses a relationship definition to configure and relate itself to other models. The basic format is:

.. code-block:: python

   {'app.ModelName': 'fieldname'}

Which will create a foreign key on ``app.ModelName`` named ``fieldname`` and relates to the assigned model (Grade, Subject, etc.). There is a more advanced syntax that allows you to specify any keyword arguments that a `Django ForeignKey field <https://docs.djangoproject.com/en/1.3/ref/models/fields/#foreignkey>`_ or `ManyToManyField <https://docs.djangoproject.com/en/1.3/ref/models/fields/#manytomanyfield>`_ will accept. 

.. code-block:: python

   {'app.ModelName': {'name': 'fieldname', 'other': 'kwargs'}}

The ``name`` key is required and is used for the field's name. You can also define several relationships within the same model:

.. code-block:: python

   {'app.ModelName': ('fieldname1', {'name': 'fieldname2', 'other': 'kwargs'})}


Registering one metadata field to model
---------------------------------------

The simplest way is to specify the name of the field, such as:

.. code-block:: python
	
	EDUMETADATA_SETTINGS = {
	    'FK_REGISTRY': {
	        'grade': {'app.AModel': 'grade'}
	    }
	}

This is equivalent to adding the following the ``AModel`` of ``app``\ :

.. code-block:: python
	
	grade = models.ForeignKey(Grade)


If you want more control over the new field, you can use a dictionary and pass other ``ForeignKey`` options. The ``name`` key is required:

.. code-block:: python
	
	EDUMETADATA_SETTINGS = {
	    'FK_REGISTRY': {
	        'grade': {
	            'app.AModel': {
	                'name': 'grade', 
	                'related_name': 'amodel_grades'
	            }
	        }
	    }
	}

This is equivalent to adding the following the ``AModel`` of ``app``\ :

.. code-block:: python

	grade = models.ForeignKey(Grade, related_name='amodel_grades')

Registering two or more of the same metadata fields to a Model
--------------------------------------------------------------

When you want more than one relation to ``Grade``\ , all but one of the fields must specify a ``related_name`` to avoid conflicts, like so:

.. code-block:: python
	
	EDUMETADATA_SETTINGS = {
	    'FK_REGISTRY': {
	        'grade':{
	            'app.MyModel': (
	                'primary_grade', 
	                {
	                    'name': 'secondary_grade', 
	                    'related_name': 'mymodel_sec_grade'
	                },
	            )
	        }
	    },

Registering one or more Many-to-Many Grade fields to a Model
------------------------------------------------------------

.. code-block:: python
	
	EDUMETADATA_SETTINGS = {
	    'M2M_REGISTRY': {
	        'app.AModel': 'grades',
	        'app.MyModel': (
	            {'name': 'other_grades', 'related_name': 'other_grades'}, 
	            {'name': 'more_grades', 'related_name': 'more_grades'}, 
	        ),
	    }
	}
