schema_query = """
CREATE SCHEMA IF NOT EXISTS das_data;
"""

users_query = """
CREATE TABLE IF NOT EXISTS das_data.users
(
    id uuid PRIMARY KEY,
    name text,
    surname text,
    username text UNIQUE,
    password text,
    gender text,
    dob timestamp,
    role text
);
"""

therapy_query = """
CREATE TABLE IF NOT EXISTS das_data.therapies
(
    id serial PRIMARY KEY,
    disease text,
    location text,
    length_of_existence_weeks_from integer,
    length_of_existence_weeks_to integer,
    dimension_width_mm integer,
    dimension_height_mm integer,
    patient_age_from integer,
    patient_age_to integer,
    gender text,
    number_of_instances_from integer,
    number_of_instances_to integer,
    doctor_id uuid REFERENCES das_data.users(id),
    description text
);
"""

image_query = """
CREATE TABLE IF NOT EXISTS das_data.images
(
    id serial PRIMARY KEY,
    name text,
    image_default_class text,
    processed boolean,
    added_at timestamp
)
"""

examination_query = """
CREATE TABLE IF NOT EXISTS das_data.examinations
(
    id serial PRIMARY KEY,
    user_id uuid REFERENCES das_data.users(id),
    image_id integer REFERENCES das_data.images(id),
    image_class text,
    processed_at timestamp
);
"""

default_doctor_query = """
INSERT INTO das_data.users (id, role) VALUES ('00000000-0000-0000-0000-000000000000', 'Doctor') 
ON CONFLICT DO NOTHING;
"""

setup_queries = [schema_query, users_query, therapy_query, image_query, examination_query, default_doctor_query]
