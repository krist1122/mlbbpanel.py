from flask import Flask, request, jsonify, render_template_string, redirect, session
import psycopg2
import os
import time
import random
import string
import uuid

app = Flask(__name__)
app.secret_key = "slider_super_secure_local_pass_key_12213"

# ==========================================
# DATABASE URL
# ==========================================
DATABASE_URL = os.getenv("DATABASE_URL")

# ==========================================
# ADMIN PASSWORD
# ==========================================
ADMIN_PASSWORD = "slider123"

# ==========================================
# DB CONNECTION FIX (IMPORTANT)
# ==========================================
def get_db_connection():
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise Exception("DATABASE_URL is missing in environment variables")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return psycopg2.connect(db_url, sslmode="require")

# ==========================================
# INIT DB (FIXED - NO BROKEN CODE)
# ==========================================
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS free_keys_table (
            license_key TEXT PRIMARY KEY,
            hwid TEXT,
            expiry_timestamp BIGINT,
            game TEXT DEFAULT 'CODM'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS free_tokens (
            token TEXT PRIMARY KEY,
            used BOOLEAN DEFAULT FALSE,
            created_at BIGINT
        )
    """)

    conn.commit()
    conn.close()
# ==========================================
# USER LANDING TEMPLATE
# ==========================================
FREE_LANDING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Kaze Lider Mods - Registration</title>

<style>

body{
    background:#ffffff;
    color:#000000;
    font-family:sans-serif;
    padding:20px;
    margin:0;
}

.vip-link{
    font-size:20px;
    font-weight:bold;
    color:#0000ff;
    text-decoration:underline;
    display:inline-block;
    margin-bottom:25px;
}

.info-text{
    font-size:16px;
    margin-bottom:20px;
}

.pricelist-title{
    font-weight:bold;
    margin-top:15px;
    margin-bottom:10px;
    font-size:18px;
}

.price-item{
    margin:6px 0;
    font-size:16px;
}

.payment-methods{
    margin-top:15px;
    font-size:16px;
}

.divider{
    margin:20px 0;
    color:#5f6368;
}

.trial-container{
    display:flex;
    align-items:center;
    gap:10px;
    margin-top:35px;
}

.tap-here{
    background:#00a2e8;
    color:white;
    font-size:10px;
    font-weight:bold;
    padding:5px 7px;
    border-radius:3px;
    text-transform:uppercase;
    animation:bounceHorizontal 0.6s infinite alternate;
}

@keyframes bounceHorizontal{
    0%{ transform:translateX(0); }
    100%{ transform:translateX(6px); }
}

.trial-link-btn{
    background:none;
    border:none;
    color:#008000;
    font-size:19px;
    font-weight:bold;
    text-decoration:underline;
    cursor:pointer;
}

.temporary-text{
    color:#ff0000;
    font-size:19px;
    font-weight:bold;
}

</style>
</head>

<body>

<a href="https://t.me/KAZELIDERMODS/380" target="_blank" class="vip-link">
Purchase VIP, No ads, More features
</a>

<div class="info-text">

<div class="pricelist-title">
Official pricelist:
</div>

<div class="price-item">₱150 → 3 Days</div>
<div class="price-item">₱300 → 7 Days</div>
<div class="price-item">₱500 → 15 Days</div>
<div class="price-item">₱730 → 30 Days</div>
<div class="price-item">₱2,000 → Permanent</div>

<div class="payment-methods">
Gcash, Paypal, Binance Wise 🙂
</div>

</div>

<div class="divider">
=======================================
</div>

<form action="/free/process" method="POST">

<div class="trial-container">

<div class="tap-here">
TAP HERE
</div>

<button type="submit" class="trial-link-btn">
Free trial link 1.
</button>

<span class="temporary-text">
(Temporary)
</span>

</div>

</form>

</body>
</html>
"""

# ==========================================
# GENERATED KEY TEMPLATE
# ==========================================
FREE_GENERATED_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Slider Free</title>

<style>

body{
    background:#000;
    color:#fff;
    font-family:sans-serif;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
    height:100vh;
    margin:0;
    padding:20px;
}

.alert-text{
    color:#d92424;
    font-size:24px;
    margin-bottom:45px;
    text-align:center;
}

.gen-btn{
    background:#4caf50;
    color:#fff;
    width:100%;
    max-width:340px;
    padding:16px;
    font-size:20px;
    border:none;
    border-radius:4px;
    cursor:pointer;
}

.key-display{
    display:none;
    background:#fff;
    color:#000;
    width:100%;
    max-width:340px;
    padding:14px;
    font-size:16px;
    text-align:center;
    border-radius:4px;
    margin-bottom:15px;
    word-break:break-all;
}

.copy-btn{
    display:none;
    background:#f39c12;
    color:#fff;
    width:100%;
    max-width:340px;
    padding:14px;
    font-size:18px;
    border:none;
    border-radius:4px;
    cursor:pointer;
}

.footer-info{
    margin-top:50px;
    text-align:center;
    font-size:15px;
    color:#b3b3b3;
}

.validity-days{
    margin-bottom:25px;
    color:#fff;
}

.tg-channel-link{
    display:block;
    color:#f39c12;
    text-decoration:none;
    margin-top:6px;
}

</style>
</head>

<body>

<div class="alert-text">
Always use latest version.
</div>

<button class="gen-btn" id="initGenBtn" onclick="showKeyScreen()">
Generate Key!
</button>

<div class="key-display" id="keyText">
{{ key }}
</div>

<button class="copy-btn" id="realCopyBtn" onclick="copyToClipboard()">
Copy key
</button>

<div class="footer-info">

<div class="validity-days">
Validity: 12 Hour's
</div>

Subscribe to my channel

<a href="https://t.me/KAZELIDERMODS" target="_blank" class="tg-channel-link">
HTTPS://T.ME/KAZELIDERMODS
</a>

</div>

<script>

function showKeyScreen(){

    document.getElementById("initGenBtn").style.display = "none";
    document.getElementById("keyText").style.display = "block";
    document.getElementById("realCopyBtn").style.display = "block";

}

function copyToClipboard(){

    var key = document.getElementById("keyText").innerText;

    navigator.clipboard.writeText(key);

    alert("Copied Free Key:\\n\\n" + key);

}

</script>

</body>
</html>
"""

# ==========================================
# ADMIN LOGIN TEMPLATE
# ==========================================
ADMIN_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>

<title>Admin Login</title>

<style>

body{
    background:#111;
    color:white;
    font-family:sans-serif;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}

.box{
    background:#1e1e1e;
    padding:30px;
    border-radius:10px;
    width:300px;
}

input{
    width:100%;
    padding:12px;
    margin-top:10px;
    margin-bottom:15px;
    border:none;
    border-radius:5px;
}

button{
    width:100%;
    padding:12px;
    background:#4caf50;
    border:none;
    color:white;
    border-radius:5px;
    cursor:pointer;
}

</style>

</head>

<body>

<div class="box">

<h2>Admin Login</h2>

<form method="POST">

<input type="password" name="password" placeholder="Enter Admin Password">

<button type="submit">
Login
</button>

</form>

</div>

</body>
</html>
"""

# ==========================================
# ADMIN PANEL TEMPLATE
# ==========================================
ADMIN_PANEL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>

<title>Admin Panel</title>

<style>

body{
    background:#0f0f0f;
    color:white;
    font-family:sans-serif;
    padding:20px;
}

table{
    width:100%;
    border-collapse:collapse;
    margin-top:20px;
}

th, td{
    border:1px solid #333;
    padding:12px;
    text-align:center;
}

th{
    background:#1f1f1f;
}

tr:nth-child(even){
    background:#181818;
}

.delete-btn{
    background:red;
    color:white;
    padding:8px 12px;
    text-decoration:none;
    border-radius:5px;
}

.logout-btn{
    background:#444;
    color:white;
    padding:10px 15px;
    text-decoration:none;
    border-radius:5px;
}

</style>

</head>

<body>

<h1>Generated Keys</h1>

<a href="/admin/logout" class="logout-btn">
Logout
</a>

<table>

<tr>
<th>License Key</th>
<th>HWID</th>
<th>Expiry</th>
<th>Game</th>
<th>Action</th>
</tr>

{% for key in keys %}

<tr>

<td>{{ key[0] }}</td>
<td>{{ key[1] }}</td>
<td>{{ key[2] }}</td>
<td>{{ key[3] }}</td>

<td>

<a class="delete-btn" href="/admin/delete/{{ key[0] }}">
Delete
</a>

</td>

</tr>

{% endfor %}

</table>

</body>
</html>
"""

# ==========================================
# USER ROUTES
# ==========================================
@app.route('/free')
def free_landing():
    return render_template_string(FREE_LANDING_TEMPLATE)

@app.route('/free/process', methods=['POST'])
def free_process_route():

    token = str(uuid.uuid4())

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO free_tokens (token, used, created_at) VALUES (%s, %s, %s)",
        (token, False, int(time.time()))
    )

    conn.commit()
    conn.close()

    # IMPORTANT: ipasa token sa link
    return redirect(f"https://sfl.gl/0hpxBx?token={token}")


# =========================
# RETURN ROUTE (OUTSIDE FUNCTION!)
# =========================
@app.route('/free/return')
def free_return():

    token = request.args.get("token")

    if not token:
        return '<script>alert("Missing Token");window.location="/free";</script>'

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT used FROM free_tokens WHERE token=%s", (token,))
    result = cursor.fetchone()

    if not result:
        return '<script>alert("Invalid Token");window.location="/free";</script>'

    if result[0]:
        return '<script>alert("Already Used");window.location="/free";</script>'

    return redirect(f"/free/generate/direct?token={token}")


# ==========================================
# FREE GENERATE KEY (FIXED)
# ==========================================
@app.route('/free/generate/direct')
def free_generate_direct():

    token = request.args.get("token")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT used FROM free_tokens WHERE token=%s", (token,))
    result = cursor.fetchone()

    if not result:
        return '<script>alert("Invalid Token");window.location="/free";</script>'

    if result[0]:
        return '<script>alert("Token Already Used");window.location="/free";</script>'

    # MARK USED (ANTI-BYPASS CORE)
    cursor.execute("UPDATE free_tokens SET used=TRUE WHERE token=%s", (token,))
    conn.commit()

    # generate key
    now = int(time.time())
    new_key = "Slider_" + ''.join(random.choices(string.ascii_letters + string.digits, k=15))
    expiry = now + (12 * 3600)

    cursor.execute(
        "INSERT INTO free_keys_table (license_key, hwid, expiry_timestamp, game) VALUES (%s,%s,%s,%s)",
        (new_key, '', expiry, 'CODM')
    )

    conn.commit()
    conn.close()

    return render_template_string(FREE_GENERATED_TEMPLATE, key=new_key)

# ==========================================
# VERIFY API
# ==========================================
@app.route('/verify', methods=['POST'])
def verify_key():
    try:
        key = request.form.get('key', '').strip()
        device_id = request.form.get('device_id', '').strip()
        game = request.form.get('game', '').strip()

        if not key:
            return jsonify({"status": 1, "msg": "Invalid Key"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT hwid, expiry_timestamp, game FROM free_keys_table WHERE license_key = %s",
            (key,)
        )

        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({"status": 1, "msg": "Invalid Key"})

        saved_hwid, expiry_timestamp, db_game = result
        now = int(time.time())

        if now > expiry_timestamp:
            conn.close()
            return jsonify({"status": 3, "msg": "Key Expired"})

        if game != db_game:
            conn.close()
            return jsonify({"status": 1, "msg": "Wrong Game"})

        if saved_hwid == "":
            cursor.execute(
                "UPDATE free_keys_table SET hwid = %s WHERE license_key = %s",
                (device_id, key)
            )
            conn.commit()

        elif saved_hwid != device_id:
            conn.close()
            return jsonify({"status": 2, "msg": "Key Used On Another Device"})

        conn.close()

        return jsonify({
            "status": 0,
            "msg": "Login Success",
            "expiry": expiry_timestamp
        })

    except Exception as e:
        return jsonify({"status": 1, "msg": str(e)})
        
        # ==========================================
# ADMIN LOGIN
# ==========================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    if request.method == "POST":
        password = request.form.get("password")

        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/panel")

        return "<script>alert('Wrong Password');window.location='/admin/login';</script>"

    return render_template_string(ADMIN_LOGIN_TEMPLATE)


# ==========================================
# ADMIN PANEL
# ==========================================
@app.route('/admin/panel')
def admin_panel():

    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM free_keys_table")
    keys = cursor.fetchall()

    conn.close()

    return render_template_string(ADMIN_PANEL_TEMPLATE, keys=keys)


# ==========================================
# DELETE KEY
# ==========================================
@app.route('/admin/delete/<key>')
def delete_key(key):

    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM free_keys_table WHERE license_key=%s", (key,))
    conn.commit()
    conn.close()

    return redirect("/admin/panel")


# ==========================================
# LOGOUT
# ==========================================
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect("/admin/login")

# ==========================================
# INIT DB ON START
# ==========================================
init_db()

# ==========================================
# RUN SERVER
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)# INIT DB (FIXED - NO BROKEN CODE)
# ==========================================
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS free_keys_table (
            license_key TEXT PRIMARY KEY,
            hwid TEXT,
            expiry_timestamp BIGINT,
            game TEXT DEFAULT 'CODM'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS free_tokens (
            token TEXT PRIMARY KEY,
            used BOOLEAN DEFAULT FALSE,
            created_at BIGINT
        )
    """)

    conn.commit()
    conn.close()
