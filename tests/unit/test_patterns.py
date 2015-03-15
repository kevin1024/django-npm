from ..util import configure_settings
configure_settings()

from npm.finders import matches_patterns

def test_pattern_matches():
    patterns = {
        'react': ['react.js'],
        'express': ['lib/*.js', 'index.js']
    }
    assert matches_patterns(patterns, 'react/react.js')
    assert not matches_patterns(patterns, 'react/reacty.js')
    assert  matches_patterns(patterns, 'express/lib/whatever.js')
    assert  matches_patterns(patterns, 'express/index.js')
    assert  not matches_patterns(patterns, 'express/index')
