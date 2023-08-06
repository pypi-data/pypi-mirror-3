===================
Products.Faq README
===================

.. contents::

Introduction
============

This product is a simple Faq content type for Plone. It provides the
following features:

 * Two new types, FaqFolder and FaqEntry. FaqFolder can contain FaqEntry and
   FaqFolder to create categories of questions.
 * Questions are collapsable in the FaqEntry's view to show or hide answers.
 * A delay can be specified to marked recent questions as new (display of a
   small icon before titles).

Installation
============

You install it the usual way - Add the product to your buildout and install
it via the Plone controlpanel

Requirements
============

 * Plone 4.0 or later (probably it works with Plone 3 but was not tested)
 * for running the tests plone.app.testing is needed.

Credits
=======

 * Jean-Charles Rogez (jean-charles.rogez@edf.fr)  -- maintainer
 * Tim Terlegard (tim@se.linux.org)
 * Edward Muller (edwardam@interlix.com)
 * Tom Gross (itconsense@gmail.com)

