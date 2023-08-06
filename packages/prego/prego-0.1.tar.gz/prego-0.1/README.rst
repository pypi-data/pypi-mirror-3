
Prego is a system test framework running as Python unittest testcases.


Matchers
--------

- test.assert_that(Host('www.google.com'), reachable())
- test.assert_that(Host('www.google.com'), listen_port(80))

+ test.assert_that(Host('localhost'), listen_port(2000))
+ test.assert_that(localhost, listen_port(2000))
+ test.assert_that(localhost, is_not(listen_port(3000)))
