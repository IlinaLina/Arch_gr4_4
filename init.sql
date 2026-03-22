CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    patronymic VARCHAR(100),
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone_number);
CREATE INDEX IF NOT EXISTS idx_contacts_last_name ON contacts(last_name);

INSERT INTO contacts (last_name, first_name, patronymic, phone_number, note) 
VALUES 
    ('Ivanov', 'Ivan', 'Ivanovich', '+7-999-123-45-67', 'Colleague, development department'),
    ('Petrova', 'Anna', 'Sergeevna', '+7-999-876-54-32', 'Family, cousin'),
    ('Sidorov', 'Petr', 'Nikolaevich', '+7-916-555-12-34', 'Friend, university'),
    ('Kuznetsova', 'Elena', 'Aleksandrovna', '+7-903-777-88-99', 'Work, accounting'),
    ('Mikhailov', 'Andrey', 'Vladimirovich', '+7-925-444-55-66', 'Client, important')
ON CONFLICT (phone_number) DO NOTHING;

SELECT 'Contacts table created successfully!' AS status;
SELECT COUNT(*) AS total_contacts FROM contacts;