# ==========================================
# USER LANDING TEMPLATE
# ==========================================
FREE_LANDING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Kaze Lider Mods - Registration</title>

<style>

body{
    background:#ffffff;
    color:#000000;
    font-family:sans-serif;
    padding:20px;
    margin:0;
}

.vip-link{
    font-size:20px;
    font-weight:bold;
    color:#0000ff;
    text-decoration:underline;
    display:inline-block;
    margin-bottom:25px;
}

.info-text{
    font-size:16px;
    margin-bottom:20px;
}

.pricelist-title{
    font-weight:bold;
    margin-top:15px;
    margin-bottom:10px;
    font-size:18px;
}

.price-item{
    margin:6px 0;
    font-size:16px;
}

.payment-methods{
    margin-top:15px;
    font-size:16px;
}

.divider{
    margin:20px 0;
    color:#5f6368;
}

.trial-container{
    display:flex;
    align-items:center;
    gap:10px;
    margin-top:35px;
}

.tap-here{
    background:#00a2e8;
    color:white;
    font-size:10px;
    font-weight:bold;
    padding:5px 7px;
    border-radius:3px;
    text-transform:uppercase;
    animation:bounceHorizontal 0.6s infinite alternate;
}

@keyframes bounceHorizontal{
    0%{ transform:translateX(0); }
    100%{ transform:translateX(6px); }
}

