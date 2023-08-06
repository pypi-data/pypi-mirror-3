Customizing Django-Fack
=======================

.. _custom-templates:

Customizing templates
---------------------

The one thing you'll probably want to do quickly is to make some custom
templates so that the FAQ app "fits" with the rest of your site. Django-Fack
uses the following templates:

    ==============================  ============================================
    Template name                   Use
    ==============================  ============================================
    ``faq/base.html``               The base template that all the other 
                                    included templates extend by default. For a
                                    quick and dirty customization you can just
                                    override this one template, making sure to
                                    provide a ``content`` block, and
                                    everything'll look OK.
                                    
                                    But to get a more custom feel you'll
                                    probably want to move on
                        
    ``faq/question_detail.html``    Used by an individual "question" detail
                                    page.
                                    
                                    The context has one variable, ``question``,
                                    which is the :class:`Question` object.
    
    ``faq/submit_question.html``    Used by the view that allows users to submit
                                    a question.
                                    
                                    The context has the obligatory ``form``
                                    variable, which is a form containing
                                    ``topic``, ``text``, and ``answer`` fields.
                                    
    ``faq/submit_thanks.html``      Shown after a successful FAQ submission.
                                    No context.
                                    
    ``faq/topic_detail.html``       Shows all the FAQs in a given topic.
    
                                    Context:
                                        * ``topic`` - a :class:`Topic`.
                                        * ``questions`` - list of
                                          :class:`Question` objects in the given
                                          topic.
                                          
    ``faq/topic_list.html``         Shows a list of all topics. Context
                                    contains a ``topic`` variable, which is
                                    a :class:`Topic` object.
    ==============================  ============================================

Subclassing FAQ views
---------------------

All of the views in Django-Fack use `class-based generic views`__ and are
designed to be extended. `Consulting the source`__ is your best bet here:
the code's fairly clear, and prose will only complicate things.

If you do choose to subclass views, you'll most likely want to write your
own URLconf (instead of ``fack.urls``). Remember that if you maintain the
names given by the default URLconf all the existing links will continue
to work.

__ http://docs.djangoproject.com/en/dev/topics/class-based-views/
__ https://github.com/revsys/django-fack/blob/master/fack/views.py