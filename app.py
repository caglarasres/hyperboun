from flask import Flask, render_template, request, jsonify
import pigpio
import spidev
import time

ESC = 4
ESC2 = 17
MIN = 1380
MAX = 1800
MAX_TEMP = 35

pi = pigpio.pi()
pi.set_servo_pulsewidth(ESC, 0)
pi.set_servo_pulsewidth(ESC2, 0)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

app = Flask(__name__)
motor_running = False  # Başlangıçta motor çalışmıyor

def read_temperature():
    try:
        raw = spi.xfer2([0, 0])
        temp_raw = ((raw[0] << 8) | raw[1]) >> 3
        temperature = temp_raw * 0.25
        return temperature
    except:
        return 0

def stop_motors():
    global motor_running
    pi.set_servo_pulsewidth(ESC, 0)
    pi.set_servo_pulsewidth(ESC2, 0)
    motor_running = False

def start_motors(pulsewidth):
    global motor_running
    pi.set_servo_pulsewidth(ESC, pulsewidth)
    pi.set_servo_pulsewidth(ESC2, pulsewidth)
    motor_running = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_speed', methods=['POST'])
def set_speed():
    global motor_running

    temp = read_temperature()
    if temp > MAX_TEMP:
        stop_motors()
        return jsonify({
            'status': 'error',
            'message': f'Sıcaklık çok yüksek ({temp:.1f}°C)! Motorlar durduruldu.'
        })

    data = request.get_json()
    speed = int(data['speed'])

    if speed < MIN or speed > MAX:
        return jsonify({'status': 'error', 'message': 'Geçersiz hız'})

    start_motors(speed)
    return jsonify({'status': 'success', 'speed': speed})

@app.route('/stop', methods=['POST'])
def stop():
    stop_motors()
    return jsonify({'status': 'stopped'})

@app.route('/temperature')
def temperature():
    temp = read_temperature()
    return jsonify({
        'temperature': temp,
        'motor_status': 'ON' if motor_running else 'OFF',
        'overheat': temp > MAX_TEMP
    })

@app.route('/cleanup')
def cleanup():
    stop_motors()
    pi.stop()
    spi.close()
    return 'Temizlendi'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
