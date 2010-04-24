=======================
Memory Tools for Python
=======================

What is it about?
=================

Memory Tools is an implementation of the Memoized pattern in different types
of storages. It enables the user to optimize computationally-expensive
functions by saving their return value in a "Storage" and giving it a "key".
The next time you call your cpu-hungry function, the wrapper looks for a
matching key. If it cannot find any stored value then it computes and stores
the result.


Where can I find the code?
==========================

Here[1], in GitHub! Feel free to fork it and send patches if you want!

[1] http://github.com/pcostesi/pymemtools/
