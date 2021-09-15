class SearchMixin:
    
    queryset = None
    SEARCH_FIELDS = ()
    
    def get_queryset(self):
        queryset = self.queryset
        params = self.request.query_params
        for search_field in self.SEARCH_FIELDS:
            search_attrs = [(k, v) for k, v in params.items() if k.startswith(search_field)]
            if search_attrs:
                field, value = search_attrs[0]
                value = self.prevent_xss(value)
                queryset = queryset.filter(**{field: value})
        return queryset
            
    @staticmethod
    def prevent_xss(text):
        return text.replace(')', '').replace('(', '').replace('.', '')
