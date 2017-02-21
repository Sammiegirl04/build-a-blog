
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

    def get_posts(self, limit, offset):
        query = Post.all().order('-created')
        return query.fetch(limit=limit, offset=offset)

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        t = jinja_env.get_template("blog.html")
        content = t.render(blogs=blogs)
        self.response.write(content)


class NewPost(Handler):
    def render_front(self, title="", body="", error=""):
        t = jinja_env.get_template("front.html")
        content = t.render(title=title, body=body, error=error)
        self.response.out.write(content)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            blog = Blog(title = title, body = body)
            blog.put()

            id = blog.key().id()
            self.redirect("/blog/%s" % id)
        else:
            error = "we need both a title and a body!"
            self.render_front(title, body, error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):

        blog = Blog.get_by_id(int(id))
        if blog:
            t = jinja_env.get_template("post.html")
            response = t.render(blog=blog)
            self.response.out.write(response)
        else:
            error = "there is no post with id %s" % id
            self.response.write(error=error)






app = webapp2.WSGIApplication([('/', MainPage),
                                ('/newpost', NewPost),
                                webapp2.Route('/blog/<id:\d+>', ViewPostHandler)], debug=True)
