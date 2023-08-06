from django import template
register = template.Library()

class VideoNode(template.Node):
    
    def __init__(self, h264, webm, poster):
        self.h264 = h264
        self.webm = webm
        self.poster = poster

    def render(self, context):
        context = {
            'webm': self.webm,
            'h264': self.h264,
            'poster': self.poster
        }
        return """<video controls="controls" poster="%(poster)s" preload>
<source src="%(h264)s" type='video/mp4; codecs="avc1.42E01E,mp4a.40.2"'>
<source src="%(webm)s"  type='video/webm; codecs="vp8, vorbis"'>
<object id="flashvideo" width="720" height="540" data="http://releases.flowplayer.org/swf/flowplayer-3.2.10.swf" type="application/x-shockwave-flash">
<param name="movie" value="http://releases.flowplayer.org/swf/flowplayer-3.2.10.swf" >
<param name="allowfullscreen" value="true" />
<param name="allowscriptaccess" value="always" />
<param name="flashvars" value='config={"clip":{"url":"%(h264)s'>
</object>
</video>""" % context




@register.tag
def video(parser, token):
    bits = token.contents.split()
    return VideoNode(bits[1], bits[2], bits[3])



@register.simple_tag
def post_status(post):
    return post.get_status_display().lower()
