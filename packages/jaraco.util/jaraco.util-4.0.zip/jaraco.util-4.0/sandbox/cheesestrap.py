
import urllib2
import urlparse
import zipfile
import tarfile
import functools

# create a custom importer

class CheeseshopLoader(object):
	"stubbed"
	
def exception_ignore(iterable):
	while True:
		try:
			item = next(iterable)
		except StopIteration:
			raise
		except Exception:
			pass
		
class CheeseshopFinder(object):
	"""
	Custom import finder for URL-based resources
	"""
	url = 'http://cheeseshop'
	
	def find_module(fullname, path=None):
		# currently, the fullname must be available on the URL
		possible_urls = self.get_urls(fullname)
		data = next(
			exception_ignore(
				itertools.imap(self.open_url, possible_urls)
			))
		_, ext = os.path.splitext(data.url)
		targz_handler = functools.partial(tarfile.open, mode='r|gz')
		handler_cls = [zipfile.ZipFile, targz_handler]['gz' in ext]
		handler = handler_cls(data)

	def open_url(self, url):
		return urllib2.urlopen(url)

	def get_urls(self, fullname):
		for ext in '.egg', '.zip', '.tar.gz':
			yield urlparse.urljoin(self.url, fullname + ext)