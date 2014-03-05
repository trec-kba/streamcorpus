
from streamcorpus import EntityType, Token, get_entity_type

def test_entity_type():
    tok_per = Token(entity_type=EntityType.PER)
    tok_foo = Token(entity_type=EntityType.CUSTOM_TYPE, custom_entity_type='foo')

    assert get_entity_type(tok_per) == 'PER'
    assert get_entity_type(tok_foo) == 'foo'

