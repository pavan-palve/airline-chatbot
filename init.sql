-- Flights Table
CREATE TABLE IF NOT EXISTS flights (
    flight_number TEXT PRIMARY KEY,
    departure TEXT,
    destination TEXT,
    date TEXT,
    time TEXT
);

-- Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    pnr TEXT PRIMARY KEY
);

-- Passengers Table
CREATE TABLE IF NOT EXISTS passengers (
    id TEXT PRIMARY KEY,
    pnr TEXT,
    flight_number TEXT,
    name TEXT,
    dob TEXT,
    FOREIGN KEY(pnr) REFERENCES bookings(pnr),
    FOREIGN KEY(flight_number) REFERENCES flights(flight_number)
);

-- Adding Initial Mock data 

-- Flights Table 
INSERT OR IGNORE INTO flights VALUES ('AK123', 'KUL', 'SIN', '2024-03-15', '10:30');
INSERT OR IGNORE INTO flights VALUES ('6E501', 'NAG', 'BOM', '2024-04-10', '08:00');
INSERT OR IGNORE INTO flights VALUES ('SQ421', 'BOM', 'SIN', '2024-04-11', '23:45');
INSERT OR IGNORE INTO flights VALUES ('AI630', 'BOM', 'NAG', '2024-04-15', '19:30');
INSERT OR IGNORE INTO flights VALUES ('AK456', 'KUL', 'BKK', '2024-03-15', '14:30');


-- Bookings Table 
INSERT OR IGNORE INTO bookings VALUES ('ABC123');
INSERT OR IGNORE INTO bookings VALUES ('PAV789'); 
INSERT OR IGNORE INTO bookings VALUES ('NAG555'); 

-- Passengers Table 
INSERT OR IGNORE INTO passengers VALUES ('PAX001', 'ABC123', 'AK123', 'John Doe', '1990-01-15');
INSERT OR IGNORE INTO passengers VALUES ('PAX002', 'PAV789', '6E501', 'Pavan Palve', '1992-05-20');
INSERT OR IGNORE INTO passengers VALUES ('PAX003', 'PAV789', 'SQ421', 'Pavan Palve', '1992-05-20');
INSERT OR IGNORE INTO passengers VALUES ('PAX004', 'NAG555', 'AI630', 'Pavan Palve', '1992-05-20');