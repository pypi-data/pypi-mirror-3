============
GraphAlchemy
============

.. contents::
    :depth: 2

Graph node-edge relationships in SQLAlchemy (and soon more orms) + networkx
integration.

The Goal
========

Set up a generalized abstraction/interface for a graph that can be used across
various platforms and within various frameworks that is easy and simple to use,
extensible, and that easily hooks into other graphing tools (like gephi_
networkx_, etc.)

What's here
===========

A basic set of node/edge abstractions + many-to-one relationships for a graph
represented in SQL with SQLAlchemy_

Using this package
==================

It's very simple to use (and examples are to come). But 

What's going to be here
=======================

1. networkx_ integration
2. testing for multiple sql databases and adapters
3. abstractions for Google App Engine, mongoalchemy_, and possibly Django ORM
4. adapter between networkx_ and web service requests (maybe?)

Testing coverage
================

Basic test suite that gets 100% line coverage for SQLAlchemy models and base
models (still missing a test for Flask-SQLAlchemy). I've only run it on SQLite
so far, but presumably it should work with other SQL databases just fine (since
it uses SQLAlchemy's `declarative base`_)

.. _sqlalchemy : http://www.sqlalchemy.org/
.. _networkx : http://networkx.lanl.gov/
.. _mongoalchemy : http://www.mongoalchemy.org/
.. _gephi : http://gephi.org/
.. _declarative base : http://docs.sqlalchemy.org/en/rel_0_7/orm/extensions/declarative.html
