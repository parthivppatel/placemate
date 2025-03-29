-- Map users to roles in the user_roles table
INSERT INTO "User_roles" (user_id, role_id)
SELECT u.id, r.id
FROM "User" u
JOIN "Roles" r ON (
    (u.email = 'student@daiict.ac.in' AND r.name = 'Student') OR
    (u.email = 'company@gmail.com' AND r.name = 'Company') OR
    (u.email = 'admin@gmail.com' AND r.name = 'Admin')
);
