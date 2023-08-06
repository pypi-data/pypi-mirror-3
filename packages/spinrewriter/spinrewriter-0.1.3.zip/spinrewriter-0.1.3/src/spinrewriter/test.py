# -*- coding: utf-8 -*-
from __future__ import print_function
import time

from spinrewriter import Api


text = "This is my {dog|cat|pet} who read a {book|novel} about animal food."
text2 = "This is my little pet who read an article about animal food."
protected_terms = ['food', 'cat']


#test code
def main():
    api = Api('info@niteoweb.com', '1e0f81b#a52de1f_e2775a1?e8aa0e5')
    response = api.api_quota()
    print(response)

    response = api.text_with_spintax(text2, protected_terms)
    print(response)

    print("Going to sleep for 10 seconds")
    time.sleep(10)

    response = api.unique_variation(text2, protected_terms)
    print(response)

    response = api.unique_variation_from_spintax(text, protected_terms)
    print(response)


if __name__ == "__main__":
    main()
