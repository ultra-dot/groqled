import network
import urequests
import json
import config
import time
import machine
import ssd1306

# Konfigurasi OLED (SSD1306 128x64)
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))  # Sesuaikan pin
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# URL API Groq
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Fungsi untuk menghubungkan ke WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.ssid, config.pw)
    
    print("Menghubungkan ke WiFi...")
    oled.fill(0)
    oled.text("Connecting WiFi", 0, 0)
    oled.show()
    
    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        print("WiFi Connected:", wlan.ifconfig())
        oled.fill(0)
        oled.text("WiFi Connected!", 0, 0)
        oled.show()
        return True
    else:
        print("Gagal terhubung ke WiFi")
        oled.fill(0)
        oled.text("WiFi Failed!", 0, 0)
        oled.show()
        return False

# Fungsi untuk mengirim teks ke Groq API
def chat_with_groq(prompt):
    headers = {
        "Authorization": "Bearer " + config.token,
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        oled.fill(0)
        oled.text("Processing...", 0, 0)
        oled.show()

        response = urequests.post(GROQ_URL, headers=headers, data=json.dumps(payload))
        result = response.json()
        response.close()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return "Error: No response from AI"
    except Exception as e:
        return "Error: " + str(e)

# Fungsi untuk menampilkan teks dengan scrolling otomatis
def scroll_text(text):
    oled.fill(0)
    words = text.split(" ")
    lines = []
    line = ""

    # Memecah teks menjadi beberapa baris
    for word in words:
        if len(line) + len(word) < 16:
            line += word + " "
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)  # Tambahkan baris terakhir

    # Jika teks cukup pendek, tampilkan langsung
    if len(lines) <= 6:
        for i, l in enumerate(lines):
            oled.text(l, 0, i * 10)
        oled.show()
        return

    # Scrolling jika lebih dari 6 baris
    for offset in range(len(lines) - 5):
        oled.fill(0)
        for i in range(6):  # Hanya menampilkan 6 baris
            if offset + i < len(lines):
                oled.text(lines[offset + i], 0, i * 10)
        oled.show()
        time.sleep(0.5)  # Delay untuk scrolling

# Main program
if connect_wifi():
    while True:
        user_input = input("Masukkan teks: ")  # Masukkan teks dari Serial
        response = chat_with_groq(user_input)
        print("Groq:", response)  # Tampilkan di Serial
        scroll_text(response)  # Tampilkan di OLED dengan scrolling