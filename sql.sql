-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS payment_history;
DROP TABLE IF EXISTS program_enrollment;
DROP TABLE IF EXISTS eligibility_criteria;
DROP TABLE IF EXISTS assistance_programs;
DROP TABLE IF EXISTS income_sources;
DROP TABLE IF EXISTS education_details;
DROP TABLE IF EXISTS household_members;
DROP TABLE IF EXISTS households;
DROP TABLE IF EXISTS users;

-- Users table for system access
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL, -- admin, case_worker, viewer
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Households table (main registry)
CREATE TABLE households (
    household_id SERIAL PRIMARY KEY,
    registration_date DATE NOT NULL,
    household_national_id VARCHAR(50) UNIQUE,
    address TEXT NOT NULL,
    primary_phone VARCHAR(20),
    secondary_phone VARCHAR(20),
    gps_coordinates POINT,
    dwelling_type VARCHAR(50),
    ownership_status VARCHAR(50),
    monthly_rent DECIMAL(10,2),
    number_of_rooms INTEGER,
    has_electricity BOOLEAN,
    has_water BOOLEAN,
    has_sanitation BOOLEAN,
    total_monthly_income DECIMAL(10,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

-- Individual members of households
CREATE TABLE household_members (
    member_id SERIAL PRIMARY KEY,
    household_id INTEGER REFERENCES households(household_id),
    national_id VARCHAR(50) UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    phone_number VARCHAR(20),
    relationship_to_head VARCHAR(50),
    marital_status VARCHAR(20),
    education_level VARCHAR(50),
    employment_status VARCHAR(50),
    monthly_income DECIMAL(10,2),
    is_household_head BOOLEAN DEFAULT FALSE,
    disability_status VARCHAR(50),
    identification_type VARCHAR(50),
    identification_number VARCHAR(50)
);

-- Education details for children/students
CREATE TABLE education_details (
    education_id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES household_members(member_id),
    school_name VARCHAR(100),
    education_level VARCHAR(50),
    grade VARCHAR(20),
    school_type VARCHAR(50), -- public/private
    currently_enrolled BOOLEAN,
    academic_year VARCHAR(20),
    performance_score DECIMAL(5,2)
);

-- Income sources
CREATE TABLE income_sources (
    source_id SERIAL PRIMARY KEY,
    household_id INTEGER REFERENCES households(household_id),
    source_type VARCHAR(50), -- salary, business, pension, etc.
    amount DECIMAL(10,2),
    frequency VARCHAR(20), -- monthly, weekly, etc.
    verification_status VARCHAR(20)
);

-- Cash transfer programs
CREATE TABLE assistance_programs (
    program_id SERIAL PRIMARY KEY,
    program_name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(15,2),
    payment_frequency VARCHAR(20),
    payment_amount DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'active'
);

-- Eligibility criteria for programs
CREATE TABLE eligibility_criteria (
    criteria_id SERIAL PRIMARY KEY,
    program_id INTEGER REFERENCES assistance_programs(program_id),
    criteria_type VARCHAR(50), -- income, education, household_size, etc.
    operator VARCHAR(10), -- >, <, =, >=, <=
    value VARCHAR(100),
    weight DECIMAL(5,2) -- for scoring based selection
);

-- Beneficiary enrollment in programs
CREATE TABLE program_enrollment (
    enrollment_id SERIAL PRIMARY KEY,
    program_id INTEGER REFERENCES assistance_programs(program_id),
    household_id INTEGER REFERENCES households(household_id),
    enrollment_date DATE,
    status VARCHAR(20),
    score DECIMAL(5,2), -- calculated eligibility score
    last_payment_date DATE,
    total_payments_made DECIMAL(10,2)
);

-- Payment history
CREATE TABLE payment_history (
    payment_id SERIAL PRIMARY KEY,
    enrollment_id INTEGER REFERENCES program_enrollment(enrollment_id),
    payment_date DATE,
    amount DECIMAL(10,2),
    status VARCHAR(20),
    payment_method VARCHAR(50),
    transaction_reference VARCHAR(100)
);

-- Audit trail for changes
CREATE TABLE audit_log (
    audit_id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    record_id INTEGER,
    action VARCHAR(20), -- INSERT, UPDATE, DELETE
    user_id INTEGER REFERENCES users(user_id),
    changes JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_household_national_id ON households(household_national_id);
CREATE INDEX idx_member_national_id ON household_members(national_id);
CREATE INDEX idx_household_members_household_id ON household_members(household_id);
CREATE INDEX idx_education_details_member_id ON education_details(member_id);
CREATE INDEX idx_income_sources_household_id ON income_sources(household_id);
CREATE INDEX idx_program_enrollment_household_id ON program_enrollment(household_id);
CREATE INDEX idx_program_enrollment_program_id ON program_enrollment(program_id);
CREATE INDEX idx_payment_history_enrollment_id ON payment_history(enrollment_id);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);