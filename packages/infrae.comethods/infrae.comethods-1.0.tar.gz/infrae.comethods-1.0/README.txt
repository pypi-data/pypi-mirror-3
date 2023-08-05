================
infrae.comethods
================

This package provides an helper to write cofunction with the help of
Python generators. It provides a decorator that let you write the
following paradigm::

  from infrae.comethod import cofunction

  @cofunction
  def processor(**options):
      # Init code
      content = yield
      while content is not None:
           # Work on content, set result in result.
           content = yield result
      # Cleanup code


If you create more of those comethods you can nest them::

  import logging

  @cofunction
  def logger(parent **options):
      logger = logging.getLogger(options.get('name', 'default'))
      logger.info('Start')
      content = yield
      while content is not None:
           result = parent(content)
           logger.info('Processed {0}, got {1}'.format(content, result))
           content = yield result
      # Cleanup code
      logger.info('Done')


And you can use it like this::

   with processor() as process:
      with logger(process) as log:
         for item in generator():
             log(item)

Or alternatively::

   with processor() as process:
      with logger(process) as log:
         log.map(generator)


Where generator is a generator that yield values to work on. Of
course, you can do more interesting things after.

You can find the Mercurial code repository at:
https://hg.infrae.com/infrae.comethods/
