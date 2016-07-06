from app import app
import webbrowser, threading

if __name__ == '__main__':
    app.debug = False

    threading.Timer(1.25, lambda: webbrowser.open("http://localhost:5000/") ).start()
    app.run()
