def get_searchable_content_for_fields(value, child_blocks, fields_to_index):
    """Returns the searchable content for a subset of indexable fields

    Intended to be used with StructBlocks or other collections of
    blocks where not all fields should be included in the public
    index.

    `fields_to_index` should be a list of field names.

    """
    content = []
    for field in fields_to_index:
        content.extend(child_blocks[field].get_searchable_content(value[field]))
    return content
