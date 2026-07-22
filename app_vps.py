from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import threading

app = Flask(__name__)
CORS(app, origins="*")

DATA_FILE = "du_lieu_du_doan.json"
lock = threading.Lock()

def tao_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=options)

def lay_du_doan():
    driver = tao_driver()
    try:
        driver.get("https://web.sunwin.date")
        wait = WebDriverWait(driver, 15)
        selectors = [".ket-qua", ".prediction", ".result", "#result"]
        for selector in selectors:
            try:
                elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                text = elem.text.strip()
                if text:
                    return text
            except:
                continue
        return driver.page_source[:2000]
    except Exception as e:
        return f"Lỗi: {str(e)}"
    finally:
        driver.quit()

def ghi_lich_su(noi_dung):
    with lock:
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            history = []
        history.append({"thoi_gian": time.strftime("%Y-%m-%d %H:%M:%S"), "noi_dung": noi_dung})
        if len(history) > 200:
            history = history[-200:]
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

@app.route("/api/predict")
def predict():
    ket_qua = lay_du_doan()
    ghi_lich_su(ket_qua)
    return jsonify({"status": "success", "result": ket_qua, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})

@app.route("/api/history")
def history():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except:
        history = []
    return jsonify({"history": history[-50:]})

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)