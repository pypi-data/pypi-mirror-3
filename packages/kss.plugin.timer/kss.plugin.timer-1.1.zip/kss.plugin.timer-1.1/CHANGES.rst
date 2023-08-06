Changelog for kss.plugin.timer
==============================

1.1 (2012-09-12)
----------------

- Moved to github: https://github.com/zestsoftware/kss.plugin.timer
  [maurits]


1.0 (2010-09-23)
----------------

- Nothing changed yet.


0.2 (2009-01-07)
----------------
- Made slightly nicer README.txt file, and added README.txt and HISTORY.txt 
  to package information, as 'long_description'. [simon]

- Copied format parameters to the update event, so that timers that weren't 
  started on this page can still be formatted. [simon]

- Fixed nasty problem where the timer got restarted after performing a server
  action. [maurits]

- Added support for preventdefault on the timer events 'start', 'stop' and
  'reset' - a bit awkward since preventing the defaults on those events
  actually means preventing the click defaults on the nodes for which the
  events are registered, but that's a consequence of the strange event
  implementation in timer. [guido_w]

- Fixed problem that made that only one timer could run at the same time,
  added an option to automatically start a timer, optionally with a start time
  (severely abusing kssattr for this... it seems like it makes sense
  though). [guido_w]

- Added 'reset' event, fixed problem with clicking the start button multiple
  times, added rudimentary unit tests (using jsbase's py.test support, hacked
  to work with 'plain' unittest). [guido_w]

- Added support for two seperate 'displayformat' config vars: one for when the
  time hasn't passed an hour, and one for when it has. Also fixed a set of
  bugs in padding (pad when X < 9 instead of 10?!?) and second display (was
  showing the total number of seconds for %S instead of the number of seconds
  in the current minute). [guido_w]
