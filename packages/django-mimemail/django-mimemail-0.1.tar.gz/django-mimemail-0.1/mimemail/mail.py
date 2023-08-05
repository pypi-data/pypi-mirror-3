import re
import os
import mimetypes
import random

from BeautifulSoup import BeautifulSoup, Tag

from django.conf import settings
from django.core.mail import  EmailMessage, SafeMIMEText, \
        SafeMIMEMultipart, make_msgid
from django.template.loader import render_to_string

from email.Utils import formatdate
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage

__all__ = ('MultipartEmail', )


def random_string(length=10):
    return ''.join(
        random.choice("abcdefghijklmnopqrstuvwxyz" +
                      "ABCDEFGHJIKLMNOPQRSTUVWXYZ0123456789")
        for _ in xrange(length))

def root_path():
    return os.path.normpath(getattr(settings, 'MIMEMAIL_MEDIA_ROOT', settings.MEDIA_ROOT))


class MimeTranslator(object):
    def __init__(self, extra_images=None):
        self.extra_images = extra_images or {}
        self.uid_count = 0

    def get_uid(self):
        self.uid_count += 1
        return self.uid_count

    def translate(self, html):
        soup = BeautifulSoup(html)
        cids = self.harvest_cids(soup)
        return soup.prettify(), cids

    def __call__(self, *args, **kwargs):
        return self.translate(*args, **kwargs)

    def harvest_cids(self, soup):
        images = []
        for tag in soup:
            if not isinstance(tag, Tag):
                continue

            for attrname, attrval in tag.attrs:
                match = re.match("^cid:(.*)$", attrval)

                if not match:
                    continue

                image, cid = self.find_image(match.group(1))
                tag[attrname] = "cid:%s" % cid
                images.append(image)

            images.extend(self.harvest_cids(tag))
        return images



    def find_image(self, cid):
        if cid in self.extra_images:
            resolved = self.extra_images[cid]
        else:
            resolved = cid

        if isinstance(resolved, basestring):
            path = os.path.normpath(os.path.join(root_path(), resolved))

            if os.path.commonprefix([path, root_path()]) != root_path():
                raise ValueError("Path: %s is outside of %s" % (path, root_path()))

            f = open(path, "rb")
            try:
                image_data = f.read()
            finally:
                f.close()
        else:
            image_data = None
            if hasattr(resolved, 'seek'):
                resolved.seek(0)

            # XXX: replace with iter check, and iter.
            for m in ['get_content_as_string', 'read']:
                if hasattr(resolved, m):
                    image_data = getattr(resolved, m)()
                    break
            if image_data is None:
                raise ValueError(
                    "%s from %s of type %s, has no applicable method" %
                    (unicode(resolved), cid, type(resolved)))

        ctype, _ = mimetypes.guess_type(cid)
        if ctype:
            _, subtype = ctype.split("/")
        else:
            subtype = "octet-stream"

        _, ext = os.path.splitext(cid)
        new_cid = "%d-%s%s" % (self.get_uid(), random_string(), ext)

        mime_image = MIMEImage(image_data, _subtype=subtype)
        mime_image.add_header("Content-ID", "<%s>" % new_cid)

        return mime_image, new_cid


class MultipartEmail(EmailMessage):
    def __init__(self, template='', context=None, html_context=None,
                 text_context=None, extra_images=None, **kwargs):

        super(MultipartEmail, self).__init__(
            body="This is a multi-part message in MIME format.", **kwargs)

        encoding = self.encoding = self.encoding or settings.DEFAULT_CHARSET

        related = MIMEMultipart("related")

        alternative = MIMEMultipart("alternative")
        related.attach(alternative)
        self.attach(related)

        text_content = render_to_string(
            "%s.txt" % template, text_context or context or {})
        text_part = SafeMIMEText(text_content, 'plain', encoding)
        alternative.attach(text_part)

        html_content = render_to_string(
            "%s.html" % template, html_context or context or {})
        html_content, images = MimeTranslator(extra_images=extra_images)(html_content)
        html_part = SafeMIMEText(html_content, 'html', encoding)
        alternative.attach(html_part)

        for image in images:
            related.attach(image)

    def message(self):
        msg = SafeMIMEMultipart(_subtype='mixed')
        msg.preamble = self.body

        for attachment in self.attachments:
            if isinstance(attachment, MIMEBase):
                msg.attach(attachment)
            else:
                msg.attach(self._create_attachment(*attachment))

        # Copy-paste from django.
        msg['Subject'] = self.subject
        msg['From'] = self.extra_headers.get('From', self.from_email)
        msg['To'] = ",".join(self.to)

        header_names = [key.lower() for key in self.extra_headers]
        if 'date' not in header_names:
            msg['Date'] = formatdate()
        if 'message-id' not in header_names:
            msg['Message-ID'] = make_msgid()

        for name, value in self.extra_headers.items():
            if name.lower() == 'from':  # From is already handled
                continue
            msg[name] = value
        return msg
