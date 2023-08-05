import colander, deform
import cherrypy

class Schema(colander.Schema):
	text = colander.SchemaNode(colander.String())

def page(formtext):
	return '<html><body>%s</body></html>' % formtext

class Server:
	@cherrypy.expose
	def index(self, **params):
		form = deform.Form(Schema(), buttons=('submit',))
		form['text'].widget = deform.widget.TextInputWidget(size=60)
		if params:
			try:
				data = form.validate(params.items())
			except deform.ValidationFailure, e:
				return page(e.render())
			return page('OK - your data was %s' % data)

		return page(form.render())

cherrypy.quickstart(Server())
