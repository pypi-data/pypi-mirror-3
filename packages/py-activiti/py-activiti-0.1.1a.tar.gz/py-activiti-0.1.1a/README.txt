==============================
 py-activiti (v.0.1 pre-alpha)
==============================

pyactiviti is a Python's library which wraps the famous Activiti BPMN2.0 Engine's API. 
Actually, pyactiviti is in early stage, so I think there will be tons of enhancements
in the near future.

Feel free to send your feedback about this project.


--------------
 Requirements
--------------

py-activiti requires *simplejon* module and *django* if you want to try the *forms* features. By the way, 
forms IS NOT YET STABLE since Activiti's forms handling is not that clear for me. I have to improve Activiti
forms features before and tips, and other wonderful ideas are welcome.

NOTA: *django* has to be installed manually !!!


--------------
 Installation
--------------

The easiest way to install py-activity is to use *pip* tool. Simply, execute the following command :

 #:> pip install py-activiti
 


--------------
 Test the API
--------------

To test the Activiti REST API, you should have installed the servlet activiti-webapp-rest2.war 
in your favorite servlet's container, for example Tomcat.I also heavily recommand to use the SVN version 
of Activiti because some bugs were fixed there.

I use the wonderful Python's tool *nose* for testing. So, you have to have *nose* installed on your system. I am
providing a simple BPMN 2.0 diagram to challenge the API. You are free to use yours and report bugs.

First, add the *py-activiti* source directory to your PYTHONPATH, like this::

 #:> export PYTHONPATH=$PYTHONPATH:${py_activiti_dir}/py_activiti/src

Then, go to the *py-activiti* directory::

 #:> cd ${py_activiti_dir}/py_activiti

and then, type the following command in order to begin to test the REST API::

 #:> nosetests-2.7 ./tests

Et voilà!

Per default, the REST API client try to connect to the following address::

 http://localhost:1234/activiti-webapp-rest2-5.9-SNAPSHOT/service/

You can update with your specific configuration, using the *ACTIVITI_SERVICES* environment variable, for example::

 #:> export ACTIVITI_SERVICES = "http://localhost:8080/activiti-webapp-rest/service/"





Enjoy,

--
Thierry Michel
Senior Project Manager @ xtensive.com 