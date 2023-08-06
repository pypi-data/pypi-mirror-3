EDUMETADATA_SETTINGS = {
    'FK_REGISTRY': {
        'grade': {
            'simpletext.SimpleTextOne': (
                'primary_grade',
                {'name': 'secondary_grade', 
                'related_name': 'simpletext_secondary_grades'}
            )
        },
        'subject': {'simpletext.SimpleTextOne': 'subject'},
        'education_category': {'simpletext.SimpleTextOne': 'education_category'},
        'alternate_type': {'simpletext.SimpleTextOne': 'alternate_type'},
        'geologic_time': {'simpletext.SimpleTextOne': 'geologic_time'},
    },
    'M2M_REGISTRY': {
        'grade': {
            'simpletext.SimpleTextTwo': (
                'grades',
                {'name': 'secondary_grades', 
                'related_name': 'simpletexttwo_secondary_grades'}
            )
        },
        'subject': {'simpletext.SimpleTextTwo': 'subject'},
        'education_category': {'simpletext.SimpleTextTwo': 'education_categories'},
        'alternate_type': {'simpletext.SimpleTextTwo': 'alternate_types'},
        'geologic_time': {'simpletext.SimpleTextTwo': 'geologic_times'},
    }
}