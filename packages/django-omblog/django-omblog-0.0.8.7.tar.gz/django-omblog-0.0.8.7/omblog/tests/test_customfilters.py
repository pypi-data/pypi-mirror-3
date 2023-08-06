# -*- coding: utf-8 -*-
from datetime import datetime
from django.test import TestCase
from omblog.models import Post


class CustomFilterTestCases(TestCase):
    
    def setUp(self):
        """setup stuff"""

    def tearDown(self):
        """teardown stuff"""
        
    
    def test_video_tag(self):
        """The video tag allows a html5 video tag to be outputted using
        {% video http://h264.url http://webm.url http://poster.url %}
        """
        p = Post()
        p.title = 'test post '
        p.source_content = '{% video http://w.video.mp4 http://w.video.webm http://w.poster.jpg %}'
        p.save()
        html = """
		<video controls="controls" poster="http://w.poster.jpg" preload>
			<source src="http://w.video.mp4" type='video/mp4; codecs="avc1.42E01E,mp4a.40.2"'>
			<source src="http://w.video.webm"  type='video/webm; codecs="vp8, vorbis"'>
			<object id="flashvideo" width="720" height="540" data="http://releases.flowplayer.org/swf/flowplayer-3.2.10.swf" type="application/x-shockwave-flash">
				<param name="movie" value="http://releases.flowplayer.org/swf/flowplayer-3.2.10.swf" >
				<param name="allowfullscreen" value="true" />
				<param name="allowscriptaccess" value="always" />
				<param name="flashvars" value='config={"clip":{"url":"http://w.video.mp4'>
			</object>
		</video>"""
        self.assertHTMLEqual(p.rendered_content, html)
