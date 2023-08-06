# -*- coding: utf-8 -*-
from sqlalchemy.orm.session import object_session


class NestedSet(object):

    def is_root(self):
        return self.parent is None

    def ancestors_query(self, cls):
        return object_session(self).query(cls)\
                .with_parent(self.parent)\
                .filter(cls.left < self.left)\
                .filter(cls.right > self.right)\
                .order_by(cls.left.asc())
