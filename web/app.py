from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import re
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

def get_db_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(
        host='postgres',
        database='phonebook',
        user='phonebook_user',
        password='123'
    )


def validate_and_format_phone(phone):
    """
    Validate and format phone number.
    Requirements:
    - Must start with +7 or 8
    - Total digits (including +7 or 8) must be 11
    - Only digits and + allowed
    - Format result as: +7-xxx-xxx-xx-xx
    """
    cleaned = re.sub(r'[\s\-\(\)]', '', phone.strip())
    
    if not (cleaned.startswith('+7') or cleaned.startswith('8')):
        return None, "Phone number must start with +7 or 8"
    
    digits = re.sub(r'\D', '', cleaned)
    
    if len(digits) != 11:
        return None, f"Phone number must contain exactly 11 digits (found {len(digits)})"
    
    if cleaned.startswith('+7'):
        formatted = f"+7-{digits[1:4]}-{digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    else:
        formatted = f"+7-{digits[1:4]}-{digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    
    return formatted, None


def validate_name(name):
    """Validate first name or last name (minimum 2 letters, only letters and hyphens)"""
    if not name or len(name.strip()) < 2:
        return False
    cleaned = name.strip().replace('-', '')
    return cleaned.isalpha()


@app.route('/')
def index():
    """Main page - list all contacts"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM contacts ORDER BY last_name, first_name')
        contacts = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('index.html', contacts=contacts)
    except Exception as e:
        return f"Database error: {e}", 500


@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    """Add new contact"""
    if request.method == 'POST':
        last_name = request.form.get('last_name', '').strip()
        first_name = request.form.get('first_name', '').strip()
        patronymic = request.form.get('patronymic', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        note = request.form.get('note', '').strip()
        
        errors = []
        
        if not validate_name(last_name):
            errors.append('Last name must contain at least 2 letters')
        if not validate_name(first_name):
            errors.append('First name must contain at least 2 letters')
        
        formatted_phone, phone_error = validate_and_format_phone(phone_number)
        if phone_error:
            errors.append(phone_error)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('form.html', 
                                 action='add', 
                                 title='Add Contact',
                                 last_name=last_name,
                                 first_name=first_name,
                                 patronymic=patronymic,
                                 phone_number=phone_number,
                                 note=note)
        
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                'INSERT INTO contacts (last_name, first_name, patronymic, phone_number, note) '
                'VALUES (%s, %s, %s, %s, %s)',
                (last_name, first_name, patronymic if patronymic else None, 
                 formatted_phone, note if note else None)
            )
            conn.commit()
            flash('Contact added successfully!', 'success')
        except psycopg2.IntegrityError:
            conn.rollback()
            flash('Error: A contact with this phone number already exists!', 'error')
        finally:
            cur.close()
            conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('form.html', action='add', title='Add Contact')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    """Edit existing contact"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        last_name = request.form.get('last_name', '').strip()
        first_name = request.form.get('first_name', '').strip()
        patronymic = request.form.get('patronymic', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        note = request.form.get('note', '').strip()
        
        errors = []
        
        if not validate_name(last_name):
            errors.append('Last name must contain at least 2 letters')
        if not validate_name(first_name):
            errors.append('First name must contain at least 2 letters')
        
        formatted_phone, phone_error = validate_and_format_phone(phone_number)
        if phone_error:
            errors.append(phone_error)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('form.html', 
                                 action='edit', 
                                 title='Edit Contact',
                                 contact={'id': id, 'last_name': last_name, 
                                         'first_name': first_name, 'patronymic': patronymic,
                                         'phone_number': phone_number, 'note': note})
        
        try:
            cur.execute(
                'UPDATE contacts SET last_name=%s, first_name=%s, patronymic=%s, '
                'phone_number=%s, note=%s, updated_at=CURRENT_TIMESTAMP WHERE id=%s',
                (last_name, first_name, patronymic if patronymic else None, 
                 formatted_phone, note if note else None, id)
            )
            conn.commit()
            flash('Contact updated successfully!', 'success')
        except psycopg2.IntegrityError:
            conn.rollback()
            flash('Error: A contact with this phone number already exists!', 'error')
        finally:
            cur.close()
            conn.close()
        
        return redirect(url_for('index'))
    
    cur.execute('SELECT * FROM contacts WHERE id = %s', (id,))
    contact = cur.fetchone()
    cur.close()
    conn.close()
    
    if not contact:
        flash('Contact not found!', 'error')
        return redirect(url_for('index'))
    
    return render_template('form.html', action='edit', title='Edit Contact', contact=contact)


@app.route('/delete/<int:id>')
def delete_contact(id):
    """Delete contact"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM contacts WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Contact deleted successfully!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
