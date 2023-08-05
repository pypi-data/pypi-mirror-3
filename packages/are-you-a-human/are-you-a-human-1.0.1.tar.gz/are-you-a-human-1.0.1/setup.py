import sys
from distutils.core import setup

package = 'ayah3' if sys.version_info[0] == 3 else 'ayah'

setup(
    name = 'are-you-a-human',
    version = '1.0.1',
    author = 'Are You a Human',
    author_email = 'support@areyouahuman.com',
    maintainer = 'Are You a Human',
    maintainer_email = 'plugins@areyouahuman.com',
    url = 'http://portal.areyouahuman.com',
    license = 'MIT (See LICENSE.txt)',
    description = 'Are You a Human (AYAH) Python integration library and CAPTCHA alternative',
    keywords = 'are you a human ayah captcha alternative',
    packages = [package],
)
