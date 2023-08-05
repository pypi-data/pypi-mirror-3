.. _getting_started:

Getting Started
===============

If you have not installed SuperTagging yet, go to the :ref:`installation` page.

Create basic settings
*********************

In your ``settings.py`` file:

.. code-block:: python
	
	SUPERTAGGING_SETTINGS = {
	    'ENABLED': True,
	    'DEBUG': True,
	}


Setting up OpenCalais API
*************************

Go to `OpenCalais <http://www.opencalais.com/>`_'s website and register for 
an api key, and in your ``settings.py`` file, alter ``SUPERTAGGING_SETTINGS``\ :

.. code-block:: python
	
	SUPERTAGGING_SETTINGS = {
	    'ENABLED': True,
	    'DEBUG': True,
	    'OPEN_CALAIS': {
	        'API_KEY': 'YOUR_API_KEY',
	    }
	}


Setting up models to be tagged
******************************

You will need to decide which models and which fields in those models you 
will want SuperTagging to mark for tagging:

.. code-block:: python

	SUPERTAGGING_SETTINGS = {
	    'ENABLED': True,
	    'DEBUG': True,
	    'OPEN_CALAIS': {
	        'API_KEY': 'YOUR_API_KEY',
	    },
	    'WATCHED_FIELDS': {
	        'stories.story': {
	            'fields':[
	                {'name': 'body'},
	            ],
	        },
	    },
	}

        
The code above tells SuperTagging to tag the **body** field of model 
**stories.story**. We can specify any number of fields and models as well.

.. code-block:: python

	SUPERTAGGING_SETTINGS = {
	    'ENABLED': True,
	    'DEBUG': True,
	    'OPEN_CALAIS': {
	        'API_KEY': 'YOUR_API_KEY',
	    },
	    'WATCHED_FIELDS': {
	        'stories.story': {
	            'fields':[
	                    {'name': 'body'},
	                    {'name': 'tease'},
	                    {'name': 'kicker'},
	            ],
	        },
	        'media.image': {
	            'fields':[
	                    {'name': 'caption'},
	                    {'name': 'description'},
	            ],
	        }
	    },
	}


View :ref:`setting_modules` for more information.

Set up automatic processing
***************************

Finally, add:

.. code-block:: python

	SUPERTAGGING_SETTINGS = {
	    'ENABLED': True,
	    'DEBUG': True,
	    'OPEN_CALAIS': {
	        'API_KEY': 'YOUR_API_KEY',
	    },
	    'WATCHED_FIELDS': {
	        'stories.story': {
	            'fields':[
	                {'name': 'body'},
	            ],
	        },
	    },
	    'AUTO_PROCESS': True,
	}

Post save and post delete signals will be connected to the models 
specified in `WATCHED_FIELDS`. Visit :ref:`reference_settings` to 
view more details about the SuperTagging settings

View the complete list of :ref:`reference_settings`

Conclusion
**********

That is all that is needed to get SuperTagging to start tagging your data. 
Upon saving a instance of one of the models specified in 
`SUPERTAGGING_MODULES`, the field(s) data will be sent to OpenCalais 
for processing.


Next step: View the :ref:`real_world_example` section of how The Washington 
Times has SuperTagging setup.