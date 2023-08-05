#!/Users/zachwill/code/dom/env/bin/python

"""
An easy way to see domain name availability from the command line.
"""

import json
from argparse import ArgumentParser
import requests
from termcolor import colored


def environment():
    """Parse any command line arguments."""
    parser = ArgumentParser()
    parser.add_argument('query', type=str, nargs='+',
                        help="Your domain name query.")
    parser.add_argument('-i', '--info', action='store_true',
                        help="Get information for a domain name.")
    args = parser.parse_args()
    return args


def domainr(environment):
    """Use domainr to get information about domain names."""
    if environment.info:
        url = "http://domai.nr/api/json/info"
    else:
        url = "http://domai.nr/api/json/search"
    json_data = requests.get(url, params={'q': environment.query})
    data = parse(json_data.content, environment.info)
    return data


def parse(content, info):
    """Parse the relevant data from JSON."""
    data = json.loads(content)
    if not info:
        # Then we're dealing with a domain name search.
        output = []
        results = data['results']
        for domain in results:
            name = domain['domain']
            availability = domain['availability']
            if availability == 'taken':
                symbol = colored(u"\u2717", 'red')
            else:
                name = colored(name, 'blue', attrs=['bold'])
                symbol = colored(u"\u2713", 'green')
            string = "%s  %s" % (symbol, name)
            output.append(string)
        return '\n'.join(output)
    # Then the user wants information on a domain name.
    return data


def main():
    args = environment()
    print domainr(args)


if __name__ == '__main__':
    main()
