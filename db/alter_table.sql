ALTER TABLE post
    ADD userId int DEFAULT NULL;


ALTER TABLE post
    ADD CONSTRAINT fk_user
    FOREIGN KEY (userID) REFERENCES "user"(id)