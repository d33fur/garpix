DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'gosts') THEN
        EXECUTE 'CREATE DATABASE gosts';
    END IF;
END
$$;

\c gosts;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'standarts') THEN
        CREATE TABLE standarts (
            id SERIAL PRIMARY KEY,
            standart_name VARCHAR(255) NOT NULL,
            standart_json JSONB NOT NULL
        );
    END IF;
END
$$;
