from pepperedform.renderutils import (build_id, sequence_getter, mapping_getter,
        rename_getter, make_start_token, field_error)


class TestRenderUtils(object):

    def _get_mock_getter(self):
        def _mock_getter(items, name, if_missing=None):
            if items:
                return items.get(name, if_missing)
            return if_missing
        return _mock_getter

    def test_build_id(self):
        render_kwargs = {
            'id_stack': ['dates', '1']
        }
        name = 'day'
        assert build_id(render_kwargs, name) == 'dates_1_day'

    def test_sequence_getter_missing(self):
        items = None
        if_missing = tuple()
        name = 'day'
        result = sequence_getter(items, name, if_missing=if_missing)
        assert result is if_missing, \
                'Should return if_missing if items is falsy.'
        
    def test_sequence_getter(self):
        items = '15'
        if_missing = tuple()
        name = 'day'
        result = sequence_getter(items, name, if_missing=if_missing)
        assert result == '15', \
            'Should return items if items is not falsy.'


    def test_rename_getter_missing(self):
        items = None
        if_missing = tuple()
        name = 'day'
        result = rename_getter(items, name, if_missing=if_missing)
        assert result is if_missing, \
                'Should return if_missing if items is falsy.'
        
    def test_rename_getter(self):
        items = '15'
        if_missing = tuple()
        name = 'day'
        result = rename_getter(items, name, if_missing=if_missing)
        assert result == '15', \
            'Should return items if items is not falsy.'

    def test_mapping_getter_missing(self):
        items = {}
        if_missing = tuple()
        name = 'day'
        result = mapping_getter(items, name, if_missing=if_missing)
        assert result is if_missing, \
                'Should return if_missing if name not in items.'
        
    def test_mapping_getter(self):
        items = {
            'day': '15'
        }
        if_missing = tuple()
        name = 'day'
        result = mapping_getter(items, name, if_missing=if_missing)
        assert result == '15', \
            'Should return value for key name in items if it exists.'

    def test_make_start_token(self):
        name = 'days'
        type_ = 'sequence'
        assert make_start_token(name, type_) == 'days:sequence'
        
    def test_field_error_missing(self):
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'errors': {},
            'id_stack': []
        }
        name = 'day'
        error = field_error(render_kwargs, name)
        assert not error, 'No error should exist'

    def test_field_error(self):
        day_error = 'Today is the wrong day'
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'errors': {
                'day': day_error
             },
            'id_stack': []
        }
        name = 'day'
        error = field_error(render_kwargs, name)
        assert error and error == day_error

