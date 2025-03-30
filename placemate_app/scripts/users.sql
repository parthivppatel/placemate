INSERT INTO "User" (email, password, phone) VALUES
    ('student@daiict.ac.in', 'pbkdf2_sha256$600000$zuubqxEeLMgCzVsmt5P5Yf$+PqWH58DWgAmO8apBEmT35FzBR0qxOjYgZcXmvCFoWM=', '1234567890'),
    ('company@gmail.com', 'pbkdf2_sha256$600000$RhKWpmOyCuVbqMXHS43lKz$G6etzwjNYg5d2Y7kqIMK8B9B48Q5UusPLbI3lQCqs2I=', '9876543210'),
    ('admin@gmail.com', 'pbkdf2_sha256$600000$ZOs84g7ueCtiIJnSPFz1gq$hy8TNiReMFSLHnivjwFaz+EEu+3sNIQXBWB3eOwlV4I=', '1112223333');


/*
Password -->
-- student@daiict.ac.in -> password123
-- company@gmail.com -> companyPass123
-- admin@gmail.com -> adminSecure123
*/