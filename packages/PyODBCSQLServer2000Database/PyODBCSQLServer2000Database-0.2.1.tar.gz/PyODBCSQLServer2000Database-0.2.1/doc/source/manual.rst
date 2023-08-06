Manual
++++++

This package is a plugin for the DatabasePipe package which allows you to use the
Database API to work with databases supporting ODBC. Specifically this driver
allows (somewhat limited) access to Microsoft SQLServer databases via the
somewhat convoluted chain of PyODBC->UnixODBC->TDS.

See the `DatabasePipe documentation <../../databasepipe/index.html>`_ for the API.
You need to specify the plugin name ``pyodbcsqlserver2000`` in your database pipe
configuration to use this plugin.
