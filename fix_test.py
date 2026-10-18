import re

content = open('tests/e2e/test_vpc_keepalive_validation.py', 'r').read()
content = re.sub(r'"vpc_domain": (\d+)', r'"vpc_domain": "\1"', content)
content = re.sub(r'{"domain": (\d+)', r'{"domain": "\1"', content)
open('tests/e2e/test_vpc_keepalive_validation.py', 'w').write(content)
print("Fixed test file")
