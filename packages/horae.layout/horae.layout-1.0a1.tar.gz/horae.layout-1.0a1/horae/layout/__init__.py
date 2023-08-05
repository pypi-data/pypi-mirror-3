from zope.i18nmessageid import MessageFactory
_ = MessageFactory('horae.layout')

# monkey patch BeautifulSoup
import soupselect
soupselect.monkeypatch()