.trial-link-btn{
    background:none;
    border:none;
    color:#008000;
    font-size:19px;
    font-weight:bold;
    text-decoration:underline;
    cursor:pointer;
}

.temporary-text{
    color:#ff0000;
    font-size:19px;
    font-weight:bold;
}

</style>
</head>

<body>

<a href="https://t.me/KAZELIDERMODS/380" target="_blank" class="vip-link">
Purchase VIP, No ads, More features
</a>

<div class="info-text">

<div class="pricelist-title">
Official pricelist:
</div>

<div class="price-item">₱150 → 3 Days</div>
<div class="price-item">₱300 → 7 Days</div>
<div class="price-item">₱500 → 15 Days</div>
<div class="price-item">₱730 → 30 Days</div>
<div class="price-item">₱2,000 → Permanent</div>

<div class="payment-methods">
Gcash, Paypal, Binance Wise 🙂
</div>

</div>

<div class="divider">
=======================================
</div>

<form action="/free/process" method="POST">

<div class="trial-container">

<div class="tap-here">
TAP HERE
</div>

<button type="submit" class="trial-link-btn">
Free trial link 1.
</button>

<span class="temporary-text">
(Temporary)
</span>

</div>

</form>

</body>
</html>
"""

# ==========================================
# GENERATED KEY TEMPLATE
# ==========================================
FREE_GENERATED_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Slider Free</title>

<style>

body{
    background:#000;
    color:#fff;
    font-family:sans-serif;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
    height:100vh;
    margin:0;
    padding:20px;
}

.alert-text{
    color:#d92424;
    font-size:24px;
    margin-bottom:45px;
    text-align:center;
}

.gen-btn{
    background:#4caf50;
    color:#fff;
    width:100%;
    max-width:340px;
    padding:16px;
    font-size:20px;
    border:none;
    border-radius:4px;
    cursor:pointer;
}

.key-display{
    display:none;
    background:#fff;
    color:#000;
    width:100%;
    max-width:340px;
    padding:14px;
    font-size:16px;
    text-align:center;
    border-radius:4px;
    margin-bottom:15px;
    word-break:break-all;
}

.copy-btn{
    display:none;
    background:#f39c12;
    color:#fff;
    width:100%;
    max-width:340px;
    padding:14px;
    font-size:18px;
    border:none;
    border-radius:4px;
    cursor:pointer;
}

.footer-info{
    margin-top:50px;
    text-align:center;
    font-size:15px;
    color:#b3b3b3;
}

.validity-days{
    margin-bottom:25px;
    color:#fff;
}

.tg-channel-link{
    display:block;
    color:#f39c12;
    text-decoration:none;
    margin-top:6px;
}

</style>
</head>

<body>

<div class="alert-text">
Always use latest version.
</div>

<button class="gen-btn" id="initGenBtn" onclick="showKeyScreen()">
Generate Key!
</button>

<div class="key-display" id="keyText">
{{ key }}
</div>

<button class="copy-btn" id="realCopyBtn" onclick="copyToClipboard()">
Copy key
</button>

<div class="footer-info">

<div class="validity-days">
Validity: 12 Hour's
</div>

Subscribe to my channel

<a href="https://t.me/KAZELIDERMODS" target="_blank" class="tg-channel-link">
HTTPS://T.ME/KAZELIDERMODS
</a>

</div>

<script>

function showKeyScreen(){

    document.getElementById("initGenBtn").style.display = "none";
    document.getElementById("keyText").style.display = "block";
    document.getElementById("realCopyBtn").style.display = "block";

}

function copyToClipboard(){

    var key = document.getElementById("keyText").innerText;

    navigator.clipboard.writeText(key);

    alert("Copied Free Key:\\n\\n" + key);

}

</script>

</body>
</html>
"""

