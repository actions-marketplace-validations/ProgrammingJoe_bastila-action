import os
import subprocess
import github
from github import Github

# Make a GET request to example.com/api/standards to retrieve the search strings
try:
    result = requests.get('https://example.com/api/standards')
    result.raise_for_status()
    search_strings = result.text.splitlines()
except requests.exceptions.RequestException as e:
    print(e)
    exit(1)

# Check out the code at the head_ref branch
subprocess.run(['git', 'checkout', os.environ['GITHUB_HEAD_REF']], check=True, stdout=subprocess.PIPE)

# Search the repository for each search string
search_counts = {}
for search_string in search_strings:
    if not search_string:
        continue
    print(f"Searching for {search_string}...")
    result = subprocess.run(['grep', '-rnw', '.', '-e', search_string], check=False, stdout=subprocess.PIPE)
    count = len(result.stdout.decode().splitlines())
    search_counts[search_string] = count

# POST the search counts to example.com/api/standard-run/
payload = {'search_counts': search_counts}
try:
    result = requests.post('https://example.com/api/standard-run/', json=payload)
    result.raise_for_status()
except requests.exceptions.RequestException as e:
    print(e)
    exit(1)

# Create a check with the search results
repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
head_sha = os.environ['GITHUB_HEAD_SHA']
search_strings_str = "\n".join(search_strings)
output = f"Search results for the following strings:\n\n{search_strings_str}{search_results}"
check = repo.create_check_run(
    name='Search Repository',
    head_sha=head_sha,
    conclusion='success',
    output={
        'title': 'Search Results',
        'summary': output
    }
)
print(f"Check created: {check.html_url}")
