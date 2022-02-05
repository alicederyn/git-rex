"""Unit and integration tests

These should be used to test:
 - edge cases in complex algorithms
 - error handling in code that handles user inputs
 - integrations that would be hard to debug if they broke in a system test

Aim to test the smallest collection of units that adequately capture meaningful
behaviour, across the most stable API boundary. In particular:
 - Mocking makes tests faster, but by increasing the API boundary, it increases
   fragility, and risks blocking agile refactoring. Use with caution.
 - If no stable API boundary exists, consider refactoring until you have one.
"""
