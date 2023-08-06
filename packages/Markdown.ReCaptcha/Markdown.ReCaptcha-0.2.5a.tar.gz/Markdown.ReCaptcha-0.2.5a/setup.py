from distutils.core import setup

setup(name='Markdown.ReCaptcha',
      py_modules=['mdx_recaptcha'],
      description='Markdown extension providing ReCaptcha email protection',
      author='Karl Gyllstrom',
      version='0.2.5a',
      author_email='karl.gyllstrom+mdx_recaptcha@gmail.com',
      url='https://github.com/gyllstromk/Markdown-ReCaptcha-extension',
      requires=['Markdown(>=2.1.1)', 'recaptcha_client']
      )
