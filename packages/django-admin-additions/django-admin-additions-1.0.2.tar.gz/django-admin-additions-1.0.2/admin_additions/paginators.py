"""
LargeTablePaginator: from http://djangosnippets.org/snippets/2593/

Use this paginator to make admin pages load more quickly for large tables when 
using PostgreSQL. It uses the reltuples statistic instead of counting the rows 
when there is no where clause.

Original author: AlecC
"""

from django.core.paginator import Paginator

class LargeTablePaginator(Paginator):
    """
    Overrides the count method to get an estimate instead of actual count when not filtered
    """
    def _get_count(self):
        """
        Changed to use an estimate if the estimate is greater than 10,000
        Returns the total number of objects, across all pages.
        """
        if self._count is None:
            try:
                estimate = 0
                if not self.object_list.query.where:
                    try:
                        cursor = connection.cursor()
                        cursor.execute("SELECT reltuples FROM pg_class WHERE relname = %s",
                            [self.object_list.query.model._meta.db_table])
                        estimate = int(cursor.fetchone()[0])
                    except:
                        pass
                if estimate < 10000:
                    self._count = self.object_list.count()
                else:
                    self._count = estimate
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                self._count = len(self.object_list)
        return self._count
    count = property(_get_count)