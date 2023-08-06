from elasticutils import get_es, S


HOST = 'localhost:9200'
INDEX = 'fooindex'
DOCTYPE = 'testdoc'


es = get_es(hosts=HOST, default_indexes=[INDEX])

es.delete_index_if_exists(INDEX)

mapping = {
    DOCTYPE: {
        'properties': {
            'id': {'type': 'integer'},
            'name': {'type': 'string', 'index': 'not_analyzed'},
            # 'revenue': {'type': 'double'}
            }
        }
    }

es.create_index(INDEX, settings={'mappings': mapping})

for mem in [{'id': 1, 'name': 'joe', 'revenue': 'a'},
            {'id': 2, 'name': 'janet', 'revenue': 3.6},
            {'id': 3, 'name': 'fred', 'revenue': 1.0}]:
    es.index(mem, INDEX, DOCTYPE, id=mem['id'])

es.refresh()

print es.get_mapping(DOCTYPE)

s = S().indexes(INDEX).doctypes(DOCTYPE).values_dict().filter(name='janet').filter(revenue='3.6')
print list(s)
s = S().indexes(INDEX).doctypes(DOCTYPE).values_dict().filter(name='joe')
print list(s)
