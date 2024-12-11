from flask import Blueprint, render_template
import sqlite3

admin = Blueprint('admin', __name__)

@admin.route('/admin')
def admin_dashboard():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Total de usuários
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]

    # Total de pagamentos
    cursor.execute('SELECT COUNT(*) FROM payments WHERE status = "approved"')
    total_payments = cursor.fetchone()[0]

    # Total de abandonos
    cursor.execute('SELECT COUNT(*) FROM abandonment')
    total_abandonments = cursor.fetchone()[0]

    # Pagamentos detalhados
    cursor.execute('''
        SELECT p.id, u.user_id, p.serie_id, p.amount, p.status, p.payment_date
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.user_id
        ORDER BY p.payment_date DESC
    ''')
    payments = cursor.fetchall()

    conn.close()

    return render_template('admin.html', 
                           total_users=total_users, 
                           total_payments=total_payments,
                           total_abandonments=total_abandonments,
                           payments=payments)

from flask import Flask
from admin import admin  # Importe o blueprint

app = Flask(__name__)
app.register_blueprint(admin)  # Registra o blueprint do painel administrativo

if __name__ == "__main__":
    app.run(debug=True)


