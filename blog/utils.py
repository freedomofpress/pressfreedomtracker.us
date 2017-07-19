def string_to_int_or_none(s):
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
        author_id = string_to_int_or_none(query.get('author'))
        organization_id = string_to_int_or_none(query.get('organization'))

        return cls(organization_id, author_id)

    def __init__(self, organization, author):
        self.organization = organization
        self.author = author

    def filter(self, blog_pages):
        field_pairs = [
            ('author', self.author),
            ('organization', self.organization),
        ]
        kwargs = {field: value for field, value in field_pairs if value}
        return blog_pages.filter(**kwargs)