# ==========================================
# ADMIN LOGIN TEMPLATE
# ==========================================
ADMIN_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>

<title>Admin Login</title>

<style>

body{
    background:#111;
    color:white;
    font-family:sans-serif;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}

.box{
    background:#1e1e1e;
    padding:30px;
    border-radius:10px;
    width:300px;
}

input{
    width:100%;
    padding:12px;
    margin-top:10px;
    margin-bottom:15px;
    border:none;
    border-radius:5px;
}

button{
    width:100%;
    padding:12px;
    background:#4caf50;
    border:none;
    color:white;
    border-radius:5px;
    cursor:pointer;
}

</style>

</head>

<body>

<div class="box">

<h2>Admin Login</h2>

<form method="POST">

<input type="password" name="password" placeholder="Enter Admin Password">

<button type="submit">
Login
</button>

</form>

</div>

</body>
</html>
"""

# ==========================================
# ADMIN PANEL TEMPLATE
# ==========================================
ADMIN_PANEL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>

<title>Admin Panel</title>

<style>

body{
    background:#0f0f0f;
    color:white;
    font-family:sans-serif;
    padding:20px;
}

table{
    width:100%;
    border-collapse:collapse;
    margin-top:20px;
}

th, td{
    border:1px solid #333;
    padding:12px;
    text-align:center;
}

th{
    background:#1f1f1f;
}

tr:nth-child(even){
    background:#181818;
}

.delete-btn{
    background:red;
    color:white;
    padding:8px 12px;
    text-decoration:none;
    border-radius:5px;
}

.logout-btn{
    background:#444;
    color:white;
    padding:10px 15px;
    text-decoration:none;
    border-radius:5px;
}

</style>

</head>

<body>

<h1>Generated Keys</h1>

<a href="/admin/logout" class="logout-btn">
Logout
</a>

<table>

<tr>
<th>License Key</th>
<th>HWID</th>
<th>Expiry</th>
<th>Game</th>
<th>Action</th>
</tr>

{% for key in keys %}

<tr>

<td>{{ key[0] }}</td>
<td>{{ key[1] }}</td>
<td>{{ key[2] }}</td>
<td>{{ key[3] }}</td>

<td>

<a class="delete-btn" href="/admin/delete/{{ key[0] }}">
Delete
</a>

</td>

</tr>

{% endfor %}

</table>

</body>
</html>
"""

