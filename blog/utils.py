def string_to_int_or_none(s):
    """Converts a valid digit string to an integer, or None if not valid"""
    if s:
        try:
            return int(s)
        except ValueError:
            return None
    else:
        return None


class BlogFilter(object):
    @classmethod
    def from_querystring(cls, query):
        """Parse a dict-like querystring object and return a `BlogFilter` for
        those values"""
        author_id = string_to_int_or_none(query.get('author'))
        organization_id = string_to_int_or_none(query.get('organization'))
        blog_type = query.get('type')

        return cls(organization_id, author_id, blog_type)

    def __init__(self, organization, author, blog_type):
        """Configure a BlogFilter

        Arguments:
        organization -- an integer id of an OrganizationPage
        author -- an integer id of a PersonPage

        """

        self.organization = organization
        self.author = author
        self.blog_type = blog_type

    def filter(self, blog_pages):
        """Filter a queryset of blog pages according to author or organization or blog_type."""
        field_pairs = [
            ('author', self.author),
            ('organization', self.organization),
            ('blog_type', self.blog_type),
        ]
        kwargs = {field: value for field, value in field_pairs if value}
        return blog_pages.filter(**kwargs)
