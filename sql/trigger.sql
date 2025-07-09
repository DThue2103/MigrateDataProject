    CREATE TRIGGER repositories_trigger_before_insert
    BEFORE INSERT ON repositories
    FOR EACH ROW
    BEGIN
        INSERT INTO repository_log_before(repositories_id, name, url, stage)
        VALUES (NEW.repositories_id, NEW.name, NEW.url, "INSERT");
    END;
    //
    CREATE TRIGGER repositories_trigger_before_delete
    BEFORE DELETE ON repositories
    FOR EACH ROW
    BEGIN
        INSERT INTO repository_log_before(repositories_id, name, url, stage)
        VALUES (OLD.repositories_id, OLD.name, OLD.url, "DELETE");
    END;
    //
    CREATE TRIGGER repositories_trigger_before_update
    BEFORE UPDATE ON repositories
    FOR EACH ROW
    BEGIN
        INSERT INTO repository_log_before(repositories_id, name, url, stage)
        VALUES (OLD.repositories_id, OLD.name, OLD.url, "UPDATE");
    END;
    //
    CREATE TRIGGER repositories_trigger_after_insert
    AFTER INSERT ON repositories
    FOR EACH ROW
    BEGIN
        INSERT INTO repository_log_after(repositories_id, name, url, stage)
        VALUES (NEW.repositories_id, NEW.name, NEW.url, "INSERT");
    END;
    //
    CREATE TRIGGER repositories_trigger_after_delete
    AFTER DELETE ON repositories
    FOR EACH ROW
    BEGIN
        INSERT INTO repository_log_after(repositories_id, name, url, stage)
        VALUES (OLD.repositories_id, OLD.name, OLD.url, "DELETE");
    END;
    //
    CREATE TRIGGER repositories_trigger_after_update
    AFTER UPDATE ON repositories
    FOR EACH ROW
    BEGIN
        INSERT INTO repository_log_after(repositories_id, name, url, stage)
        VALUES (NEW.repositories_id, NEW.name, NEW.url, "UPDATE");
    END;
    //

