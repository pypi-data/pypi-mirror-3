import re
from urlparse import urlparse
from cgi import parse_qs

from zope import interface, component

from Products.CMFCore.utils import getToolByName

from raptus.article.media import interfaces

class BaseEmbedder(object):
    interface.implements(interfaces.IVideoEmbedder)
    component.adapts(interfaces.IVideoEmbed)
    
    _template = """"""
    _expression = ""
    
    def __init__(self, context):
        self.context = context
        
    def matches(self):
        return re.match(self._expression, self.context.getRemoteUrl()) is not None
    
    def getEmbedCode(self):
        props = getToolByName(self.context, 'portal_properties').raptus_article
        return self._template % dict(url=self.getUrl(),
                                     width=props.getProperty('media_video_width', 0),
                                     height=props.getProperty('media_video_height', 0))

class YouTube(BaseEmbedder):
    name = "YouTube"
    _template = """
    <object width="%(width)s" height="%(height)s">
      <param name="wmode" value="transparent"></param>
      <param name="movie" value="%(url)s"></param>
      <param name="allowFullScreen" value="true"></param>
      <param name="allowscriptaccess" value="always"></param>
      <embed src="%(url)s" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" wmode="transparent" width="%(width)s" height="%(height)s"></embed>
    </object>
    """
    _expression = "^http(s)?://(www\.)?youtube\.com"
    
    def getUrl(self):
        url = urlparse(self.context.getRemoteUrl())
        qs = parse_qs(url[4])
        return "http://www.youtube.com/v/%s" % qs.get('v', ['',])[0]

class YouTubeShort(YouTube):
    _expression = "^http://youtu.be/"
    
    def getUrl(self):
        return "http://www.youtube.com/v/%s" % self.context.getRemoteUrl()[16:]

class GoogleVideo(BaseEmbedder):
    name = "GoogleVideo"
    _template = """
    <object width="%(width)s" height="%(height)s">
      <param name="wmode" value="transparent"></param>
      <param name="movie" value="%(url)s"></param>
      <param name="allowFullScreen" value="true"></param>
      <param name="allowscriptaccess" value="always"></param>
      <embed id="VideoPlayback" src="%(url)s" style="width:%(width)spx; height:%(height)spx;" allowFullScreen="true" allowScriptAccess="always" type="application/x-shockwave-flash"></embed>
    </object>
    """
    _expression = "^http(s)?://video\.google\.com"
    
    def getUrl(self):
        url = urlparse(self.context.getRemoteUrl())
        qs = parse_qs(url[4])
        return "http://video.google.com/googleplayer.swf?docid=%s" % qs.get('docid', ['',])[0]

class Vimeo(BaseEmbedder):
    name = "Vimeo"
    _template = """
    <object width="%(width)s" height="%(height)s"><param name="allowfullscreen" value="true" />
      <param name="allowscriptaccess" value="always" />
      <param name="movie" value="%(url)s" />
      <embed src="%(url)s" type="application/x-shockwave-flash" allowfullscreen="true" allowscriptaccess="always" width="%(width)s" height="%(height)s"></embed>
    </object>
    """
    _expression = "^http(s)?://(www\.)?vimeo\.com"
    
    def getUrl(self):
        url = urlparse(self.context.getRemoteUrl())
        return "http://vimeo.com/moogaloop.swf?clip_id=%s&amp;server=vimeo.com" % url[2].split('/')[1]

class MyVideo(BaseEmbedder):
    name = "MyVideo"
    _template = """
    <object style="width:%(width)spx;height:%(height)spx;" width="%(width)s" height="%(height)s">
      <param name="movie' value="%(url)s"></param>
      <param name="AllowFullscreen" value="true"></param>
      <param name="AllowScriptAccess" value="always"></param>
      <embed src="%(url)s" width="%(width)s" height="%(height)s" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true"></embed>
    </object>
    """
    _expression = "^http(s)?://(www\.)?myvideo\.[a-z]{2,3}"
    
    def getUrl(self):
        return self.context.getRemoteUrl().replace('/watch/', '/movie/')
