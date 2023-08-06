#  Copyright (c) 2011, Karl Gyllstrom
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met: 
#
#  1. Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer. 
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution. 
#  
#     THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#     ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#     WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#     DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#     ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#     (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#     LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#     ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#     (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#     SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  
#     The views and conclusions contained in the software and documentation are those
#     of the authors and should not be interpreted as representing official policies, 
#     either expressed or implied, of the FreeBSD Project.

from recaptcha.client.mailhide import _doterizeemail, asurl
import markdown


class ReCaptchaExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        r = ReCaptchaMailPattern(markdown.inlinepatterns.AUTOMAIL_RE, md)
        if not self.getConfig('recaptcha_public_key') or not self.getConfig('recaptcha_private_key'):
            raise ValueError('missing recaptcha key')

        r.public_key = self.getConfig('recaptcha_public_key')
        r.private_key = self.getConfig('recaptcha_private_key')
        md.inlinePatterns['automail'] = r


def makeExtension(configs={}):
    return ReCaptchaExtension(configs=dict(configs))


class ReCaptchaMailPattern(markdown.inlinepatterns.Pattern):
    """
    Return a ReCaptchaMail link Element given an automail link (`<foo@example.com>`).
    """
    def handleMatch(self, m):
        el = markdown.util.etree.Element('span')

        link = markdown.util.etree.Element('a')
        email = self.unescape(m.group(2))
        if email.startswith("mailto:"):
            email = email[len("mailto:"):]

        url = asurl(email, self.public_key, self.private_key)

        (userpart, domainpart) = _doterizeemail(email)
        prefix = markdown.util.etree.Element('span')
        prefix.text = markdown.util.AtomicString(userpart)
        link.text = markdown.util.AtomicString('...')
        link.set('href', url)
        postfix = markdown.util.etree.Element('span')
        postfix.text = markdown.util.AtomicString(domainpart)

        el.extend([prefix, link, postfix])

        return el
