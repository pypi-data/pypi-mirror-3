class Zone(object):

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return 'Zone {id: %d, name: %s}' % (self.id, self.name)


class Record(object):

    def __init__(self, id, name, type, priority, content, ttl):
        self.id = id
        self.name = name
        self.type = type
        self.priority = priority
        self.content = content
        self.ttl = ttl

    def __str__(self):
        return ('Record {'
                'id: %d, '
                'name: %s, '
                'type: %s, '
                'priority: %s, '
                'content: %s, '
                'ttl: %d'
                '}') % (self.id,
                        self.name,
                        self.type,
                        self.priority,
                        self.content,
                        self.ttl)
