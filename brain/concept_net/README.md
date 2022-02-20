# Using concept Net to get relationship between concepts

## Get all concept edge related to a give text
```python
from brain import get_concepts
concepts = get_concepts(cocnept_name="cool",
                        lang="en")
```

## Get related concepts using related API
```python
from brain import get_related_concepts
concepts = get_related_concepts(cocnept_name="cool",
                                query_lang="en",
                                related_lang="en")
```

## Check if two concepts are related
```python
from brain import find_relations
concepts = find_relations(concept_1="earth",
                          concept_2="round",
                          query_lang="en")
```