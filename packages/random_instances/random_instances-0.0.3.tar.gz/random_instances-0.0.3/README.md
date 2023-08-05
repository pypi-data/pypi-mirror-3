Random Instances
====================================

This module exports a **get\_or\_create_random** function that improves Django's 
[get_or_create](http://djangoproject.com/documentation/models/get_or_create/)
on two aspects:

* invoking **get\_or\_create_random** with parameters that match MULTIPLE instances
does not raise an error, but rather returns one of those instances at random

* invoking **get\_or\_create_random** with parameters that do not match ANY instance
returns a NEW instance of that model (the same occurs with get_or_create). The
improvement is that **get\_or\_create_random** can be invoked without passing a value
for all the 'required' fields of the model. If these fields are not passed, 
they are automatically filled with random values (e.g.: CharFields are filled
with random strings, ImageFields with random images).

The goal is to make prototyping faster, as model instances can be obtained and 
created by specifying just the minimum set of desired fields. This is useful
when writing tests and can avoid having to write complex fixtures.

Installation
====================================

Download and install the package from GitHub, or do it the easy way:

    pip install random_instances

Example usages
====================================

Say you have the following **Subject** model defined in the **subjects** 
application, and no instances of Subject in the database:

    from django.db import models
    class Subject(models.Model):
        word             = models.CharField(unique=True, max_length=255)
        is_current       = models.BooleanField(default=False)

To get or create a random subject, type:

    from random_instances import get_or_create_random
    from subjects.models import Subject
    get_or_create_random(Subject)
    
This will generate an instance of Subject with the following values:

* word => a random string (no longer than 255 characters)
* is_current => a random Boolean value (True or False)

To get or create a subject with a specific value for the *word* field, type:

    get_or_create_random(Subject, word='Peace')

This will generate an instance of Subject with the following values:

* word => 'Peace'
* is_current => a random Boolean value (True or False)

To get a subject or create one with some *default* values, type:

    get_or_create_random(Subject, word='Peace', defaults={'is_current': True})

This will get a Subject instance with word='Peace', if any exists. 
Otherwise, a new one will be created with the following values:

* word => 'Peace'
* is_current => True

In short, **get\_or\_create_random** creates a new instance whenever an 
existing appropriate one cannot be found. The fields of the newly created 
instance are filled according to these ordered rules:

* if the field has been assigned a value in the function parameters, that value is used
* if the field is required (blank=False, null=False), a random value is used
* otherwise, the field is left unassigned


Testing and contributing
====================================

The module contains a suite of tests that can be executed by importing
random_instances into the INSTALLED\_APPS of a Django project and running:

    python manage.py test random_instances

To contribute to the module and report bugs, add the appropriate tests, check
that they pass, then send a pull request with the patch or the fixed bug.


To do
====================================

As of v0.0.2, add relationship fields (ForeignKey, ManyToMany, OneToOne) and
add tests to check that all the fields parameters are respected (e.g., maximum
length for CharField, number of digits for Decimals).


Acknowledgments
====================================

This project was partly inspired by [Dilla](https://github.com/beheadedmyway/dilla).


How random_instances contributes to Test-Driven Development
====================================

After a couple of weeks using [lettuce](http://www.lettuce.it) I found out that
one of the steps I use most often is: 

    Given there is a Photographer 

(substitute Photographer for any Django model you have). For instance, 
one typical scenario is: 

    Given there is a Photographer 
    And I navigate to his detail page 
    Then I should see his pictures 

In this kind of story, I don't care *which* photographer the test will 
run against: any will (or should) work. So the most straightforward 
implementation of this step would be: 

    Photographer.objects.get_or_create() 

that either returns an existing photographer or creates a new one. The 
problem with [Django's get\_or\_create](http:// 
www.djangoproject.com/documentation/models/get_or_create/) is that it will *fail* if 
the query returns multiple instances (in the previous case, if there 
are multiple photographers). 
What I need is a function that returns a *random* instance if any 
exists, otherwise creates a new one. **random_instances** serves this purpose.

Basic Usage
----------------------- 
Using random_instances, the step:

    Given there is a Photographer 

can be easily implemented as: 

    from random_instances import get_or_create_random 
    get_or_create_random(Photographer) 

Optional Fields
----------------------------- 
This function follows the prototype of [Django's get\_or\_create](http:// 
www.djangoproject.com/documentation/models/get_or_create/), so you can 
pass desired and default values for the model's field. For instance, 
say that Photographer has a "name" CharField, an "is\_famous" 
BooleanField and an "avatar" ImageField, then you can have the step: 

    Given there is a Photographer named "Helmut Newton" 

easily implemented as: 

    get_or_create_random(Photographer, name="Helmut Newton") 

which will either return that photographer (if existing) or create a 
new one. 
If you have this step as the Background of a Scenario (that is, 
executed before each scenario), then the instance will only be created 
the first time, and retrieved the successive ones, resulting in better 
performance (shorter time) for the test suite to complete. 

Required fields 
----------------------------- 
What happens if get_or_create_random is invoked without specifying a 
value for a required field? 
For instance, imagine that the Photographer model has an "is\_famous" 
BooleanField that is required (blank=False, null=False) and does not 
have a default value. If your step states: 

    Given there is a Photographer named "Helmut Newton" 

then you do not really care about the value of "is\_famous", so it 
would be a waste of time to specify one just because the field is 
required. The solution provided by get_or_create_random is quite 
intuitive: every field that is required and does not have a default 
value is *automatically* assign a *random* value, coherently with the 
field type (e.g., a random string for CharField, a random number for 
IntegerField, a random image for ImageField). 
For this reason, the implementation 

    get_or_create_random(Photographer, name="Helmut Newton") 

would still work, even without specifying a value for "is\_famous", 
which would be randomly set to True or False. If you really care about 
this value, then you can always set it explicitly, e.g.: 

    Given there is a famous Photographer named "Helmut Newton" 

which would be implemented as: 

    get_or_create_random(Photographer, name="Helmut Newton", is_famous=True) 


Summing up
----------------------- 

random_instances can be beneficial to lettuce users, although 
it has a broader extent (can be actually used inside the same Django 
application to generate random instances of models... anyone sees a nice
usage for that?). It's a faster and more meaningful way to 
create fixtures, since you only specify the fields that you are interested 
in.