# ==========================================
# USER ROUTES
# ==========================================
@app.route('/free')
def free_landing():
    return render_template_string(FREE_LANDING_TEMPLATE)

@app.route('/free/process', methods=['POST'])
def free_process_route():

    token = str(uuid.uuid4())

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO free_tokens (token, used, created_at) VALUES (%s, %s, %s)",
        (token, False, int(time.time()))
    )

    conn.commit()
    conn.close()

    # IMPORTANT: ipasa token sa link
    return redirect(f"https://sfl.gl/0hpxBx?token={token}")


# =========================
# RETURN ROUTE (OUTSIDE FUNCTION!)
# =========================
@app.route('/free/return')
def free_return():

    token = request.args.get("token")

    if not token:
        return '<script>alert("Missing Token");window.location="/free";</script>'

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT used FROM free_tokens WHERE token=%s", (token,))
    result = cursor.fetchone()

    if not result:
        return '<script>alert("Invalid Token");window.location="/free";</script>'

    if result[0]:
        return '<script>alert("Already Used");window.location="/free";</script>'

    return redirect(f"/free/generate/direct?token={token}")


# ==========================================
# FREE GENERATE KEY (FIXED)
# ==========================================
@app.route('/free/generate/direct')
def free_generate_direct():

    token = request.args.get("token")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT used FROM free_tokens WHERE token=%s", (token,))
    result = cursor.fetchone()

    if not result:
        return '<script>alert("Invalid Token");window.location="/free";</script>'

    if result[0]:
        return '<script>alert("Token Already Used");window.location="/free";</script>'

    # MARK USED (ANTI-BYPASS CORE)
    cursor.execute("UPDATE free_tokens SET used=TRUE WHERE token=%s", (token,))
    conn.commit()

    # generate key
    now = int(time.time())
    new_key = "Slider_" + ''.join(random.choices(string.ascii_letters + string.digits, k=15))
    expiry = now + (12 * 3600)

    cursor.execute(
        "INSERT INTO free_keys_table (license_key, hwid, expiry_timestamp, game) VALUES (%s,%s,%s,%s)",
        (new_key, '', expiry, 'CODM')
    )

    conn.commit()
    conn.close()

    return render_template_string(FREE_GENERATED_TEMPLATE, key=new_key)

