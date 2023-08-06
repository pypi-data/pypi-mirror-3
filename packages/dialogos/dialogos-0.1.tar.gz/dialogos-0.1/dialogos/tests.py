from django.conf import settings
from django.template import Template, Context

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from eldarion.test import TestCase

from dialogos.forms import UnauthenticatedCommentForm, AuthenticatedCommentForm
from dialogos.models import Comment


class CommentTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user("gimli", "myaxe@dwarf.org", "gloin")
        self.user2 = User.objects.create_user("aragorn", "theking@gondor.gov", "strider")
    
    def assert_renders(self, tmpl, context, value):
        tmpl = Template(tmpl)
        self.assertEqual(tmpl.render(context), value)
    
    def post_comment(self, obj, data):
        return self.post("post_comment",
            content_type_id=ContentType.objects.get_for_model(obj).pk,
            object_id=obj.pk,
            data=data
        )
    
    def test_post_comment(self):
        g = User.objects.create(username="Gandalf")
        
        response = self.post_comment(g, data={
            "name": "Frodo Baggins",
            "comment": "Where'd you go?",
        })
        self.assertEqual(response.status_code, 302)
        
        self.assertEqual(Comment.objects.count(), 1)
        c = Comment.objects.get()
        self.assertEqual(c.author, None)
        self.assertEqual(c.name, "Frodo Baggins")
        
        response = self.post_comment(g, data={
            "comment": "Where is everyone?"
        })
        self.assertEqual(Comment.objects.count(), 1)
        
        with self.login("gimli", "gloin"):
            response = self.post_comment(g, data={
                "comment": "I thought you were watching the hobbits?"
            })
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Comment.objects.count(), 2)
            
            c = Comment.objects.order_by("id")[1]
            self.assertEqual(c.comment, "I thought you were watching the hobbits?")
            self.assertEqual(c.author, self.user)
    
    def test_delete_comment(self):
        g = User.objects.create(username="Boromir")
        with self.login("gimli", "gloin"):
            response = self.post_comment(g, data={
                "comment": "Wow, you're a jerk.",
            })
            comment = Comment.objects.get()
        
        response = self.post("delete_comment", comment_id=comment.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        
        with self.login("aragorn", "strider"):
            response = self.post("delete_comment", comment_id=comment.pk)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Comment.objects.count(), 1)
        
        with self.login("gimli", "gloin"):
            response = self.post("delete_comment", comment_id=comment.pk)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Comment.objects.count(), 0)
    
    def test_ttag_comment_count(self):
        g = User.objects.create(username="Sauron")
        self.post_comment(g, data={
            "name": "Gandalf",
            "comment": "You can't win",
        })
        self.post_comment(g, data={
            "name": "Gollum",
            "comment": "We wants our precious",
        })
        
        self.assert_renders(
            "{% load dialogos_tags %}{% comment_count o %}", 
            Context({"o": g}),
            "2"
        )
    
    def test_ttag_comments(self):
        g = User.objects.create(username="Sauron")
        self.post_comment(g, data={
            "name": "Gandalf",
            "comment": "You can't win",
        })
        self.post_comment(g, data={
            "name": "Gollum",
            "comment": "We wants our precious",
        })
        
        c = Context({"o": g})
        self.assert_renders(
            "{% load dialogos_tags %}{% comments o as cs %}",
            c,
            ""
        )
        self.assertEqual(list(c["cs"]), list(Comment.objects.all()))
    
    def test_ttag_comment_form(self):
        g = User.objects.create(username="Sauron")
        c = Context({"o": g})
        self.assert_renders(
            "{% load dialogos_tags %}{% comment_form o as comment_form %}",
            c,
            ""
        )
        self.assertTrue(isinstance(c["comment_form"], UnauthenticatedCommentForm))
        
        with self.login("gimli", "gloin"):
            c = Context({"o": g, "user": self.user})
            self.assert_renders(
                "{% load dialogos_tags %}{% comment_form o as comment_form %}",
                c,
                ""
            )
            self.assertTrue(isinstance(c["comment_form"], AuthenticatedCommentForm))
    
    def test_ttag_comment_target(self):
        g = User.objects.create(username="legolas")
        self.assert_renders(
            "{% load dialogos_tags %}{% comment_target o %}",
            Context({"o": g}),
            "/comment/%d/%d/" % (ContentType.objects.get_for_model(g).pk, g.pk)
        )
