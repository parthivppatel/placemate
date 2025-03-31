INSERT INTO "User" (email, password, phone) VALUES
    ('student@daiict.ac.in', 'pbkdf2_sha256$600000$zuubqxEeLMgCzVsmt5P5Yf$+PqWH58DWgAmO8apBEmT35FzBR0qxOjYgZcXmvCFoWM=', '1234567890'),
    ('company@gmail.com', 'pbkdf2_sha256$600000$RhKWpmOyCuVbqMXHS43lKz$G6etzwjNYg5d2Y7kqIMK8B9B48Q5UusPLbI3lQCqs2I=', '9876543210'),
    ('admin@gmail.com', 'pbkdf2_sha256$600000$ZOs84g7ueCtiIJnSPFz1gq$hy8TNiReMFSLHnivjwFaz+EEu+3sNIQXBWB3eOwlV4I=', '1112223333');
    ('202412117@daiict.ac.in', 'pbkdf2_sha256$600000$3kRdRBPlHYyr6OUXkwtNdg$z81ZGLQAQgscQ7vyTUVf7B9qqRNaiYtF0MVXpGDB838=', '1234567890');


/*
Password -->
-- student@daiict.ac.in -> password123
-- company@gmail.com -> companyPass123
-- admin@gmail.com -> adminSecure123
-- 202412117@daiict.ac.in -> parthiv69
*/

-- Map users to roles in the user_roles table
INSERT INTO "User_roles" (user_id, role_id)
SELECT u.id, r.id
FROM "User" u
JOIN "Roles" r ON (
    (u.email = 'student@daiict.ac.in' AND r.name = 'Student') OR
    (u.email = 'company@gmail.com' AND r.name = 'Company') OR
    (u.email = 'admin@gmail.com' AND r.name = 'Admin') OR 
    (u.email = '202412117@daiict.ac.in' AND r.name = 'Admin')
);
