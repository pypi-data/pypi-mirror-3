from DateTime import DateTime

class ExcludeFromNavMixin:

    def exclude_from_nav(self):
        try:
            week = self.getWeekAsDate() + 7
            if week >= DateTime():
                return False
            else:
                return True
        except AttributeError:
            raise
