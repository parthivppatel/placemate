 -- Insert academic courses with manual IDs

INSERT INTO "courses" (id, branch_id, name, is_active) VALUES
-- Information Technology (branch_id = 1)
(1, 1, 'B.Sc IT', true),
(2, 1, 'M.Sc IT', true),
(3, 1, 'Diploma in Information Technology', true),

-- Computer Science (branch_id = 2)
(4, 2, 'B.Sc Computer Science', true),
(5, 2, 'M.Sc Computer Science', true),
(6, 2, 'B.Tech Computer Science', true),
(7, 2, 'M.Tech Computer Science', true),
(8, 2, 'Diploma in Computer Science', true),

-- Electronics and Communication (branch_id = 3)
(9, 3, 'B.E Electronics and Communication', true),
(10, 3, 'M.E Electronics and Communication', true),

-- Electrical Engineering (branch_id = 4)
(11, 4, 'B.E Electrical Engineering', true),
(12, 4, 'M.E Electrical Engineering', true),

-- Mechanical Engineering (branch_id = 5)
(13, 5, 'B.E Mechanical Engineering', true),
(14, 5, 'M.E Mechanical Engineering', true),

-- Civil Engineering (branch_id = 6)
(15, 6, 'B.E Civil Engineering', true),
(16, 6, 'M.E Civil Engineering', true),

-- Data Science (branch_id = 7)
(17, 7, 'B.Sc Data Science', true),
(18, 7, 'M.Sc Data Science', true),

-- Artificial Intelligence (branch_id = 8)
(19, 8, 'B.Sc Artificial Intelligence', true),
(20, 8, 'M.Sc Artificial Intelligence', true),

-- Cybersecurity (branch_id = 9)
(21, 9, 'B.Sc Cybersecurity', true),
(22, 9, 'M.Sc Cybersecurity', true),

-- Commerce (branch_id = 10)
(23, 10, 'B.Com with Computer Applications', true),

-- Management (branch_id = 11)
(24, 11, 'BBA', true),
(25, 11, 'MBA in Information Systems', true),
(26, 11, 'MBA in Technology Management', true),

-- Science (branch_id = 12)
(27, 12, 'B.Sc General', true),
(28, 12, 'M.Sc General', true),

-- Arts (branch_id = 13)
(29, 13, 'BA in English', true),
(30, 13, 'MA in English', true);
