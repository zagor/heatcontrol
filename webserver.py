import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import logging

import config
import ntp
import temperature
import tibber

_default_config = {'web_port': 8080}

_body = '''
<body>
<h1>Heat pump control</h1>
<h2>Current status</h2>

<h2>Configuration</h2>
Time: <span id="time">-</span><br>
CPU temperature: <span id="temperature">-</span>

<div id="status">No data</div>

</div>
'''.encode()

_log = logging.getLogger(__name__)


def build_chart(hour_offset=0, title='Elpris idag'):
    high_price = config.get('high_price')
    low_price = config.get('low_price')
    buf = f'<canvas id="chart{hour_offset}" style="width:100%;"></canvas>'
    buf += '<script>'
    hours = ', '.join(str(i) for i in range(24))
    buf += f'var hours = [{hours}];'
    prices = [f'{tibber._prices[i + hour_offset]:.02f}' for i in range(24)]
    buf += f'var prices = [{", ".join(prices)}];'
    colors = [' '] * 24
    border = ['0'] * 24
    current_hour = datetime.datetime.now().hour
    for h in range(24):
        price = tibber._prices[h + hour_offset]
        if price >= high_price:
            color = '"red"'
        elif price <= low_price:
            color = '"green"'
        else:
            color = '"orange"'
        colors[h] = color
        if h + hour_offset == current_hour:
            border[h] = '5'
    buf += f'var colors = [{", ".join(colors)}];'
    buf += f'var borders = [{", ".join(border)}];'
    buf += '''
const ctx%d = document.getElementById('chart%d').getContext('2d');
new Chart(ctx%d, {
  type: "bar",
  data: {
    labels: hours,
    datasets: [{
      data: prices,
      backgroundColor: colors,
      borderColor: "black",
      borderWidth: borders,
    }]
  },
  options: {
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: "%s",
        font: { size: 30 },
      },
    },
    animation: { duration: 0 },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { font: { size: 15 }, },
      }
    },
  },
});
</script>
    ''' % (hour_offset, hour_offset, hour_offset, title)
    return buf


class MyServer(BaseHTTPRequestHandler):
    def send(self, string):
        self.wfile.write(string.encode('utf-8'))
        self.wfile.write('\n'.encode('utf-8'))

    def send_index(self):
        self.send_response_only(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.send("<html><head><title>Heat pump control</title></head>")
        self.send('<body>')
        self.send('<h2>Status</h2>')
        if tibber.has_prices():
            self.send(f'<p>Current price: {tibber.get_current_price():.2f} kr')
        self.send(f'<p>Current temp setting: {temperature.current_temp} &deg;C')
        self.send(f'<p>Current fan setting: {temperature.current_fan or "auto"}')
        self.send('<h2>Configuration</h2>')
        self.send('<form action="/save-config" method="post"><table>')
        for key, value in config._config.items():
            self.send(f'<tr><th>{key}</th><td><input name="{key}" value="{value}"></input></td></tr>')
        self.send('<tr><th colspan=2><input type="submit" value="Save"></input></th></tr>')
        self.send('</table></form>')
        self.send("</body></html>")


    def send_prices(self):
        self.send_response_only(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.send("<html><head><title>Heat pump control</title></head>")
        self.send('<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>')
        self.send('<body>')
        if not tibber.has_prices():
            self.send('<p>No prices :(')
            self.send("</body></html>")
            return
        self.send(build_chart())
        if len(tibber._prices) > 24:
            self.send(build_chart(hour_offset=24, title='Elpris imorgon'))
        self.send("</body></html>")

    def do_GET(self):
        if self.path == "/":
            self.send_index()
        elif self.path == "/prices":
            self.send_prices()


def _threadloop():
    hostname = "localhost"
    server_port = config.get('web_port')
    server = HTTPServer((hostname, server_port), MyServer)
    _log.info(f'Started http://{hostname}:{server_port}')
    server.serve_forever()
    server.server_close()
    _log.error('Unexpected exit')


def init():
    config.put_defaults(_default_config)
    t = Thread(target=_threadloop, name='Webserver')
    t.daemon = True
    t.start()


if __name__ == "__main__":
    init()
