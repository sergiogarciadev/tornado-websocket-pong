import os
from tornado.options import options, define, parse_command_line
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
import tornado.websocket
import tornado.gen

waiting_player = None

class PongWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        global waiting_player
        self.player = 2 if waiting_player else 1
        self.mate = None
        self.write_message("player:" + str(self.player))
        
        if waiting_player:
            waiting_player.mate = self
            self.mate = waiting_player
            self.send("start")
            waiting_player = None
        else:
            waiting_player = self

    def send(self, message):
        self.write_message(message)
        self.mate.write_message(message)

    def on_message(self, message):
        print(message)
        self.send(message + ":" + str(self.player))

    def on_close(self):
        if not self.mate: return
        self.mate.mate = None
        self.mate.write_message('end')


def main():
    parse_command_line()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_folder = os.path.join(current_dir, '.')
    tornado_app = tornado.web.Application([
        ('/pong', PongWebSocket),
        (r"/", tornado.web.RedirectHandler, {"url": "/pong.html"}),
        (r'/(.*)', tornado.web.StaticFileHandler, { 'path': static_folder }),
    ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()