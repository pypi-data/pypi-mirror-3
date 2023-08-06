from pprint import pprint
from blend import galaxy

url = 'http://127.0.0.1:8000'
key = 'c18666899798c5ad233c511cd2d66c2d'

gi = galaxy.GalaxyInstance(url, key)

ll = gi.libraries.get_libraries()


# ~~~~~~~~~~ OR ~~~~~~~~~~


gi = galaxy.GalaxyInstance(url, key)

lc = galaxy.libraries.LibraryClient(gi)
ll = lc.get_libraries()
