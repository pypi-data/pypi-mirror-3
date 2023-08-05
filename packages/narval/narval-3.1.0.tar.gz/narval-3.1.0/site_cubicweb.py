
options = (
    ('bot-pyro-id',
     {'type' : 'string',
      'default' : ':narval.narval',
      'help': ('Identifier of the narval bot in the pyro name-server.'),
      'group': 'narval', 'level': 1,
      }),
    ('bot-pyro-ns',
     {'type' : 'string',
      'default' : None,
      'help': ('Pyro name server\'s host where the bot is registered. If not '
               'set, will be detected by a broadcast query. You can also '
               'specify a port using <host>:<port> notation.'),
      'group': 'narval', 'level': 1,
      }),
    # XXX only for all-in-one or repository config
    ('plan-cleanup-delay',
     {'type' : 'time',
      'default' : '60d',
      'help': ('Interval of time after which plans can be '
               'deleted. Default to 60 days. Set it to 0 if you don\'t '
               'want automatic deletion.'),
      'group': 'narval', 'level': 1,
      }),
    )