# ==========================================
# VERIFY API
# ==========================================
@app.route('/verify', methods=['POST'])
def verify_key():
    try:
        key = request.form.get('key', '').strip()
        device_id = request.form.get('device_id', '').strip()
        game = request.form.get('game', '').strip()

        if not key:
            return jsonify({"status": 1, "msg": "Invalid Key"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT hwid, expiry_timestamp, game FROM free_keys_table WHERE license_key = %s",
            (key,)
        )

        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({"status": 1, "msg": "Invalid Key"})

        saved_hwid, expiry_timestamp, db_game = result
        now = int(time.time())

        if now > expiry_timestamp:
            conn.close()
            return jsonify({"status": 3, "msg": "Key Expired"})

        if game != db_game:
            conn.close()
            return jsonify({"status": 1, "msg": "Wrong Game"})

        if saved_hwid == "":
            cursor.execute(
                "UPDATE free_keys_table SET hwid = %s WHERE license_key = %s",
                (device_id, key)
            )
            conn.commit()

        elif saved_hwid != device_id:
            conn.close()
            return jsonify({"status": 2, "msg": "Key Used On Another Device"})

        conn.close()

        return jsonify({
            "status": 0,
            "msg": "Login Success",
            "expiry": expiry_timestamp
        })

    except Exception as e:
        return jsonify({"status": 1, "msg": str(e)})
        
        # ==========================================
# ADMIN LOGIN
# ==========================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    if request.method == "POST":
        password = request.form.get("password")

        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/panel")

        return "<script>alert('Wrong Password');window.location='/admin/login';</script>"

    return render_template_string(ADMIN_LOGIN_TEMPLATE)


# ==========================================
# ADMIN PANEL
# ==========================================
@app.route('/admin/panel')
def admin_panel():

    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM free_keys_table")
    keys = cursor.fetchall()

    conn.close()

    return render_template_string(ADMIN_PANEL_TEMPLATE, keys=keys)


# ==========================================
# DELETE KEY
# ==========================================
@app.route('/admin/delete/<key>')
def delete_key(key):

    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM free_keys_table WHERE license_key=%s", (key,))
    conn.commit()
    conn.close()

    return redirect("/admin/panel")


# ==========================================
# LOGOUT
# ==========================================
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect("/admin/login")

# ==========================================
# INIT DB ON START
# ==========================================
init_db()

# ==========================================
# RUN SERVER
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
