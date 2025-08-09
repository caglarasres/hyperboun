import json, serial, time

PORT = "/dev/ttyACM0"   # sende farklı olabilir
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)

while True:
    line = ser.readline()
    if not line:
        continue

    s = line.decode("utf-8", errors="ignore").strip()
    # ham satırı görmek istersen aç:
    # print(s)

    if not s:
        continue

    try:
        data = json.loads(s)

        t = data.get("t_ms")

        mpu = data.get("mpu6050") or {}
        accelg = mpu.get("accel_g") or {}
        gyro   = mpu.get("gyro_dps") or {}

        ax = accelg.get("x", 0.0); ay = accelg.get("y", 0.0); az = accelg.get("z", 0.0)
        gx = gyro.get("x", 0.0);   gy = gyro.get("y", 0.0);   gz = gyro.get("z", 0.0)
        mputemp = mpu.get("temp_c", 0.0)

        maxC = data.get("max6675_c", 0.0)

        acs = data.get("acs724") or {}
        acsamp  = acs.get("amps", 0.0)
        acsvout = acs.get("vout", 0.0)
        acsvzero= acs.get("vzero", 0.0)

        print(
            f"{t} ms | "
            f"IMU a[g]=({ax:.6f},{ay:.6f},{az:.6f}) "
            f"gyr[dps]=({gx:.6f},{gy:.6f},{gz:.6f}) "
            f"Timu={mputemp:.2f} C | "
            f"MAX6675={maxC:.2f} C | "
            f"I={acsamp:.6f} A (Vout={acsvout:.6f} V, Vzero={acsvzero:.6f} V)"
        )

    except json.JSONDecodeError as e:
        print("JSON hatası:", e, "Line:", s)
        continue
