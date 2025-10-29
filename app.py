from flask import Flask, render_template_string, request, redirect, url_for, session, send_file
import csv, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "chilukuri_secret_key")

CSV_FILE = "bookings.csv"

# Admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# ------------------- HOME PAGE TEMPLATE -------------------
HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CHILUKURI GROUP OF TRAVELS</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: url('https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1500&q=80') no-repeat center center fixed;
      background-size: cover;
      color: white;
    }
    .container {
      background: rgba(0,0,0,0.75);
      padding: 40px;
      border-radius: 15px;
      margin-top: 40px;
    }
    .card img {
      height: 180px;
      object-fit: cover;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1 class="text-center mb-4 text-warning">🚐 CHILUKURI GROUP OF TRAVELS 🚗</h1>
    <h4 class="text-center mb-4 text-info">Book your journey with us!</h4>

    <h3 class="text-center mt-4 text-success">📝 Book Your Vehicle</h3>
    <form action="/book" method="post" class="mt-4">
      <div class="row">
        <div class="col-md-6 mb-3">
          <label class="form-label">Client Name:</label>
          <input type="text" class="form-control" name="name" required>
        </div>
        <div class="col-md-6 mb-3">
          <label class="form-label">Email Address:</label>
          <input type="email" class="form-control" name="email" required>
        </div>
      </div>
      <div class="row">
        <div class="col-md-6 mb-3">
          <label class="form-label">Phone Number:</label>
          <input type="text" class="form-control" name="phone" required>
        </div>
        <div class="col-md-6 mb-3">
          <label class="form-label">Select Vehicle Type:</label>
          <select class="form-select" name="vehicle" required>
            <option value="Car">Car</option>
            <option value="Bus">Bus</option>
            <option value="Cargo Truck">Cargo Truck</option>
          </select>
        </div>
      </div>
      <div class="mb-3">
        <label class="form-label">Pickup Location:</label>
        <input type="text" class="form-control" name="pickup" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Destination:</label>
        <input type="text" class="form-control" name="destination" required>
      </div>
      <div class="text-center">
        <button type="submit" class="btn btn-success px-5">Book Now</button>
      </div>
    </form>

    <div class="text-center mt-4">
      <a href="/admin-login" class="btn btn-warning">🔐 Admin Login</a>
    </div>
  </div>
</body>
</html>
"""

# ------------------- ROUTES -------------------

@app.route("/")
def home():
    return render_template_string(HOME_PAGE)


@app.route("/book", methods=["POST"])
def book():
    # Generate booking ID
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r") as f:
            lines = f.readlines()
            next_id = len(lines)
    else:
        next_id = 1

    booking_id = f"BK{next_id:03d}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = [
        booking_id,
        request.form["name"],
        request.form["email"],
        request.form["phone"],
        request.form["vehicle"],
        request.form["pickup"],
        request.form["destination"],
        timestamp
    ]

    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Booking ID", "Name", "Email", "Phone", "Vehicle", "Pickup", "Destination", "Booking Time"])
        writer.writerow(data)

    return f"""
    <h3>✅ Booking Successful</h3>
    <p>Thank you, {data[1]}! Your booking ID is <strong>{booking_id}</strong>.</p>
    <a href='/'>Back to Home</a>
    """


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("view_bookings"))
        else:
            return "<h3>❌ Invalid credentials</h3><a href='/admin-login'>Try again</a>"

    return """
    <div style='max-width:400px;margin:auto;margin-top:100px'>
        <h2>Admin Login</h2>
        <form method='POST'>
            <label>Username:</label><br>
            <input type='text' name='username' class='form-control' required><br>
            <label>Password:</label><br>
            <input type='password' name='password' class='form-control' required><br><br>
            <button type='submit' class='btn btn-primary'>Login</button>
        </form>
    </div>
    """


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("home"))


@app.route("/view-bookings")
def view_bookings():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    if not os.path.exists(CSV_FILE):
        return "<h3>No bookings found yet.</h3><a href='/logout'>Logout</a>"

    with open(CSV_FILE) as f:
        rows = list(csv.reader(f))
    headers, data = rows[0], rows[1:]

    html = """
    <html><head>
    <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>
    </head><body class='bg-light'>
    <div class='container mt-5'>
    <h2 class='text-center text-primary mb-4'>📋 Booking Records</h2>
    <div class='text-center mb-3'>
        <a href='/search-booking' class='btn btn-info me-2'>🔍 Search Booking by ID</a>
        <a href='/download-bookings' class='btn btn-success me-2'>⬇ Download CSV</a>
        <a href='/logout' class='btn btn-danger'>Logout</a>
    </div>
    <table class='table table-bordered table-striped shadow'>
    <thead class='table-dark'><tr>""" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead><tbody>"

    for row in data:
        html += "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"

    html += "</tbody></table></div></body></html>"
    return html


@app.route("/search-booking", methods=["GET", "POST"])
def search_booking():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        booking_id = request.form["booking_id"].strip().upper()

        if not os.path.exists(CSV_FILE):
            return "<h3>No bookings found.</h3>"

        with open(CSV_FILE) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Booking ID"] == booking_id:
                    result = "<h3 class='text-success'>Booking Found!</h3><table class='table table-bordered'>"
                    for k, v in row.items():
                        result += f"<tr><th>{k}</th><td>{v}</td></tr>"
                    result += "</table><a href='/view-bookings'>Back</a>"
                    return result
        return f"<h3>No booking found with ID {booking_id}</h3><a href='/search-booking'>Try again</a>"

    return """
    <div style='max-width:400px;margin:auto;margin-top:100px'>
        <h2>🔍 Search Booking</h2>
        <form method='POST'>
            <label>Enter Booking ID (e.g., BK001):</label><br>
            <input type='text' name='booking_id' class='form-control' required><br><br>
            <button type='submit' class='btn btn-primary'>Search</button>
        </form>
    </div>
    """


@app.route("/download-bookings")
def download_bookings():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    if os.path.exists(CSV_FILE):
        return send_file(CSV_FILE, as_attachment=True)
    return "<h3>No file found.</h3>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
