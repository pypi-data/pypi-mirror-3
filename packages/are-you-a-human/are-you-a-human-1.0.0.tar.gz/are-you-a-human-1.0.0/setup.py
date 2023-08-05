import sys
from distutils.core import setup

package = 'ayah3' if sys.version_info.major == 3 else 'ayah'

setup(
    name = 'are-you-a-human',
    version = '1.0.0',
    author = 'Are You a Human',
    author_email = 'support@areyouahuman.com',
    maintainer = 'Seth Livingston',
    maintainer_email = 'sethlivingston@gmail.com',
    url = 'http://portal.areyouahuman.com',
    license = 'GPL 3.0 (See LICENSE.txt)',
    description = 'Are You a Human (AYAH) Python integration library and CAPTCHA alternative',
    keywords = 'are you a human ayah captcha alternative',
    packages = [package],
)
