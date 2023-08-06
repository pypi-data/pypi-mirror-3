{{ fullname }}
{{ underline }}

.. automodule:: {{ fullname }}

   {% block functions %}
   {% if functions %}
   ---------
   Functions
   ---------

   {% for item in functions %}
   .. autofunction:: {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
   {% if classes %}
   -------
   Classes
   -------

   {% for item in classes %}
   .. autoclass:: {{ item }}
       :members:
       :undoc-members:
       :member-order: bysource
       :show-inheritance:
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block exceptions %}
   {% if exceptions %}
   ----------
   Exceptions
   ----------

   {% for item in exceptions %}
   .. autoexception:: {{ item }}
       :members:
       :undoc-members:
       :show-inheritance:
   {%- endfor %}
   {% endif %}
   {% endblock %}
