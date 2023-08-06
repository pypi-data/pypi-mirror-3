# -*- coding: utf-8 -*-

from urlparse import urlparse
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from redturtle.video.remote_thumb import RemoteThumb
from redturtle.video.browser.videoembedcode import VideoEmbedCode

class YoutubeGetThumbnail(object):

    def getThumb(self):
        """
        Youtube API 2.0 use this format to return images:
        http://img.youtube.com/vi/<video id>/{0,1,2,3}.jpg;

        video id: an alphanumeric string like 'ODA33daiSS';
        image format: always 'jpg', so we use a fix 'image/jpeg' as mimetype;
        {0,1,2,3}: youtube should provide 4 thumb. The first one (0) is the
                   biggest one; the others are smaller, so we take the biggest.

        So you can call somethign like:
             http://img.youtube.com/vi/S9UABZVATeY/0.jpg
        """
        parsed_remote_url = urlparse(self.context.getRemoteUrl())
        video_id = self.get_video_id(parsed_remote_url)
        img_url = 'http://img.youtube.com/vi/%s/0.jpg'%video_id
        thumb_obj = RemoteThumb(img_url,
                                'image/jpeg',
                                '%s-image.jpg'%video_id)
        return thumb_obj


class ClassicYoutubeEmbedCode(YoutubeGetThumbnail, VideoEmbedCode):
    """ ClassicYoutubeEmbedCode
    Provides a way to have a html code to embed Youtube video in a web page

    >>> from zope.interface import implements
    >>> from redturtle.video.interfaces import IRTRemoteVideo
    >>> from redturtle.video.interfaces import IVideoEmbedCode
    >>> from zope.component import getMultiAdapter
    >>> from redturtle.video.tests.base import TestRequest

    >>> class RemoteVideo(object):
    ...     implements(IRTRemoteVideo)
    ...     remoteUrl = 'http://www.youtube.com/watch?v=s43WGi_QZEE&feature=related'
    ...     size = {'width': 425, 'height': 349}
    ...     def getRemoteUrl(self):
    ...         return self.remoteUrl
    ...     def getWidth(self):
    ...         return self.size['width']
    ...     def getHeight(self):
    ...         return self.size['height']

    >>> remotevideo = RemoteVideo()
    >>> adapter = getMultiAdapter((remotevideo, TestRequest()),
    ...                                         IVideoEmbedCode,
    ...                                         name = 'youtube.com')
    >>> adapter.getVideoLink()
    'http://www.youtube.com/v/s43WGi_QZEE'

    >>> print adapter()
    <div class="youtubeEmbedWrapper">
    <object width="425" height="349">
      <param name="movie" value="http://www.youtube.com/v/s43WGi_QZEE" />
      <param name="allowFullScreen" value="true" />
      <param name="allowscriptaccess" value="always" />
      <param name="wmode" value="transparent">
      <embed src="http://www.youtube.com/v/s43WGi_QZEE" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" wmode="transparent" width="425" height="349"></embed>
    </object>
    </div>
    <BLANKLINE>

    """
    template = ViewPageTemplateFile('classic_youtubeembedcode_template.pt')

    def getVideoLink(self):
        qs = urlparse(self.context.getRemoteUrl())[4]
        params = qs.split('&')
        for param in params:
            k, v = param.split('=')
            if k == 'v':
                return 'http://www.youtube.com/v/%s' % v
    
    def get_video_id(self, parsed_remote_url):
        qs = parsed_remote_url[4]
        return dict([x.split("=") for x in qs.split("&")])['v']
        


class ShortYoutubeEmbedCode(YoutubeGetThumbnail, VideoEmbedCode):
    """ ShortYoutubeEmbedCode 
    Provides a way to have a html code to embed Youtube video in a web page (short way).
    Also, the new version of the embed URL must works:
    
    >>> from zope.interface import implements
    >>> from redturtle.video.interfaces import IRTRemoteVideo
    >>> from redturtle.video.interfaces import IVideoEmbedCode
    >>> from zope.component import getMultiAdapter
    >>> from redturtle.video.tests.base import TestRequest

    >>> class RemoteVideo(object):
    ...     implements(IRTRemoteVideo)
    ...     remoteUrl = 'http://youtu.be/s43WGi_QZEE'
    ...     size = {'width': 425, 'height': 349}
    ...     def getRemoteUrl(self):
    ...         return self.remoteUrl
    ...     def getWidth(self):
    ...         return self.size['width']
    ...     def getHeight(self):
    ...         return self.size['height']

    >>> remotevideo = RemoteVideo()
    >>> adapter = getMultiAdapter((remotevideo, TestRequest()), 
    ...                                         IVideoEmbedCode, 
    ...                                         name = 'youtu.be')
    >>> adapter.getVideoLink()
    'http://youtu.be/s43WGi_QZEE'

    >>> print adapter()
    <div class="youtubeEmbedWrapper">
    <object width="425" height="349">
      <param name="movie" value="http://www.youtube.com/v/s43WGi_QZEE" />
      <param name="allowFullScreen" value="true" />
      <param name="allowscriptaccess" value="always" />
      <param name="wmode" value="transparent">
      <embed src="http://www.youtube.com/v/s43WGi_QZEE" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" wmode="transparent" width="425" height="349"></embed>
    </object>
    </div>
    <BLANKLINE>

    """
    template = ViewPageTemplateFile('short_youtubeembedcode_template.pt')

    def getEmbedVideoLink(self):
        """Video link, just for embedding needs"""
        path = urlparse(self.context.getRemoteUrl())[2]
        return 'http://www.youtube.com/v%s' % path

    def getVideoLink(self):
        path = urlparse(self.context.getRemoteUrl())[2]
        return 'http://youtu.be%s' % path
    
    def get_video_id(self, parsed_remote_url):
        return parsed_remote_url[2].replace('/','')

