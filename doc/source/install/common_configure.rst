2. Edit the ``/etc/ranger/ranger.conf`` file and complete the following
   actions:

   * In the ``[database]`` section, configure database access:

     .. code-block:: ini

        [database]
        ...
        connection = mysql+pymysql://ranger:RANGER_DBPASS@controller/ranger
