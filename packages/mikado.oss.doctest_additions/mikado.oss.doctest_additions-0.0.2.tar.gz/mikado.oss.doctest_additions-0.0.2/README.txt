============================
doctests, and better testing
============================


This might be a silly idea.

doctest is great.  It is common-sense, well implemented.

The 12 factor app is also great, again common-sense, clearly laid out.

One issue I found was that 12 factor-app recommends printing out log
messages to stdout, so they can be dealt with not by app specific
defaults but global sysytem wide processes.  Thats a good idea.

Having unit tests that are just snippets of examples is also a good
idea.

But suddenly my doctests fail because log messages appear in the
middle of the output


::

   >>> factorial(5)
   120

   <pass>   

becomes

::

   >>> factorial(5)
   Multiplying by 5 
   Multiplying by 4
   Multiplying by 3
   Multiplying by 2
   Multiplying by 1
   120
  
   <fail>


I cannot use ELLIPSIS here because I want to ignore the whole line.
And anyway, the number of lines coming out will depend on the function
call.  errr....If only there was some way to ignore whole lines

I would like to have a means of defining my own OutputChecker class,
and passing that in to the TestRunner.

I honestly could not see a sensible way to do it.



Attempt one
-----------

patch doctest module, so that I can pass in an OutputChecker class.
Basically I want to subclass OutputChecker and then every test I run will
clithely ignore anyline starting [logline].

Seems a good idea

::


    1476c1476
    < class OutputChecker:
    ---
    > class OutputChecker(object):

    OutputChecker cannot use super unless it becomes a 
    new-style object.  That's easy, but will it have 
    unintended side-effects elsewhere?    



    1761c1762,1763
    <             raise_on_error=False, exclude_empty=False):
    ---
    >             raise_on_error=False, exclude_empty=False, 
    >             test_checker=None):

    change the call function of "testmod" so it will accept a new
    OutputChecker.  

    1846c1853,1856
    <         runner = DebugRunner(verbose=verbose, optionflags=optionflags)
    ---
    >         if test_checker:
    >             runner = DebugRunner(checker=test_checker, verbose=verbose, optionflags=optionflags)
    >         else:
    >             runner = DebugRunner(verbose=verbose, optionflags=optionflags)

    

    1848c1858,1861
    <         runner = DocTestRunner(verbose=verbose, optionflags=optionflags)
    ---
    >         if test_checker:
    >             runner = DocTestRunner(checker=test_checker, verbose=verbose, optionflags=optionflags)
    >         else:
    >             runner = DocTestRunner(verbose=verbose, optionflags=optionflags)

    inside testmod, pass in the subclassed object, and hand it off to DocTestRunner


Well, it worked.  I patched doctest.py on my system and hey presto. all fine.

But, although it seems a good idea, I am loathe to start monkeypatching code in the
"batteries included" area, especially as I am sticking code on cloud, wanting other people
to join in the development, running fabric installs on reamote servers.

It  could get VERY messy.

And testmod is a function.  I cannot subclass it which would have been nice.


Attempt two
-----------

Michael Mulich pointed me at some of his old code, that passed in
checker= through the DocFileSuite.  Well I have always tended to ignore 
the unittest code - it never really sat as well as doctests for me.

But yes, there in the docs, "checker=".  But only in DocFileSuite.
Why not in testmod, or testfile.  Well, the DocTest class is where the
action happens - it accepts checker.  DocFileSuite passes **kwds to
DocTestSuite which passes to DocSOmethingElse Which passes to ...

So, there is one route in without monkeypatching - create a unittest
suite, and pass in my subclass OutputChecker

Except OutputChecker is not able to be called with super, as it is 
old-style.

Attempt Three
-------------

OK, I have just cut and paste OutputChecker from doctest, changed the
code right there and now will include it in my tests.

Its really not elegant.

But its a lot less hassle than patching all over the place.  Maybe.

