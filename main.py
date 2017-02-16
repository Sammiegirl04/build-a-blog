
import webapp2
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self, title="", body="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog"
                            "ORDER BY created DESC")
        self.render("front.html", title=title, body=body, error=error, blogs=blogs)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Blog(title = title, body = body)
            a.put()
            self.redirect("/")
        else:
            error = "we need both a title and a body!"
            self.render_front(title, body, error)

app = webapp2.WSGIApplication([
    ('/', Handler)
], debug=True)
