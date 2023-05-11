import requests
import json
import re
from pathlib import Path
import sys
import os

base_url = 'https://bastilaapi-production.up.railway.app'
# base_url = 'https://bastila.dev'


def fetch_patterns(session):
    response = session.get(f'{base_url}/api/check/standard-changes/')
    response.raise_for_status()
    standards = response.json()

    return standards['results']


def search_files(patterns):
    results = []

    # Loop over every pattern
    for pattern in patterns:
        # Loop over every file
        snippet_instances = 0
        for path in Path('.').glob('**/*'):
            if path.is_dir():
                continue

            with open(path, 'rb') as f:
                content = f.read()

            patterns_in_file = re.findall(pattern['snippet'].encode(), content)
            snippet_instances += len(patterns_in_file)

        pattern_failed = pattern['previous_count'] and (snippet_instances > pattern['previous_count'])
        results.append({
            'id': pattern['id'],
            'previous_count': pattern['previous_count'],
            'count': snippet_instances,
            'is_successful': not pattern_failed,
            'fix_recommendation': pattern['fix_recommendation']
        })

    return results


def post_results(session, result):
    response = session.post(
        f'{base_url}/api/check/check-results/',
        data=json.dumps(result)
    )
    response.raise_for_status()
    return response


def create_check(session):
    response = session.post(
        f'{base_url}/api/check/code-checks/',
        data=json.dumps({})
    )
    response.raise_for_status()
    return response.json()


def main():
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Api-Key {os.getenv('BASTILA_KEY')}',
        'Content-Type': 'application/json'
    })
    print('Starting')

    try:
        check = create_check(session)
    except Exception as e:
        sys.exit(e)

    print('Started Check')

    try:
        patterns = fetch_patterns(session)
    except Exception as e:
        sys.exit(e)

    print('Patterns Fetched')

    try:
        results = search_files(patterns)
    except Exception as e:
        sys.exit(e)

    print('Code Searched')

    result = {
        'check': check['id'],
        'results': results
    }
    try:
        post_results(session, result)
    except Exception as e:
        sys.exit(e)

    print('Results Saved')

    is_regression = False
    for result in results:
        if not result['is_successful']:
            is_regression = True

    if is_regression:
        sys.exit(1)
        print('Check Failed')

    print('Success')


if __name__ == '__main__':
    main()
