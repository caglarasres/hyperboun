from flask import Flask, render_template, request, jsonify
import pigpio
import serial
import time

# === DonanÄ±m ayarlarÄ± ===
ESC = 4
ESC2 = 18
MIN = 1380
MAX = 1800
MAX_TEMP = 35

# === pigpio baÅŸlat ===
pi = pigpio.pi()
pi.set_servo_pulsewidth(ESC, 0)
pi.set_servo_pulsewidth(ESC2, 0)

# === Arduino seri port ayarlarÄ± ===
try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)
    time.sleep(2)  # Arduino'nun reset ve seri baÅŸlatmasÄ± iÃ§in bekle
except serial.SerialException:
    arduino = None
    print("Arduino'ya baÄŸlanÄ±lamadÄ±. LÃ¼tfen baÄŸlantÄ±yÄ± kontrol edin.")

app = Flask(__name__)
motor_running = False

# === Arduino'dan sÄ±caklÄ±k oku ===
def read_temperature():
    if not arduino:
        return 0

    try:
        line = arduino.readline().decode('utf-8').strip()
        if line:
            return float(line)
        else:
            return 0
    except Exception as e:
        print(f"Hata: {e}")
        return 0

# === Motor kontrol ===
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

# === Flask route'lar ===
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
            'message': f'SÄ±caklÄ±k Ã§ok yÃ¼ksek ({temp:.1f}Â°C)! Motorlar durduruldu.'
        })

    data = request.get_json()
    speed = int(data['speed'])

    if speed < MIN or speed > MAX:
        return jsonify({'status': 'error', 'message': 'GeÃ§ersiz hÄ±z'})

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
    if arduino:
        arduino.close()
    return 'Temizlendi'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
